"""CLI entry point for git-staging tool.

Non-interactive hunk-level staging via Dulwich.

Usage:
    python git-staging.pyz parse [--repo PATH]
    python git-staging.pyz stage [--repo PATH] --spec SPEC_JSON
    python git-staging.pyz unstage [--repo PATH] --spec SPEC_JSON
    python git-staging.pyz commit [--repo PATH] --spec SPEC_JSON --message MSG
"""

import argparse
import json
import sys

from parser import parse_repo
from stager import stage_spec
from unstager import unstage_spec
from committer import commit_staged


def _read_spec(raw: str) -> dict:
    """Read spec from inline JSON or @filepath."""
    if raw.startswith("@"):
        filepath = raw[1:]
        with open(filepath, "r") as f:
            return json.load(f)
    return json.loads(raw)


def main() -> int:
    repo_parent = argparse.ArgumentParser(add_help=False)
    repo_parent.add_argument("--repo", default=".", help="Path to git repository (default: .)")

    ap = argparse.ArgumentParser(
        prog="git-staging",
        description="Non-interactive hunk-level staging tool",
    )
    sub = ap.add_subparsers(dest="command", required=True)

    sub.add_parser("parse", parents=[repo_parent], help="Parse repository state (read-only)")

    stage_p = sub.add_parser("stage", parents=[repo_parent], help="Stage files/hunks per spec")
    stage_p.add_argument("--spec", required=True, help="JSON spec or @filepath")

    unstage_p = sub.add_parser("unstage", parents=[repo_parent], help="Unstage files (reset to HEAD)")
    unstage_p.add_argument("--spec", required=True, help="JSON spec or @filepath")

    commit_p = sub.add_parser("commit", parents=[repo_parent], help="Stage and commit per spec")
    commit_p.add_argument("--spec", required=True, help="JSON spec or @filepath")
    commit_p.add_argument("--message", required=True, help="Commit message")

    args = ap.parse_args()

    try:
        if args.command == "parse":
            result = parse_repo(args.repo)
        elif args.command == "stage":
            spec = _read_spec(args.spec)
            result = stage_spec(args.repo, spec)
        elif args.command == "unstage":
            spec = _read_spec(args.spec)
            result = unstage_spec(args.repo, spec)
        elif args.command == "commit":
            spec = _read_spec(args.spec)
            result = commit_staged(args.repo, spec, args.message)
        else:
            ap.print_help(sys.stderr)
            return 1

        json.dump(result, sys.stdout, indent=2, ensure_ascii=False)
        sys.stdout.write("\n")
        return 0

    except Exception as exc:
        error = {"ok": False, "error": str(exc)}
        json.dump(error, sys.stderr, indent=2, ensure_ascii=False)
        sys.stderr.write("\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
