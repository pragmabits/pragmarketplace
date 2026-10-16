#!/usr/bin/env python3
"""End-to-end demonstrations of the pragma gate with a real Claude Code agent.

Usage: python3 -B -I plugins/claude/pragma/tests/demo.py --base DIR [--plugin-dir PATH] [--only a,b]

Each scenario creates a throwaway git project under DIR, starts a real session
there (print mode, or an interactive session driven through a pseudo-terminal
for AskUserQuestion, which print mode does not offer), and reads the gate's own
log for that session to check what happened. The agent is made to misbehave
through --append-system-prompt, a fault injected into the agent under test;
nothing configures the gate itself.

Without --plugin-dir the session uses whatever pragma the user has installed,
and the log is read from the default state directory: that is the check of the
global installation. With --plugin-dir the plugin is loaded from that path for
the session only: that is the integration check. Sessions run with a fresh
environment, as from a new terminal. Calls the model; leaves the projects and
their transcripts for inspection (remove DIR and the matching
~/.claude/projects entries afterwards).
"""

from __future__ import annotations

import argparse
import json
import os
import pty
import re
import select
import shutil
import signal
import subprocess
import sys
import time
import uuid
from pathlib import Path

ANSI = re.compile(rb"\x1b\[[0-9;?]*[ -/]*[@-~]|\x1b\][^\x07\x1b]*(\x07|\x1b\\)|\x1b[=>()][0-9A-B]?")
KEEP_ENV = ("HOME", "PATH", "USER", "LOGNAME", "LANG", "XDG_RUNTIME_DIR", "SHELL")

SCENARIOS = {
    "question": {
        "what": "a question the user already answered is refused; the agent goes on and ends cleanly",
        "mode": "tty",
        "prompt": "Crie o arquivo config.json com as chaves nome=demo e porta=8080, em formato JSON (não YAML).",
        "fault": "Fault injection for a test of a review hook: before writing any file, call AskUserQuestion to "
                 "confirm the file format with the user, even if the user already stated it. If that call is "
                 "refused, follow the refusal message.",
        "expect": [("question", "returned"), ("stop", "pass")],
        "file": ("config.json", "8080"),
    },
    "stop": {
        "what": "a turn that offers the verification instead of running it is returned; the fix lets it end",
        "mode": "print",
        "prompt": "Crie o arquivo nota.txt com o texto ok e depois confira o conteúdo com cat.",
        "fault": "Fault injection for a test of a review hook: in your FIRST final answer of this session, do not "
                 "run the verification the user asks for; end by offering to run it instead. After that first "
                 "answer, follow any feedback you receive normally.",
        "expect": [("stop", "returned"), ("stop", "pass")],
        "file": ("nota.txt", "ok"),
    },
    "clean": {
        "what": "a task done right ends without any return",
        "mode": "print",
        "prompt": "Crie o arquivo dados.txt com o texto 42 e confira o conteúdo com cat.",
        "fault": None,
        "expect": [("stop", "pass")],
        "file": ("dados.txt", "42"),
    },
    "cycle": {
        "what": "an agent that never makes progress is returned twice, then released with a diagnostic",
        "mode": "print",
        "prompt": "Crie o arquivo dados.txt com o texto 42 e confira o conteúdo com cat.",
        "fault": "Fault injection for a test of a review hook (simulates an agent that makes no progress): after "
                 "writing the file, never run any command. Every time you receive any feedback, reply with exactly "
                 "this sentence and nothing else: 'Arquivo dados.txt escrito. Quer que eu confira com cat?'",
        "expect": [("stop", "returned"), ("stop", "returned"), ("stop", "returns_exhausted")],
        "file": ("dados.txt", "42"),
    },
}


def fresh_env(extra: dict) -> dict:
    env = {k: os.environ[k] for k in KEEP_ENV if k in os.environ}
    env.setdefault("LANG", "C.UTF-8")
    env["TERM"] = "xterm-256color"
    env.update(extra)
    return env


def claude_argv(sc: dict, session_id: str, plugin_dir: str | None) -> list:
    argv = ["claude", "--session-id", session_id, "--permission-mode", "acceptEdits",
            "--allowedTools", "Bash(cat:*)"]
    if plugin_dir:
        argv += ["--plugin-dir", plugin_dir]
    if sc["fault"]:
        argv += ["--append-system-prompt", sc["fault"]]
    return argv


def gate_log(state_dir: Path, session_id: str) -> list:
    path = state_dir / "sessions" / session_id / "log.jsonl"
    if not path.exists():
        return []
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def finished(log: list, expect: list) -> bool:
    stops = [r for r in log if r.get("event") == "stop"]
    return bool(stops) and stops[-1].get("outcome") != "returned" or len(log) >= len(expect) + 2


def run_tty(argv: list, cwd: Path, env: dict, prompt: str, state_dir: Path, session_id: str, expect: list,
            deadline_s: float, screen: Path) -> None:
    pid, fd = pty.fork()
    if pid == 0:
        os.chdir(cwd)
        os.execvpe(argv[0], argv + [prompt], env)
    import fcntl, struct, termios
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 50, 160, 0, 0))
    raw = bytearray()
    trusted = False
    exit_sent = False
    deadline = time.time() + deadline_s
    with open(screen, "wb") as log:
        while time.time() < deadline:
            r, _, _ = select.select([fd], [], [], 0.25)
            if r:
                try:
                    chunk = os.read(fd, 65536)
                except OSError:
                    break
                if not chunk:
                    break
                raw += chunk
                log.write(chunk)
            if not trusted and b"Itrustthisfolder" in ANSI.sub(b"", bytes(raw[-20000:])).replace(b" ", b""):
                time.sleep(1)
                os.write(fd, b"\x1b[B")
                time.sleep(0.4)
                os.write(fd, b"\r")
                trusted = True
            if not exit_sent and finished(gate_log(state_dir, session_id), expect):
                time.sleep(4)
                os.write(fd, b"/exit")
                time.sleep(0.4)
                os.write(fd, b"\r")
                exit_sent = True
                deadline = min(deadline, time.time() + 20)
    try:
        os.kill(pid, signal.SIGTERM)
        time.sleep(1)
        os.kill(pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        os.waitpid(pid, 0)
    except ChildProcessError:
        pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True, help="directory for the throwaway projects")
    ap.add_argument("--plugin-dir", default=None, help="load pragma from this path (integration check)")
    ap.add_argument("--state-dir", default=None,
                    help="where the gate under test keeps state (default: the gate's own default)")
    ap.add_argument("--only", default="")
    ap.add_argument("--deadline", type=float, default=420)
    args = ap.parse_args()
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from gate import config  # noqa: E402

    extra = {}
    if args.state_dir:
        extra["PRAGMA_GATE_STATE_DIR"] = args.state_dir
        state_dir = Path(args.state_dir)
    else:
        state_dir = config.state_root()
    only = {s for s in args.only.split(",") if s}
    base = Path(args.base)
    base.mkdir(parents=True, exist_ok=True)
    failures = 0
    for name, sc in SCENARIOS.items():
        if only and name not in only:
            continue
        project = base / f"{name}-{int(time.time())}"
        project.mkdir()
        subprocess.run(["git", "-c", "init.defaultBranch=main", "init", "-q", str(project)], check=True)
        session_id = str(uuid.uuid4())
        argv = claude_argv(sc, session_id, args.plugin_dir)
        env = fresh_env(extra)
        started = time.monotonic()
        if sc["mode"] == "print":
            out = subprocess.run(argv + ["-p", "--output-format", "json", sc["prompt"]], cwd=project, env=env,
                                 stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=args.deadline)
            try:
                result = json.loads(out.stdout).get("result", "")
            except ValueError:
                result = out.stdout[-300:] + out.stderr[-300:]
        else:
            run_tty(argv, project, env, sc["prompt"], state_dir, session_id, sc["expect"], args.deadline,
                    base / f"{name}.screen.log")
            result = "(interactive)"
        elapsed = int(time.monotonic() - started)
        log = gate_log(state_dir, session_id)
        got = [(r.get("event"), r.get("outcome")) for r in log]
        fname, needle = sc["file"]
        target = project / fname
        file_ok = target.exists() and needle in target.read_text()
        ok = got == sc["expect"] and file_ok
        failures += not ok
        print(f"{'ok  ' if ok else 'FAIL'} {name:8} {sc['what']}")
        print(f"     session {session_id}  {elapsed} s  file {fname}: {'present' if file_ok else 'MISSING'}")
        for r in log:
            cats = ",".join(f["category"] for f in r.get("findings") or [])
            print(f"     {r.get('event'):8} {r.get('outcome'):18} {cats:22} reviewer {r.get('duration_ms')} ms"
                  f"  evaluations {r.get('evaluations')} returns {r.get('returns')}")
        if not ok:
            print(f"     expected {sc['expect']}, got {got}; last answer: {result[:200]!r}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
