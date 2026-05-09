---
name: project-survey
description: Use this before scaffolding any loop, sub-agent, or orchestration in a pre-existing project. Surveys the repo for existing conventions, stack, agents, paths, off-limits scopes, and test commands. Reads or creates `.architect.json` to persist findings. Invoke at the start of /loop-contract, /subagent-contract, and /architect's scaffold stage. Skip only when the user has explicitly opted out for the session.
---

# Project Survey

Before scaffolding anything in an existing project, you need to know what's already there. This skill runs that discovery and writes the answers to `.architect.json` so future scaffolds don't re-prompt.

The goal is **not** to lecture the user about their project. It's to surface the constraints so the scaffold respects them, instead of generating a generic template that ignores institutional knowledge.

**This skill delegates mechanical work to scripts.** Stack detection, file discovery, off-limits paths, and staleness checks are handled by Python scripts in `scripts/`. The skill's job is to interpret prose (CLAUDE.md conventions), present results to the user, and write the final config.

---

## When to run

**Run discovery when:**
- A scaffold is about to be generated (`.claude/loops/...` or `.claude/agents/...`)
- `.architect.json` is missing or empty
- `.architect.json` exists but is reported stale by `check_staleness.py`
- The user explicitly says "re-survey" or "rerun discovery"

**Skip discovery when:**
- `.architect.json` is present and current — read it and proceed
- The user has already answered the relevant question in this session
- The command is read-only (`/triage`, `/coordination-audit` — these don't write files; though `/coordination-audit` reads `.architect.json` if present)

---

## How to run the survey

### Step 1 — Check staleness

Run the staleness script first. It's cheap (file existence checks only) and tells you whether to use the cached config or run a fresh survey:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/check_staleness.py --root <repo-root>
```

The output JSON has `stale: false` (use cached) or `stale: true` with `reasons` (run fresh survey, mention the reasons to the user).

If `stale: false` and `config_present: true`, read `.architect.json` and proceed to scaffolding. Skip the rest of this skill.

### Step 2 — Run mechanical discovery

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/survey.py --root <repo-root>
```

The script returns a JSON survey covering stack, test commands, existing infrastructure, off-limits paths, and whether `CLAUDE.md` exists. It does NOT extract conventions from `CLAUDE.md` — that's prose understanding, which is your job.

### Step 3 — Read CLAUDE.md if present

If the survey reports `claude_md_present: true`, read the file and extract:

- Conventions about agent use ("always use a reviewer", "never modify generated files")
- Branch protections, scope rules, "don't touch" directories that aren't already in the off-limits list
- Project-specific orchestration patterns

Add these as a `conventions` array to the survey JSON before showing the user.

### Step 4 — Present and confirm

Show the user a summary in this exact shape (using the data from steps 2 and 3):

```
PROJECT SURVEY (first run)

Stack: <stack.primary, additional listed in parens>
Test command(s): <stack.test_commands as "<label>: <command>" lines>
Existing sub-agents: <list names + role one-liners, or "none">
Existing custom commands: <list, or "none">
CLAUDE.md conventions: <2-4 lines from your reading, or "none found">
Off-limits paths: <paths.off_limits>
Scaffold output paths: <paths.loops and paths.agents>
```

Then call `AskUserQuestion`:

Question: "Anything missing or wrong?"

Options:
- **Confirm and proceed** — write `.architect.json` and continue
- **Adjust a specific field** — ask which field, take the user's input, update the survey
- **Add an off-limits scope** — append to off_limits list
- **Re-survey with different scope** — re-run with a different `--root`

### Step 5 — Write `.architect.json`

After confirmation, write the full survey (with conventions added) to `.architect.json` at the repo root. Include the `version`, `surveyed_at`, all fields from `survey.py`, and the `conventions` array you derived from CLAUDE.md.

If the user supplied any free-form information that doesn't fit the schema, put it under `user_overrides`.

---

## `.architect.json` schema

```json
{
  "version": "1",
  "surveyed_at": "<ISO timestamp from survey.py>",
  "stack": { ... from survey.py ... },
  "paths": { ... from survey.py ... },
  "existing_infrastructure": { ... from survey.py ... },
  "conventions": [
    "<one line per convention extracted from CLAUDE.md>"
  ],
  "user_overrides": {}
}
```

The `user_overrides` block is reserved for things the user told you that don't fit elsewhere. Keep it free-form.

---

## How scaffold commands consume this

When `/loop-contract`, `/subagent-contract`, or `/architect` reach the scaffold stage, they:

1. Run `check_staleness.py`. If fresh, read `.architect.json`.
2. If stale or missing, invoke this skill.
3. Use `paths.loops` / `paths.agents` for output location.
4. Use `stack.test_commands` to populate the stopping criterion if the user described it generically ("when tests pass" → the project's actual test command).
5. Add `paths.off_limits` to the scaffold's guardrails section automatically.
6. Reference `existing_infrastructure.agents` — if a relevant existing sub-agent could do the job, **recommend reusing it instead of scaffolding a new one**.
7. Apply `conventions` as additional guardrails or notes in the generated file.

Step 6 is the most important. It's where the plugin actively avoids duplicating work that already exists. If the user runs `/subagent-contract "agent that runs tests and parses failures"` and the project has a `test-runner` sub-agent, the scaffold command should *stop and say so*, not generate a competing one.

---

## What to NOT do

- Do not write `.architect.json` without showing the survey to the user first.
- Do not re-implement `survey.py`'s logic in prose — call the script.
- Do not block on missing fields — if a field is genuinely unknown, leave it `null` and proceed; ask only once per session.
- Do not lecture the user about their project structure. The survey is a checklist, not a critique.
- Do not silently override user-specified paths or conventions because the plugin's defaults disagree. The user's project wins.
- Do not run discovery on every command. Use `check_staleness.py` to decide; cached configs are the default.
