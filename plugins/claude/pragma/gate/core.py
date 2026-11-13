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
import re
import time

from . import evaluator

LABEL = {"question": "question review", "stop": "stop review"}
CACHE_KEEP = 8
CITED_MAX = 3      # cited items shown as evidence per finding
HEAD_CHARS = 110   # an item's start, shown when none of the reviewer's quotes is found in it
QUOTE_CHARS = 240  # a quote longer than this is shown cut
QUOTE_MIN = 4      # a shorter quote proves nothing about where it came from
QUOTE_MARKS = ('"', "“", "”", "'", "...", "…")


def cache_key(event: str, package: dict, model: str | None, cfg: dict) -> str:
    material = {"event": event, "rubric": evaluator.rubric_digest(event), "model": model,
                "effort": cfg.get("effort"), "package": package}
    return hashlib.sha256(json.dumps(material, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def _flat(text: str) -> str:
    return " ".join(text.split())


def _strings(value) -> list:
    """The strings inside a decoded JSON value, in order; keys are left out."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [s for v in value.values() for s in _strings(v)]
    if isinstance(value, list):
        return [s for v in value for s in _strings(v)]
    return []


ESCAPE = re.compile(r'\\(?:u([0-9a-fA-F]{4})|(["\\/bfnrt]))')
ESCAPED = {'"': '"', "\\": "\\", "/": "/", "b": "\b", "f": "\f", "n": "\n", "r": "\r", "t": "\t"}


def _unescaped(text: str) -> str:
    """The text with its JSON escapes read, as a reviewer quoting it may write it.

    Tool output often carries escapes as text (`can't encode character
    '\\u00e7'`), and the reviewer, reading the package as JSON, quotes them
    decoded ('ç').
    """
    out = ESCAPE.sub(lambda m: chr(int(m.group(1), 16)) if m.group(1) else ESCAPED[m.group(2)], text)
    return out.encode("utf-16", "surrogatepass").decode("utf-16", "replace")  # joins escaped surrogate pairs


def _decoded(encoded: str) -> str:
    """A JSON-encoded text as the reviewer reads it: its strings when it is whole, unescaped when it was cut."""
    try:
        return "\n".join(_strings(json.loads(encoded)))
    except ValueError:
        return _unescaped(encoded)


def _texts(package: dict) -> dict:
    """Every reference of the package, with the texts a quote of it can come from; the first is its own."""
    found = {}

    def add(ref, *texts):
        if ref:
            own = [t for t in texts if isinstance(t, str)]
            found[ref] = own + [u for u in map(_unescaped, own) if u not in own]

    request = package.get("request")
    if request:
        add(request["ref"], request["text"])
        for attached in request.get("attached_files", []):
            add(attached["ref"], attached.get("text"))
    for context in package.get("context", []):
        add(context["ref"], context.get("text"))
    for item in package.get("history", []) + package.get("turn", []):
        if item.get("kind") == "tool":
            encoded = item.get("input", "")
            add(item["ref"], f"{item.get('tool')} {encoded}", _decoded(encoded))
            if item.get("result"):
                add(item["result"]["ref"], item["result"].get("text", ""))
        else:
            add(item["ref"], item.get("text"))
    final = package.get("final_response")
    if final:
        add("F", final["text"])
        for ref in final.get("same_as", []):  # the closing blocks the final response is made of
            add(ref, final["text"])
    proposed = package.get("proposed_question")
    if proposed:
        questions = proposed["questions"]
        add("Q", json.dumps(questions, ensure_ascii=False),
            _decoded(questions) if isinstance(questions, str) else "\n".join(_strings(questions)))
    return found


def _head(text: str) -> str:
    line = _flat(text)
    return line[:HEAD_CHARS] + ("..." if len(line) > HEAD_CHARS else "")


def _quote_forms(quote: str) -> list:
    """The quote as given, then without the quotation marks or ellipses a reviewer may put around it."""
    given = _flat(quote)
    bare = given
    trimmed = True
    while trimmed:
        trimmed = False
        for mark in QUOTE_MARKS:
            if bare.startswith(mark):
                bare, trimmed = bare[len(mark):].lstrip(), True
            if bare.endswith(mark):
                bare, trimmed = bare[:-len(mark)].rstrip(), True
    return [form for form in dict.fromkeys((given, bare)) if len(form) >= QUOTE_MIN]


def _quoted(quote: str, texts: list) -> str | None:
    """The quote as it stands in one of the texts, with "..." where the text goes on; None if none holds it."""
    for form in _quote_forms(quote):
        for text in texts:
            line = _flat(text)
            at = line.find(form)
            if at < 0:
                continue
            if len(form) > QUOTE_CHARS:
                return ("..." if at else "") + form[:QUOTE_CHARS] + "..."
            return ("..." if at else "") + form + ("..." if at + len(form) < len(line) else "")
    return None


def _evidence(finding: dict, texts: dict) -> tuple[list, int, int]:
    """Return (cited, quotes given, quotes found): up to CITED_MAX (ref, excerpt) pairs, the quoted items first.

    A cited item shows the first of the reviewer's quotes found in it, so the
    reader sees the passage that proves the finding, not the item's start; an
    item that holds none shows its start. A quote found in no cited item is
    not shown: only text the package holds can be evidence.
    """
    quotes = finding.get("quotes") or []
    cited = [r for r in dict.fromkeys(finding["refs"]) if r in texts]
    quoted = {}
    for ref in cited:
        for quote in quotes:
            excerpt = _quoted(quote, texts[ref])
            if excerpt is not None:
                quoted[ref] = excerpt
                break
    found = sum(1 for quote in quotes if any(_quoted(quote, texts[r]) is not None for r in cited))
    shown, seen = [], set()
    for ref in [r for r in cited if r in quoted] + [r for r in cited if r not in quoted]:
        excerpt = quoted.get(ref) or _head(texts[ref][0])
        if excerpt in seen:  # a closing block of F quoted as F was
            continue
        seen.add(excerpt)
        shown.append((ref, excerpt))
        if len(shown) == CITED_MAX:
            break
    return shown, len(quotes), found


def agent_message(event: str, findings: list, package: dict, returns: int, limit: int) -> tuple[str, dict]:
    """Return (the message for the agent, how many of the reviewer's quotes were given and found)."""
    texts = _texts(package)
    lines = [f"pragma {LABEL[event]} (return {returns} of {limit}):"]
    given = found = 0
    for f in findings:
        lines.append(f"- [{f['category']}] {f['description']}")
        cited, n_given, n_found = _evidence(f, texts)
        given, found = given + n_given, found + n_found
        if cited:
            lines.append("  Evidence: " + "; ".join(f"{ref}: \"{excerpt}\"" for ref, excerpt in cited))
        lines.append(f"  Action: {f['action']}")
    lines.append("This return comes from the pragma control, not from the user. It grants no new "
                 "permission and does not widen the request. If the evidence does not support it, "
                 "say so with that evidence instead of complying.")
    return "\n".join(lines), {"given": given, "found": found}


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
                decision["agent_message"], record["quotes"] = agent_message(
                    event, verdict["findings"], package, budget["returns"], int(limits["returns"]))
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
