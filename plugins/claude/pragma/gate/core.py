"""Decide what one review moment does: budgets, cache, reviewer call, outcome.

Tool-agnostic. The adapter hands in the request's state, the evidence package
and a persist callback; it gets back whether to let the moment through, what
to tell the agent and, at most once per request, what to tell the user.
Control failures (timeout, reviewer error, invalid reply, exhausted budget)
always let the moment through and are never recorded as approval.
"""

from __future__ import annotations

import hashlib
import json
import time

from . import evaluator

LABEL = {"question": "question review", "stop": "stop review"}
CACHE_KEEP = 8


def cache_key(event: str, package: dict, model: str | None, cfg: dict) -> str:
    material = {"event": event, "rubric": evaluator.rubric_digest(event), "model": model,
                "effort": cfg.get("effort"), "package": package}
    return hashlib.sha256(json.dumps(material, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _excerpts(package: dict) -> dict:
    found = {}

    def add(ref, text):
        if ref and isinstance(text, str):
            line = " ".join(text.split())
            found[ref] = line[:110] + ("..." if len(line) > 110 else "")

    if package.get("request"):
        add(package["request"]["ref"], package["request"]["text"])
    for item in package.get("history", []) + package.get("turn", []):
        if item.get("kind") == "tool":
            add(item["ref"], f"{item.get('tool')} {item.get('input', '')}")
            if item.get("result"):
                add(item["result"]["ref"], item["result"].get("text", ""))
        else:
            add(item["ref"], item.get("text"))
    if package.get("final_response"):
        add("F", package["final_response"]["text"])
    if package.get("proposed_question"):
        add("Q", json.dumps(package["proposed_question"]["questions"], ensure_ascii=False))
    return found


def agent_message(event: str, findings: list, package: dict, returns: int, limit: int) -> str:
    excerpts = _excerpts(package)
    lines = [f"pragma {LABEL[event]} (return {returns} of {limit}):"]
    for f in findings:
        lines.append(f"- [{f['category']}] {f['description']}")
        cited = [f"{r}: \"{excerpts[r]}\"" for r in f["refs"][:3] if r in excerpts]
        if cited:
            lines.append("  Evidence: " + "; ".join(cited))
        lines.append(f"  Action: {f['action']}")
    lines.append("This return comes from the pragma control, not from the user. It grants no new "
                 "permission and does not widen the request. If the evidence does not support it, "
                 "say so with that evidence instead of complying.")
    return "\n".join(lines)


def release(event: str, req: dict, reason: str, outcome: str, log_path: str) -> dict:
    """Let the moment through without a review, telling the user once per request."""
    decision = {"action": "allow", "agent_message": None, "user_message": None,
                "record": {"event": event, "outcome": outcome, "released": True}}
    if not req.get("diagnostic_shown"):
        req["diagnostic_shown"] = True
        decision["user_message"] = f"pragma {LABEL[event]} {reason} (log: {log_path})"
    return decision


def review(event: str, req: dict, package: dict, refs: set, cfg: dict, model: str | None,
           work_root, persist, log_path: str) -> dict:
    budget = req["budgets"][event]
    limits = cfg["budgets"][event]
    key = cache_key(event, package, model, cfg)
    record = {"event": event, "cache": False}
    failure = None
    verdict = None
    cached = req["cache"].get(key)
    if cached is not None:
        verdict = cached["verdict"]
        record["cache"] = True
    elif budget["evaluations"] >= int(limits["evaluations"]):
        failure = f"skipped: the {event} evaluation budget of this request ({limits['evaluations']}) is used up"
        record["outcome"] = "evaluations_exhausted"
    else:
        budget["evaluations"] += 1
        persist()  # a hook killed mid-call must not get the attempt back
        result = evaluator.run(event, package, refs, cfg, model, work_root)
        for k in ("status", "duration_ms", "duration_api_ms", "usage", "model", "model_used", "effort", "reason"):
            if result.get(k) is not None:
                record[k] = result[k]
        if result["status"] == "ok":
            verdict = result["verdict"]
            req["cache"][key] = {"verdict": verdict, "at": time.time()}
            while len(req["cache"]) > CACHE_KEEP:
                req["cache"].pop(next(iter(req["cache"])))
        else:
            state_word = "unavailable" if result["status"] in ("timeout", "error") else "inconclusive"
            failure = f"{state_word}: {result.get('reason', result['status'])}"
            record["outcome"] = result["status"]
    record["evaluations"] = budget["evaluations"]
    decision = {"action": "allow", "agent_message": None, "user_message": None, "record": record}
    if verdict is not None:
        record["verdict"] = verdict["verdict"]
        if verdict["verdict"] == "revise":
            record["findings"] = [{"category": f["category"], "refs": f["refs"]} for f in verdict["findings"]]
            if budget["returns"] < int(limits["returns"]):
                budget["returns"] += 1
                decision["action"] = "block"
                decision["agent_message"] = agent_message(event, verdict["findings"], package,
                                                          budget["returns"], int(limits["returns"]))
                record["outcome"] = "returned"
            else:
                first = verdict["findings"][0]
                failure = (f"not returned: the correction budget of this request ({limits['returns']}) "
                           f"is used up; still open: [{first['category']}] {first['description']}")
                record["outcome"] = "returns_exhausted"
        elif verdict["verdict"] == "unknown":
            failure = "inconclusive: missing " + "; ".join(verdict["missing"])
            record["outcome"] = "unknown"
        else:
            record["outcome"] = "pass"
    record["returns"] = budget["returns"]
    if failure is not None:
        record["released"] = True
        if not req.get("diagnostic_shown"):
            req["diagnostic_shown"] = True
            decision["user_message"] = f"pragma {LABEL[event]} {failure[:400]} (log: {log_path})"
    return decision
