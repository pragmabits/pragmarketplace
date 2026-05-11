#!/usr/bin/env python3
"""Prepare metadata and output paths for agent-agnostic session reports."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


LANG_RE = re.compile(r"^[a-z]{2}(?:-[A-Z]{2})?$")


def run_git(repo: Path, args: list[str], fallback: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode != 0:
        return fallback
    output = result.stdout.strip()
    return output if output else fallback


def resolve_repo_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip()).resolve()

    env_root = os.environ.get("CODEX_PROJECT_DIR")
    if env_root and Path(env_root).is_dir():
        return Path(env_root).resolve()
    return Path.cwd().resolve()


def sanitize_user(value: str) -> str:
    cleaned = re.sub(r"\s+", "-", value.strip().lower())
    cleaned = re.sub(r"[^a-z0-9._-]", "", cleaned)
    if not cleaned or cleaned == "unknown":
        return "unknown-user"
    return cleaned


def parse_report_args(raw_args: list[str]) -> dict[str, Any]:
    language = ""
    title_words: list[str] = []
    index = 0
    while index < len(raw_args):
        arg = raw_args[index]
        if arg == "--lang":
            value = raw_args[index + 1] if index + 1 < len(raw_args) else ""
            if not LANG_RE.match(value):
                raise SystemExit(f"error: --lang expects xx or xx-YY (got: {value or '<missing>'})")
            language = value
            index += 2
            continue
        if arg.startswith("--lang="):
            value = arg.split("=", 1)[1]
            if not LANG_RE.match(value):
                raise SystemExit(f"error: --lang expects xx or xx-YY (got: {value or '<missing>'})")
            language = value
            index += 1
            continue
        title_words.append(arg)
        index += 1
    return {
        "language": language,
        "title_hint": " ".join(title_words).strip(),
    }


def prepare(raw_args: list[str]) -> dict[str, Any]:
    parsed = parse_report_args(raw_args)
    repo = resolve_repo_root()
    sessions_dir = repo / ".sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%dT%H%M%SZ")
    filename_timestamp = now.strftime("%Y-%m-%dT%H%M%S")
    git_user = run_git(repo, ["config", "user.name"], "unknown")
    safe_user = sanitize_user(git_user)
    filename = f"{safe_user}-{filename_timestamp}.md"

    return {
        "repo_root": str(repo),
        "sessions_dir": str(sessions_dir),
        "output_path": str(sessions_dir / filename),
        "filename": filename,
        "timestamp_utc": timestamp,
        "timestamp_filename": filename_timestamp,
        "git_user": git_user,
        "sanitized_git_user": safe_user,
        "branch": run_git(repo, ["branch", "--show-current"], "unknown"),
        "base_commit": run_git(repo, ["log", "-1", "--format=%h (%s)"], "no-commits"),
        "commits_last_day": run_git(
            repo,
            ["log", "--oneline", "--since=1 day ago"],
            "(none or not a git repo)",
        ),
        "diff_stat": run_git(repo, ["diff", "--stat"], ""),
        "status_short": run_git(repo, ["status", "--short"], ""),
        "args": raw_args,
        "language": parsed["language"],
        "title_hint": parsed["title_hint"],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare metadata for an agent-agnostic session report.")
    parser.add_argument("mode", nargs="?", default="prepare", choices=["prepare"])
    parser.add_argument("report_args", nargs=argparse.REMAINDER)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = prepare(args.report_args)
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
