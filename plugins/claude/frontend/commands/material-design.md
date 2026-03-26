---
name: material-design
description: Material Design 3 expert — tokens, theming, color, typography, shape, elevation, motion, layout, component patterns
argument-hint: "[question or task] - e.g. \"set up MD3 color tokens\" or \"how to implement dark mode with MD3\""
---

# Material Design 3 Expert

Convenient entrypoint for the material-design agent. All Material Design 3 guidance — tokens, theming, color, typography, shape, elevation, motion, responsive layout, and component patterns — is handled by the agent.

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

Otherwise, invoke the material-design agent with the resolved plugin root.

Use the Agent tool with:
- **subagent_type**: `material-design`
- **description**: "Material Design 3 expert guidance"
- **prompt**: Include the plugin root and user context, then instruct the agent to look up docs and answer.

Prompt template:
```
Answer the user's Material Design 3 question using current documentation.

Plugin root: ${CLAUDE_PLUGIN_ROOT}
User context: $ARGUMENTS

CRITICAL: Before answering, detect whether the user's project uses Material Design 3 by scanning for --md-sys-* tokens, @material/web in package.json, or md-* custom elements. If the project does not use MD3, warn the user and ask how to proceed.

Follow your Documentation Lookup Protocol and Design System Detection steps. Consult the bundled reference docs at ${CLAUDE_PLUGIN_ROOT}/docs/material-design/web/ for exact token values. Verify answers against current documentation before responding.
```

### Post-agent: Commit strategy

After the agent returns, apply the commit strategy protocol from `<plugin-root>/references/commit-strategy.md`:

1. If `$ARGUMENTS` contains `ORCHESTRATED=true`, skip — the orchestrator handles commits
2. If the agent did not modify any files (pure Q&A), skip
3. Otherwise, detect available commit strategies from the session context (skill/agent names containing "commit")
4. Present AskUserQuestion with detected options + "Do not commit"
5. Execute the user's chosen strategy

This command does not answer questions directly. The material-design agent owns all MD3 guidance — tokens, theming, color system, typography, shape, elevation, motion, layout, and component patterns.
