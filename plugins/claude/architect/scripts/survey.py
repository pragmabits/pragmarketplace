#!/usr/bin/env python3
"""
survey.py — Detect project structure for the architect plugin.

Inspects a repository and emits a JSON survey describing:
  - Detected stack(s) and test commands
  - Existing sub-agents and slash commands under .claude/
  - Off-limits paths (gitignore, CODEOWNERS, generated files)
  - Default scaffold output paths

Used by the `project-survey` skill as the mechanical inspection layer.
The skill handles the prose-derived parts (interpreting CLAUDE.md
conventions) and presents results to the user.

USAGE
    python3 survey.py [--root <path>]

ARGUMENTS
    --root <path>   Repository root to survey. Defaults to CWD.

OUTPUT
    A single JSON object on stdout with this shape:
    {
      "root": "<absolute path>",
      "surveyed_at": "<ISO 8601 timestamp>",
      "stack": {
        "primary": "python" | "node" | "rust" | "go" | "java" | "mixed" | "unknown",
        "additional": ["..."],
        "test_commands": {"<label>": "<command>"}
      },
      "paths": {
        "loops": ".claude/loops/",
        "agents": ".claude/agents/",
        "off_limits": ["..."]
      },
      "existing_infrastructure": {
        "agents": [{"name": "...", "path": "...", "role": "..." | null}],
        "commands": [{"name": "...", "path": "...", "description": "..." | null}]
      },
      "claude_md_present": true | false,
      "claude_md_path": "<path>" | null,
      "architect_json_present": true | false
    }

EXIT CODES
    0   Survey completed (regardless of findings)
    2   Invalid arguments or root path doesn't exist

NOTES
    This script is intentionally read-only. It does NOT write
    .architect.json — that's the skill's job after user confirmation.

    Conventions found in CLAUDE.md are NOT extracted here, because
    that requires prose understanding. The skill reads CLAUDE.md
    itself and synthesizes the conventions list.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def detect_stack(root: Path) -> dict:
    """Detect language stacks and test commands from manifest files."""
    detected = []
    test_commands = {}

    # Python
    if (root / "pyproject.toml").exists() or (root / "setup.py").exists() or (root / "requirements.txt").exists():
        detected.append("python")
        # Try to find test command
        if (root / "pytest.ini").exists() or (root / "pyproject.toml").exists():
            test_commands["python"] = "pytest"
        elif (root / "tox.ini").exists():
            test_commands["python"] = "tox"

    # Node — check root and common subdirectories
    for pkg_path in [root / "package.json"] + list(root.glob("*/package.json")):
        if pkg_path.exists() and pkg_path.is_file():
            try:
                with open(pkg_path) as f:
                    pkg = json.load(f)
                rel_dir = str(pkg_path.parent.relative_to(root)) or "."
                label = "node" if rel_dir == "." else f"node_in_{rel_dir.replace('/', '_')}"
                if "node" not in detected:
                    detected.append("node")
                test_script = pkg.get("scripts", {}).get("test")
                if test_script:
                    if rel_dir == ".":
                        test_commands[label] = "npm test"
                    else:
                        test_commands[label] = f"npm test --prefix {rel_dir}"
            except (json.JSONDecodeError, OSError):
                pass

    # Rust
    if (root / "Cargo.toml").exists():
        detected.append("rust")
        test_commands["rust"] = "cargo test"

    # Go
    if (root / "go.mod").exists():
        detected.append("go")
        test_commands["go"] = "go test ./..."

    # Java/Kotlin
    if (root / "pom.xml").exists():
        detected.append("java")
        test_commands["java"] = "mvn test"
    elif (root / "build.gradle").exists() or (root / "build.gradle.kts").exists():
        detected.append("java")
        test_commands["java"] = "./gradlew test"

    # Make/Just (fallback)
    if (root / "Makefile").exists() and "make_test" not in test_commands:
        # Try to find a `test:` target
        try:
            with open(root / "Makefile") as f:
                if re.search(r"^test\s*:", f.read(), re.MULTILINE):
                    test_commands.setdefault("make", "make test")
        except OSError:
            pass

    primary = detected[0] if detected else "unknown"
    if len(detected) > 1:
        primary = "mixed"

    return {
        "primary": primary,
        "additional": detected[1:] if len(detected) > 1 else [],
        "test_commands": test_commands,
    }


def detect_off_limits(root: Path) -> list[str]:
    """Detect paths that should not be modified by scaffolds."""
    off_limits = set()

    # Always-on patterns
    for always in ["node_modules/", "vendor/", "*.lock", "dist/", "build/"]:
        off_limits.add(always)

    # .gitignore: pull in entries that look like generated/build artifacts
    gitignore = root / ".gitignore"
    if gitignore.exists():
        try:
            with open(gitignore) as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    # Heuristic: treat directory-shaped or generated-looking entries as off-limits
                    if any(marker in line.lower() for marker in ["generated", "build", "dist", "out", "target"]):
                        off_limits.add(line)
        except OSError:
            pass

    # CODEOWNERS: list every covered path (a CODEOWNER means "this code is owned, be careful")
    for codeowners_path in [root / "CODEOWNERS", root / ".github" / "CODEOWNERS", root / "docs" / "CODEOWNERS"]:
        if codeowners_path.exists():
            try:
                with open(codeowners_path) as f:
                    for line in f:
                        line = line.strip()
                        if not line or line.startswith("#"):
                            continue
                        # First whitespace-separated token is the path pattern
                        parts = line.split()
                        if parts:
                            off_limits.add(parts[0])
            except OSError:
                pass
            break

    # Generated-file patterns
    off_limits.add("*.generated.*")
    off_limits.add("*_pb2.py")
    off_limits.add("*_pb2_grpc.py")

    return sorted(off_limits)


def extract_role_one_liner(agent_file: Path) -> str | None:
    """Try to extract a one-line role summary from a sub-agent markdown file."""
    try:
        with open(agent_file) as f:
            content = f.read()
    except OSError:
        return None

    # Look for "## Role" heading and grab the next non-empty line
    role_match = re.search(r"^##\s+Role[^\n]*\n+(.+?)(?:\n\n|\n##|\Z)", content, re.MULTILINE | re.DOTALL)
    if role_match:
        first_line = role_match.group(1).strip().split("\n")[0]
        if first_line and not first_line.startswith("#"):
            return first_line[:200]  # Cap length

    # Fall back to frontmatter description
    fm_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if fm_match:
        desc_match = re.search(r"^description:\s*(.+?)$", fm_match.group(1), re.MULTILINE)
        if desc_match:
            return desc_match.group(1).strip()[:200]

    return None


def extract_command_description(command_file: Path) -> str | None:
    """Extract the description from a command's frontmatter."""
    try:
        with open(command_file) as f:
            content = f.read()
    except OSError:
        return None

    fm_match = re.search(r"^---\n(.*?)\n---", content, re.DOTALL)
    if fm_match:
        desc_match = re.search(r"^description:\s*(.+?)$", fm_match.group(1), re.MULTILINE)
        if desc_match:
            return desc_match.group(1).strip()[:200]
    return None


def discover_existing_infrastructure(root: Path) -> dict:
    """List existing sub-agents and slash commands under .claude/."""
    agents = []
    commands = []

    agents_dir = root / ".claude" / "agents"
    if agents_dir.is_dir():
        for agent_file in sorted(agents_dir.glob("*.md")):
            agents.append({
                "name": agent_file.stem,
                "path": str(agent_file.relative_to(root)),
                "role": extract_role_one_liner(agent_file),
            })

    commands_dir = root / ".claude" / "commands"
    if commands_dir.is_dir():
        for cmd_file in sorted(commands_dir.glob("*.md")):
            commands.append({
                "name": cmd_file.stem,
                "path": str(cmd_file.relative_to(root)),
                "description": extract_command_description(cmd_file),
            })

    return {"agents": agents, "commands": commands}


def main() -> int:
    parser = argparse.ArgumentParser(description="Survey a repository for the architect plugin.")
    parser.add_argument("--root", default=".", help="Repository root (default: cwd)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        return 2

    survey = {
        "root": str(root),
        "surveyed_at": datetime.now(timezone.utc).isoformat(),
        "stack": detect_stack(root),
        "paths": {
            "loops": ".claude/loops/",
            "agents": ".claude/agents/",
            "off_limits": detect_off_limits(root),
        },
        "existing_infrastructure": discover_existing_infrastructure(root),
        "claude_md_present": (root / "CLAUDE.md").exists(),
        "claude_md_path": "CLAUDE.md" if (root / "CLAUDE.md").exists() else None,
        "architect_json_present": (root / ".architect.json").exists(),
    }

    print(json.dumps(survey, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
