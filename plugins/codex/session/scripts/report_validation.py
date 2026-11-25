"""Validate a new handoff report without printing its sensitive contents."""

import re
from pathlib import Path

from session_recall import NONE_LINE, RULE, SEP_LINE, STATUS_WORDS, TABLE_LINE, cells, read_lines, structural_flags


SECRET_PATTERNS = {
    "private key block": r"-----BEGIN [A-Z0-9 ]*PRIVATE KEY(?: BLOCK)?-----",
    "GitHub token": r"(?:gh[pousr]_[A-Za-z0-9]{16,}|github_pat_[A-Za-z0-9_]{16,})",
    "GitLab token": r"glpat-[A-Za-z0-9_-]{16,}",
    "npm token": r"npm_[A-Za-z0-9]{16,}",
    "API secret key": r"sk-[A-Za-z0-9_-]{16,}",
    "API key": r"(?:sk|pk|rk)_(?:live|test)_[A-Za-z0-9]{8,}",
    "AWS access key id": r"(?:AKIA|ASIA)[0-9A-Z]{16}",
    "Slack token": r"xox[abposr]-[A-Za-z0-9-]{8,}",
    "Google API key": r"AIza[0-9A-Za-z_-]{30,}",
    "JSON web token": r"eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}",
    "bearer token": r"(?i:bearer) [A-Za-z0-9._~+/=-]{20,}",
    "basic authorization": r"(?i:authorization:)[ \t]*(?i:basic) [A-Za-z0-9+/=]{8,}",
}
SECRET_PATTERNS = {kind: re.compile(pattern) for kind, pattern in SECRET_PATTERNS.items()}
ENV_REF = re.compile(r"\$(?:[A-Za-z_][A-Za-z0-9_]*|\{[A-Za-z_][A-Za-z0-9_]*\})|%[A-Za-z_][A-Za-z0-9_]*%")
TOKEN_URL = re.compile(r"[A-Za-z][A-Za-z0-9+.-]*://[^/\s:@]+:(?P<value>[^/\s@]+)@")
TOKEN_ARG = re.compile(r"""--(?:password|passwd|pass|token|api-?key|secret)[= ]["'\x60]?(?P<value>[^\s"'\x60]{3,})""", re.I)
ASSIGNMENT = re.compile(
    r"""[A-Za-z0-9_.-]*(?:password|passwd|passphrase|secret|token|api[_-]?key|access[_-]?key|private[_-]?key|credentials?)"""
    r"""["']?\s*(?P<sep>[:=])[*_]*\s*(?P<quote>["'\x60]?)(?P<value>[^\s"'\x60,;)]{4,})""", re.I,
)
STAND_INS = set(
    "changeme change_me password passwd passw0rd p@ssw0rd secret admin root letmein hunter2 qwerty "
    "example sample dummy fake test testing placeholder redacted default foobar".split()
)


def sensitive_kinds(line: str) -> set[str]:
    kinds = {kind for kind, pattern in SECRET_PATTERNS.items() if pattern.search(line)}
    for kind, pattern in (("URL with embedded credentials", TOKEN_URL), ("credential on a command line", TOKEN_ARG)):
        if any(not ENV_REF.fullmatch(match["value"]) for match in pattern.finditer(line)):
            kinds.add(kind)
    for match in ASSIGNMENT.finditer(line):
        value = match["value"]
        if ENV_REF.fullmatch(value) or value.startswith(("/", "./", "~/")):
            continue
        if (match["sep"] == "=" or match["quote"] or value.lower() in STAND_INS
                or (not value.isdecimal() and (len(value) >= 16 or not re.fullmatch(r"[A-Za-z-]+", value)))):
            kinds.add("credential assignment")
    return kinds


def defect_findings(rows: list[tuple[int, str]], heading: int) -> list[str]:
    rows = [(number, line) for number, line in rows if line.strip() and not RULE.fullmatch(line)]
    if len(rows) == 1 and NONE_LINE.fullmatch(rows[0][1]):
        return []
    if not rows or not TABLE_LINE.match(rows[0][1]):
        return [f"structure: line {heading}: §6.3 needs the defects table or none"]
    header = [re.sub(r"[*_\x60]", "", cell).strip().lower() for cell in cells(rows[0][1])]
    if "status" not in header:
        return [f"structure: line {rows[0][0]}: §6.3 has no Status column"]
    if len(rows) < 2 or not SEP_LINE.fullmatch(rows[1][1]):
        return [f"structure: line {rows[0][0]}: §6.3 has no table separator"]
    status = header.index("status")
    problems = []
    for number, line in rows[2:]:
        if not TABLE_LINE.match(line):
            problems.append(f"structure: line {number}: §6.3 holds only the defects table")
            continue
        values = cells(line)
        if status >= len(values) or re.sub(r"[*_\x60]", "", values[status]).strip().lower() not in {"confirmed", "suspected"}:
            problems.append(f"structure: line {number}: §6.3 Status must be confirmed or suspected")
    return problems


def findings(path: Path, stamp: str, roots: set[str], worktree_names: set[str]) -> list[str]:
    lines = read_lines(path)
    outside = [(number, line) for number, (line, visible) in
               enumerate(zip(lines, structural_flags(lines)), 1) if visible]
    problems = [
        f"sensitive: line {number}: {kind}"
        for number, line in enumerate(lines, 1) for kind in sorted(sensitive_kinds(line))
    ]
    names = re.compile(r"(?<!\w)(?:" + "|".join(re.escape(name) for name in sorted(worktree_names)) + r")(?!\w)") if worktree_names else None
    for number, line in enumerate(lines, 1):
        if any(root != "/" and root in line for root in roots):
            problems.append(f"privacy: line {number}: use a project-relative path")
        if names and names.search(line):
            problems.append(f"privacy: line {number}: omit the worktree name")

    if not re.fullmatch(r"# Session Report: \S.*", next((line for line in lines if line.strip()), "")):
        problems.append("structure: the first nonblank line must be the report title")
    headings = ["## Session contract", *(f"## {index}." for index in range(1, 7)),
                "### 6.1", "### 6.2", "### 6.3"]
    starts = {}
    previous = 0
    for heading in headings:
        hits = [number for number, line in outside if line.startswith(heading)]
        if len(hits) != 1:
            problems.append(f"structure: expected one {heading} heading")
        if hits:
            starts[heading] = hits[0]
            if hits[0] < previous:
                problems.append(f"structure: line {hits[0]}: {heading} is out of order")
            previous = hits[0]

    def field(label: str, start: int = 0, end: int = len(lines) + 1) -> list[str]:
        prefix = f"**{label}:**"
        return [line[len(prefix):].strip() for number, line in outside
                if start < number < end and line.startswith(prefix)]

    dates = field("Timestamp (UTC)")
    if len(dates) != 1 or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{6}Z", dates[0]):
        problems.append("structure: expected one Timestamp (UTC) field in YYYY-MM-DDTHHMMSSZ form")
    elif dates[0] != f"{stamp}Z":
        problems.append("coherence: the header timestamp differs from the filename")
    harness = field("Harness")
    if len(harness) != 1 or not harness[0]:
        problems.append("structure: expected one Harness field")
    for label in ("Branch", "Model"):
        if field(label):
            problems.append(f"structure: new reports omit the {label} field")
    if "## Session contract" in starts and "## 1." in starts:
        goal = field("Goal status", starts["## Session contract"], starts["## 1."])
        if len(goal) != 1 or goal[0] not in STATUS_WORDS:
            problems.append("structure: Goal status must be achieved, partial, abandoned or redirected")
    if "### 6.3" in starts:
        heading = starts["### 6.3"]
        end = next((number for number, line in outside if number > heading and re.match(r"^#{1,3} ", line)),
                   len(lines) + 1)
        problems.extend(defect_findings([(number, line) for number, line in outside if heading < number < end], heading))
    return problems
