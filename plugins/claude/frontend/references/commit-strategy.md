# Commit Strategy Protocol

Shared reference for the post-implementation commit strategy prompt. This document is the single source of truth — all commands and the orchestrator agent reference it.

## When to trigger

After the agent completes implementation work that modifies files. Do NOT trigger for:
- Pure Q&A / guidance tasks (no files changed)
- Tasks running under orchestration (`ORCHESTRATED=true` in the prompt)

## Orchestration flag

When the frontend orchestrator dispatches a specialist agent, it includes `ORCHESTRATED=true` in the agent prompt. This tells the specialist that the orchestrator owns the commit decision — the specialist must not prompt for commits.

**Commands**: After the specialist agent returns, check whether the original user prompt contained `ORCHESTRATED=true`. If it did, skip the commit strategy prompt entirely.

**Orchestrator agent**: The orchestrator itself always runs the commit strategy prompt in Phase 8 (Commit Strategy), after the Phase 7 summary, since it is the top-level coordinator.

## Detection of available commit strategies

Before presenting options, dynamically detect which commit-related agents and skills are available in the current session. Look for these signals:

1. **Check the available skills list** in the system prompt / system-reminder for skill names containing "commit" (e.g., `git:commit`, `commit`)
2. **Check the available agents list** for agent types containing "commit" (e.g., `git:commit-maker`, `commit-maker`)

Build the options list dynamically from what's detected. Always include "Do not commit" as the final option.

**Example detection result:**
- Found skill: `git:commit` and agent: `git:commit-maker` -> offer "Use git:commit-maker"
- Found skill: `commit` -> offer "Use /commit"
- Nothing found -> only offer "Do not commit"

## How to prompt

Use AskUserQuestion with a single question:

- **header**: "Commit"
- **question**: "Implementation is complete. How would you like to handle committing the changes?"
- **options**: Dynamically built from detection (see above), always ending with "Do not commit"

**Option format for each detected strategy:**
```
label: "Use <agent-or-skill-name>"
description: "<brief description of what it does>"
```

**"Do not commit" option:**
```
label: "Do not commit"
description: "Skip committing — you'll handle it manually or later"
```

## How to execute the chosen strategy

- **"Use git:commit-maker"** or any commit agent: Invoke the Skill tool with `skill: "git:commit"` (or the detected skill name). Pass any relevant context about what was implemented as args.
- **"Use /commit"** or other commit skills: Invoke the Skill tool with the detected skill name.
- **"Do not commit"**: Do nothing. Inform the user that changes are ready in the working tree.

## Example flow (in a command)

```
1. Agent completes implementation work
2. Agent returns result to command
3. Command checks: was ORCHESTRATED=true in the prompt?
   - YES -> skip commit prompt, return result to user
   - NO -> continue to step 4
4. Command checks: did the agent modify files? (look for file creation/modification in agent output)
   - NO -> skip commit prompt, return result to user
   - YES -> continue to step 5
5. Detect available commit strategies from session context
6. Present AskUserQuestion with detected options + "Do not commit"
7. Execute chosen strategy
```

## Example flow (in the orchestrator agent)

```
1. All specialist agents complete implementation (Phase 5)
2. Quality review completes (Phase 6)
3. Summary is presented (Phase 7)
4. Detect available commit strategies from session context
5. Present AskUserQuestion with detected options + "Do not commit"
6. Execute chosen strategy
```
