---
name: commit
description: Strategic commits with semantic analysis and hook-validated messages
argument-hint: [context or instruction] - e.g. "complete feature" or "split by context"
---

# Strategic Git Commit

Entrypoint for the commit workflow. All logic runs inline — no sub-agent.

## User Context

$ARGUMENTS

## Execution

### Resolve plugin root

```
Plugin root: ${CLAUDE_PLUGIN_ROOT}
```

### Argument handling

If `$ARGUMENTS` is exactly `--resolve-root`:
- Output the plugin root path: `${CLAUDE_PLUGIN_ROOT}`
- Stop here

### Execute commit workflow

Follow the commit skill workflow directly:

1. Run the **Analyze** step — combined git status/diff/log command
2. Follow **Strategize** — determine semantic boundaries, one commit per semantic change, whole-file staging only
3. Execute **Stage and Commit** — `git add` + `git commit` for each planned commit. Hooks validate messages transparently.
4. Apply **Decisions** — ask the user only when the strategy is genuinely ambiguous
5. Run the **Report** step — show commits created and final status

Use `$ARGUMENTS` as additional context for commit strategy decisions (e.g., "split by module" influences grouping, "amend" triggers amend mode).

Do not invoke any agent. The commit skill contains the complete workflow — follow it directly.
