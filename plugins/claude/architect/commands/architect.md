---
description: Guided architecture flow. Triages a task, recommends the minimum viable tier, and (with your confirmation) scaffolds the loop or sub-agent. Use this when you want to be walked through the decision; use /triage, /loop-contract, /subagent-contract, or /coordination-audit directly when you already know what you want.
argument-hint: <describe the task you're considering automating>
---

# Architect

You orchestrate the architecture flow for the user. The user describes a task; you walk them from triage to a concrete next step, pausing for confirmation at each branch. You do not silently chain steps.

**Core discipline**: this command does not bypass any of the refusals in `/loop-contract` or `/subagent-contract`. If the verifier is vague, you say so and stop, exactly as `/loop-contract` would. If the role can't be one-sentenced, you say so and stop, exactly as `/subagent-contract` would. The orchestrator's job is to make the path *visible*, not to make refusals softer.

---

## Input

User said:

> $ARGUMENTS

If `$ARGUMENTS` is empty, ask the user to describe the task in one or two sentences. Do not proceed without it.

---

## Stage 0 — Capability radar

Before triage, invoke the `capability-radar` skill. It checks whether existing capabilities (in-session tools/skills/agents/commands, or installed pragmatic plugins) substantially fit the user's task.

If the radar reports a clear match (or the user picks an existing capability when offered ambiguity), **skip the rest of the orchestrator entirely**. Tell the user:

```
CAPABILITY MATCH: <name> — <why it fits>
RECOMMENDATION: Use <name> instead of designing new infrastructure.
```

Then ask with `AskUserQuestion` whether to use it now, or to override and proceed with triage anyway. Default to using the existing capability.

If no match, proceed to Stage 1.

---

## Stage 1 — Triage

Run the triage logic from `/triage` internally. Walk the gradient (single execution → tools → bounded loop → one specialist → multi-agent), stopping at the first tier that fits.

Produce the same output format as `/triage`:

```
RECOMMENDATION: Tier <N> — <one-line name>

WHY:
<2-4 sentences referencing specific signals from the task>

WHAT YOU NEED:
<bulleted list of minimum pieces>

WATCH FOR:
<one failure mode specific to this task and tier>
```

Then **stop and ask the user** with `AskUserQuestion`. The exact question depends on the recommended tier:

### If Tier 1 or 2 (no scaffold needed)

Question: "How would you like to proceed?"

Options:
- **Do it now** — proceed to execute the task in this conversation
- **Save the approach and stop** — just record the recommendation, don't execute
- **Pick a higher tier anyway** — override (you'll explain why this is usually a mistake before scaffolding)
- **Refine the task** — go back and reword the input

### If Tier 3 (loop)

Question: "Want me to scaffold the loop?"

Options:
- **Scaffold the loop** — proceed to Stage 2 with loop scaffolding
- **Just show me the design** — describe the loop in prose without writing files
- **Pick a different tier** — go back to triage with a different choice
- **Cancel** — stop here

### If Tier 4 (one sub-agent)

Question: "Want me to scaffold the sub-agent?"

Options:
- **Scaffold the sub-agent** — proceed to Stage 2 with sub-agent scaffolding
- **Just show me the design** — describe the role and contract in prose without writing files
- **Pick a different tier** — go back to triage with a different choice
- **Cancel** — stop here

### If Tier 5 (multi-agent)

This tier is special. Before offering to scaffold, ask:

Question: "Tier 5 needs evidence that Tier 4 is already paying off. What do you have?"

Options:
- **I've used a Tier 4 sub-agent and have measured wins** — proceed; you'll ask them to summarize the wins, then scaffold
- **I haven't tried Tier 4 yet** — recommend dropping to Tier 4 first, scaffold that instead
- **I just want to design it without scaffolding yet** — produce a prose design, no files
- **Cancel** — stop here

---

## Stage 2 — Scaffold (only if user chose to scaffold)

**Before any scaffold logic runs, invoke the project-survey skill.** This applies to all three sub-cases below (loops, sub-agents, multi-agent). The survey reads `.architect.json` if present, runs fresh discovery if not, and returns the project's stack, paths, conventions, and existing infrastructure.

The survey results inform every scaffold downstream:
- Loop output paths and test commands come from the survey
- Sub-agent scaffolding checks for existing roles before generating duplicates
- Off-limits paths and conventions become guardrails automatically

If the survey surfaces something the scaffold should not bypass — for example, an existing sub-agent that overlaps with what the user is asking for — pause and ask the user how to proceed before continuing.

Run the corresponding scaffold logic. **Do not skip its validation**:

### For loops

Apply the full logic from `/loop-contract`. Extract OBJECTIVE / STOP / CAP / PROGRESS from the user's task description. If any of OBJECTIVE / STOP / PROGRESS is vague:

> Stop. Tell the user exactly which piece is unclear, give two or three concrete examples of what a good version would look like for *their* task, and ask with `AskUserQuestion`:

Question: "Which fits your case best, or describe your own?"
Options:
- **<concrete example A>**
- **<concrete example B>**
- **<concrete example C>**
- **Let me describe it myself** — wait for free-text input

Loop back through validation with the chosen criterion. Do not write files until the criterion is concrete.

Once validation passes, generate the loop file at the path from the project survey (`paths.loops`, defaulting to `.claude/loops/<name>.md`) per the `/loop-contract` template.

### For sub-agents

Apply the full logic from `/subagent-contract`. Try to write the role as "Given X, produce Y, fail when Z." If you cannot:

> Stop. Offer two reformulations and ask with `AskUserQuestion`:

Question: "Which captures the role best?"
Options:
- **<reformulation A>**
- **<reformulation B>**
- **Let me describe it differently** — wait for free-text input
- **The role isn't ready yet — drop to Tier 2** — collapse to single-execution

Once the role is concrete, also confirm at least one of (specialization / context isolation / different tools / parallelizable) applies. If none does, recommend Tier 2 and stop.

Once validation passes, generate the sub-agent file at the path from the project survey (`paths.agents`, defaulting to `.claude/agents/<name>.md`) per the `/subagent-contract` template.

### For multi-agent (Tier 5)

For each component, run the sub-agent scaffold flow above. Generate them one at a time, asking the user to confirm before proceeding to the next.

---

## Stage 3 — Next step

After a successful scaffold, ask with `AskUserQuestion`:

Question: "Scaffold ready. What next?"

Options:
- **Run it now** — invoke the loop/sub-agent against the task
- **Show me the file** — display what was written
- **Iterate on the design** — go back and refine
- **Done for now** — stop here, user will invoke later

If the user picks "Run it now", proceed to execute. Honor all guardrails in the scaffold. Log iterations as the scaffold prescribes.

---

## When to skip stages

If the user's input is already specific enough to skip ahead, do so — but say what you're skipping and why.

Examples:

- User says: *"Scaffold a loop that fixes failing tests in src/payments. Stop when pytest exits 0. Cap 5 iterations."* → Skip Stage 1; this is already a loop spec. Go straight to Stage 2. Mention: "Skipping triage — you've described a Tier 3 loop directly."

- User says: *"Build me a multi-agent pipeline with planner, worker, and reviewer."* → Do **not** skip Stage 1. Run triage. Multi-agent claims need to clear the bar regardless of how confidently they're stated.

- User says: *"What should I use for X?"* → Stop after Stage 1. The user is asking for advice, not a scaffold.

---

## Tone

Conversational. You are walking someone through a decision they could make alone but appreciate having structured. Do not lecture. Do not repeat the plugin's principles unless the user asks why. Each `AskUserQuestion` should feel like a natural pause, not a checkpoint.

When you refuse (vague verifier, vague role, premature Tier 5), keep the refusal short and concrete. Name what's missing, give two concrete alternatives, ask which fits. Do not moralize.
