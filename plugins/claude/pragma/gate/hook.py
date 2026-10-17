#!/usr/bin/env python3
"""Claude Code adapter for the pragma gate. Usage: hook.py <event>

Events: session-start, user-prompt-submit, message-display, pre-tool-use
(AskUserQuestion only), stop. Reads the hook input on stdin and answers on
stdout in Claude Code's hook format. Any failure of the gate itself lets the
session go on: this script exits 0 and, at most once per request, says why in
a systemMessage.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from gate import config, display, state  # noqa: E402

EVENTS = {"session-start", "user-prompt-submit", "message-display", "pre-tool-use", "stop"}


def emit(obj: dict) -> None:
    sys.stdout.write(json.dumps(obj, ensure_ascii=False))
    sys.stdout.write("\n")


def main(argv: list) -> int:
    if os.environ.get("PRAGMA_GATE_EVALUATOR"):
        return 0  # the reviewer's own process: never review the reviewer
    event = argv[1] if len(argv) > 1 else ""
    if event not in EVENTS:
        print(f"pragma gate: unknown event {event!r}", file=sys.stderr)
        return 0
    try:
        data = json.loads(sys.stdin.read() or "null")
    except ValueError:
        print("pragma gate: hook input is not JSON; skipped", file=sys.stderr)
        return 0
    if not isinstance(data, dict) or not isinstance(data.get("session_id"), str):
        print("pragma gate: hook input has no session_id; skipped", file=sys.stderr)
        return 0
    cfg, problem = config.load()
    if problem:
        print(f"pragma gate: {problem}; using defaults", file=sys.stderr)
    if not cfg.get("enabled", True):
        return 0
    root = config.state_root()
    sdir = state.session_dir(root, data["session_id"])

    if event == "session-start":
        display.clear(sdir)
        state.prune(root, cfg["retention_days"])
        return 0

    prompt_id = data.get("prompt_id")
    if event == "user-prompt-submit":
        with state.locked(sdir, 5) as got:
            if got:
                st = state.load(sdir)
                state.request(st, prompt_id or f"prompt-{time.time():.0f}", cfg, "user-prompt-submit")
                st["current"] = prompt_id
                state.save(sdir, st)
        display.clear(sdir)  # what the previous request showed is no longer needed
        return 0

    if data.get("agent_id"):
        return 0  # subagents are not reviewed directly; the main stop covers what they return
    if event == "message-display":
        display.record(root, sdir, data)
        return 0

    # Loaded only for the reviewed moments: Claude Code waits on message-display
    # before showing each batch of text, so that path stays light.
    from gate import core, evidence, transcript
    if event == "pre-tool-use":
        if data.get("tool_name") != "AskUserQuestion":
            return 0
        kind = "question"
        extras = {"questions": (data.get("tool_input") or {}).get("questions")}
    else:
        kind = "stop"
        extras = {"final_response": data.get("last_assistant_message"),
                  "background_tasks": data.get("background_tasks") or []}

    started = time.monotonic()
    record = {"ts": time.strftime("%Y-%m-%dT%H:%M:%S%z"), "prompt_id": prompt_id}
    decision = None
    with state.locked(sdir, float(cfg["lock_wait_s"])) as got:
        if not got:
            record.update(event=kind, outcome="lock_timeout", released=True)
            decision = {"action": "allow", "agent_message": None, "record": record,
                        "user_message": f"pragma {core.LABEL[kind]} skipped: another review of this session was still running"}
        else:
            st = state.load(sdir)
            key = prompt_id or st.get("current") or "unidentified"
            req = state.request(st, key, cfg, "hook" if key not in st["requests"] else "user-prompt-submit")
            index = transcript.update_index(sdir / "index.json", data.get("transcript_path") or "")
            model = cfg.get("model") or index.get("model")
            if index.get("missing"):
                # Without the transcript there is no evidence to judge; a call
                # could only come back inconclusive.
                decision = core.release(kind, req, "skipped: the session transcript is not available",
                                        "no_transcript", str(sdir / "log.jsonl"))
            else:
                if kind == "question":
                    index, extras["shown"], extras["notes"], record["display"] = display.for_question(
                        root, sdir, cfg, index, data.get("tool_use_id"), prompt_id)
                else:
                    index, record["final_wait"] = transcript.settle_final(
                        sdir / "index.json", index, extras["final_response"], float(cfg["stop_wait_s"]))
                    if record["final_wait"]["held"] is False:
                        extras["notes"] = [transcript.FINAL_MISSING]
                    display.tidy(sdir, index, prompt_id)
                if not transcript.holds_prompt(index, prompt_id):
                    # Judging now would mean judging against an earlier request.
                    decision = core.release(kind, req, "skipped: the current request is not in the transcript yet",
                                            "no_request", str(sdir / "log.jsonl"))
                else:
                    with transcript.Loader(index["path"]) as loader:
                        package, refs, stats = evidence.build(kind, index["items"], loader, prompt_id, extras,
                                                              int(cfg["package_limit_bytes"]))
                    record.update(package=stats)
                    decision = core.review(kind, req, package, refs, cfg, model, root / "evalbox",
                                           lambda: state.save(sdir, st), str(sdir / "log.jsonl"))
            record.update(decision["record"])
            state.save(sdir, st)
    record["hook_ms"] = int((time.monotonic() - started) * 1000)
    state.log(sdir, record)

    if decision["action"] == "block":
        if kind == "stop":
            emit({"decision": "block", "reason": decision["agent_message"]})
        else:
            emit({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                         "permissionDecisionReason": decision["agent_message"]}})
    elif decision.get("user_message"):
        emit({"systemMessage": decision["user_message"]})
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv))
    except Exception:  # the gate must never break the session it watches
        import traceback
        print("pragma gate: internal error; the session continues without review\n" + traceback.format_exc()[-1500:],
              file=sys.stderr)
        emit({"systemMessage": "pragma gate: internal error; this moment went on without review (details on stderr)"})
        sys.exit(0)
