---
name: vuejs
description: Vue.js ecosystem expert — Vue 3, Vite, Nuxt 3, Pinia, Vue Router, VueUse, and Vitest guidance
argument-hint: [question or task] - e.g. "create a composable for dark mode" or "how to set up Pinia stores"
---

# Vue.js Ecosystem Expert

Convenient entrypoint for the vuejs agent. All Vue 3, Vite, Nuxt 3, Pinia, Vue Router, VueUse, and Vitest guidance is handled by the agent.

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

Otherwise, invoke the vuejs agent with the resolved plugin root.

Use the Agent tool with:
- **subagent_type**: `vuejs`
- **description**: "Vue.js ecosystem expert guidance"
- **prompt**: Include the plugin root and user context, then instruct the agent to look up docs and answer.

Prompt template:
```
Answer the user's Vue.js ecosystem question using current documentation.

Plugin root: ${CLAUDE_PLUGIN_ROOT}
User context: $ARGUMENTS

Follow your Documentation Lookup Protocol and Project Context Detection steps. Verify answers against current documentation before responding.
```

This command does not answer questions directly. The vuejs agent owns all Vue ecosystem guidance — components, routing, state management, testing, build tools, and SSR patterns.
