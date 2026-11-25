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

import hashlib
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
REPORT_NAME = re.compile(r"[a-z0-9._-]+-(?P<id>(?P<stamp>[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{6})(?:-[0-9]+)?)\.md")


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
        if arg == "--no-commit":
            index += 1
            continue
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
    root = project_root().resolve()
    sessions_dir = root / SESSIONS_REL
    if sessions_dir.resolve() != sessions_dir:
        raise SystemExit("error: .harness/sessions must be inside the project without symlink redirects")
    sessions_dir.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    git_user = run_git(root, ["config", "user.name"]) or "unknown"
    session_id = f"{sanitize_user(git_user)}-{stamp[:-1]}"
    suffix = 2
    while os.path.lexists(sessions_dir / f"{session_id}.md"):
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


def report_path(root: Path, raw_path: str) -> tuple[Path, str]:
    path = Path(raw_path).absolute()
    if (path.parent.resolve() != (root / SESSIONS_REL).absolute()
            or path.is_symlink() or not path.is_file() or not REPORT_NAME.fullmatch(path.name)):
        raise ValueError("expected an existing session report in the project's .harness/sessions directory")
    return path, (SESSIONS_REL / path.name).as_posix()


def index_digest(root: Path, relative: str) -> str:
    entries = subprocess.run(["git", "ls-files", "--stage", "-z"], cwd=root,
                             capture_output=True, check=True).stdout
    encoded_path = os.fsencode(relative)
    other_entries = (entry for entry in entries.split(b"\0")
                     if entry and entry.partition(b"\t")[2] != encoded_path)
    return hashlib.sha256(b"\0".join(other_entries)).hexdigest()


def check_report(root: Path, path: Path) -> list[str]:
    # Isolated Python excludes the script directory. Add the known plugin path,
    # independently of the working directory, to share the reader's Markdown rules.
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from report_validation import findings

    roots = {str(root), str(path.parent.parent.parent)}
    git_dir = run_git(root, ["rev-parse", "--absolute-git-dir"])
    common_dir = run_git(root, ["rev-parse", "--path-format=absolute", "--git-common-dir"])
    worktree_names = set()
    if git_dir and common_dir and Path(git_dir).resolve() != Path(common_dir).resolve():
        main_name = Path(common_dir).parent.name
        worktree_names = {name for name in (root.name, Path(git_dir).name) if len(name) >= 3 and name != main_name}
    return findings(path, REPORT_NAME.fullmatch(path.name).group("stamp"), roots, worktree_names)


def plan_commit(root: Path, path: Path, relative: str) -> dict[str, Any]:
    if run_git(root, ["rev-parse", "--is-inside-work-tree"]) != "true":
        raise ValueError("the report is not inside a Git worktree")
    for marker in ("MERGE_HEAD", "CHERRY_PICK_HEAD", "REVERT_HEAD", "rebase-merge", "rebase-apply"):
        location = run_git(root, ["rev-parse", "--git-path", marker])
        if location and (root / location).exists():
            raise ValueError("a merge, rebase, cherry-pick or revert is in progress")
    head = run_git(root, ["rev-parse", "--verify", "HEAD"])
    blob = run_git(root, ["hash-object", "--", relative])
    if not blob:
        raise ValueError("cannot hash the report")
    old_blob = run_git(root, ["rev-parse", "--verify", f"HEAD:{relative}"]) if head else None
    if old_blob:
        if old_blob != blob:
            raise ValueError("this report is already committed with different content")
        return {"result": "already-committed", "commit": run_git(root, ["log", "-1", "--format=%h", "--", relative])}
    ignored = subprocess.run(["git", "check-ignore", "-q", "--", relative], cwd=root,
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    if ignored.returncode == 0:
        raise ValueError("the repository ignores the report path")
    if ignored.returncode != 1:
        raise ValueError("Git could not check whether the report path is ignored")
    if not all(run_git(root, ["var", identity]) for identity in ("GIT_AUTHOR_IDENT", "GIT_COMMITTER_IDENT")):
        raise ValueError("Git has no usable author or committer identity")
    problems = check_report(root, path)
    if problems:
        return {"result": "check-failed", "findings": problems}
    staged = run_git(root, ["ls-files", "--stage", "--", relative])
    if staged is None or (staged and run_git(root, ["rev-parse", "--verify", f":{relative}"]) != blob):
        raise ValueError("the report has a preexisting index entry that differs from the file")
    return {
        "result": "ready",
        "path": relative,
        "head": head or "unborn",
        "blob": blob,
        "other_index": index_digest(root, relative),
        "already_staged": bool(staged),
        "message": f"chore: add session report {REPORT_NAME.fullmatch(path.name).group('id')}",
    }


def verify_commit(root: Path, relative: str, previous: str, blob: str, index_before: str) -> dict[str, Any]:
    head = run_git(root, ["rev-parse", "--verify", "HEAD"])
    if (head or "unborn") == previous:
        return {
            "result": "no-commit",
            "other_index_preserved": index_before == index_digest(root, relative),
            "staged_blob": run_git(root, ["rev-parse", "--verify", f":{relative}"]),
        }
    parents = run_git(root, ["show", "-s", "--format=%P", head]) if head else None
    changed = run_git(root, ["diff-tree", "--root", "--no-commit-id", "--name-only", "-r", head]) if head else None
    checks = {
        "expected_parent": parents == ("" if previous == "unborn" else previous),
        "only_report": changed == relative,
        "expected_report": bool(head) and run_git(root, ["rev-parse", "--verify", f"{head}:{relative}"]) == blob,
        "other_index_preserved": index_before == index_digest(root, relative),
    }
    return {"result": "committed" if all(checks.values()) else "committed-unverified",
            "commit": head, **checks}


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] in {"check", "plan-commit", "check-staged", "verify-commit"}:
        command = args.pop(0)
        count = 4 if command in {"check-staged", "verify-commit"} else 1
        if len(args) != count:
            print("error: supply the report path and, for verification, head, blob and other_index", file=sys.stderr)
            return 2
        root = project_root().resolve()
        try:
            path, relative = report_path(root, args[0])
            if command == "check":
                problems = check_report(root, path)
                output = {"result": "check-failed" if problems else "checked", "findings": problems}
            elif command == "plan-commit":
                output = plan_commit(root, path, relative)
            else:
                output = verify_commit(root, relative, *args[1:])
                if command == "check-staged":
                    if (output["result"] != "no-commit" or not output["other_index_preserved"]
                            or output["staged_blob"] != args[2]
                            or run_git(root, ["hash-object", "--", relative]) != args[2]):
                        raise ValueError("HEAD, the staging area, or the report changed after planning")
                    output = {"result": "ready-to-commit"}
        except (OSError, ValueError, subprocess.SubprocessError) as error:
            reason = (str(error) if isinstance(error, ValueError) and not isinstance(error, UnicodeError)
                      else "report or Git state could not be read")
            output = {"result": "refused", "reason": reason}
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return {"check-failed": 3, "refused": 4, "committed-unverified": 7}.get(output["result"], 0)
    if args and args[0] == "prepare":
        args = args[1:]
    print(json.dumps(prepare(args), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
