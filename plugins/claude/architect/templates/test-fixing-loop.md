# Worked Example: Test-Fixing Loop

> **Note — this file is a worked reference, not a scaffold.** It lives in
> `templates/` to illustrate the architecture below; it does **not** match
> the section-name contract enforced by `scripts/validate.py` and will
> fail `/coordination-audit` if copied into `.claude/loops/` as-is. To
> generate a real, validator-passing loop file, run `/loop-contract`
> instead.

A concrete reference architecture for the canonical case where sub-agents and looping pay off: **fixing failing tests in a scoped module**.

This is the example because:
- Each sub-agent's role fits in one objective sentence
- The verifier is a real test runner, not vibes
- Iteration has a clear progress metric (failing-test count)
- Scope is bounded (one module)
- Failure is recoverable (revert the diff)

If your case doesn't have these properties, this template is the wrong shape for your problem.

---

## Architecture

```
┌─────────────────┐
│   Main agent    │  Orchestrates. Owns the loop and the cap.
│  (orchestrator) │
└────────┬────────┘
         │
   ┌─────┴─────┐
   ▼           ▼
┌──────┐   ┌──────┐
│ fix- │   │veri- │
│worker│   │fier- │
│      │   │judge │
└──────┘   └──────┘
   │           │
   │ patch     │ PASS/FAIL
   └─────┬─────┘
         │
         ▼
   loop iterates
   until PASS or cap
```

### Roles

**Main agent (orchestrator)**
- Holds the loop counter, cap, and stall detection
- Calls fix-worker with the current failure context
- Calls verifier-judge with the criterion
- Decides: iterate / stop-pass / stop-cap / stop-stall / abort

**fix-worker** (sub-agent)
- Role: Given failing test output and a scope path, produce the smallest diff that addresses the topmost failure without modifying files outside scope.
- Input: failing test output, scope path
- Output: diff (unified format) + one-line hypothesis
- Failure: returns FAIL=cannot-fix-locally if the fix would require changes outside scope

**verifier-judge** (sub-agent — included in this plugin)
- Role: Given a stopping criterion and the current state, return PASS/FAIL with one-line evidence
- Already defined in `agents/verifier-judge.md`

---

## Why this shape passes the three filters

1. **One-sentence roles**: each sub-agent has a clean "given X, produce Y, fail when Z" definition
2. **Objective verifier**: pytest exit code, not "does it look fixed"
3. **Different concerns**: fix-worker writes code; verifier-judge runs tests. Different tool sets, different contexts.

---

## Loop contract

- **Stopping criterion**: `pytest <scope>/ exits 0`
- **Iteration cap**: 5
- **Progress metric**: number of failing tests (must decrease or stay equal-with-different-failures)
- **Stall**: 2 consecutive iterations with no decrease → STALLED
- **Guardrails**:
  - fix-worker may only modify files under `<scope>`
  - No commits, no pushes
  - No package installs
  - If a fix would require schema or dependency changes, abort

---

## Per-iteration log line (JSON)

```json
{
  "iter": 2,
  "failing_count_before": 5,
  "hypothesis": "TypeError in checkout.py:88 because amount is str not int",
  "diff_summary": "src/payments/checkout.py: cast amount to int at parse time",
  "verdict": "FAIL",
  "evidence": "3 of 5 prior failures resolved; 2 new failures in test_refund.py",
  "failing_count_after": 2,
  "decision": "iterate"
}
```

---

## When to **not** use this shape

- Failures span multiple unrelated modules → no clean scope, drop to single-execution
- "Fix" requires API design decisions → human input needed, not a loop
- No tests exist → there's no verifier; write tests first or use single-execution review
- Tests are flaky → the criterion is unreliable; fix the tests before automating fixes
