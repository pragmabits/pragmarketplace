#!/usr/bin/env python3
"""Recall, search and resume session reports from <project-root>/.harness/sessions/.

Read-only: nothing here creates a directory or writes a file.

The parsing follows the shared report contract, the same one the Claude Code
plugin's recall (lib/report.jq) implements, so both tools read each other's
reports: fixed anchors (Session contract, ## 1. to ## 6., ### 6.1 to ### 6.3),
`none` for empty sections, `\\|` as a literal pipe inside table cells, and
optional authorship fields (Harness, Model, Agent, Harness version, Report
generator). Reports written before those fields existed are read as well.

Exit codes: 0 success (including "no sessions" notices), 1 error, 2 usage error
or ambiguous reference.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SESSIONS_REL = Path(".harness") / "sessions"
NO_SESSIONS = "No sessions found in .harness/sessions/"
USAGE = (
    "Usage: session_recall.py <list [--limit N] | filter <key:value>... [--limit N] | "
    "grep <pattern> [--limit N] | resume [<session-id>] [--item <text>] | last [<n>]>"
)
NAME_RE = re.compile(r"^(?:(?P<user>.*)-)?(?P<ts>\d{4}-\d{2}-\d{2}T\d{6})(?:-(?P<n>\d+))?$")
STATUS_WORDS = ("achieved", "partial", "abandoned", "redirected")


class RecallError(Exception):
    """An error to print on stderr, with its exit code."""

    def __init__(self, message: str, code: int = 1) -> None:
        super().__init__(message)
        self.code = code


# ---------------------------------------------------------------------------
# Locating reports
# ---------------------------------------------------------------------------

def project_root() -> Path:
    """Git root of the current directory, then CODEX_PROJECT_DIR, then cwd."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        text=True, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=False,
    )
    if result.returncode == 0 and result.stdout.strip():
        return Path(result.stdout.strip())
    env_root = os.environ.get("CODEX_PROJECT_DIR")
    if env_root and Path(env_root).is_dir():
        return Path(env_root)
    return Path.cwd()


def load_session_files() -> list[Path] | None:
    """Report paths, newest first. None when the directory does not exist."""
    directory = project_root() / SESSIONS_REL
    if not directory.exists() and not directory.is_symlink():
        return None
    if not directory.is_dir():
        raise RecallError("error: .harness/sessions exists but is not a directory")
    if not os.access(directory, os.R_OK | os.X_OK):
        raise RecallError("error: cannot read .harness/sessions/: permission denied")
    keyed = []
    for path in directory.glob("*.md"):
        match = NAME_RE.match(path.stem)
        if match:
            keyed.append((match.group("ts"), int(match.group("n") or 1), path))
    keyed.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return [path for _, _, path in keyed]


def split_inputs(paths: list[Path]) -> tuple[list[Path], list[str], list[str]]:
    """Readable non-empty files, then IDs of empty and of unreadable files."""
    readable, empty, unreadable = [], [], []
    for path in paths:
        if not os.access(path, os.R_OK):
            unreadable.append(path.stem)
        elif path.stat().st_size == 0:
            empty.append(path.stem)
        else:
            readable.append(path)
    return readable, empty, unreadable


def read_lines(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    return [line.rstrip("\r") for line in text.split("\n")[:-1]] if text.endswith("\n") \
        else [line.rstrip("\r") for line in text.split("\n")]


# ---------------------------------------------------------------------------
# Parsing the shared report contract
# ---------------------------------------------------------------------------

BLANK = re.compile(r"^\s*$")
RULE = re.compile(r"^\s*(-{3,}|\*{3,}|_{3,})\s*$")
NONE_LINE = re.compile(r"^\s*[*_`]*\s*(none|nenhum|nenhuma|n/a)\s*[*_`]*\s*\.?\s*$", re.IGNORECASE)
TABLE_LINE = re.compile(r"^\s*\|")
SEP_LINE = re.compile(r"^\s*\|?\s*:?-{3,}:?\s*(\|\s*:?-{3,}:?\s*)*\|?\s*$")
BULLET = re.compile(r"^([-*+]|[0-9]+[.)]) ")
BULLET_PREFIX = re.compile(r"^([-*+]|[0-9]+[.)]) +")
INDENTED = re.compile(r"^\s+\S")
ROW_CLOSED = re.compile(r"(?<!\\)\|\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")


def cells(row: str) -> list[str]:
    text = row.replace("\\|", "\x01").strip()
    if text.startswith("|"):
        text = text[1:]
    if text.endswith("|"):
        text = text[:-1]
    return [cell.replace("\x01", "|").strip() for cell in text.split("|")]


def structural_flags(lines: list[str]) -> list[bool]:
    """True for lines outside fenced code blocks; fence lines themselves are False."""
    flags, fence = [], False
    for line in lines:
        if FENCE.match(line):
            fence = not fence
            flags.append(False)
        else:
            flags.append(not fence)
    return flags


def first_index(lines: list[str], flags: list[bool], start: int, end: int, pattern: str) -> int | None:
    compiled = re.compile(pattern)
    for index in range(start, end):
        if flags[index] and compiled.search(lines[index]):
            return index
    return None


def field_in(lines: list[str], start: int, end: int, label: str) -> str | None:
    prefix = f"**{label}:**"
    for index in range(start, end):
        if lines[index].startswith(prefix):
            return lines[index][len(prefix):].strip()
    return None


def classify(rows: list[tuple[int, str]]) -> dict[str, Any]:
    """Classify a pending subsection (or any table section) body.

    States: items, none, incomplete (rows read, one looks cut off), unrecognized.
    """
    content = [(n, t) for n, t in rows if not BLANK.match(t) and not RULE.match(t)]
    if not content:
        return {"state": "unrecognized", "reason": "empty (expected a table or `none`)"}
    if len(content) == 1 and NONE_LINE.match(content[0][1]):
        return {"state": "none"}
    table = [(n, t) for n, t in content if TABLE_LINE.match(t)]
    other = [t for n, t in content if not TABLE_LINE.match(t)]
    if table:
        if len(table) < 2 or not SEP_LINE.match(table[1][1]):
            return {"state": "unrecognized", "reason": "table without a header separator",
                    "unparsed": [t for _, t in content]}
        columns = cells(table[0][1])
        data = table[2:]
        if not data:
            result = {"state": "unrecognized",
                      "reason": "table has no rows (an empty subsection is written as `none`)",
                      "columns": columns}
            if other:
                result["notes"] = other
            return result
        open_rows = [n for n, t in data if not ROW_CLOSED.search(t)]
        result = {
            "state": "incomplete" if open_rows else "items",
            "columns": columns,
            "items": [{"label": cells(t)[0], "raw": t, "cells": cells(t), "line": n} for n, t in data],
        }
        if open_rows:
            result["reason"] = "row at line {} does not end with | (possibly truncated)".format(
                ", ".join(str(n) for n in open_rows))
        if other:
            result["notes"] = other
        return result
    items: list[dict[str, Any]] = []
    notes: list[str] = []
    for n, t in content:
        if BULLET.match(t):
            label = BULLET_PREFIX.sub("", t, count=1)
            items.append({"label": label, "raw": t, "cells": [label], "line": n})
        elif INDENTED.match(t) and items:
            items[-1]["raw"] += "\n" + t
        else:
            notes.append(t)
    if items:
        result = {"state": "items", "columns": None, "items": items}
        if notes:
            result["notes"] = notes
        return result
    return {"state": "unrecognized", "reason": "neither a table, a list, nor `none`",
            "unparsed": [t for _, t in content]}


def model_info(value: str | None) -> dict[str, Any]:
    """Confirmed identifier, alias reported as such, explicit unknown, or no field."""
    if value is None:
        return {"state": "absent", "value": None}
    if value.lower() == "unknown":
        return {"state": "unknown", "value": None}
    if value.lower().startswith("alias:"):
        return {"state": "alias", "value": re.sub(r"^alias:\s*", "", value, flags=re.IGNORECASE)}
    return {"state": "confirmed", "value": value}


def header_field(lines: list[str], end: int, label: str) -> str | None:
    value = field_in(lines, 0, end, label)
    return None if value is None else value.replace("`", "").strip()


def parse_report(path: Path) -> dict[str, Any]:
    lines = read_lines(path)
    flags = structural_flags(lines)
    total = len(lines)
    session_id = path.stem
    name = NAME_RE.match(session_id)
    first_h2 = first_index(lines, flags, 0, total, r"^## ")
    first_h2 = total if first_h2 is None else first_h2

    title = None
    for index in range(total):
        if flags[index] and lines[index].startswith("# Session Report: "):
            title = lines[index][len("# Session Report: "):].strip()
            break
    timestamp = field_in(lines, 0, total, "Timestamp (UTC)")
    branch = field_in(lines, 0, total, "Branch")
    if branch is not None:
        branch = branch.replace("`", "").strip()

    contract: dict[str, Any] = {}
    ci = first_index(lines, flags, 0, total, r"^## Session contract")
    if ci is not None:
        ce = first_index(lines, flags, ci + 1, total, r"^## ")
        ce = total if ce is None else ce
        contract = {
            "goal": field_in(lines, ci, ce, "User goal (entering session)"),
            "goal_status": field_in(lines, ci, ce, "Goal status"),
            "direction_changes": field_in(lines, ci, ce, "Direction changes"),
            "status_note": field_in(lines, ci, ce, "Status evidence")
            or field_in(lines, ci, ce, "If partial, abandoned, or redirected"),
        }
    status_match = re.search("|".join(STATUS_WORDS), (contract.get("goal_status") or "").lower())

    topics = None
    s2 = first_index(lines, flags, 0, total, r"^## 2\.")
    if s2 is not None:
        e2 = first_index(lines, flags, s2 + 1, total, r"^## ")
        e2 = total if e2 is None else e2
        topics = [lines[i][4:].strip() for i in range(s2 + 1, e2) if flags[i] and lines[i].startswith("### ")]

    s4 = first_index(lines, flags, 0, total, r"^## 4\.")
    if s4 is None:
        decisions: dict[str, Any] = {"state": "missing", "reason": "section 4 (Decisions) not found"}
    else:
        e4 = first_index(lines, flags, s4 + 1, total, r"^## ")
        e4 = total if e4 is None else e4
        decisions = classify([(i + 1, lines[i]) for i in range(s4 + 1, e4)])

    s6 = first_index(lines, flags, 0, total, r"^## 6\.")
    if s6 is None:
        pending: dict[str, Any] = {
            "state": "incomplete",
            "reasons": ["section 6 (Pending Items) not found — the report may be truncated or in an unrecognized format"],
            "subsections": {},
        }
    else:
        e6 = first_index(lines, flags, s6 + 1, total, r"^## ")
        e6 = total if e6 is None else e6
        subs: dict[str, Any] = {}
        for key, pattern, label in (("in_progress", r"6\.1", "6.1"), ("promised", r"6\.2", "6.2"),
                                    ("known_issues", r"6\.3", "6.3")):
            heading = first_index(lines, flags, s6 + 1, e6, r"^### " + pattern)
            if heading is None:
                subs[key] = {"state": "missing", "reason": f"heading ### {label} not found"}
                continue
            end = first_index(lines, flags, heading + 1, e6, r"^#{1,3} ")
            end = e6 if end is None else end
            subs[key] = {**classify([(i + 1, lines[i]) for i in range(heading + 1, end)]), "line": heading + 1}
        reasons = [
            f"{key}: {value['state']}" + (f" — {value['reason']}" if value.get("reason") else "")
            for key, value in subs.items() if value["state"] not in ("items", "none")
        ]
        if all(value["state"] == "none" for value in subs.values()):
            state = "none"
        elif reasons:
            state = "incomplete"
        else:
            state = "items"
        pending = {"state": state, "subsections": subs}
        if reasons:
            pending["reasons"] = reasons

    return {
        "session_id": session_id,
        "file_path": str(path),
        "user": name.group("user") if name else None,
        "name_timestamp": name.group("ts") if name else None,
        "title": title,
        "timestamp": timestamp,
        "branch": branch,
        "goal": contract.get("goal"),
        "goal_status": contract.get("goal_status"),
        "status_word": status_match.group(0) if status_match else None,
        "status_note": contract.get("status_note"),
        "direction_changes": contract.get("direction_changes"),
        "work_topics": topics,
        "decisions": decisions,
        "pending": pending,
        "origin": {
            "harness": header_field(lines, first_h2, "Harness"),
            "model": model_info(header_field(lines, first_h2, "Model")),
            "agent": header_field(lines, first_h2, "Agent"),
            "harness_version": header_field(lines, first_h2, "Harness version"),
            "report_generator": header_field(lines, first_h2, "Report generator"),
        },
        "malformed": title is None or timestamp is None,
    }


def pending_counts(report: dict[str, Any]) -> dict[str, int | None]:
    pending = report["pending"]
    if pending["state"] == "none":
        return {"in_progress": 0, "promised": 0, "known_issues": 0}
    subs = pending.get("subsections") or {}
    counts: dict[str, int | None] = {}
    for key in ("in_progress", "promised", "known_issues"):
        sub = subs.get(key) or {}
        if sub.get("state") == "items":
            counts[key] = len(sub["items"])
        elif sub.get("state") == "none":
            counts[key] = 0
        else:
            counts[key] = None
    return counts


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def md(value: str | None) -> str:
    return (value or "").replace("|", "\\|")


def table(rows: list[dict[str, Any]], with_branch: bool, limit: int | None) -> list[str]:
    if with_branch:
        out = ["| Session ID | Title | Timestamp | Branch | Status |",
               "|------------|-------|-----------|--------|--------|"]
    else:
        out = ["| Session ID | Title | Timestamp | Status |",
               "|------------|-------|-----------|--------|"]
    for row in rows[:limit] if limit else rows:
        values = [row["session_id"], row["title"], row["timestamp"]]
        if with_branch:
            values.append(row["branch"])
        values.append(row["goal_status"])
        out.append("| " + " | ".join(md(v) for v in values) + " |")
    if limit and len(rows) > limit:
        out.append("")
        out.append(f"{len(rows)} total, showing {limit}. Use --limit <higher> or filter further to see more.")
    return out


def notices(bad: list[dict[str, Any]], empty: list[str], unreadable: list[str]) -> list[str]:
    out = []
    if bad:
        out += ["", "Skipped {} file(s) without the '# Session Report:' title or the '**Timestamp (UTC):**' "
                    "field: {}".format(len(bad), ", ".join(r["session_id"] for r in bad))]
    if empty:
        out += ["", "Skipped empty file(s): " + ", ".join(empty)]
    if unreadable:
        out += ["", "Could not read: " + ", ".join(unreadable)]
    return out


def positive_int(value: str | None, label: str) -> int:
    if value is None or not re.fullmatch(r"[1-9][0-9]*", value):
        raise RecallError(f"error: {label} must be a positive integer (got: {value or ''})")
    return int(value)


def take_limit(args: list[str], command: str, allow_other: bool) -> tuple[int | None, list[str]]:
    limit, rest, index = None, [], 0
    while index < len(args):
        if args[index] == "--limit":
            limit = positive_int(args[index + 1] if index + 1 < len(args) else None, "--limit value")
            index += 2
            continue
        if not allow_other:
            raise RecallError(f"error: {command} accepts only --limit N (got: {args[index]})", 2)
        rest.append(args[index])
        index += 1
    return limit, rest


def loaded_or_notice() -> list[Path] | None:
    paths = load_session_files()
    if paths is None:
        print(f"{NO_SESSIONS} (the directory does not exist)")
        return None
    if not paths:
        print(NO_SESSIONS)
        return None
    return paths


# ---------------------------------------------------------------------------
# Subcommands
# ---------------------------------------------------------------------------

def cmd_list(args: list[str]) -> int:
    limit, _ = take_limit(args, "list", allow_other=False)
    paths = loaded_or_notice()
    if paths is None:
        return 0
    readable, empty, unreadable = split_inputs(paths)
    reports = [parse_report(p) for p in readable]
    ok = [r for r in reports if not r["malformed"]]
    bad = [r for r in reports if r["malformed"]]
    lines = [NO_SESSIONS] if not ok else table(ok, False, limit)
    print("\n".join(lines + notices(bad, empty, unreadable)))
    return 0


def cmd_filter(args: list[str]) -> int:
    limit, criteria = take_limit(args, "filter", allow_other=True)
    if not criteria:
        raise RecallError("error: filter requires at least one key:value criterion", 2)
    wanted: dict[str, str] = {}
    for criterion in criteria:
        if ":" not in criterion:
            raise RecallError(f'error: criterion "{criterion}" must be key:value', 2)
        key, value = criterion.split(":", 1)
        if not value:
            raise RecallError(f'error: criterion "{criterion}" has an empty value', 2)
        if key == "status" and value not in STATUS_WORDS:
            raise RecallError(f"error: status must be achieved, partial, abandoned or redirected (got: {value})", 2)
        if key in ("since", "until") and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise RecallError(f"error: {key} must be a date in YYYY-MM-DD form (got: {value})", 2)
        if key not in ("user", "branch", "status", "since", "until"):
            raise RecallError(f'error: unknown filter key "{key}" (allowed: user, branch, status, since, until)', 2)
        wanted[key] = value
    paths = loaded_or_notice()
    if paths is None:
        return 0
    readable, empty, unreadable = split_inputs(paths)
    hits = []
    for report in (parse_report(p) for p in readable):
        if report["malformed"]:
            continue
        date = (report["name_timestamp"] or "")[:10]
        if "user" in wanted and (report["user"] or "").lower() != wanted["user"].lower():
            continue
        if "branch" in wanted and report["branch"] != wanted["branch"]:
            continue
        if "status" in wanted and report["status_word"] != wanted["status"]:
            continue
        if "since" in wanted and date < wanted["since"]:
            continue
        if "until" in wanted and date > wanted["until"]:
            continue
        hits.append(report)
    lines = [f"No sessions match: {' '.join(criteria)}"] if not hits else table(hits, "branch" in wanted, limit)
    print("\n".join(lines + notices([], empty, unreadable)))
    return 0


def section_for_line(lines: list[str], target: int) -> str:
    current, fence = "", False
    for number, line in enumerate(lines, start=1):
        if FENCE.match(line):
            fence = not fence
        elif not fence and line.startswith("## "):
            current = line
        if number == target:
            break
    return current


def cmd_grep(args: list[str]) -> int:
    limit, words = take_limit(args, "grep", allow_other=True)
    if not words:
        raise RecallError("error: grep requires a pattern", 2)
    pattern = " ".join(words)
    regex_mode = pattern.startswith("re:")
    if regex_mode:
        pattern = pattern[3:]
    if not pattern:
        raise RecallError("error: grep requires a non-empty pattern", 2)
    try:
        compiled = re.compile(pattern if regex_mode else re.escape(pattern), re.IGNORECASE)
    except re.error:
        raise RecallError(f"error: invalid regular expression: {pattern}", 2)
    paths = loaded_or_notice()
    if paths is None:
        return 0
    readable, empty, unreadable = split_inputs(paths)
    matched = []
    for path in readable:
        lines = read_lines(path)
        if any(compiled.search(line) for line in lines):
            matched.append((path, lines))
            if limit and len(matched) >= limit:
                break
    out: list[str] = []
    if not matched:
        out.append(f"No matches for: {pattern}")
    for index, (path, lines) in enumerate(matched):
        if index:
            out.append("")
        title = next((l[len("# Session Report: "):] for l in lines if l.startswith("# Session Report: ")), "")
        out += [f"### {path.stem} — {title}", ""]
        count = 0
        for number, line in enumerate(lines, start=1):
            if count >= 3:
                break
            if compiled.search(line):
                heading = section_for_line(lines, number) or "(before any ## section)"
                out += [f"{heading} — line {number}", f"  > {line}", ""]
                count += 1
    print("\n".join(out + notices([], empty, unreadable)).rstrip("\n"))
    return 0


def resolve_id(ref: str, paths: list[Path]) -> Path:
    ref = ref[:-3] if ref.endswith(".md") else ref
    for path in paths:
        if path.stem == ref:
            return path
    matches = [path for path in paths if ref in path.stem]
    if not matches:
        raise RecallError(f"No session matches: {ref}", 1)
    if len(matches) > 1:
        raise RecallError(f'Ambiguous reference "{ref}" matches:\n'
                          + "\n".join(f"  {p.stem}" for p in matches), 2)
    return matches[0]


def cmd_resume(args: list[str]) -> int:
    ref, item, has_item, index = None, "", False, 0
    while index < len(args):
        arg = args[index]
        if arg == "--item":
            has_item, item = True, " ".join(args[index + 1:])
            break
        if arg.startswith("--"):
            raise RecallError(f"error: unknown resume option: {arg} (allowed: --item <text>)", 2)
        if ref is not None:
            raise RecallError(
                f'error: resume takes at most one session reference (got "{ref}" and "{arg}"); '
                "name the item to resume with: resume [<session-id>] --item <text>", 2)
        ref = arg
        index += 1
    if has_item and not item:
        raise RecallError("error: --item requires the text of the item to resume", 2)
    paths = loaded_or_notice()
    if paths is None:
        return 0
    path = resolve_id(ref, paths) if ref else paths[0]
    if not os.access(path, os.R_OK):
        raise RecallError(f"error: cannot read session report {path.stem}")
    if path.stat().st_size == 0:
        raise RecallError(f"error: session report {path.stem} is empty")
    report = parse_report(path)
    pending = report["pending"]
    payload: dict[str, Any] = {
        "session_id": report["session_id"],
        "title": report["title"],
        "file_path": report["file_path"],
        "timestamp": report["timestamp"],
        "goal": report["goal"],
        "goal_status": report["goal_status"],
        "status_note": report["status_note"],
        "direction_changes": report["direction_changes"],
        "origin": report["origin"],
        "pending_state": pending["state"],
    }
    if item:
        payload["requested_item"] = item
    if pending["state"] == "none":
        payload["empty"] = True
    if pending.get("reasons"):
        payload["incomplete_reasons"] = pending["reasons"]
    if pending["subsections"]:
        payload["subsections"] = {k: v.get("items", []) for k, v in pending["subsections"].items()}
        payload["subsection_states"] = {k: {kk: vv for kk, vv in v.items() if kk != "items"}
                                        for k, v in pending["subsections"].items()}
    payload["decisions"] = report["decisions"]
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    return 0


def cmd_last(args: list[str]) -> int:
    if len(args) > 1:
        raise RecallError(f"error: last takes one optional count (got {len(args)} arguments)", 2)
    count = positive_int(args[0] if args else "1", "<n>")
    paths = loaded_or_notice()
    if paths is None:
        return 0
    available = len(paths)
    readable, empty, unreadable = split_inputs(paths[:count])
    sessions = []
    for report in (parse_report(p) for p in readable):
        sessions.append({
            "session_id": report["session_id"], "file_path": report["file_path"], "title": report["title"],
            "timestamp": report["timestamp"], "goal_status": report["goal_status"], "goal": report["goal"],
            "status_note": report["status_note"], "origin": report["origin"],
            "work_topics": report["work_topics"], "pending_state": report["pending"]["state"],
            "pending_counts": pending_counts(report), "malformed": report["malformed"],
        })
    print(json.dumps({
        "requested": count, "available": available, "sessions": sessions,
        "skipped_empty": ", ".join(empty), "unreadable": ", ".join(unreadable),
    }, indent=2, ensure_ascii=False))
    if count > available:
        print(f"\nOnly {available} session(s) available; all are shown.")
    return 0


COMMANDS = {"list": cmd_list, "filter": cmd_filter, "grep": cmd_grep, "resume": cmd_resume, "last": cmd_last}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] not in COMMANDS:
        print(USAGE, file=sys.stderr)
        return 2
    try:
        return COMMANDS[args[0]](args[1:])
    except RecallError as error:
        print(str(error), file=sys.stderr)
        return error.code


if __name__ == "__main__":
    raise SystemExit(main())
