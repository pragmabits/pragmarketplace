# Frontend Plugin

Frontend development orchestrator for Claude Code — coordinates CSS, Tailwind CSS, Vue.js, Nuxt, shadcn/ui, Font Awesome, and design specialists for cross-domain frontend tasks.

## Overview

This plugin bundles all frontend-related specialist agents, skills, and documentation into a single package, adding a central orchestrator that coordinates cross-domain frontend work.

For single-domain tasks, the specialist agents and commands work independently. For tasks spanning multiple domains, the frontend orchestrator manages the full workflow: discovery, exploration, architecture, implementation, and quality review.

## Architecture

```
frontend/
├── agents/
│   ├── frontend.md          # Orchestrator agent (NEW)
│   ├── css.md               # CSS specialist
│   ├── tailwindcss.md        # Tailwind CSS specialist
│   ├── vuejs.md              # Vue.js/Nuxt specialist
│   ├── shadcn.md             # shadcn/ui specialist
│   └── fontawesome.md        # Font Awesome specialist
├── commands/
│   ├── frontend.md           # /frontend orchestrator command (NEW)
│   ├── css.md                # /css
│   ├── tailwindcss.md        # /tailwindcss
│   ├── vuejs.md              # /vuejs
│   ├── nuxt.md               # /nuxt
│   ├── shadcn.md             # /shadcn
│   └── fontawesome.md        # /fontawesome
├── skills/
│   ├── frontend/             # Orchestrator skill (NEW)
│   ├── frontend-design/      # Design aesthetics skill
│   ├── css-*/                # 6 CSS skills
│   ├── tw-*/                 # 6 Tailwind CSS skills
│   ├── vue-*/                # 8 Vue.js skills
│   ├── nuxt/                 # Nuxt skill
│   ├── shadcn/               # shadcn/ui skill
│   └── fontawesome-icons/    # Font Awesome skill
├── hooks/
│   ├── hooks.json            # TW4 validation hooks
│   └── validate-tw-output.sh
└── docs/
    ├── css/                  # CSS quick references
    ├── fontawesome/          # FA7 official docs (75 files)
    └── shadcn/               # shadcn/ui official docs
```

## Commands

| Command | Purpose |
|---------|---------|
| `/frontend [task]` | Cross-domain orchestrator for multi-technology tasks |
| `/css [question]` | Pure CSS, SCSS, Sass, Less, PostCSS guidance |
| `/tailwindcss [question]` | Tailwind CSS 4 utilities, theming, migration |
| `/vuejs [question]` | Vue 3, Vite, Pinia, Vue Router, VueUse, Vitest |
| `/nuxt [question]` | Nuxt 3 pages, server routes, middleware, SSR |
| `/shadcn [question]` | shadcn/ui components, CLI, theming |
| `/fontawesome [question]` | Font Awesome icons, animation, styling |

## When to Use What

**Use `/frontend`** when the task spans 2+ domains:
```
/frontend build a Vue dashboard with sidebar, Tailwind theming, shadcn components, and FA icons
/frontend create a responsive landing page with hero section, features, and contact form
/frontend redesign the admin panel with dark mode support
```

**Use specialist commands** for single-domain tasks:
```
/css how do container queries work?
/tailwindcss migrate my TW3 project to TW4
/vuejs create a composable for dark mode
/shadcn add a date picker component
/fontawesome suggest icons for a settings page
```

## Skills (25 total)

### Orchestration
- **frontend** — Cross-domain task coordination

### Design
- **frontend-design** — Distinctive, production-grade UI aesthetics

### CSS (6)
- css-layout, css-animation, css-selectors, css-responsive, css-performance, css-preprocessors

### Tailwind CSS (6)
- tw-config, tw-theme, tw-utility, tw-layout, tw-responsive, tw-migration

### Vue.js (9)
- vue-component, vue-state, vue-test, vue-styling, vue-forms, vue-ui, vue-data, vue-animation, nuxt

### UI Libraries (2)
- shadcn, fontawesome-icons

## Hooks

- **TW4 Validation** — PreToolUse hook validates Tailwind CSS 4 patterns on Write/Edit operations

## Prerequisites

- Claude Code with plugin support
- context7 MCP server configured (recommended for documentation access)
- Internet access for WebSearch/WebFetch fallback

## Author

**pragmabits** — [pragmarketplace](https://github.com/pragmabits/pragmarketplace)
