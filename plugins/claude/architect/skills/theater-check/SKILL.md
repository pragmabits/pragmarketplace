---
name: theater-check
description: Use this whenever the user is designing, sketching, or proposing a multi-agent setup, agent pipeline, multi-step orchestration, or "agent that reviews / refines / plans for another agent." Triggers on phrases like "I want one agent that does X, another that does Y", "planner and worker", "review agent", "orchestrator", "multi-agent", "agent pipeline", "subagent for X". Runs four filter questions before any architecture is committed to, starting with whether an existing capability already covers the task.
---

# Theater Check

The user is sketching a multi-agent design. Most of these proposals collapse to a single agent with tools once you ask the right questions. Run the three filters below **before** scaffolding anything.

## The four filter questions

Walk through these in order. Ask the user the ones you can't answer from context. Question 1 is special: it can short-circuit the whole design before the user spends thought on the rest.

### 1. Does an existing capability already cover this?

Invoke the `capability-radar` skill. The user may already have a tool, skill, sub-agent, slash command, or pragmatic plugin component that does what they're describing. If so, the multi-agent design is moot before it starts — they should use the existing thing.

Only proceed to questions 2–4 if the radar reports no fit, or the user explicitly chooses to design new infrastructure anyway.

### 2. Can each piece be described in one objective sentence?

Try to write each agent's role as: **"Given X, produce Y, failing when Z."**

If you can't, that piece is theater. Examples:

- ❌ "An agent that thinks about the problem" — no Y, no Z
- ❌ "A reviewer agent" — review *what* against *what*?
- ✅ "Given a diff, return a list of test functions whose behavior the diff likely changes"

### 3. Is there an objective verifier between stages?

If agent A's output goes to agent B, what tells you A's output was good enough to hand off? If the answer is "B will figure it out" or "the user will see," there is no verifier — and the pipeline is a single agent stretched over multiple turns at higher cost.

A real verifier is a test, a schema, a metric, a rubric — something that can return PASS/FAIL without asking a human.

### 4. Does each agent have a different context, different tools, or run in parallel?

If every agent sees the same context and uses the same tools, you have one agent in three hats. The cost (prompt overhead, handoff loss, debugging difficulty) is real; the gain (specialization, isolation, parallelism) is fictional.

## What to do based on the answers

### All four pass cleanly
Proceed. Recommend `/subagent-contract` for each role and `/loop-contract` if there's iteration.

### Question 1 fails (existing capability covers it)
The whole design is unnecessary. Recommend the existing capability and stop. This is the cheapest collapse and the most common one.

### One of questions 2–4 fails
Tell the user *which* failed and *why*, in plain language. Then recommend the collapse:

- If question 2 fails → drop the vague piece; it's not a real role
- If question 3 fails → use a single agent (Tier 2) until the user can articulate a verifier
- If question 4 fails → use a single agent; the "pipeline" is doing nothing the single agent wouldn't do

Offer `/triage` for a tier recommendation, or `/architect` if they want to be walked through the full flow including scaffolding.

### User pushes back ("but it's clearer this way")

Acknowledge that *describing* the work in stages is often genuinely useful. But describing in stages and *implementing* in stages are different things. A single prompt can say "first plan, then code, then review" and execute it in one turn. Multi-agent should be reserved for cases where the cost is paid back in measurable wins.

## Tone

Be direct, not preachy. The user is thinking through a design; your job is to surface the questions they'd ask themselves if they had more time. One pass through the filters, clear recommendation, then move on. Do not lecture.

## When NOT to invoke

- The user is asking *how* sub-agents or loops work in general — that's a docs question, not a design review
- The user has already run `/triage` or `/architect` and committed to a tier — respect the decision
- The task is clearly single-agent (no mention of multiple roles, stages, or pipelines)
