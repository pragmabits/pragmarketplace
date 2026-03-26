---
name: md3-foundations
description: "This skill should be used when the user asks about Material Design 3 foundations, \"MD3 color system\", \"MD3 tokens\", \"md-sys-color\", \"md-sys-typescale\", \"MD3 typography scale\", \"Material Design shape\", \"MD3 elevation\", \"MD3 motion tokens\", \"MD3 easing\", \"MD3 duration\", \"surface tint\", or any --md-sys-* or --md-ref-* CSS custom property. Covers color roles, typography scale, shape scale, elevation, motion, and the three-tier token architecture."
---

This skill provides comprehensive guidance on Material Design 3 foundational design tokens — color, typography, shape, elevation, and motion — for framework-agnostic web implementation using CSS custom properties.

## Design System Detection

Before applying any MD3 guidance, detect whether the project uses Material Design 3. Check for these indicators:

**Positive MD3 indicators** (any match = MD3 project):
- CSS custom properties matching `--md-sys-*` or `--md-ref-*` or `--md-comp-*`
- `@material/web` or `@material/material-color-utilities` in package.json
- `@angular/material` with `provideM3Theme` or `--mat-sys-*` tokens
- Import of `@material/*` SCSS modules
- HTML custom elements matching `md-*` (e.g., `<md-filled-button>`)
- Explicit MD3 config files or theme files referencing Material Design 3

**If no indicators found**: warn the user that the project does not appear to use MD3. Offer to either (a) set up MD3 tokens from scratch or (b) adapt guidance to the project's existing design system. Do NOT silently apply MD3 patterns to a non-MD3 project.

## Token Architecture

MD3 uses a three-tier CSS custom property system:

| Tier | Prefix | Purpose |
|---|---|---|
| Reference | `--md-ref-*` | Raw values (hex, px, font names) |
| System | `--md-sys-*` | Semantic roles and decisions |
| Component | `--md-comp-*` | Element-specific overrides |

Resolution chain: Component → System → Reference → Concrete value.

## Core Token Categories

### Color (`--md-sys-color-*`)

29+ color roles organized by function: accent (primary, secondary, tertiary), error, surface, and utility.

Each accent role follows the pattern:
- `*-<role>` — the color itself
- `*-on-<role>` — content color with accessible contrast
- `*-<role>-container` — container/background variant
- `*-on-<role>-container` — content on container
- `*-<role>-fixed` / `*-<role>-fixed-dim` — fixed variants (no light/dark switch)

Light/dark theming: swap tone values from the same tonal palette. All `on-*` tokens guarantee accessible contrast ratios.

### Typography (`--md-sys-typescale-*`)

15 type styles: 5 roles (Display, Headline, Title, Body, Label) x 3 sizes (Large, Medium, Small).

Token pattern: `--md-sys-typescale-<role>-<size>-<property>` where property is `font`, `size`, `line-height`, `weight`, or `tracking`.

Typeface references: `--md-ref-typeface-brand` (display) and `--md-ref-typeface-plain` (body).

### Shape (`--md-sys-shape-corner-*`)

7-step scale: none (0px), extra-small (4px), small (8px), medium (12px), large (16px), extra-large (28px), full (9999px).

### Elevation (`--md-sys-elevation-level*`)

6 levels (0-5). MD3 primarily uses **tonal elevation** (surface-tint overlay) rather than shadow-only. Box-shadow values available for shadow elevation.

### Motion (`--md-sys-motion-*`)

Easing: standard, standard-decelerate, standard-accelerate, emphasized, emphasized-decelerate, emphasized-accelerate, linear.

Duration: 16 steps from short1 (50ms) to extra-long4 (1000ms).

## Documentation Lookup Protocol

### Step 1: Bundled Reference Docs (Primary)

Consult the bundled quick-reference files at `${CLAUDE_PLUGIN_ROOT}/docs/material-design/web/`:

| File | Content |
|---|---|
| `color-system.md` | All color tokens, tone mappings, baseline hex values, dynamic color |
| `typography.md` | Full type scale values, typeface tokens, CSS examples |
| `shape-elevation-motion.md` | Shape scale, elevation levels + shadows, easing curves, durations |
| `layout-accessibility.md` | Breakpoints, grid, canonical layouts, a11y, state layers, token tiers |

### Step 2: context7 MCP (If Available)

Search for `material-web` or `material-design` libraries for additional API details.

### Step 3: WebSearch / WebFetch (Fallback)

```
site:material-web.dev <topic>
site:m3.material.io <topic>
site:github.com/material-components/material-web <topic>
```

## Response Process

1. **Detect MD3 usage** — scan the project for MD3 indicators before providing guidance
2. **Identify token tier** — determine if the question is about reference, system, or component tokens
3. **Consult bundled docs** — read the relevant reference file for exact values
4. **Provide CSS examples** — working, copy-pasteable CSS with custom properties
5. **Flag accessibility** — ensure `on-*` pairings meet WCAG contrast ratios
6. **Flag compatibility** — note browser support for any modern CSS features used
