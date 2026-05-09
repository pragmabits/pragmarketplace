#!/usr/bin/env python3
"""
validate.py — Structural validation for generated loop and sub-agent files.

Checks that scaffolded files have the required structural elements
(frontmatter fields, required sections, populated placeholders).
This is the mechanical layer of /coordination-audit; it catches
"file is missing the Guardrails section" without spending tokens.

The judgment-level checks ("is this role really one objective sentence?")
remain in the audit command itself.

USAGE
    python3 validate.py [--root <path>] [--target loops|agents|both]

ARGUMENTS
    --root <path>        Repository root. Defaults to CWD.
    --target <kind>      What to validate. One of: loops, agents, both.
                         Defaults to both.
    --paths-from-config  If set, read .architect.json for paths
                         instead of using defaults (.claude/loops/,
                         .claude/agents/).

OUTPUT
    A single JSON object on stdout:
    {
      "checked": <total file count>,
      "ok": <count of files with no issues>,
      "issues": [
        {
          "file": "<relative path>",
          "kind": "loop" | "agent",
          "severity": "error" | "warning",
          "code": "<short identifier>",
          "message": "<human-readable>"
        }
      ]
    }

EXIT CODES
    0   No errors found (warnings allowed)
    1   At least one error found
    2   Invalid arguments

ISSUE CODES (loops)
    missing-objective         No "## Objective" section
    missing-stop              No "## Stopping criterion" section
    missing-cap               No "## Iteration cap" section or value not numeric
    missing-progress          No "## Progress metric" section
    missing-guardrails        No "## Guardrails" section
    missing-observability     No "## Observability" section
    placeholder-unfilled      "<...>" placeholder text remains in body
    cap-too-high              Iteration cap > 10 (warning)

ISSUE CODES (agents)
    missing-frontmatter       File has no --- frontmatter block
    missing-name              Frontmatter has no name field
    missing-description       Frontmatter has no description field
    generic-description       Description is too short or generic (warning)
    missing-role              No "## Role" section
    missing-input-contract    No "## Input contract" section
    missing-output-contract   No "## Output contract" section
    missing-failure-mode      No "## Failure mode" section
    missing-do-not            No "## What you do NOT do" section
    placeholder-unfilled      "<...>" placeholder text remains in body
"""

import argparse
import json
import re
import sys
from pathlib import Path


# --- Loop validation --------------------------------------------------------

LOOP_REQUIRED_SECTIONS = {
    "missing-objective": r"^##\s+Objective\b",
    "missing-stop": r"^##\s+Stopping criterion\b",
    "missing-cap": r"^##\s+Iteration cap\b",
    "missing-progress": r"^##\s+Progress metric\b",
    "missing-guardrails": r"^##\s+Guardrails\b",
    "missing-observability": r"^##\s+Observability\b",
}

PLACEHOLDER_PATTERN = re.compile(r"<[a-z][^>]{0,100}>", re.IGNORECASE)


def validate_loop(file_path: Path, content: str) -> list[dict]:
    issues = []

    for code, pattern in LOOP_REQUIRED_SECTIONS.items():
        if not re.search(pattern, content, re.MULTILINE):
            issues.append({
                "file": str(file_path),
                "kind": "loop",
                "severity": "error",
                "code": code,
                "message": f"Required section missing: {code.replace('missing-', '')}",
            })

    # Iteration cap value check
    cap_match = re.search(r"^##\s+Iteration cap\s*\n+(.+?)(?:\n\n|\n##|\Z)", content, re.MULTILINE | re.DOTALL)
    if cap_match:
        cap_text = cap_match.group(1).strip()
        cap_num_match = re.search(r"\b(\d+)\b", cap_text)
        if cap_num_match:
            cap_value = int(cap_num_match.group(1))
            if cap_value > 10:
                issues.append({
                    "file": str(file_path),
                    "kind": "loop",
                    "severity": "warning",
                    "code": "cap-too-high",
                    "message": f"Iteration cap of {cap_value} is above the recommended max of 10",
                })

    # Placeholder check (excluding fenced blocks AND inline-backtick spans
    # where placeholders like `<module>` are legitimate metavariable docs)
    body_without_blocks = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
    body_without_blocks = re.sub(r"`[^`\n]*`", "", body_without_blocks)
    placeholders = PLACEHOLDER_PATTERN.findall(body_without_blocks)
    # Filter out HTML-like things that look like real tags
    real_placeholders = [p for p in placeholders if not re.match(r"<\s*(br|hr|/\w+|\w+\s*/)\s*>", p)]
    if real_placeholders:
        issues.append({
            "file": str(file_path),
            "kind": "loop",
            "severity": "warning",
            "code": "placeholder-unfilled",
            "message": f"Unfilled placeholder text remains: {real_placeholders[0]}",
        })

    return issues


# --- Agent validation -------------------------------------------------------

AGENT_REQUIRED_SECTIONS = {
    "missing-role": r"^##\s+Role\b",
    "missing-input-contract": r"^##\s+Input contract\b",
    "missing-output-contract": r"^##\s+Output contract\b",
    "missing-failure-mode": r"^##\s+Failure mode\b",
    "missing-do-not": r"^##\s+What you do NOT do\b",
}

GENERIC_DESC_PATTERNS = [
    r"^helps?\s+with\s+\w+",
    r"^reviews?\s+\w+",
    r"^handles?\s+\w+",
    r"^processes?\s+\w+",
]


def validate_agent(file_path: Path, content: str) -> list[dict]:
    issues = []

    # Frontmatter check
    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        issues.append({
            "file": str(file_path),
            "kind": "agent",
            "severity": "error",
            "code": "missing-frontmatter",
            "message": "Sub-agent file has no frontmatter block",
        })
        return issues

    frontmatter = fm_match.group(1)

    if not re.search(r"^name:\s*\S+", frontmatter, re.MULTILINE):
        issues.append({
            "file": str(file_path),
            "kind": "agent",
            "severity": "error",
            "code": "missing-name",
            "message": "Frontmatter has no name field",
        })

    desc_match = re.search(r"^description:\s*(.+?)$", frontmatter, re.MULTILINE)
    if not desc_match:
        issues.append({
            "file": str(file_path),
            "kind": "agent",
            "severity": "error",
            "code": "missing-description",
            "message": "Frontmatter has no description field",
        })
    else:
        desc = desc_match.group(1).strip()
        if len(desc) < 30:
            issues.append({
                "file": str(file_path),
                "kind": "agent",
                "severity": "warning",
                "code": "generic-description",
                "message": f"Description is too short ({len(desc)} chars); risks under- or over-invocation",
            })
        elif any(re.match(p, desc, re.IGNORECASE) for p in GENERIC_DESC_PATTERNS):
            issues.append({
                "file": str(file_path),
                "kind": "agent",
                "severity": "warning",
                "code": "generic-description",
                "message": "Description matches a generic pattern; specify what makes this sub-agent distinct",
            })

    # Required sections
    for code, pattern in AGENT_REQUIRED_SECTIONS.items():
        if not re.search(pattern, content, re.MULTILINE):
            issues.append({
                "file": str(file_path),
                "kind": "agent",
                "severity": "error",
                "code": code,
                "message": f"Required section missing: {code.replace('missing-', '').replace('-', ' ')}",
            })

    # Placeholder check (same logic as loop validator: strip fenced blocks + inline backticks)
    body_without_blocks = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
    body_without_blocks = re.sub(r"`[^`\n]*`", "", body_without_blocks)
    placeholders = PLACEHOLDER_PATTERN.findall(body_without_blocks)
    real_placeholders = [p for p in placeholders if not re.match(r"<\s*(br|hr|/\w+|\w+\s*/)\s*>", p)]
    if real_placeholders:
        issues.append({
            "file": str(file_path),
            "kind": "agent",
            "severity": "warning",
            "code": "placeholder-unfilled",
            "message": f"Unfilled placeholder text remains: {real_placeholders[0]}",
        })

    return issues


# --- Path resolution --------------------------------------------------------

def resolve_paths(root: Path, paths_from_config: bool) -> tuple[Path, Path]:
    loops_path = root / ".claude" / "loops"
    agents_path = root / ".claude" / "agents"

    if paths_from_config:
        config_file = root / ".architect.json"
        if config_file.exists():
            try:
                with open(config_file) as f:
                    config = json.load(f)
                paths = config.get("paths", {})
                if "loops" in paths:
                    loops_path = root / paths["loops"]
                if "agents" in paths:
                    agents_path = root / paths["agents"]
            except (json.JSONDecodeError, OSError):
                pass

    return loops_path, agents_path


# --- Main -------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Validate generated loop and sub-agent files.")
    parser.add_argument("--root", default=".", help="Repository root (default: cwd)")
    parser.add_argument("--target", choices=["loops", "agents", "both"], default="both",
                        help="What to validate")
    parser.add_argument("--paths-from-config", action="store_true",
                        help="Read paths from .architect.json instead of using defaults")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        return 2

    loops_path, agents_path = resolve_paths(root, args.paths_from_config)

    issues = []
    checked = 0

    if args.target in ("loops", "both") and loops_path.is_dir():
        for loop_file in sorted(loops_path.glob("*.md")):
            try:
                with open(loop_file) as f:
                    content = f.read()
            except OSError as e:
                print(f"Warning: could not read {loop_file}: {e}", file=sys.stderr)
                continue
            checked += 1
            issues.extend(validate_loop(loop_file.relative_to(root), content))

    if args.target in ("agents", "both") and agents_path.is_dir():
        for agent_file in sorted(agents_path.glob("*.md")):
            try:
                with open(agent_file) as f:
                    content = f.read()
            except OSError as e:
                print(f"Warning: could not read {agent_file}: {e}", file=sys.stderr)
                continue
            checked += 1
            issues.extend(validate_agent(agent_file.relative_to(root), content))

    has_errors = any(i["severity"] == "error" for i in issues)
    ok_count = checked - len({i["file"] for i in issues})

    output = {
        "checked": checked,
        "ok": ok_count,
        "issues": [{**i, "file": str(i["file"])} for i in issues],
    }
    print(json.dumps(output, indent=2))
    return 1 if has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
