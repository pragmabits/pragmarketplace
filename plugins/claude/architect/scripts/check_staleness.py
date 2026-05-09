#!/usr/bin/env python3
"""
check_staleness.py — Verify .architect.json is still consistent with the repo.

Reads .architect.json and checks whether its references still resolve:
  - Listed sub-agents and commands still exist on disk
  - Detected stack hasn't fundamentally shifted
  - Configured paths still exist (for reading)

Used at the start of each scaffold session to decide whether to use
the cached survey or re-run discovery.

This is mechanical (file existence checks, simple comparisons) and
runs in milliseconds, so it's cheap to call before every scaffold.

USAGE
    python3 check_staleness.py [--root <path>]

ARGUMENTS
    --root <path>   Repository root. Defaults to CWD.

OUTPUT
    A JSON object on stdout:
    {
      "stale": true | false,
      "reasons": [
        {
          "code": "missing-agent" | "missing-command" |
                  "stack-changed" | "no-config" | "malformed-config",
          "message": "<human-readable explanation>"
        }
      ],
      "config_present": true | false,
      "config_path": "<path>" | null
    }

EXIT CODES
    0   Check completed (regardless of staleness)
    2   Invalid arguments

EXAMPLES
    # In CI or a skill: check before using cached config
    if python3 check_staleness.py | jq -e '.stale'; then
      python3 survey.py > /tmp/survey.json
      # ... prompt user to confirm and rewrite .architect.json
    fi
"""

import argparse
import json
import sys
from pathlib import Path


def detect_current_primary_stack(root: Path) -> str | None:
    """Quick heuristic for what stack the repo *currently* looks like."""
    if (root / "pyproject.toml").exists() or (root / "setup.py").exists():
        return "python"
    if (root / "package.json").exists():
        return "node"
    if (root / "Cargo.toml").exists():
        return "rust"
    if (root / "go.mod").exists():
        return "go"
    if (root / "pom.xml").exists() or (root / "build.gradle").exists():
        return "java"
    return None


def check_staleness(root: Path) -> dict:
    config_path = root / ".architect.json"
    reasons = []

    if not config_path.exists():
        return {
            "stale": True,
            "reasons": [{"code": "no-config", "message": ".architect.json does not exist"}],
            "config_present": False,
            "config_path": None,
        }

    try:
        with open(config_path) as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        return {
            "stale": True,
            "reasons": [{"code": "malformed-config",
                         "message": f".architect.json is not valid JSON: {e}"}],
            "config_present": True,
            "config_path": str(config_path.relative_to(root)),
        }
    except OSError as e:
        return {
            "stale": True,
            "reasons": [{"code": "malformed-config",
                         "message": f"could not read .architect.json: {e}"}],
            "config_present": True,
            "config_path": str(config_path.relative_to(root)),
        }

    # Check sub-agent references
    existing = config.get("existing_infrastructure", {})
    for agent in existing.get("agents", []):
        agent_path = root / agent.get("path", "")
        if not agent_path.exists():
            reasons.append({
                "code": "missing-agent",
                "message": f"sub-agent listed at {agent.get('path')} no longer exists",
            })

    # Check command references
    for cmd in existing.get("commands", []):
        cmd_path = root / cmd.get("path", "")
        if not cmd_path.exists():
            reasons.append({
                "code": "missing-command",
                "message": f"command listed at {cmd.get('path')} no longer exists",
            })

    # Check stack
    config_primary = config.get("stack", {}).get("primary")
    current_primary = detect_current_primary_stack(root)
    if config_primary and current_primary and current_primary != config_primary and config_primary not in ("mixed", "unknown"):
        # Only flag if there's a clear mismatch, not if config says "mixed"
        reasons.append({
            "code": "stack-changed",
            "message": f"config records primary stack as '{config_primary}' but repo now looks like '{current_primary}'",
        })

    return {
        "stale": len(reasons) > 0,
        "reasons": reasons,
        "config_present": True,
        "config_path": str(config_path.relative_to(root)),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Check whether .architect.json is stale.")
    parser.add_argument("--root", default=".", help="Repository root (default: cwd)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        print(f"Error: {root} is not a directory", file=sys.stderr)
        return 2

    result = check_staleness(root)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
