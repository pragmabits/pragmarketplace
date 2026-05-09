---
description: Scaffold a bounded loop with stopping criterion, iteration cap, and progress evaluator. Refuses if the verifier is unclear.
argument-hint: <describe what the loop does, what success looks like, and how you measure progress>
---

# Loop Contract

A loop without a verifier is a roulette wheel. This command generates a loop **only after** confirming the three required pieces exist:

1. **Stopping criterion** — objective signal that says "done"
2. **Maximum iteration limit** — hard cap, not a hope
3. **Progress evaluator** — way to tell if iteration N is better than N-1

If any of these is vague, the command refuses to scaffold and instead helps the user define the missing piece.

It also surveys the project before scaffolding, so the generated loop respects existing conventions, paths, and infrastructure rather than imposing a generic template.

---

## Step 0 — Capability radar

Before anything else, invoke the `capability-radar` skill. The user may have a capability (in-session skill, sub-agent, slash command, or pragmatic plugin component) that already does the work this loop would do. If so, scaffolding is the wrong move.

Common matches at this stage:
- The user wants a loop that runs tests until they pass, and an existing skill/command already runs tests with structured output
- The user wants a loop that validates schemas, and an existing tool does schema validation

If the radar reports a clear match, stop and recommend the existing capability. Do not proceed with scaffolding unless the user explicitly chooses "generate new" in the radar's `AskUserQuestion`.

---

## Step 1 — Project survey

After the capability radar clears (i.e., nothing fits or the user opted to generate new), invoke the **project-survey** skill. Read `.architect.json` if present; otherwise run a fresh survey. The survey output gives you:

- Where loop files should be written (`paths.loops`)
- The default test command for this stack (`stack.test_commands`) — useful when the user says "when tests pass" without specifying
- Off-limits paths to add to guardrails (`paths.off_limits`)
- Existing sub-agents that might already do the job (`existing_infrastructure.agents`)
- Project-specific conventions to honor (`conventions`)

If an existing sub-agent in the project could serve as the verifier for this loop, **mention it before generating** — the loop should reference it rather than reinvent it.

---

## Input

User said:

> $ARGUMENTS

---

## Step 2 — Extract the three pieces

From the user's description, identify:

- **OBJECTIVE**: What is the loop trying to achieve? (one sentence)
- **STOP**: What concrete signal ends the loop? (e.g., "tests pass", "JSON validates against schema", "linter clean", "all files processed")
- **CAP**: Hard iteration limit. Default to 5 if user did not specify; ask if uncertain.
- **PROGRESS**: How does iteration N+1 know it improved over N? (e.g., "fewer failing tests", "lower error count", "schema errors reduced")

If any of OBJECTIVE / STOP / PROGRESS is missing or vague (e.g., "until it looks good", "until I'm happy", "high quality"):

> **STOP. Do not generate the loop.**
>
> Tell the user exactly which piece is unclear, give two or three concrete examples of what a good version would look like for *their* task, and ask them to specify it. Then stop.

If the user offers "Claude judges it" as the verifier, accept it only if you can also write the rubric Claude would apply (specific criteria, not "is it good"). If you cannot write the rubric, treat the verifier as missing.

## Step 3 — Generate the scaffold

Produce a file at `<paths.loops>/<short-name>.md` (from the project survey; defaults to `.claude/loops/`). Pick a short kebab-case name from the objective.

**Apply survey-derived adjustments before writing:**
- If the user's stopping criterion was generic ("when tests pass"), substitute the project's actual test command from `stack.test_commands`.
- Append every entry in `paths.off_limits` to the Guardrails section automatically.
- Append every relevant entry in `conventions` to the Guardrails section.
- If `existing_infrastructure.agents` includes a sub-agent that fits as the verifier or per-iteration step executor, reference it by name in the Per-iteration steps instead of duplicating its work.

```markdown
# Loop: <name>

## Objective
<one sentence>

## Stopping criterion
<concrete signal — e.g., "pytest exit code 0">

## Iteration cap
<N>

## Progress metric
<what improves between iterations>

## Per-iteration steps
1. <action — e.g., "Run the failing tests and capture stderr">
2. <action — e.g., "Identify the smallest change that addresses the topmost error">
3. <action — e.g., "Apply the change">
4. <action — e.g., "Re-run tests; record pass/fail count">

## Guardrails
- Do not modify files outside <scope>
- Do not modify <each path from paths.off_limits>
- Do not run destructive commands (<list>)
- No automatic commits or pushes
- <each relevant convention from the survey>
- If progress metric does not improve for 2 consecutive iterations, stop and report

## Observability
For each iteration, log:
- iteration number
- hypothesis ("I think the failure is X because Y")
- command(s) executed
- result (pass/fail count, error summary)
- decision for next iteration (or "stop: criterion met" / "stop: cap reached" / "stop: no progress")

Append logs to `.claude/loops/<name>.log` as JSON lines.

## Exit conditions (any of)
- Stopping criterion met → SUCCESS
- Iteration cap reached → PARTIAL (report best state)
- No progress for 2 iterations → STALLED (report and ask for human input)
- Guardrail violation attempted → ABORT
```

## Step 4 — Write it and confirm

After writing the file:

1. Show the user the path.
2. Show the OBJECTIVE / STOP / CAP / PROGRESS values you extracted, so they can verify.
3. Tell them exactly how to invoke it: "Read `.claude/loops/<name>.md` and execute the loop until an exit condition fires."
4. Remind them: **the scaffold is a contract. If you find yourself wanting to skip the verifier or extend the cap mid-run, the loop is failing — don't paper over it.**

---

## Anti-patterns to actively prevent

If the user describes any of these, name the problem:

- **"It will get better with more iterations"** without a metric → no, it won't; you'll oscillate.
- **"Claude can just judge"** without a rubric → that's vibes, not verification.
- **"No cap, run until done"** → no. Caps are mandatory.
- **"The loop figures out the criterion"** → criteria are inputs, not outputs.
