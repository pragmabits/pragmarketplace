# Tailwind CSS 4 Plugin for Claude Code

Expert guidance for Tailwind CSS 4 — utility authoring, CSS-first theming, responsive layouts, dark mode, TW3→TW4 migration, and PostCSS/Vite setup powered by runtime documentation lookup.

## Prerequisites

- **context7 MCP** (optional but recommended) — enables the agent to fetch up-to-date Tailwind CSS documentation at runtime
- Without context7, the agent falls back to WebSearch (`site:tailwindcss.com`) and WebFetch

## Commands

| Command | Description |
|---------|-------------|
| `/tailwindcss [question]` | Ask the Tailwind CSS 4 expert agent any question about utilities, theming, layouts, migration, or setup |

## Skills

| Skill | Triggers |
|-------|----------|
| **tw-config** | Setup, installation, `@import "tailwindcss"`, PostCSS, Vite, `@source`, `@layer` |
| **tw-theme** | `@theme`, design tokens, colors, spacing, fonts, CSS custom properties |
| **tw-utility** | `@utility`, `@custom-variant`, custom classes, extending Tailwind |
| **tw-layout** | Flex, grid, container queries, `@container`, `@sm:`, gap, columns |
| **tw-responsive** | Breakpoints, dark mode, `sm:`/`md:`/`lg:`, `@variant dark`, media queries |
| **tw-migration** | TW3→TW4, deprecated patterns, `bg-opacity`, `@tailwind` directives, config migration |

## Hooks

The plugin includes a PreToolUse hook that validates Write and Edit operations for Tailwind CSS 4 patterns:

- **Warns** on deprecated `@tailwind` directives, opacity utilities, `theme()` function, and `@apply` with deprecated utilities
- **Blocks** contradictory files that mix `@tailwind` directives with `@import "tailwindcss"`
- **Warns** when creating `tailwind.config.js/ts` files (CSS-first config preferred in TW4)

## Agent

The `tailwindcss` agent (`sonnet` model, `cyan` color) provides:

- TW4-first guidance with CSS-first configuration
- Runtime documentation lookup via context7 MCP + WebSearch fallback
- Project context detection (TW3 vs TW4, Vite vs PostCSS, framework detection)
- Migration guidance from TW3 to TW4
- Persistent memory for user preferences and project context
