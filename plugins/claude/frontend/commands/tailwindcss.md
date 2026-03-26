---
name: tailwindcss
description: Tailwind CSS 4 expert — utility authoring, theming, layouts, responsive design, and TW3→TW4 migration
argument-hint: "[question or task] - e.g. 'how to create a custom color theme' or 'migrate my TW3 project'"
---

# Tailwind CSS 4 Expert

Convenient entrypoint for the tailwindcss agent. All Tailwind CSS 4 utility authoring, CSS-first theming, responsive layouts, dark mode, migration, and PostCSS/Vite setup guidance is handled by the agent.

## User Context

$ARGUMENTS

## Execution

### Resolve plugin root

Before invoking the agent, determine the absolute path to this plugin's root directory:

```
Plugin root: ${CLAUDE_PLUGIN_ROOT}
```

### Argument handling

If `$ARGUMENTS` is exactly `--resolve-root`:
- Output the plugin root path: `${CLAUDE_PLUGIN_ROOT}`
- Do not invoke the agent
- Stop here

### Invoke agent

Otherwise, invoke the tailwindcss agent with the resolved plugin root.

Use the Agent tool with:
- **subagent_type**: `tailwindcss`
- **description**: "Tailwind CSS 4 expert guidance"
- **prompt**: Include the plugin root and user context, then instruct the agent to look up docs and answer.

Prompt template:
```
Answer the user's Tailwind CSS question using current documentation.

Plugin root: ${CLAUDE_PLUGIN_ROOT}
User context: $ARGUMENTS

Follow your Documentation Lookup Protocol and Project Context Detection steps. Verify answers against current documentation before responding.
```

### Post-agent: Commit strategy

After the agent returns, apply the commit strategy protocol from `<plugin-root>/references/commit-strategy.md`:

1. If `$ARGUMENTS` contains `ORCHESTRATED=true`, skip — the orchestrator handles commits
2. If the agent did not modify any files (pure Q&A), skip
3. Otherwise, detect available commit strategies from the session context (skill/agent names containing "commit")
4. Present AskUserQuestion with detected options + "Do not commit"
5. Execute the user's chosen strategy

This command does not answer questions directly. The tailwindcss agent owns all Tailwind CSS guidance — utility authoring, theming, layouts, responsive design, dark mode, migration, and setup patterns.
