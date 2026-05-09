---
description: Audit an existing multi-agent or loop setup. Estimates orchestration overhead vs. observed gain. Flags theater.
argument-hint: <optional: path to a specific setup, otherwise audits .claude/agents and .claude/loops>
---

# Coordination Cost Audit

Every sub-agent and loop adds overhead: prompt tokens, context handoff, debugging difficulty, semantic loss between agents. This audit asks the question most teams skip: **is the gain from decomposition outweighing the cost?**

---

## Scope

Read `.architect.json` first if it exists — it tells you where the project keeps its agents and loops, and what conventions to honor.

If `$ARGUMENTS` points to a specific path, audit that. Otherwise, audit:
- `<paths.agents>` from the survey (defaults to `.claude/agents/`) — all sub-agents
- `<paths.loops>` from the survey (defaults to `.claude/loops/`) — all bounded loops
- `CLAUDE.md` — any orchestration patterns described
- `.architect.json` — the project's stated conventions

**Project conventions take precedence over plugin defaults.** If the project's `conventions` say "always use a reviewer sub-agent for security paths" and the plugin's general principles would recommend dropping it, the project wins. Surface the tension when it matters, but do not silently override the project's stated norms. The audit's job is to evaluate the setup against *both* the plugin's principles and the project's own rules — and to flag when those conflict.

---

## Step 1 — Run structural validation

Before reading individual files, run the validator script. It catches all the mechanical issues (missing required sections, generic descriptions, unfilled placeholders, caps too high) without spending tokens reading every file character by character:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate.py --root <repo-root> --paths-from-config
```

The script returns JSON with a list of structural `issues`, each with a `code`, `severity`, and `message`. Use this output as your "ISSUES" section directly — these issues are factual and don't need re-evaluation.

After the structural pass, only spend tokens on the **judgment-level** checks below for files that didn't already fail mechanical validation.

---

## Step 2 — Judgment-level checks (Claude only)

For each file the validator reported as OK (or with only warnings), apply these checks. These require reading prose and judging — the script can't do them:

## For each sub-agent, check (judgment only)

The validator already caught: missing required sections, generic descriptions, unfilled placeholders. Skip those — they're already in the issues list. Focus on:

1. **Role specificity** — Even when the `## Role` section *exists*, does it fit the form "Given X, produce Y, failing when Z" with concrete X/Y/Z? "Given input, produce output, failing on error" passes structural validation but is still vague → flag.
2. **Tool minimality** — Does the sub-agent use the smallest tool set its role requires? A "review" agent with Write and Bash tools is suspicious → flag. (The script doesn't have a tool inventory; you have to read the frontmatter.)
3. **Output contract substance** — The validator checks that `## Output contract` exists. You check whether it specifies a *structured* format (JSON, fixed sections, exit codes) vs. freeform prose → flag freeform.
4. **Overlap** — Compare each sub-agent's role against the others. Two agents with overlapping roles → one is theater → flag.
5. **Same-context smell** — If the sub-agent's effective context is "everything the main agent has anyway," there's no isolation gain → flag.

## For each loop, check (judgment only)

The validator caught: missing sections, caps above 10, unfilled placeholders. Focus on:

1. **Stopping criterion substance** — The section exists; does it name an objective signal (test exit code, schema, metric) or vibes ("until good", "Claude judges")? Vibes → flag.
2. **Progress metric substance** — The section exists; can iteration N+1 actually know whether it improved over N? "Quality improves" is not a metric → flag.
3. **Stall detection** — Does the Guardrails section explicitly bail out on N consecutive non-improving iterations? If not → flag.
4. **Observability completeness** — Does the log format include all four of: hypothesis, command, result, next-step decision? Missing any one means you're watching it fail, not debugging it → flag.

## For the overall setup

1. **Gradient check** — Could a lower tier (single execution, single execution with tools, or just one sub-agent) deliver the same result? If yes, the higher tier is theater.
2. **Coordination depth** — How many handoffs does a typical task involve? More than 2–3 hops between agents is a smell unless each hop has a clear contract.
3. **Evidence of gain** — Has the user pointed to *measured* wins (faster, fewer errors, cleaner output, lower context pressure)? If "it feels more organized" is the only justification, that's theater.

---

## Output format

```
INVENTORY
- Sub-agents: <count> — <list names>
- Loops: <count> — <list names>

ISSUES (most severe first)
1. <agent or loop name>: <one-line problem> — <one-line fix>
2. ...

THEATER WATCH
<sub-agents or loops that probably should not exist yet, with one sentence each on why>

RECOMMENDED COLLAPSES
<for each redundant or premature piece, what tier it should drop to>

CONVENTION CONFLICTS
<places where plugin principles and project conventions disagree, with one sentence each on what the conflict is and which the user should pick. Empty if none.>

WHAT TO MEASURE
<2-3 specific things to observe over the next few uses to decide whether the current setup is paying off>
```

Be direct. The point of this audit is to identify pieces to delete, not to validate what exists. Default to recommending collapse, not expansion.

If the setup is actually clean, say so plainly — but only after running the checks. Empty output sections are fine. Do not invent issues.
