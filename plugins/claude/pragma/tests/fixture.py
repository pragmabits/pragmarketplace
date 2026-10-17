"""Fictitious Claude Code transcripts for the gate's tests."""

from __future__ import annotations

import json
from pathlib import Path


class Transcript:
    """Writes a Claude Code style JSONL transcript, one entry per call."""

    def __init__(self, path: Path, model: str = "claude-test-model"):
        self.path = path
        self.model = model
        self.n = 0
        path.write_text("")

    def _write(self, entry: dict):
        self.n += 1
        entry.setdefault("uuid", f"u{self.n}")
        entry.setdefault("isSidechain", False)
        with open(self.path, "a") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")

    def _assistant(self, block: dict):
        self._write({"type": "assistant", "message": {"role": "assistant", "model": self.model, "content": [block]}})

    def user(self, text, prompt_id):
        self._write({"type": "user", "promptId": prompt_id, "origin": {"kind": "human"},
                     "message": {"role": "user", "content": text}})

    def assistant(self, text):
        self._assistant({"type": "text", "text": text})

    def thinking(self, text):
        self._assistant({"type": "thinking", "thinking": text})

    def _thinking_entry(self, text, display):
        entry = {"type": "assistant", "message": {"role": "assistant", "model": self.model, "content": [
            {"type": "thinking", "thinking": text, "signature": "c2lnbmF0dXJl"}]}}
        if display:
            entry["thinkingDisplay"] = display
        self._write(entry)

    def reasoning(self, display=None):
        """The agent's reasoning, as Claude Code records it: a thinking block with no text."""
        self._thinking_entry("", display)

    def narration(self, text, display=None):
        """Narration: a thinking block with text, which the screen shows as a summary."""
        self._thinking_entry(text, display)

    def tool(self, tool_id, name, tool_input, result, prompt_id, is_error=False):
        self._assistant({"type": "tool_use", "id": tool_id, "name": name, "input": tool_input})
        self._write({"type": "user", "promptId": prompt_id,
                     "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_id,
                                                              "content": result, "is_error": is_error}]}})

    def answer(self, prompt_id, n, question, choice):
        """AskUserQuestion answered by the user."""
        self.tool(f"toolu_ask{n}", "AskUserQuestion", {"questions": [{"question": question}]},
                  f'Your questions have been answered: "{question}"="{choice}". '
                  "You can now continue with these answers in mind.", prompt_id)

    def refused_question(self, prompt_id, n, questions, reason):
        """AskUserQuestion refused by a PreToolUse hook, as Claude Code records it."""
        self.tool(f"toolu_ask{n}", "AskUserQuestion", {"questions": questions},
                  f"PreToolUse:AskUserQuestion hook error: {reason}", prompt_id, is_error=True)

    def attach_file(self, path, text):
        """A file the user mentioned with @, as Claude Code attaches it."""
        self._write({"type": "attachment", "attachment": {"type": "file", "filename": path, "displayPath": path,
                     "content": {"type": "text", "file": {"filePath": path, "content": text}}}})

    def context(self, git_status, email="person@example.com"):
        """The session context Claude Code injects (git status, the user's address)."""
        self._write({"type": "attachment", "attachment": {"type": "session_context", "context": {
            "userEmail": f"The user's email address is {email}.", "gitStatus": git_status}}})

    def stop_feedback(self, text, prompt_id):
        self._write({"type": "user", "isMeta": True, "promptId": prompt_id,
                     "message": {"role": "user", "content": "Stop hook feedback:\n" + text}})
