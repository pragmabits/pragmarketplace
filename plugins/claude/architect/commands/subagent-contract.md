---
description: Scaffold a specialized sub-agent with explicit contract, guardrails, and one-sentence role. Refuses if the role is vague.
argument-hint: <describe the sub-agent's role, inputs, outputs, and what it should NOT do>
---

# Sub-agent Contract

A sub-agent without a one-sentence role is architectural theater. This command generates a sub-agent **only after** confirming:

1. **Role fits in one objective sentence** ("review diffs and flag scope creep" — yes; "think better about code" — no)
2. **Closed input/output contract** (what comes in, what goes out, what failure looks like)
3. **A reason it should not just be a tool call or a Tier 2 single execution**
4. **No existing sub-agent in the project already does this** (checked via project survey)

If any is missing, the command refuses and helps the user clarify.

---

## Step 0 — Capability radar

Before anything else, invoke the `capability-radar` skill. The user may already have a capability — an in-session sub-agent, skill, slash command, or a component from an installed pragmatic plugin — that does what the requested sub-agent would do.

This is a wider net than the project-survey check (which only looks at the current repo). The radar covers user-global agents (`~/.claude/agents/`), plugin-contributed agents, and active session capabilities. If any of these substantially fit, scaffolding a new sub-agent is duplication, regardless of whether the project itself already has a match.

If the radar reports a clear match, stop and recommend the existing capability. Do not proceed unless the user explicitly chooses "generate new" in the radar's `AskUserQuestion`.

---

## Step 1 — Project survey

After the capability radar clears, invoke the **project-survey** skill. Read `.architect.json` if present; otherwise run a fresh survey.

The most important check at this stage: **does an existing project sub-agent already do what the user is asking for?** This is the project-local version of the capability radar's check, and it can fire even when the radar didn't (e.g., a project sub-agent the radar's broader net missed).

If `existing_infrastructure.agents` contains an agent whose role overlaps substantially with what the user described, **stop and surface it**:

> The project already has a sub-agent that overlaps with this role:
>
> - `<existing-agent-name>`: <its one-line role>
>
> Options: reuse the existing one / extend the existing one / generate a distinct new one (you'll explain how it differs) / cancel.

Use `AskUserQuestion` with those four options. Do not silently generate a duplicate. Sub-agent sprawl is one of the failure modes `/coordination-audit` warns about; this command should not create it.

Also use the survey's `paths.agents` for the output location and `conventions` for additional guardrails.

---

## Input

User said:

> $ARGUMENTS

---

## Step 2 — Validate the role

Try to write the sub-agent's role as **one sentence in this exact form**:

> "Given <input>, produce <output>, failing closed when <failure condition>."

If you cannot write that sentence cleanly from the user's description, **refuse**. Tell the user the role is too vague and offer two concrete reformulations they could pick from. Then stop.

Also reject these patterns outright:

- "Sub-agent that thinks / reflects / refines" with no objective output → architectural theater
- "Sub-agent that reviews the main agent" with no rubric → theater
- Sub-agent doing what a single tool call could do (read a file, run a command) → just use the tool
- Sub-agent that needs the same full context as the main agent → no isolation gain, drop it

## Step 3 — Justify it over the alternatives

Before generating, confirm at least one is true:
- **Specialization**: distinct skill or rubric the main agent shouldn't carry
- **Context isolation**: smaller, scoped context (one module, one file set)
- **Different tools/permissions**: fewer or different tools than main agent
- **Parallelizable**: main agent will spawn N of these in parallel

Tell the user which one(s) apply. If none apply, recommend Tier 2 (single execution with tools) instead of generating the sub-agent.

## Step 4 — Generate

Write the sub-agent to `<paths.agents>/<name>.md` (from the project survey; defaults to `.claude/agents/`) using kebab-case from the role. Apply survey-derived adjustments: append every relevant `convention` to the "What you do NOT do" section, and use the project's actual test command (from `stack.test_commands`) in any examples. Use this template:

```markdown
---
name: <name>
description: <One sentence describing when the main agent should delegate to this sub-agent. Be specific — generic descriptions cause both over- and under-invocation.>
tools: <minimal list — only what the role requires; e.g., Read, Grep, Bash>
---

# <Title>

## Role (one sentence)
Given <input>, produce <output>, failing closed when <failure>.

## Input contract
- <field>: <description>
- <field>: <description>

## Output contract
Return exactly:
```
<structured format — e.g., JSON schema, fixed sections, exit codes>
```

## Failure mode
When <condition>, return:
```
STATUS=FAIL
REASON=<short explanation>
```
Do not attempt to recover. The main agent decides next steps.

## What you do
<3-7 numbered steps, concrete>

## What you do NOT do
- Do not <action outside scope>
- Do not modify files outside <scope>
- Do not invoke other sub-agents
- Do not run destructive commands (<list>)
- Do not ask the user clarifying questions — if input is ambiguous, fail closed with a clear REASON

## Examples
### Good input → good output
<one concrete example>

### Bad input → fail-closed output
<one concrete example>
```

## Step 5 — Confirm

After writing:

1. Show the path.
2. Echo the one-sentence role back to the user. If it still feels vague when read aloud, offer to revise before they use it.
3. Show how to invoke: the main agent will pick this up automatically based on the `description` field, or the user can request it explicitly ("use the <name> sub-agent for this").
4. Suggest running `/coordination-audit` after the sub-agent has been used a few times, to check whether it's actually paying off.

---

## Anti-patterns to actively prevent

- **Sub-agent stack with no measured wins** — refuse to scaffold a second sub-agent until the first one's value is shown.
- **Vague descriptions** — `description: "helps with code"` causes the main agent to invoke at random. Push for specificity.
- **Tool sprawl** — a sub-agent with the full default toolset is not isolated. Trim aggressively.
- **Recovery logic in sub-agents** — sub-agents fail closed. The main agent orchestrates retries.
