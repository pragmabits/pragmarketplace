---
name: loop-forensics
description: Use this when a loop is misbehaving — running too long, oscillating between solutions, not converging, hitting its iteration cap without success, or when the user says things like "it keeps going back and forth", "it's not making progress", "the loop is stuck", "Claude won't stop iterating". Diagnoses the failure mode and recommends a fix.
---

# Loop Forensics

Loops fail in a small number of recognizable ways. Diagnose first, fix second.

**Pattern detection is mechanical** — counting iterations, comparing values, looking for alternation. Delegate that to the analyzer script. Your role is the *prescription*: what change to make, given the diagnosis.

---

## Step 1 — Run the analyzer

If the loop has a log file (typically `.claude/loops/<name>.log`), run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/loop_log_analyze.py <log-file>
```

The script returns JSON with detected `patterns`. Each pattern has a `code` (oscillation, stagnation, no-progress, cap-reached, scope-creep, verifier-flapping), `severity`, `evidence`, and the iterations involved.

If there is no log file, you'll need to read the loop definition (`.claude/loops/<name>.md`) and ask the user what symptoms they observed. Skip to Step 3 in that case.

## Step 2 — Map patterns to prescriptions

Each pattern code maps to a known fix. Use this table; the analyzer tells you which patterns fired, you tell the user what to do.

### `oscillation` (A→B→A→B in failing_count_after)
**What it means:** Two competing constraints both seem necessary; the agent satisfies one and breaks the other.
**Fix:** Make both constraints part of the verifier *simultaneously*. If both must hold to PASS, the loop can't oscillate to a state that PASSes one only.

### `stagnation` (failing_count unchanged across 3+ consecutive iterations)
**What it means:** Each iteration applies a change but it doesn't move the metric. Either the agent is making cosmetic edits, or the metric is the wrong one.
**Fix:** Add a "no-progress" stop condition (bail out after 2 unchanged iterations). Then ask: is the metric measuring the right thing? If the agent is fixing tests but the failure count stays the same, maybe the failures are in different tests each time — track which specific tests fail, not just the count.

### `no-progress` (cap reached, last failing_count >= first)
**What it means:** The loop ran the full cap without net improvement. Either the task isn't loop-shaped, or the verifier is wrong.
**Fix:** Stop and reconsider. Run `/triage` on the underlying task — it may belong in Tier 2 (single execution with tools) rather than Tier 3 (loop).

### `cap-reached` (loop hit cap without PASS)
**What it means:** The loop didn't converge in the time given. Could be too few iterations, or could be that the task is harder than expected.
**Fix:** Look at the `total_progress` field. If progress is positive and steady, raising the cap may help (but cap above 10 is usually a smell — see [scope-creep](#scope-creep)). If progress is small or zero, raising the cap won't help; the loop needs redesign.

### `scope-creep` (files modified expanded across iterations)
**What it means:** Each iteration's "fix" touches more files than the last. The loop is growing its blast radius.
**Fix:** Tighten the Guardrails section: explicit "do not modify files outside `<scope>`". If the fix genuinely needs broader changes, abort the loop and surface to the user — broadening should be a deliberate decision, not a silent expansion.

### `verifier-flapping` (verdict alternates PASS/FAIL)
**What it means:** The verifier itself is unreliable. Tests are flaky, the rubric is ambiguous, or the criterion has hidden non-determinism.
**Fix:** The loop is not the problem; the verifier is. Stop the loop, fix the verifier (deflake the tests, tighten the rubric, eliminate non-determinism), then resume.

## Step 3 — Patterns the analyzer can't detect

These need you to read the loop definition and reason:

### No verifier
**Signal:** Stopping criterion is "until it's good", "Claude judges", or absent. (Structural validator should also catch this.)
**Diagnosis:** This isn't a loop, it's a roulette wheel. There's no signal that says stop, so it stops when context runs out or the model gives up.
**Fix:** Define an objective criterion. **Before recommending the user create a verifier from scratch, invoke `capability-radar`** — if an in-session capability or pragmatic-installed plugin already provides verification (a test runner, schema validator, lint checker), reference it instead. Only recommend creating new verification infrastructure if no existing capability fits.

If no objective criterion is possible at all, the task is not loop-shaped — use a single execution and human review instead.

### Verifier too loose
**Signal:** Criterion is technically objective but admits many "passing" states (e.g., "tests pass" when only one test exists).
**Diagnosis:** The loop converges to *a* passing state, not *the* desired state. Symptoms: the fix is local but wrong, or the agent games the test.
**Fix:** Tighten the rubric. Add additional checks (regression tests, type checks, schema validation, "no files modified outside scope").

### Context bloat
**Signal:** Each iteration adds more accumulated context (previous failures, hypotheses, partial fixes). After a few rounds the agent loses the thread.
**Diagnosis:** The loop is carrying its own debris.
**Fix:** Each iteration should start from the *current artifact + criterion + last failure*, not the whole history. Truncate aggressively. Consider isolating verification in a sub-agent so the main agent never sees the full debug stream — invoke `capability-radar` first to check whether such a sub-agent already exists (the bundled `verifier-judge` is the plugin's own example, but the user may have their own).

---

## Output format

```
DIAGNOSIS: <pattern name(s) from the analyzer, or "no log available — judgment-based">

EVIDENCE:
<the analyzer's evidence lines, or your observations from the loop definition>

FIX:
<concrete change to the loop file or process>

IF FIX DOESN'T WORK:
<the next pattern to suspect, or "collapse to single-execution">
```

## When to recommend collapse

If two diagnostics fire on the same loop, or if the user has already tried fixing once without success, recommend collapsing the loop to Tier 2 (single execution with tools) and a manual verification pass. Loops that need repeated tuning are usually solving a problem that wasn't loop-shaped to begin with.
