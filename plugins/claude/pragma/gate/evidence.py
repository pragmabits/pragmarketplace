"""Build the evidence package the reviewer judges, within a byte limit.

Tool-agnostic: it takes indexed items (see transcript.py for the kinds) and a
loader that returns each item's content. Everything selected keeps its stable
reference; everything left out is recorded in `omitted`, and every cut text
says where and how much was cut.
"""

from __future__ import annotations

import json

KIND_NAMES = {
    "U": "user", "N": "user_answer", "A": "assistant", "T": "tool",
    "H": "hook_feedback", "I": "interrupt", "S": "harness_message",
    "M": "user_file", "C": "harness_context",
    "D": "assistant",  # shown on screen, not yet in the transcript (display.py)
    "G": "assistant",  # narration, shown on screen as a summary; marked `summarized`
}
# Per-item text caps (characters). The request, the question and the final
# response get the largest share; tool output keeps its head and its tail,
# where exit status and summaries usually are.
CAP_REQUEST = 12000
CAP_FINAL = 16000
CAP_QUESTION = 8000
CAP_USER = 3000
CAP_ASSISTANT = 3000
CAP_TOOL_INPUT = 1500
CAP_TOOL_RESULT = 3000
CAP_HOOK = 2000
CAP_ATTACHED = 12000       # each file attached to the current request
CAP_ATTACHED_TOTAL = 24000
CAP_CONTEXT = 2000
RESERVE = 2048  # room for the omitted list and envelope


def cut(text: str, cap: int) -> str:
    if text is None:
        return ""
    if len(text) <= cap:
        return text
    head = cap * 2 // 3
    tail = cap - head
    return f"{text[:head]}\n[... {len(text) - cap} characters cut here ...]\n{text[-tail:]}"


def cut_parts(head: str, dropped: int, tail: str, cap: int) -> str:
    """cut() for a text kept as its head and tail, with `dropped` characters already gone between them."""
    if not dropped:
        return cut(head + tail, cap)
    keep = cap * 2 // 3
    return (f"{head[:keep]}\n[... {len(head) + dropped + len(tail) - cap} characters cut here ...]\n"
            f"{tail[-(cap - keep):]}")


def _size(obj) -> int:
    return len(json.dumps(obj, ensure_ascii=False, separators=(",", ":")).encode("utf-8"))


def _render(item: dict, loader, results: dict) -> dict:
    kind = item["kind"]
    out = {"ref": item["ref"], "kind": KIND_NAMES.get(kind, kind)}
    if kind == "D":
        out["text"] = cut_parts(item["head"], item["dropped"], item["tail"], CAP_ASSISTANT)
        return out
    content = loader.text(item)
    if kind == "T":
        raw_input = content.get("input")
        out["tool"] = content.get("tool") or item.get("name")
        out["input"] = cut(json.dumps(raw_input, ensure_ascii=False), CAP_TOOL_INPUT)
        res = results.get(item.get("tool_id"))
        if res is not None:
            res_content = loader.text(res)
            out["result"] = {"ref": res["ref"], "is_error": res_content.get("is_error", False),
                             "text": cut(res_content.get("text", ""), CAP_TOOL_RESULT)}
        else:
            out["result"] = None
        return out
    if kind == "M":
        out["file"] = content.get("file")
    if kind == "G":
        out["summarized"] = True
    cap = {"U": CAP_USER, "N": CAP_USER, "A": CAP_ASSISTANT, "G": CAP_ASSISTANT, "H": CAP_HOOK}.get(kind, CAP_USER)
    out["text"] = cut(content.get("text", ""), cap)
    return out


def build(event: str, items: list, loader, prompt_id: str | None, extras: dict, limit: int) -> tuple[dict, set, dict]:
    """Return (package, refs present, stats)."""
    notes = list(extras.get("notes") or [])
    results = {i.get("tool_id"): i for i in items if i["kind"] in ("R", "N") and i.get("tool_id")}
    visible = [i for i in items if i["kind"] not in ("R", "C")]  # results ride inside their tool call
    latest_context = {}
    for i in items:
        if i["kind"] == "C":
            latest_context[i.get("ctype")] = i
    # Where the current request starts.
    start = None
    if prompt_id:
        for pos, item in enumerate(visible):
            if item["kind"] == "U" and item.get("prompt_id") == prompt_id:
                start = pos
                break
    if start is None:
        for pos in range(len(visible) - 1, -1, -1):
            if visible[pos]["kind"] == "U":
                start = pos
                break
        if start is not None:
            notes.append("request located as the last user message: its prompt id was not found in the transcript")
    package = {"event": event}
    if start is None:
        package["request"] = None
        notes.append("the user's request was not found in the transcript")
        history, turn = [], visible
    else:
        req = visible[start]
        package["request"] = {"ref": req["ref"], "text": cut(loader.text(req).get("text", ""), CAP_REQUEST)}
        history, turn = visible[:start], visible[start + 1:]
        # Files attached with @ arrive right after the prompt and are part of it.
        attached = []
        while turn and turn[0]["kind"] == "M":
            attached.append(turn.pop(0))
        room = CAP_ATTACHED_TOTAL
        for item in attached:
            content = loader.text(item)
            text = cut(content.get("text", ""), max(1000, min(CAP_ATTACHED, room)))
            room -= len(text)
            package["request"].setdefault("attached_files", []).append(
                {"ref": item["ref"], "file": content.get("file"), "text": text})
    # Text shown on screen that the transcript did not hold yet is the newest of the turn.
    turn = turn + list(extras.get("shown") or [])
    if latest_context:
        package["context"] = [{"ref": i["ref"], "kind": "harness_context", "type": i.get("ctype"),
                               "text": cut(loader.text(i).get("text", ""), CAP_CONTEXT)}
                              for i in sorted(latest_context.values(), key=lambda i: i["line"])]
    if event == "question":
        questions = extras.get("questions")
        encoded = json.dumps(questions, ensure_ascii=False)
        if len(encoded) > CAP_QUESTION:
            questions = cut(encoded, CAP_QUESTION)
        package["proposed_question"] = {"ref": "Q", "questions": questions}
    else:
        final = extras.get("final_response")
        if final is None:
            last_a = [i for i in turn if i["kind"] == "A"]
            if last_a:
                final = loader.text(last_a[-1]).get("text", "")
                notes.append("final response taken from the transcript: the stop event carried none")
        package["final_response"] = {"ref": "F", "text": cut(final or "", CAP_FINAL)}
        # The closing assistant blocks are the final response itself: list
        # their refs on F instead of sending the same text twice.
        same = []
        for item in reversed(turn):
            if item["kind"] != "A" or not final or loader.text(item).get("text", "").strip() not in final:
                break
            same.append(item)
        if same:
            package["final_response"]["same_as"] = [i["ref"] for i in reversed(same)]
            turn = [i for i in turn if i not in same]
        if extras.get("background_tasks"):
            package["background_tasks"] = extras["background_tasks"]
    base = _size(package) + RESERVE

    # Selection order: what the user said and decided, and the text shown with
    # the question, then this turn's actions, then earlier assistant text and
    # actions. Newest first in each.
    decisive = ("U", "N", "H", "I", "M")
    first = decisive + ("D",)
    tiers = [
        [i for i in turn if i["kind"] in first],
        [i for i in history if i["kind"] in decisive],
        [i for i in turn if i["kind"] not in first],
        [i for i in history if i["kind"] in ("A", "G")],
        [i for i in history if i["kind"] not in decisive + ("A", "G")],
    ]
    chosen = {}
    used = base
    omitted_refs = []
    full = False
    for tier in tiers:
        for item in reversed(tier):
            if full:
                omitted_refs.append(item)
                continue
            rendered = _render(item, loader, results)
            size = _size(rendered) + 1
            if used + size > limit:
                omitted_refs.append(item)
                # Small items may still fit; stop trying once little room is left.
                if limit - used < 512:
                    full = True
                continue
            chosen[item["ref"]] = rendered
            used += size
    package["history"] = [chosen[i["ref"]] for i in history if i["ref"] in chosen]
    package["turn"] = [chosen[i["ref"]] for i in turn if i["ref"] in chosen]
    omitted = []
    left_out = {id(i) for i in omitted_refs}
    for section, pool in (("history", history), ("turn", turn)):
        refs = [i for i in pool if id(i) in left_out]
        if refs:
            kinds = {}
            for i in refs:
                name = KIND_NAMES.get(i["kind"], i["kind"])
                kinds[name] = kinds.get(name, 0) + 1
            omitted.append({"section": section, "count": len(refs), "first": refs[0]["ref"],
                            "last": refs[-1]["ref"], "kinds": kinds, "reason": "package size limit"})
    package["omitted"] = omitted
    package["notes"] = notes
    refs = set(chosen)
    for rendered in chosen.values():
        if rendered.get("result"):
            refs.add(rendered["result"]["ref"])
    if package.get("request"):
        refs.add(package["request"]["ref"])
        refs.update(f["ref"] for f in package["request"].get("attached_files", []))
    refs.update(c["ref"] for c in package.get("context", []))
    refs.add("Q" if event == "question" else "F")
    refs.update(package.get("final_response", {}).get("same_as", []))
    stats = {"bytes": _size(package), "items": len(chosen),
             "omitted": sum(o["count"] for o in omitted), "notes": len(notes)}
    return package, refs, stats
