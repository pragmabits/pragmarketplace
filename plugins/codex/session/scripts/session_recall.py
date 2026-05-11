#!/usr/bin/env python3
"""Recall and search agent-agnostic session reports."""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


TIMESTAMP_RE = re.compile(r"(\d{4}-\d{2}-\d{2}T\d{6})$")
TITLE_RE = re.compile(r"^# Session Report: (.*)$", re.MULTILINE)
TIMESTAMP_LINE_RE = re.compile(r"^\*\*Timestamp \(UTC\):\*\* (.*)$", re.MULTILINE)
BRANCH_RE = re.compile(r"^\*\*Branch:\*\* `?([^`\n]+)`?$", re.MULTILINE)


@dataclass(frozen=True)
class Session:
    path: Path
    session_id: str
    title: str
    timestamp: str
    branch: str
    status: str


def git_root() -> Path:
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


def sessions_dir() -> Path:
    return git_root() / ".sessions"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


def first_match(pattern: re.Pattern[str], text: str, fallback: str = "") -> str:
    match = pattern.search(text)
    if not match:
        return fallback
    return match.group(1).strip()


def session_user(session_id: str) -> str:
    return re.sub(r"-\d{4}-\d{2}-\d{2}T\d{6}$", "", session_id)


def goal_status(text: str) -> str:
    in_contract = False
    for line in text.splitlines():
        if line.startswith("## Session contract"):
            in_contract = True
            continue
        if in_contract and line.startswith("## "):
            break
        if in_contract and line.startswith("**Goal status:**"):
            return line.removeprefix("**Goal status:**").strip() or "unknown"
    return "unknown"


def session_sort_key(path: Path) -> str:
    base = path.stem
    match = TIMESTAMP_RE.search(base)
    return match.group(1) if match else ""


def load_sessions() -> list[Session]:
    directory = sessions_dir()
    if not directory.is_dir():
        return []
    paths = sorted(directory.glob("*.md"), key=session_sort_key, reverse=True)
    sessions: list[Session] = []
    for path in paths:
        if not session_sort_key(path):
            continue
        text = read_text(path)
        title = first_match(TITLE_RE, text)
        timestamp = first_match(TIMESTAMP_LINE_RE, text)
        if not title or not timestamp:
            continue
        sessions.append(
            Session(
                path=path.resolve(),
                session_id=path.stem,
                title=title,
                timestamp=timestamp,
                branch=first_match(BRANCH_RE, text, "unknown"),
                status=goal_status(text),
            )
        )
    return sessions


def md_escape(value: str) -> str:
    return value.replace("|", r"\|")


def emit_table(sessions: list[Session], limit: int | None) -> None:
    shown = sessions if limit is None else sessions[:limit]
    print("| Session ID | Title | Timestamp | Branch | Status |")
    print("|------------|-------|-----------|--------|--------|")
    for item in shown:
        print(
            "| "
            + " | ".join(
                [
                    md_escape(item.session_id),
                    md_escape(item.title),
                    md_escape(item.timestamp),
                    md_escape(item.branch),
                    md_escape(item.status),
                ]
            )
            + " |"
        )
    if limit is not None and len(sessions) > limit:
        print()
        print(f"{len(sessions)} total, showing {limit}. Use --limit <higher> or filter further to see more.")


def cmd_list(args: argparse.Namespace) -> int:
    sessions = load_sessions()
    if not sessions:
        print("No sessions found in .sessions/")
        return 0
    emit_table(sessions, args.limit)
    return 0


def cmd_filter(args: argparse.Namespace) -> int:
    if not args.criteria:
        print("error: filter requires at least one key:value criterion", file=sys.stderr)
        return 1

    filters: dict[str, str] = {}
    for criterion in args.criteria:
        if ":" not in criterion:
            print(f'error: criterion "{criterion}" must be key:value', file=sys.stderr)
            return 1
        key, value = criterion.split(":", 1)
        if key not in {"user", "branch", "status", "since", "until"}:
            print(
                f'error: unknown filter key "{key}" (allowed: user, branch, status, since, until)',
                file=sys.stderr,
            )
            return 1
        filters[key] = value

    matches: list[Session] = []
    for item in load_sessions():
        if "user" in filters and session_user(item.session_id) != filters["user"]:
            continue
        if "branch" in filters and item.branch != filters["branch"]:
            continue
        if "status" in filters and item.status != filters["status"]:
            continue
        date = item.timestamp[:10]
        if "since" in filters and date < filters["since"]:
            continue
        if "until" in filters and date > filters["until"]:
            continue
        matches.append(item)

    if not matches:
        print(f"No sessions match: {' '.join(args.criteria)}")
        return 0
    emit_table(matches, args.limit)
    return 0


def section_for_line(lines: list[str], line_number: int) -> str:
    current = "(before any ## section)"
    for index, line in enumerate(lines, start=1):
        if line.startswith("## "):
            current = line
        if index == line_number:
            return current
    return current


def cmd_grep(args: argparse.Namespace) -> int:
    pattern = " ".join(args.pattern).strip()
    if not pattern:
        print("error: grep requires a pattern", file=sys.stderr)
        return 1

    regex_mode = pattern.startswith("re:")
    needle = pattern[3:] if regex_mode else re.escape(pattern)
    try:
        compiled = re.compile(needle, re.IGNORECASE)
    except re.error as exc:
        print(f"error: invalid regex: {exc}", file=sys.stderr)
        return 1

    matched = []
    for item in load_sessions():
        text = read_text(item.path)
        if compiled.search(text):
            matched.append(item)
            if args.limit is not None and len(matched) >= args.limit:
                break

    if not matched:
        print(f"No matches for: {pattern[3:] if regex_mode else pattern}")
        return 0

    for session_index, item in enumerate(matched):
        if session_index:
            print()
        print(f"### {item.session_id} - {item.title}")
        print()
        lines = read_text(item.path).splitlines()
        count = 0
        for line_number, line in enumerate(lines, start=1):
            if compiled.search(line):
                print(f"{section_for_line(lines, line_number)} - line {line_number}")
                print(f"  > {line}")
                print()
                count += 1
                if count >= 3:
                    break
    return 0


def resolve_session(ref: str | None) -> tuple[Session | None, int]:
    sessions = load_sessions()
    if not sessions:
        print("No sessions found in .sessions/")
        return None, 0
    if not ref:
        return sessions[0], 0
    normalized = ref.removesuffix(".md")
    matches = [item for item in sessions if item.session_id == normalized or normalized in item.session_id]
    if not matches:
        print(f"No session matches: {ref}", file=sys.stderr)
        return None, 1
    if len(matches) > 1:
        print(f'error: ambiguous reference "{ref}" matches:', file=sys.stderr)
        for item in matches:
            print(f"  {item.session_id}", file=sys.stderr)
        return None, 2
    return matches[0], 0


def extract_section(text: str, number: int) -> str:
    lines = text.splitlines()
    capture = False
    output: list[str] = []
    prefix = f"## {number}."
    for line in lines:
        if line.startswith(prefix):
            capture = True
            continue
        if capture and line.startswith("## "):
            break
        if capture:
            output.append(line)
    return "\n".join(output)


def extract_subsection(section: str, subsection: str) -> str:
    lines = section.splitlines()
    capture = False
    output: list[str] = []
    prefix = f"### {subsection}"
    for line in lines:
        if line.startswith(prefix):
            capture = True
            continue
        if capture and line.startswith("### "):
            break
        if capture:
            output.append(line)
    return "\n".join(output)


def table_items(body: str) -> list[dict[str, str]]:
    useful = [line for line in body.splitlines() if line.strip()]
    if useful and useful[0].strip() == "none":
        return []

    rows: list[dict[str, str]] = []
    after_separator = False
    for line in useful:
        stripped = line.strip()
        if stripped.startswith("|") and re.match(r"^\|[\s:-]+\|", stripped):
            after_separator = True
            continue
        if not after_separator or not stripped.startswith("|"):
            continue
        cells = [cell.strip() for cell in stripped.strip("|").split("|")]
        if not cells or not cells[0] or set(cells[0]) <= {"-"}:
            continue
        rows.append({"label": cells[0], "raw": stripped})
    return rows


def cmd_resume(args: argparse.Namespace) -> int:
    item, code = resolve_session(args.session_id)
    if item is None:
        return code

    text = read_text(item.path)
    section6 = extract_section(text, 6)
    if not section6:
        print(
            json.dumps(
                {
                    "session_id": item.session_id,
                    "title": item.title,
                    "file_path": str(item.path),
                    "empty": True,
                },
                indent=2,
            )
        )
        return 0

    subsections = {
        "in_progress": table_items(extract_subsection(section6, "6.1")),
        "promised": table_items(extract_subsection(section6, "6.2")),
        "known_issues": table_items(extract_subsection(section6, "6.3")),
    }
    if not any(subsections.values()):
        payload = {
            "session_id": item.session_id,
            "title": item.title,
            "file_path": str(item.path),
            "empty": True,
        }
    else:
        payload = {
            "session_id": item.session_id,
            "title": item.title,
            "file_path": str(item.path),
            "subsections": subsections,
        }
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_last(args: argparse.Namespace) -> int:
    sessions = load_sessions()
    if not sessions:
        print("No sessions found in .sessions/")
        return 0
    selected = sessions[: args.n]
    for item in selected:
        print(item.path)
    if args.n > len(sessions):
        print()
        print(f"Only {len(sessions)} session(s) available; all paths shown.")
    return 0


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a positive integer") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="session_recall.py",
        description="List, search, and resume agent-agnostic session reports.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    list_parser = subparsers.add_parser("list")
    list_parser.add_argument("--limit", type=positive_int)
    list_parser.set_defaults(func=cmd_list)

    filter_parser = subparsers.add_parser("filter")
    filter_parser.add_argument("criteria", nargs="*")
    filter_parser.add_argument("--limit", type=positive_int)
    filter_parser.set_defaults(func=cmd_filter)

    grep_parser = subparsers.add_parser("grep")
    grep_parser.add_argument("pattern", nargs="*")
    grep_parser.add_argument("--limit", type=positive_int)
    grep_parser.set_defaults(func=cmd_grep)

    resume_parser = subparsers.add_parser("resume")
    resume_parser.add_argument("session_id", nargs="?")
    resume_parser.set_defaults(func=cmd_resume)

    last_parser = subparsers.add_parser("last")
    last_parser.add_argument("n", nargs="?", type=positive_int, default=1)
    last_parser.set_defaults(func=cmd_last)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
