---
name: frontend
description: Frontend development orchestrator — coordinates CSS, Tailwind CSS, Vue.js, Nuxt, shadcn/ui, Font Awesome, and design specialists for cross-domain frontend tasks
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

Follow your Phased Workflow:
1. Discovery — understand the task
2. Domain Identification & Exploration — identify specialist domains, launch parallel exploration agents
3. Clarifying Questions — resolve ambiguities
4. Architecture Design — dispatch architecture agents, synthesize proposals
5. Implementation — coordinate specialist agents
6. Quality Review — launch review agents
7. Summary — document results

Remember: You are the orchestrator. Delegate ALL implementation work to specialist agents (css, tailwindcss, vuejs, shadcn, fontawesome). Do not write frontend code yourself.
```

### Post-agent: Commit strategy

The frontend orchestrator agent handles the commit strategy prompt internally (Phase 8). This command does not need to prompt separately — the orchestrator already asks the user.

This command does not implement frontend work directly. The frontend orchestrator agent coordinates all specialist agents — CSS, Tailwind CSS, Vue.js, shadcn/ui, and Font Awesome — to deliver cohesive cross-domain results.
