"""Claude Code adapter: an incremental index over a session transcript (JSONL).

The index keeps references only (kind, line, byte offset, length, ids), never
message text, so the gate's state holds no copy of the conversation. Each hook
call parses only the bytes appended since the previous call; item text is read
back from the transcript by offset when an evidence package is built.

Item kinds (the letter is the reference prefix; the number is the line):
  U  a message the user typed           N  the user's answer to AskUserQuestion
  A  text the assistant showed          T  a tool call
  R  a tool result                      H  feedback returned by a Stop hook
  I  an interruption by the user        S  a message the harness injected
  M  a file the user attached with @    C  context the harness showed the agent
                                           (git status, environment, date)
Thinking blocks and meta entries other than Stop hook feedback are skipped.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

INDEX_VERSION = 2
STOP_FEEDBACK = "Stop hook feedback:"
CONTEXT_TYPES = ("session_context", "environment", "date")


def _text_blocks(content) -> str:
    if isinstance(content, str):
        return content
    parts = []
    if isinstance(content, list):
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text":
                parts.append(block.get("text", ""))
            elif block.get("type") == "image":
                parts.append("[image]")
    return "\n".join(parts)


def _classify(entry: dict, tool_names: dict) -> list[dict]:
    """Return the index items one transcript entry contributes."""
    etype = entry.get("type")
    if entry.get("isSidechain"):
        return []
    if etype == "attachment":
        att = entry.get("attachment") or {}
        if att.get("type") == "file":
            return [{"kind": "M"}]
        if att.get("type") in CONTEXT_TYPES:
            return [{"kind": "C", "ctype": att["type"]}]
        return []
    if etype not in ("user", "assistant"):
        return []
    message = entry.get("message") or {}
    content = message.get("content")
    items = []
    if etype == "assistant":
        if not isinstance(content, list):
            return []
        for pos, block in enumerate(content):
            if not isinstance(block, dict):
                continue
            if block.get("type") == "text" and block.get("text", "").strip():
                items.append({"kind": "A", "block": pos})
            elif block.get("type") == "tool_use":
                tool_names[block.get("id")] = block.get("name")
                items.append({"kind": "T", "block": pos, "tool_id": block.get("id"), "name": block.get("name")})
        return items
    # user entries
    prompt_id = entry.get("promptId")
    if isinstance(content, list) and any(isinstance(b, dict) and b.get("type") == "tool_result" for b in content):
        for pos, block in enumerate(content):
            if isinstance(block, dict) and block.get("type") == "tool_result":
                tool_id = block.get("tool_use_id")
                # A refused question comes back as an error result: the user never saw it.
                answered = tool_names.get(tool_id) == "AskUserQuestion" and not block.get("is_error")
                kind = "N" if answered else "R"
                items.append({"kind": kind, "block": pos, "tool_id": tool_id, "prompt_id": prompt_id,
                              "is_error": bool(block.get("is_error"))})
        return items
    text = _text_blocks(content)
    if not text.strip():
        return []
    if entry.get("isMeta"):
        if text.startswith(STOP_FEEDBACK):
            return [{"kind": "H", "prompt_id": prompt_id}]
        return []
    if text.startswith("[Request interrupted"):
        return [{"kind": "I", "prompt_id": prompt_id}]
    origin = entry.get("origin")
    if isinstance(origin, dict) and origin.get("kind") not in (None, "human"):
        return [{"kind": "S", "prompt_id": prompt_id}]
    return [{"kind": "U", "prompt_id": prompt_id}]


def update_index(index_path: Path, transcript_path: str) -> dict:
    """Bring the stored index up to date with the transcript and return it."""
    index = None
    try:
        index = json.loads(index_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        index = None
    try:
        st = os.stat(transcript_path)
    except OSError:
        return {"version": INDEX_VERSION, "path": transcript_path, "missing": True, "items": [], "lines": 0}
    if (not isinstance(index, dict) or index.get("version") != INDEX_VERSION
            or index.get("path") != transcript_path or index.get("inode") != st.st_ino
            or index.get("parsed_bytes", 0) > st.st_size):
        index = {"version": INDEX_VERSION, "path": transcript_path, "inode": st.st_ino,
                 "parsed_bytes": 0, "lines": 0, "model": None, "items": [], "tool_names": {}}
    tool_names = index.setdefault("tool_names", {})
    with open(transcript_path, "rb") as fh:
        fh.seek(index["parsed_bytes"])
        data = fh.read()
    offset = index["parsed_bytes"]
    pos = 0
    while True:
        nl = data.find(b"\n", pos)
        if nl < 0:
            break  # a partial last line is parsed on a later call
        raw = data[pos:nl]
        line_off = offset + pos
        index["lines"] += 1
        line = index["lines"]
        pos = nl + 1
        if not raw.strip():
            continue
        try:
            entry = json.loads(raw)
        except ValueError:
            continue
        if not isinstance(entry, dict):
            continue
        if entry.get("type") == "assistant":
            model = (entry.get("message") or {}).get("model")
            if isinstance(model, str) and model and not model.startswith("<"):
                index["model"] = model
        found = _classify(entry, tool_names)
        for n, item in enumerate(found, 1):
            suffix = f"-{n}" if len(found) > 1 else ""
            item.update({"ref": f"{item['kind']}{line}{suffix}", "line": line, "off": line_off, "len": len(raw)})
            index["items"].append(item)
    index["parsed_bytes"] = offset + pos
    # Names only decide whether a result is an answer to AskUserQuestion.
    index["tool_names"] = {k: v for k, v in tool_names.items() if v == "AskUserQuestion"}
    tmp = index_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(index, separators=(",", ":")), encoding="utf-8")
    os.replace(tmp, index_path)
    return index


class Loader:
    """Reads an indexed item's content back from the transcript."""

    def __init__(self, transcript_path: str):
        self.path = transcript_path
        self._fh = None

    def __enter__(self):
        self._fh = open(self.path, "rb")
        return self

    def __exit__(self, *exc):
        if self._fh:
            self._fh.close()

    def _entry(self, item: dict) -> dict:
        self._fh.seek(item["off"])
        return json.loads(self._fh.read(item["len"]))

    def text(self, item: dict) -> dict:
        """Return the item's visible content as {'text': ...} or tool fields."""
        try:
            entry = self._entry(item)
        except (OSError, ValueError):
            return {"text": "[unreadable transcript entry]"}
        content = (entry.get("message") or {}).get("content")
        kind = item["kind"]
        if kind in ("A", "T") and isinstance(content, list) and item.get("block", 0) < len(content):
            block = content[item["block"]]
            if kind == "A":
                return {"text": block.get("text", "")}
            return {"tool": block.get("name"), "input": block.get("input")}
        if kind == "M":
            att = entry.get("attachment") or {}
            file = (att.get("content") or {}).get("file") or {}
            return {"file": att.get("displayPath") or att.get("filename"), "text": file.get("content", "")}
        if kind == "C":
            att = entry.get("attachment") or {}
            if att.get("type") == "session_context":
                # The git status the agent saw; the user's address stays out.
                return {"text": str((att.get("context") or {}).get("gitStatus", ""))}
            if att.get("type") == "environment":
                return {"text": json.dumps(att.get("snapshot"), ensure_ascii=False)}
            return {"text": str(att.get("date", ""))}
        if kind in ("R", "N") and isinstance(content, list) and item.get("block", 0) < len(content):
            block = content[item["block"]]
            return {"text": _text_blocks(block.get("content")), "is_error": bool(block.get("is_error"))}
        text = _text_blocks(content)
        if kind == "H" and text.startswith(STOP_FEEDBACK):
            text = text[len(STOP_FEEDBACK):].lstrip()
        return {"text": text}
