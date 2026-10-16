"""Per-session state outside any project: requests, budgets, cache, log.

Layout under the state root (see config.state_root):
  sessions/<session>/state.json   requests with their budgets and cached verdicts
  sessions/<session>/index.json   transcript references (transcript.py)
  sessions/<session>/log.jsonl    one line per hook decision: outcome, timing,
                                  usage, categories and refs; no message text
  sessions/<session>/lock         serializes evaluations within the session
  evalbox/                        the reviewer's throwaway working directories
"""

from __future__ import annotations

import contextlib
import fcntl
import json
import os
import re
import shutil
import time
from pathlib import Path

LOG_MAX_BYTES = 1024 * 1024


def session_dir(root: Path, session_id: str) -> Path:
    safe = re.sub(r"[^A-Za-z0-9_-]", "_", session_id)[:80] or "unknown"
    path = root / "sessions" / safe
    path.mkdir(parents=True, exist_ok=True)
    return path


@contextlib.contextmanager
def locked(path: Path, wait_s: float):
    """Hold an exclusive lock on <path>/lock; yields False if it never came."""
    fh = open(path / "lock", "a+")
    deadline = time.monotonic() + wait_s
    got = False
    try:
        while True:
            try:
                fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
                got = True
                break
            except BlockingIOError:
                if time.monotonic() >= deadline:
                    break
                time.sleep(0.1)
        yield got
    finally:
        if got:
            fcntl.flock(fh, fcntl.LOCK_UN)
        fh.close()


def load(path: Path) -> dict:
    try:
        data = json.loads((path / "state.json").read_text(encoding="utf-8"))
        if isinstance(data, dict) and isinstance(data.get("requests"), dict):
            return data
    except (OSError, ValueError):
        pass
    return {"requests": {}, "order": []}


def save(path: Path, data: dict) -> None:
    tmp = path / "state.json.tmp"
    tmp.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    os.replace(tmp, path / "state.json")


def request(data: dict, key: str, cfg: dict, origin: str) -> dict:
    """The budgets of one user request, created on first sight."""
    req = data["requests"].get(key)
    if req is None:
        req = {"created": time.time(), "origin": origin, "diagnostic_shown": False, "cache": {},
               "budgets": {kind: {"evaluations": 0, "returns": 0} for kind in cfg["budgets"]}}
        data["requests"][key] = req
        data.setdefault("order", []).append(key)
        keep = int(cfg.get("max_requests_kept", 30))
        while len(data["order"]) > keep:
            old = data["order"].pop(0)
            data["requests"].pop(old, None)
    for kind in cfg["budgets"]:
        req["budgets"].setdefault(kind, {"evaluations": 0, "returns": 0})
    return req


def log(path: Path, record: dict) -> None:
    target = path / "log.jsonl"
    try:
        if target.exists() and target.stat().st_size > LOG_MAX_BYTES:
            os.replace(target, path / "log.1.jsonl")
        with open(target, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
    except OSError:
        pass


def prune(root: Path, retention_days: float) -> int:
    """Remove session directories untouched for longer than the retention."""
    removed = 0
    cutoff = time.time() - float(retention_days) * 86400
    base = root / "sessions"
    if not base.is_dir():
        return 0
    for child in base.iterdir():
        try:
            newest = max((p.stat().st_mtime for p in child.iterdir()), default=child.stat().st_mtime)
            if newest < cutoff:
                shutil.rmtree(child, ignore_errors=True)
                removed += 1
        except OSError:
            continue
    box = root / "evalbox"
    if box.is_dir():
        for child in box.iterdir():  # leftovers of a killed hook
            try:
                if child.stat().st_mtime < time.time() - 3600:
                    shutil.rmtree(child, ignore_errors=True)
            except OSError:
                continue
    return removed
