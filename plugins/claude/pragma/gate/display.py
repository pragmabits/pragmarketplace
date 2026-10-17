"""Claude Code adapter: assistant text shown on screen that the transcript may not hold yet.

Claude Code writes the transcript asynchronously. When the PreToolUse of a
question runs, the message that holds the question, and the text the agent
wrote right before it, are usually not in the file yet. MessageDisplay hands
each batch of lines shown on screen to a hook; this module keeps them, per
message, so the question review sees what the user saw.

This is the only part of the gate's state that holds message text, so it is
kept small and short-lived:
  - one request at a time: a new prompt, or a batch from another prompt,
    empties it;
  - every review drops the messages the transcript already holds;
  - at most MAX_MESSAGES messages, the newest, each cut to KEEP_CHARS
    characters (its head and its tail, as evidence.cut keeps them);
  - session start empties it, and the retention prune removes the session.

Layout under the state root:
  sessions/<session>/shown.json  the captured messages of the current request
  sessions/<session>/shown.lock  guards it; never the review lock, which a
                                 review holds for up to a minute, while
                                 Claude Code waits on this hook to show a batch
  display.seen                   touched on every batch: this installation
                                 delivers MessageDisplay, so a message with
                                 nothing captured had no text
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

from . import state, transcript

FILE = "shown.json"
LOCK = "shown.lock"
SEEN = "display.seen"
MAX_MESSAGES = 6
KEEP_CHARS = 6000  # above evidence.CAP_ASSISTANT, so the package cuts as if it had the whole text
PROBE = 200  # characters compared at each end to tell whether the transcript holds a message
LOCK_WAIT_S = 1.0

NOT_CAPTURED = ("the assistant message that holds this question is not in the transcript yet, and no text shown "
                "on screen could be captured: text the agent showed with the question may be missing")
INCOMPLETE = ("the last text shown on screen was still being displayed when this review ran: its end may be "
              "missing from the last D item")


def _load(sdir: Path) -> dict | None:
    try:
        data = json.loads((sdir / FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data if isinstance(data, dict) and isinstance(data.get("messages"), list) else None


def _save(sdir: Path, data: dict) -> None:
    tmp = sdir / (FILE + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    os.replace(tmp, sdir / FILE)


def _remove(sdir: Path) -> None:
    try:
        (sdir / FILE).unlink()
    except FileNotFoundError:
        pass


def _append(msg: dict, delta: str) -> None:
    if not msg["dropped"]:
        whole = msg["head"] + delta
        if len(whole) <= KEEP_CHARS:
            msg["head"] = whole
            return
        msg["head"], tail = whole[:KEEP_CHARS * 2 // 3], whole[KEEP_CHARS * 2 // 3:]
    else:
        tail = msg["tail"] + delta
    room = KEEP_CHARS - len(msg["head"])
    msg["dropped"] += max(0, len(tail) - room)
    msg["tail"] = tail[-room:]


def record(root: Path, sdir: Path, data: dict) -> None:
    """Keep one MessageDisplay batch. Prints nothing: the screen shows the original text."""
    try:
        (root / SEEN).touch()
    except OSError:
        pass
    delta, mid = data.get("delta"), data.get("message_id")
    if not isinstance(delta, str) or not isinstance(mid, str):
        return
    with state.locked(sdir, LOCK_WAIT_S, LOCK) as got:
        if not got:
            return
        shown = _load(sdir)
        if shown is None or shown.get("prompt_id") != data.get("prompt_id"):
            shown = {"prompt_id": data.get("prompt_id"), "messages": []}
        msgs = shown["messages"]
        msg = next((m for m in msgs if m.get("id") == mid), None)
        if msg is None:
            if not delta.strip():
                return
            msg = {"id": mid, "head": "", "tail": "", "dropped": 0, "final": False}
            msgs.append(msg)
            del msgs[:-MAX_MESSAGES]
        _append(msg, delta)
        msg["final"] = msg["final"] or bool(data.get("final"))
        _save(sdir, shown)


def clear(sdir: Path) -> None:
    """Forget everything captured in this session."""
    with state.locked(sdir, LOCK_WAIT_S, LOCK):
        _remove(sdir)


def active(root: Path, retention_days: float) -> bool:
    """Whether this installation has delivered MessageDisplay recently."""
    try:
        return time.time() - (root / SEEN).stat().st_mtime < float(retention_days) * 86400
    except OSError:
        return False


def _messages(sdir: Path, prompt_id) -> list:
    shown = _load(sdir)
    return shown["messages"] if shown is not None and shown.get("prompt_id") == prompt_id else []


def _flat(text: str) -> str:
    return " ".join(text.split())


def _turn_texts(items: list, loader, prompt_id) -> list:
    start = next((p for p, i in enumerate(items)
                  if i["kind"] == "U" and prompt_id and i.get("prompt_id") == prompt_id), None)
    if start is None:
        start = max((p for p, i in enumerate(items) if i["kind"] == "U"), default=-1)
    return [loader.text(i).get("text", "") for i in items[start + 1:] if i["kind"] == "A"]


def tidy(sdir: Path, index: dict, prompt_id) -> list:
    """Drop what the transcript already holds, and other requests' text; return the rest."""
    with state.locked(sdir, LOCK_WAIT_S, LOCK) as got:
        shown = _load(sdir)
        if shown is None:
            return []
        if not got:  # a capture is stuck: read, change nothing
            return shown["messages"] if shown.get("prompt_id") == prompt_id else []
        if shown.get("prompt_id") != prompt_id:
            _remove(sdir)
            return []
        with transcript.Loader(index["path"]) as loader:
            joined = _flat("\n".join(_turn_texts(index["items"], loader, prompt_id)))
        kept = []
        for m in shown["messages"]:
            head = _flat(m["head"])[:PROBE]
            tail = _flat(m["tail"] or m["head"])[-PROBE:]
            if not (head and head in joined and tail in joined):
                kept.append(m)
        if not kept:
            _remove(sdir)
        elif len(kept) < len(shown["messages"]):
            shown["messages"] = kept
            _save(sdir, shown)
        return kept


def settle(sdir: Path, prompt_id, wait_s: float, caught_up) -> int:
    """Wait for the end of the message being shown; return the milliseconds waited.

    The last batch of a message's text reaches MessageDisplay a few hundred
    milliseconds after the PreToolUse of the call that ends the message has
    started. The wait ends when a message has received its last batch since
    the wait began and the newest one is complete, when caught_up() says the
    transcript now holds the call, or after wait_s.
    """
    started = time.monotonic()
    before = {m.get("id"): m.get("final") for m in _messages(sdir, prompt_id)}
    next_check = started + 0.2
    while True:
        msgs = _messages(sdir, prompt_id)
        if msgs and msgs[-1].get("final") and any(m.get("final") and not before.get(m.get("id")) for m in msgs):
            break
        now = time.monotonic()
        if now - started >= wait_s:
            break
        if now >= next_check:
            if caught_up():
                break
            next_check = now + 0.2
        time.sleep(0.05)
    return int((time.monotonic() - started) * 1000)


def for_question(root: Path, sdir: Path, cfg: dict, index: dict, tool_use_id, prompt_id) -> tuple:
    """Return (index, D items for the package, notes, log record) for a question review."""
    def has_call(idx):
        return bool(tool_use_id) and any(i["kind"] == "T" and i.get("tool_id") == tool_use_id for i in idx["items"])

    def caught_up():
        nonlocal index
        index = transcript.update_index(sdir / "index.json", index["path"])
        return has_call(index)

    info = {"gap": not has_call(index), "waited_ms": 0}
    notes = []
    if info["gap"]:
        if active(root, cfg["retention_days"]):
            info["waited_ms"] = settle(sdir, prompt_id, float(cfg["display_wait_s"]), caught_up)
        else:
            notes.append(NOT_CAPTURED)
    msgs = tidy(sdir, index, prompt_id)
    if msgs and not msgs[-1].get("final"):
        notes.append(INCOMPLETE)
    items = [{"kind": "D", "ref": f"D{n}", "head": m["head"], "tail": m["tail"], "dropped": m["dropped"]}
             for n, m in enumerate(msgs, 1)]
    info["shown"] = len(items)
    return index, items, notes, info
