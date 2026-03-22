"""Commit mode: stage per spec and create a commit.

Does NOT validate the commit message. Validation stays with validate-commit.py.
"""

import os
import time

from dulwich.repo import Repo

from stager import stage_spec


def commit_staged(repo_path: str, spec: dict, message: str) -> dict:
    """Stage per spec and create a commit.

    Returns:
        {"ok": True, "commit": "sha", "message": "...", "staged": {...}}
    """
    repo_path = os.path.abspath(repo_path)

    # Stage first
    stage_result = stage_spec(repo_path, spec)
    if not stage_result["ok"]:
        return stage_result

    # Create commit
    repo = Repo(repo_path)

    # Read committer info from git config
    config = repo.get_config_stack()
    try:
        name = config.get(b"user", b"name").decode("utf-8")
        email = config.get(b"user", b"email").decode("utf-8")
    except KeyError:
        raise ValueError(
            "Git user.name and user.email must be configured. "
            "Run: git config user.name 'Name' && git config user.email 'email@example.com'"
        )

    author = f"{name} <{email}>".encode("utf-8")
    commit_time = int(time.time())
    # Get timezone offset from local time (handles DST correctly)
    tz = time.localtime(commit_time).tm_gmtoff

    commit_sha = repo.do_commit(
        message=message.encode("utf-8"),
        author=author,
        committer=author,
        author_timestamp=commit_time,
        author_timezone=tz,
        commit_timestamp=commit_time,
        commit_timezone=tz,
    )

    sha_str = commit_sha.decode("ascii") if isinstance(commit_sha, bytes) else str(commit_sha)

    return {
        "ok": True,
        "commit": sha_str[:7],
        "commit_full": sha_str,
        "message": message,
        "staged": stage_result["staged"],
    }
