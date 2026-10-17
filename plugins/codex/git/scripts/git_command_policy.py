#!/usr/bin/env python3
"""Codex hook policy for git commands used by the commit workflow."""

from __future__ import annotations

import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


CONTROL_TOKENS = {"&&", "||", ";", "|"}
SHELLS = {"bash", "sh", "zsh"}
SHELL_FLAGS = {"-c", "-lc"}
DIRECTORY_CHANGES = {"cd", "pushd"}


def load_payload() -> dict[str, Any]:
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return {}
        payload = json.loads(raw)
        return payload if isinstance(payload, dict) else {}
    except json.JSONDecodeError:
        return {}


def command_from_payload(payload: dict[str, Any]) -> str:
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, dict):
        return ""
    command = tool_input.get("command", tool_input.get("cmd", ""))
    return command if isinstance(command, str) else ""


def tokenize(command: str) -> list[str]:
    try:
        lexer = shlex.shlex(command, posix=True, punctuation_chars=True)
        lexer.whitespace_split = True
        return list(lexer)
    except ValueError:
        return command.split()


def split_segments(tokens: list[str]) -> list[list[str]]:
    segments: list[list[str]] = []
    current: list[str] = []
    for token in tokens:
        if token in CONTROL_TOKENS:
            if current:
                segments.append(current)
                current = []
            continue
        current.append(token)
    if current:
        segments.append(current)
    return segments


def shell_wrapper_reason(tokens: list[str]) -> str | None:
    if len(tokens) >= 3 and tokens[0] in SHELLS and tokens[1] in SHELL_FLAGS:
        script = " ".join(tokens[2:])
        if "git" in script:
            return "Run git commands directly instead of through a shell wrapper so Codex rules and hooks can inspect them."
    return None


def first_git_segment(segment: list[str]) -> list[str] | None:
    try:
        index = segment.index("git")
    except ValueError:
        return None
    return segment[index:]


def directory_change(segment: list[str]) -> list[str] | None:
    """Return the segment from its cd or pushd on, or None when it starts with neither."""
    start = 0
    while start < len(segment) and segment[start] == "(":
        start += 1
    if start < len(segment) and segment[start] in DIRECTORY_CHANGES:
        return segment[start:]
    return None


def repository_root(cwd: Any) -> str | None:
    if not isinstance(cwd, str) or not Path(cwd).is_dir():
        return None
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    root = result.stdout.strip()
    return root if result.returncode == 0 and root else None


def directory_change_reason(root: str | None) -> str:
    target = f"the repository root ({root})" if root else "the repository root"
    return (
        "cd before git in one command is blocked; run git with the command's working directory "
        f"(workdir) set to {target} instead. A cd does not carry over to the next command."
    )


def git_command_reason(git_tokens: list[str]) -> str | None:
    if len(git_tokens) < 2:
        return None

    if "-C" in git_tokens[1:]:
        return "git -C is blocked; run git from the repository root."

    subcommand_index = 1
    while subcommand_index < len(git_tokens) and git_tokens[subcommand_index].startswith("-"):
        subcommand_index += 1
    if subcommand_index >= len(git_tokens):
        return None

    subcommand = git_tokens[subcommand_index]
    args = git_tokens[subcommand_index + 1 :]

    if subcommand == "add" and any(arg in {"-p", "--patch"} for arg in args):
        return "Interactive patch staging is blocked; stage whole files with git add -- <files>."

    if subcommand == "config" and any(arg in {"user.name", "user.email"} for arg in args):
        return "Changing git user.name or user.email is blocked; use the existing repository identity."

    if subcommand == "commit" and any(arg in {"-n", "--no-verify"} for arg in args):
        return "Bypassing git hooks is blocked; fix the hook rejection instead."

    if subcommand == "push" and any(arg in {"-f", "--force", "--force-with-lease"} for arg in args):
        return "Force push is outside the commit workflow and must be handled explicitly by the user."

    if subcommand == "reset" and "--hard" in args:
        return "git reset --hard is destructive and outside the commit workflow."

    if subcommand == "clean" and any(arg.startswith("-") and "f" in arg for arg in args):
        return "git clean -f is destructive and outside the commit workflow."

    if subcommand == "checkout" and "--" in args:
        return "git checkout -- <path> can discard worktree changes and is outside the commit workflow."

    if subcommand == "restore" and any(not arg.startswith("-") for arg in args):
        return "git restore <path> can discard worktree changes and is outside the commit workflow."

    return None


def deny_payload(event: str, reason: str) -> dict[str, Any]:
    if event == "PermissionRequest":
        return {
            "systemMessage": reason,
            "hookSpecificOutput": {
                "hookEventName": "PermissionRequest",
                "decision": {
                    "behavior": "deny",
                    "message": reason,
                },
            },
        }
    return {
        "systemMessage": reason,
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": reason,
        },
    }


def main() -> int:
    payload = load_payload()
    event = str(payload.get("hook_event_name") or "PreToolUse")
    command = command_from_payload(payload)
    if not command.strip():
        return 0

    tokens = tokenize(command)
    reason = shell_wrapper_reason(tokens)
    if reason:
        print(json.dumps(deny_payload(event, reason)))
        return 0

    # Codex hands hooks the session directory, not the command's workdir, so a
    # git command run below the root cannot be told apart here; only a cd
    # before git, which the command itself shows, is blocked.
    moved = False
    for segment in split_segments(tokens):
        change = directory_change(segment)
        # A newline does not split segments: "cd web\ngit status" is one, and
        # the token after cd is its target, not a command.
        if change is not None:
            moved = True
            segment = change[2:]
        git_tokens = first_git_segment(segment)
        if not git_tokens:
            continue
        if moved:
            print(json.dumps(deny_payload(event, directory_change_reason(repository_root(payload.get("cwd"))))))
            return 0
        reason = git_command_reason(git_tokens)
        if reason:
            print(json.dumps(deny_payload(event, reason)))
            return 0

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
