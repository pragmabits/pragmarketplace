---
name: nuxt
description: Nuxt 3 expert — pages, server routes, middleware, modules, and SSR guidance
argument-hint: [question or task] - e.g. "add server route for authentication" or "how to use middleware"
---

# Nuxt 3 Expert

Convenient entrypoint for the vuejs agent with Nuxt 3 focus. All Nuxt 3 pages, server routes, middleware, modules, composables, and SSR guidance is handled by the agent.

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

Otherwise, invoke the vuejs agent with the resolved plugin root and Nuxt 3 focus.

Use the Agent tool with:
- **subagent_type**: `vuejs`
- **description**: "Nuxt 3 expert guidance"
- **prompt**: Include the plugin root, user context, and Nuxt focus.

Prompt template:
```
Answer the user's Nuxt 3 question using current documentation.

Plugin root: ${CLAUDE_PLUGIN_ROOT}
User context: $ARGUMENTS

IMPORTANT: This was invoked via /nuxt, so prioritize Nuxt 3-specific guidance. Focus on Nuxt 3 auto-imports, file-based routing, server routes (Nitro), middleware, modules, SSR/SSG/SPA rendering modes, data fetching (useFetch, useAsyncData), page meta, and runtime config.

Follow your Documentation Lookup Protocol (prioritize "nuxt" search term) and Project Context Detection steps. Verify answers against current documentation before responding.
```

### Post-agent: Commit strategy

After the agent returns, apply the commit strategy protocol from `<plugin-root>/references/commit-strategy.md`:

1. If `$ARGUMENTS` contains `ORCHESTRATED=true`, skip — the orchestrator handles commits
2. If the agent did not modify any files (pure Q&A), skip
3. Otherwise, detect available commit strategies from the session context (skill/agent names containing "commit")
4. Present AskUserQuestion with detected options + "Do not commit"
5. Execute the user's chosen strategy

This command does not answer questions directly. The vuejs agent owns all Nuxt 3 guidance — pages, server routes, middleware, modules, composables, data fetching, and SSR patterns.
