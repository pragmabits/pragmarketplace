# Vue.js Ecosystem Plugin

Vue.js ecosystem expert for Claude Code — comprehensive guidance on Vue 3, Vite, Nuxt 3, Pinia, Vue Router, VueUse, and Vitest.

## Overview

This plugin provides expert-level guidance for the entire Vue.js ecosystem through a single comprehensive agent. Unlike plugins that bundle documentation locally, this plugin **fetches current documentation at runtime** via context7 MCP and WebSearch, ensuring always-up-to-date answers.

## Features

### Core Framework
- **Vue 3** — Components, Composition API, `<script setup>`, reactivity system, TypeScript integration
- **Vite** — Build configuration, dev server, plugins, HMR, environment variables
- **Nuxt 3** — Pages, server routes, middleware, modules, SSR/SSG, auto-imports
- **Pinia** — Stores, actions, getters, composition, SSR state hydration
- **Vue Router** — Routes, guards, lazy loading, dynamic routes, nested routes
- **VueUse** — Composable utilities (150+ functions)
- **Vitest** — Testing, mocking, component tests, coverage

### Styling
- **Tailwind CSS** — v4 Vite plugin, utility classes, CSS-based configuration
- **CVA** — Type-safe component variants with `class-variance-authority`
- **clsx + tailwind-merge** — Conditional class merging with `cn()` utility

### Forms
- **vee-validate** — v4 Composition API form validation
- **zod** — Schema-based validation with `toTypedSchema` bridge

### UI Components
- **Reka UI** — Headless, accessible components (successor to Radix Vue)
- **Lucide** — Tree-shakeable Vue icon components
- **Vue Sonner** — Toast notification system
- **Fontsource** — Self-hosted fonts

### Data
- **TanStack Query** — Server state management, caching, mutations
- **@internationalized/date** — Locale-aware date objects for date pickers

### Animation
- **Motion** — Declarative spring-physics animations for Vue

## Installation

Install via the pragmatic:

```bash
claude /install vuejs
```

Or add manually to your Claude Code plugin configuration.

## Usage

### Commands

#### `/vuejs [question]`
General Vue.js ecosystem questions:
```
/vuejs how do I create a composable for dark mode toggle?
/vuejs set up Vite with path aliases and proxy
/vuejs what's the difference between ref and reactive?
```

#### `/nuxt [question]`
Nuxt 3-focused questions:
```
/nuxt add authentication middleware
/nuxt create server API route with validation
/nuxt configure hybrid rendering with route rules
```

### Agent

The `vuejs` agent triggers automatically when you mention Vue.js ecosystem technologies in conversation — no command needed.

### Skills

Four skills provide trigger surfaces for specific domains:

| Skill | Triggers on |
|-------|-------------|
| `vue-component` | Component creation, `<script setup>`, reactivity, composables |
| `nuxt` | Nuxt 3 pages, server routes, middleware, modules, SSR |
| `vue-state` | Pinia stores, Vue Router configuration and guards |
| `vue-test` | Vitest testing, Vue Test Utils, component/composable testing |
| `vue-styling` | Tailwind CSS, CVA, clsx, tailwind-merge, `cn()` utility |
| `vue-forms` | vee-validate, zod, `useForm`, `toTypedSchema`, form validation |
| `vue-ui` | Reka UI, lucide icons, vue-sonner toasts, fontsource fonts |
| `vue-data` | TanStack Query, `useQuery`, `useMutation`, `@internationalized/date` |
| `vue-animation` | Motion animations, springs, `AnimatePresence`, scroll/gesture animations |

## How Documentation Works

This plugin uses a **runtime documentation lookup** strategy:

1. **context7 MCP** (primary) — `resolve-library-id` then `query-docs` for structured documentation
2. **WebSearch** (fallback) — Site-specific queries (`site:vuejs.org`, `site:nuxt.com`, etc.)
3. **WebFetch** (targeted) — Direct page retrieval for specific documentation URLs

This ensures answers always reflect the latest API changes without requiring plugin updates.

## Architecture

```
vuejs/
├── .claude-plugin/plugin.json     # Plugin manifest
├── agents/vuejs.md                # Single comprehensive agent (opus model)
├── commands/
│   ├── vuejs.md                   # /vuejs command entrypoint
│   └── nuxt.md                    # /nuxt command entrypoint
└── skills/
    ├── vue-component/             # Vue 3 components & reactivity
    ├── nuxt/                      # Nuxt 3 development
    ├── vue-state/                 # Pinia + Vue Router
    ├── vue-test/                  # Vitest + Vue Test Utils
    ├── vue-styling/               # Tailwind CSS, CVA, clsx, tailwind-merge
    ├── vue-forms/                 # vee-validate, zod
    ├── vue-ui/                    # Reka UI, lucide, vue-sonner, fontsource
    ├── vue-data/                  # TanStack Query, @internationalized/date
    └── vue-animation/             # Motion animations
```

## Prerequisites

- Claude Code with plugin support
- context7 MCP server configured (recommended for best documentation access)
- Internet access for WebSearch/WebFetch fallback

## Author

**pragmabits** — [pragmatic](https://github.com/pragmabits/pragmarketplace)
