#!/usr/bin/env python3
"""Stand-in for `claude -p` in the gate's deterministic tests.

FAKE_PLAN: JSON file with a list of steps, consumed one per call, the last one
repeating. A step is {"verdict": "pass"|"revise"|"unknown", "category": ...,
"refs": [...] (default: the request ref and F or Q)}, or {"raw": "text"} to
print text instead of JSON, or {"exit": n}, plus an optional {"sleep": s}.
FAKE_LOG: directory where each call records argv, cwd, selected env, the
prompt received and its start and end times.
"""

import fcntl
import json
import os
import re
import sys
import time


def main():
    log_dir = os.environ["FAKE_LOG"]
    plan = json.load(open(os.environ["FAKE_PLAN"]))
    with open(os.path.join(log_dir, "counter"), "a+") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX)
        fh.seek(0)
        n = len(fh.read())
        fh.write("x")
    step = plan[min(n, len(plan) - 1)]
    prompt = sys.stdin.read()
    started = time.time()
    record = {"n": n, "argv": sys.argv[1:], "cwd": os.getcwd(), "pid": os.getpid(), "start": started,
              "env": {k: os.environ.get(k) for k in ("PRAGMA_GATE_EVALUATOR", "CLAUDE_PROJECT_DIR",
                                                     "CLAUDE_CODE_SESSION_ID")}}
    path = os.path.join(log_dir, f"call-{n}.json")
    with open(path, "w") as fh:
        json.dump(record, fh)
    match = re.search(r"```json\n(.*)\n```", prompt, re.S)
    package = json.loads(match.group(1)) if match else {}
    with open(os.path.join(log_dir, f"package-{n}.json"), "w") as fh:
        json.dump(package, fh)
    if step.get("sleep"):
        time.sleep(step["sleep"])
    record["end"] = time.time()
    with open(path, "w") as fh:
        json.dump(record, fh)
    if "exit" in step:
        sys.stderr.write("fake failure\n")
        sys.exit(step["exit"])
    if "raw" in step:
        sys.stdout.write(step["raw"])
        return
    verdict = step.get("verdict", "pass")
    reply = {"verdict": verdict, "findings": [], "missing": []}
    if verdict == "revise":
        refs = step.get("refs")
        if refs is None:
            refs = [r for r in ((package.get("request") or {}).get("ref"),
                                "Q" if package.get("event") == "question" else "F") if r]
        reply["findings"] = [{"category": step.get("category", "delegated_work"), "refs": refs,
                              "description": "fake finding", "action": "fake action"}]
    elif verdict == "unknown":
        reply["missing"] = ["fake missing item"]
    out = {"type": "result", "subtype": "success", "is_error": False, "result": json.dumps(reply),
           "structured_output": reply, "duration_api_ms": 1,
           "usage": {"input_tokens": 10, "output_tokens": 5}, "modelUsage": {"fake-model": {}}}
    sys.stdout.write(json.dumps(out))


if __name__ == "__main__":
    main()
