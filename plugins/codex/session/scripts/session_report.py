#!/usr/bin/env python3
"""Prepare the path and metadata of a session report in <project-root>/.harness/sessions/.

Run by the report skill when the user has asked for a report file. It creates
the sessions directory (and nothing else) and prints JSON the agent uses as
facts:

  output_path, session_id      where to write; a taken name gets -2, -3, ...
                               so no report, from either integration, is replaced
  timestamp_utc                one clock read; the filename comes from it too
  git_user                     for the Git user field and the filename prefix
  head_observed, head_subject  HEAD when the report was prepared, not the
                               session's starting point
  repository_state             read now: upstream ahead/behind (as this clone
                               last saw the remote, not fetched), staged,
                               unstaged and untracked counts, stashes, an
                               operation in progress
  status_short                 working tree as context only: it can hold work
                               that predates the session or is someone else's
  origin                       the authorship header lines (see report_origin)
  language, title_hint         from the arguments

There is no Branch field and no list of recent commits: neither is evidence of
what this session did, and the shared report contract leaves both out.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SESSIONS_REL = Path(".harness") / "sessions"
LANG_RE = re.compile(r"^[a-z]{2}(?:-[A-Z]{2})?$")
PLUGIN_ROOT = Path(__file__).resolve().parent.parent


def run_git(repo: Path, args: list[str]) -> str | None:
    result = subprocess.run(
        ["git", *args], cwd=repo, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False,
    )
    if result.returncode != 0:
        return None
    return result.stdout.rstrip("\n")


def project_root() -> Path:
    """Git root of the current directory, then CODEX_PROJECT_DIR, then cwd."""
    top = run_git(Path.cwd(), ["rev-parse", "--show-toplevel"])
    if top:
        return Path(top)
    env_root = os.environ.get("CODEX_PROJECT_DIR")
    if env_root and Path(env_root).is_dir():
        return Path(env_root)
    return Path.cwd()


def sanitize_user(value: str) -> str:
    cleaned = re.sub(r"\s+", "-", value.strip().lower())
    cleaned = re.sub(r"[^a-z0-9._-]", "", cleaned)
    if not cleaned or cleaned == "unknown":
        return "unknown-user"
    return cleaned


def plugin_version() -> str:
    try:
        return json.loads((PLUGIN_ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))["version"]
    except (OSError, ValueError, KeyError):
        return ""


def report_origin() -> dict[str, Any]:
    """Authorship header values. Each one rests on a stated source or is unknown.

    Harness: this script is part of the Codex plugin and runs from its report
    skill, which only Codex loads. The CODEX_* variables Codex sets in its shells
    (CODEX_THREAD_ID, CODEX_VERSION) are not in the official documentation, so
    nothing here depends on them.

    No Model line: Codex documents no way for a script to learn the model of the
    current turn. The session rollout files are undocumented, and their
    turn_context records the requested model, which a server-side reroute can
    differ from; configured defaults are not the model of this execution. A
    field that could only ever say "unknown" is left out instead.

    No Harness version line either: no documented source for the running
    process (a `codex` on PATH may be another one).
    """
    version = plugin_version()
    return {
        "lines": [
            "**Harness:** codex",
            f"**Report generator:** session/codex{(' ' + version) if version else ''}",
        ],
        "sources": {
            "harness": "this script belongs to the Codex integration",
            "model": "no line: no documented source gives a script the model of the current turn",
            "harness_version": "no line: no documented source for the running process",
        },
    }


def repository_state(root: Path, status_short: str) -> dict[str, Any]:
    """The repository's state, read now: the only basis for statements about it.

    Remote-tracking refs are this clone's last view of the remote; nothing is
    fetched, so the remote itself is not seen. No branch name is reported.
    """
    if run_git(root, ["symbolic-ref", "-q", "HEAD"]) is None:
        upstream = "HEAD is detached; there is no upstream branch to compare with"
    else:
        counts = run_git(root, ["rev-list", "--left-right", "--count", "@{upstream}...HEAD"])
        if counts:
            behind, ahead = counts.split()
            upstream = (f"{ahead} local commit(s) not in the upstream branch, {behind} upstream commit(s) "
                        "not here — as this clone last saw the remote; nothing was fetched")
        else:
            upstream = "no upstream branch configured"
    staged = unstaged = untracked = 0
    for line in status_short.splitlines():
        if line.startswith("??"):
            untracked += 1
            continue
        staged += line[:1] != " "
        unstaged += line[1:2] != " "
    operation = "none"
    for marker, name in (("MERGE_HEAD", "merge"), ("rebase-merge", "rebase"), ("rebase-apply", "rebase"),
                         ("CHERRY_PICK_HEAD", "cherry-pick"), ("REVERT_HEAD", "revert"), ("BISECT_LOG", "bisect")):
        path = run_git(root, ["rev-parse", "--git-path", marker])
        if path and (root / path).exists():
            operation = name
            break
    stashes = run_git(root, ["stash", "list"]) or ""
    return {
        "upstream": upstream,
        "staged": staged,
        "unstaged": unstaged,
        "untracked": untracked,
        "stash_entries": len(stashes.splitlines()),
        "operation_in_progress": operation,
    }


def parse_report_args(raw_args: list[str]) -> dict[str, str]:
    language = ""
    title_words: list[str] = []
    index = 0
    while index < len(raw_args):
        arg = raw_args[index]
        if arg == "--lang" or arg.startswith("--lang="):
            value = arg.split("=", 1)[1] if "=" in arg else (raw_args[index + 1] if index + 1 < len(raw_args) else "")
            if not LANG_RE.match(value):
                raise SystemExit(f"error: --lang expects xx or xx-YY (got: {value or '<missing>'})")
            language = value
            index += 1 if "=" in arg else 2
            continue
        title_words.append(arg)
        index += 1
    return {"language": language, "title_hint": " ".join(title_words).strip()}


def prepare(raw_args: list[str]) -> dict[str, Any]:
    parsed = parse_report_args(raw_args)
    root = project_root()
    sessions_dir = root / SESSIONS_REL
    sessions_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    git_user = run_git(root, ["config", "user.name"]) or "unknown"
    session_id = f"{sanitize_user(git_user)}-{stamp[:-1]}"
    suffix = 2
    while (sessions_dir / f"{session_id}.md").exists():
        if suffix > 99:
            raise SystemExit(f"error: more than 98 reports named {session_id} already exist")
        session_id = f"{sanitize_user(git_user)}-{stamp[:-1]}-{suffix}"
        suffix += 1

    in_git = run_git(root, ["rev-parse", "--is-inside-work-tree"]) == "true"
    head = run_git(root, ["rev-parse", "--short", "HEAD"]) if in_git else None
    status_short = (run_git(root, ["status", "--short"]) or "") if in_git else ""
    return {
        "output_path": str(sessions_dir / f"{session_id}.md"),
        "session_id": session_id,
        "timestamp_utc": stamp,
        "git_user": git_user,
        "head_observed": head or ("no commits yet" if in_git else "not a git repository"),
        "head_subject": (run_git(root, ["log", "-1", "--format=%s"]) or "") if head else "",
        "status_short": status_short,
        "repository_state": repository_state(root, status_short) if in_git else None,
        "origin": report_origin(),
        "language": parsed["language"],
        "title_hint": parsed["title_hint"],
    }


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] == "prepare":
        args = args[1:]
    print(json.dumps(prepare(args), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
