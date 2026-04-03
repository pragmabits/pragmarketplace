---
name: frontend
description: Frontend development orchestrator — coordinates CSS, Tailwind CSS, Vue.js, Nuxt, shadcn/ui, Font Awesome, Material Design 3, HTMX + Go, and design specialists for cross-domain frontend tasks
argument-hint: "[task description] - e.g. 'build a Vue dashboard with Tailwind, shadcn components, and FA icons'"
---

# Frontend Development Orchestrator

Entrypoint for the frontend orchestrator agent. This command coordinates multiple specialist agents for cross-domain frontend development tasks.

**When to use this command**: Tasks that span 2+ frontend domains (CSS, Tailwind, Vue, shadcn, Font Awesome, design).

**When NOT to use this command**: Single-domain tasks. Use the specialist commands instead:
- `/css` — Pure CSS, SCSS, Sass, Less, PostCSS
- `/tailwindcss` — Tailwind CSS 4 utilities, theming, migration
- `/vuejs` — Vue 3, Vite, Pinia, Vue Router, VueUse, Vitest
- `/nuxt` — Nuxt 3 pages, server routes, middleware, SSR
- `/shadcn` — shadcn/ui components, CLI, theming
- `/fontawesome` — Font Awesome icons, animation, styling
- `/htmx-go` — HTMX attributes, Go handlers, templ components, SSE/WebSocket
- `/material-design` — MD3 tokens, theming, color, typography, layout

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

Otherwise, invoke the frontend orchestrator agent with the resolved plugin root.

Use the Agent tool with:
- **subagent_type**: `frontend`
- **description**: "Frontend orchestrator for cross-domain task"
- **prompt**: Include the plugin root, user context, and orchestration instructions.

Prompt template:
```
Coordinate a cross-domain frontend development task.

Plugin root: ${CLAUDE_PLUGIN_ROOT}
User request: $ARGUMENTS

Follow your Workflow:
1. Understand — read the request, AskUserQuestion if anything is unclear, identify specialist domains
2. Explore & Plan — launch parallel exploration agents, draft implementation plan, get user approval
3. Execute — dispatch specialist agents in batches, track progress
4. Complete — summarize results, run commit strategy

Remember your Non-Negotiable Rules: delegate ALL code to specialists (frontend:css, frontend:tailwindcss, frontend:vuejs, frontend:shadcn, frontend:fontawesome, frontend:material-design, frontend:htmx-go). Never write frontend code yourself. Use AskUserQuestion for every question, confirmation, and choice.
```

### Post-agent: Commit strategy

The frontend orchestrator agent handles the commit strategy prompt internally (Phase 8). This command does not need to prompt separately — the orchestrator already asks the user.

This command does not implement frontend work directly. The frontend orchestrator agent coordinates all specialist agents — CSS, Tailwind CSS, Vue.js, shadcn/ui, and Font Awesome — to deliver cohesive cross-domain results.
