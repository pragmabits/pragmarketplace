---
name: capability-radar
description: Use this before scaffolding, recommending, or running a task to check whether existing capabilities (skills, commands, sub-agents, tools available in this session, or plugins from the pragmatic marketplace) already fit. Triggered by /triage, /loop-contract, /subagent-contract, theater-check, and loop-forensics as a Step 0. Prioritizes existing capabilities over generating new ones.
---

# Capability Radar

Before generating anything, check what already exists. The plugin's whole stance is "default to the lowest tier that works" — and "Tier 0" is *not generating anything because it already exists somewhere*.

This skill is the standing check that runs before the main logic of every scaffold or recommendation command. It surfaces existing capabilities that fit the user's task, in a defined priority order, and directs the calling command to use them instead of generating duplicates.

---

## What counts as a "capability"

In priority order — higher tier wins:

1. **In-session tools** — built-in Claude Code tools (Read, Write, Bash, Grep, etc.) and any MCP server tools active in this session
2. **In-session skills** — skills active in this conversation (visible by name/description in your context)
3. **In-session sub-agents** — sub-agents available via `.claude/agents/` (project-local) or `~/.claude/agents/` (user-global) or contributed by installed plugins
4. **In-session slash commands** — commands available via `.claude/commands/`, `~/.claude/commands/`, or installed plugins
5. **Installed plugins from the pragmatic marketplace** — full plugins installed from `pragmatic` whose contributed components fit the task

Anything outside these is out of scope. Uninstalled plugins are not surfaced — install-mid-task is too disruptive.

---

## How to run the check

### Step 1 — Inspect your own context (no script needed)

You already have the in-session capabilities in your context. Look at:

- The tool list in your system prompt (Read, Write, Bash, image_search, etc., plus any MCP tools)
- The skills list (auto-invocable skills with their descriptions)
- Any agents/commands the project has via `.architect.json` (if `project-survey` already ran)

For each, ask: **does this substantially fit the user's task?** "Substantially" is the key word — not "tangentially related" or "could be involved." A code-review skill substantially fits "review my diff for issues"; it does not substantially fit "scaffold a loop that fixes failing tests."

### Step 2 — Inspect installed pragmatic plugins (script)

Run:

```bash
python3 ${CLAUDE_PLUGIN_ROOT}/scripts/marketplace_inventory.py
```

The output lists every plugin installed from `pragmatic` and the components each contributes. Each component has a name and (usually) a description.

For each plugin, read the description and components. Apply the same "substantially fits" judgment: does any component clearly do what the user is asking for?

If `marketplace_known: false` in the output, the user does not have pragmatic configured. Skip plugin matching and proceed with only in-session capabilities.

### Step 3 — Decide

Based on what you found, follow this decision tree:

#### A. One capability clearly fits

Tell the calling command: **prioritize this capability**. Do not scaffold.

Format:

```
CAPABILITY MATCH: <name> (<source: in-session | pragmatic plugin>)
WHY IT FITS: <one sentence>
RECOMMENDATION: Use <name> instead of generating new infrastructure.
```

The calling command should then either invoke the capability directly (if the user's intent is clear) or tell the user how to use it.

#### B. Multiple capabilities plausibly fit

Surface them and ask the user with `AskUserQuestion`:

Question: "Found existing capabilities that may fit. Which would you like to use?"

Options:
- **<capability A>** — <one-line description of how it fits>
- **<capability B>** — <one-line description of how it fits>
- **None — generate new** — proceed with the scaffold/recommendation as planned
- **Cancel**

Do not list more than 3 candidates. If you have more, surface only the top 3 by fit quality.

#### C. Nothing fits

Tell the calling command: **proceed normally**. No interruption to the user. Do not announce that the radar found nothing — silence is fine.

---

## What to NOT do

- Do not list capabilities that only tangentially touch the task. Vague matches turn into noise that the user has to read past on every command.
- Do not invent capabilities. If a tool name or skill description is unclear, treat it as not-a-match.
- Do not match on keywords alone. "Review" in a description does not mean a sub-agent is a code reviewer; you have to read what it actually does.
- Do not surface uninstalled plugins, even if they exist in the pragmatic catalog. Install-mid-task is too disruptive.
- Do not run on every user turn — only when invoked by another command/skill as Step 0.
- Do not block on the script. If `marketplace_inventory.py` errors out, proceed with in-session check only.

---

## Calibration: "substantially fits"

Use this test: **if the user invoked the existing capability directly, would they get most of what they asked for, or would they immediately need to do something else?**

- Substantial fit: user runs the existing thing, gets the result, may need to format or follow up but the work is done
- Tangential: user runs it and gets partial info, still has to do most of the work themselves

Err on the side of *not* matching when in doubt. A false negative means the user proceeds with a normal scaffold. A false positive means the user gets pushed toward the wrong tool and has to back out — that's worse.
