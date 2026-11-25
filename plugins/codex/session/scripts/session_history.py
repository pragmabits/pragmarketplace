"""Summarize local Codex activity after a report through the App Server."""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def rpc(process: subprocess.Popen[str], method: str, params: dict | None = None) -> dict:
    request = {"method": method}
    if params is not None:
        request.update(id=1, params=params)
    process.stdin.write(json.dumps(request) + "\n")
    process.stdin.flush()
    if params is None:
        return {}
    for line in process.stdout:
        reply = json.loads(line)
        if reply.get("id") == 1:
            if not isinstance(reply.get("result"), dict):
                raise ValueError(f"App Server rejected {method}")
            return reply["result"]
    raise ValueError("App Server closed the connection")


def pages(process: subprocess.Popen[str], method: str, params: dict):
    cursor = None
    seen = set()
    while True:
        request = {**params, "cursor": cursor} if cursor else params
        page = rpc(process, method, request)
        yield from page["data"]
        cursor = page.get("nextCursor")
        if not cursor:
            return
        if cursor in seen:
            raise ValueError("App Server repeated a page")
        seen.add(cursor)


def project_worktrees() -> list[str]:
    root = Path.cwd().resolve()
    result = subprocess.run(["git", "worktree", "list", "--porcelain", "-z"], cwd=root,
                            capture_output=True, check=False)
    if result.returncode != 0:
        return [str(root)]
    paths = {str(root)}
    for field in result.stdout.split(b"\0"):
        if field.startswith(b"worktree "):
            path = Path(os.fsdecode(field[len(b"worktree "):]))
            if path.is_dir():
                paths.add(str(path.resolve()))
    return sorted(paths)


def report_time(session_id: str) -> int:
    match = re.search(r"([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{6})(?:-[0-9]+)?$", session_id)
    return int(datetime.strptime(match[1], "%Y-%m-%dT%H%M%S").replace(tzinfo=timezone.utc).timestamp())


def prompts_after(process: subprocess.Popen[str], thread_id: str, cutoff: int) -> tuple[dict[str, float], bool]:
    prompts = {}
    complete = True
    saw_turn = False
    for turn in pages(process, "thread/turns/list", {
        "threadId": thread_id, "sortDirection": "desc", "itemsView": "full", "limit": 15,
    }):
        saw_turn = True
        started, finished = turn.get("startedAt"), turn.get("completedAt")
        if isinstance(started, int) and isinstance(finished, int) and finished <= cutoff:
            # Older turns may have no timestamps. Keep paging until the returned
            # dates can exclude this turn; don't infer dates from UUIDs or file mtimes.
            continue
        for item in turn["items"]:
            if item["type"] != "userMessage":
                continue
            millis = item.get("startedAtMs") or item.get("completedAtMs")
            if isinstance(millis, int):
                timestamp = millis / 1000
            elif isinstance(started, int) and started > cutoff:
                timestamp = started
            else:
                complete = False
                continue
            if timestamp > cutoff:
                prompts[item["id"]] = timestamp
    # Listing an updated thread does not guarantee the server has turn history
    # ready to return, especially for paginated histories after a cold start.
    return prompts, complete and saw_turn


def read_activity(process: subprocess.Popen[str], cutoff: int, current: str | None) -> dict:
    rpc(process, "initialize", {"clientInfo": {"name": "pragmarketplace_session", "version": "1"}})
    rpc(process, "initialized")
    paths = project_worktrees()
    tracked = {}
    params = {
        "cwd": paths, "sortKey": "updated_at", "sortDirection": "desc", "limit": 25,
        "sourceKinds": ["cli", "vscode", "appServer"],
        "useStateDbOnly": True, "currentAccountOnly": True,
    }
    for archived in (False, True):
        for thread in pages(process, "thread/list", {**params, "archived": archived}):
            if thread["updatedAt"] <= cutoff:
                break
            if thread.get("cwd") in paths and not thread.get("parentThreadId") and not thread.get("ephemeral"):
                tracked[thread["id"]] = thread
    current_session = tracked.get(current, {}).get("sessionId") or current
    complete = current is not None
    sessions = {}
    for thread in tracked.values():
        thread_id = thread["id"]
        session_id = thread.get("sessionId") or thread_id
        if current in (thread_id, session_id) or current_session == session_id:
            continue
        try:
            prompts, exact = prompts_after(process, thread_id, cutoff)
        except (KeyError, ValueError, OSError):
            complete = False
            continue
        complete = complete and exact
        if prompts:
            session = sessions.setdefault(session_id, {"ids": [], "prompts": {}})
            session["ids"].append(thread_id)
            session["prompts"].update(prompts)
    items = []
    for session in sessions.values():
        when = datetime.fromtimestamp(max(session["prompts"].values()), tz=timezone.utc)
        items.append({"ids": sorted(session["ids"]), "last_activity": when.isoformat(),
                      "prompts_after": len(session["prompts"])})
    items.sort(key=lambda item: item["last_activity"], reverse=True)
    return {"state": "read" if complete else "partial", "current_known": current is not None, "items": items}


def activity(cutoff: int, current: str | None) -> dict:
    with tempfile.TemporaryFile() as stderr:
        with subprocess.Popen(["codex", "app-server", "--stdio"], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                              stderr=stderr, text=True, encoding="utf-8") as process:
            try:
                return read_activity(process, cutoff, current)
            except (OSError, ValueError):
                stderr.seek(0)
                error = stderr.read(32768).lower()
                if (b"error: read-only file system" in error
                        or (b"failed to initialize sqlite state runtime" in error
                            and b"unable to open database file" in error)):
                    return {"state": "unavailable", "reason": "local-profile-access"}
                raise
            finally:
                if process.poll() is None:
                    process.terminate()


def main() -> None:
    report, newest = sys.argv[1:]
    result = {"report": report, "since": None, "sessions": {"state": "unavailable"}}
    try:
        result["since"] = datetime.fromtimestamp(report_time(report), tz=timezone.utc).isoformat()
        cutoff = report_time(newest)
        # This hint is present on local Codex shells. If absent, still return
        # activity, explicitly marking that the running thread could be listed.
        current = os.environ.get("CODEX_THREAD_ID") or None
        result["sessions"] = activity(cutoff, current)
        result["sessions"]["after"] = datetime.fromtimestamp(cutoff, tz=timezone.utc).isoformat()
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError):
        pass
    print(json.dumps(result))


if __name__ == "__main__":
    main()
