---
name: tw-migration
description: "This skill should be used when the user asks about migrating from Tailwind CSS v3 to v4, upgrading, or fixing deprecated patterns. Trigger phrases include \"tailwind.config.js\", \"migrate\", \"migration\", \"upgrade\", \"v3\", \"v4\", \"deprecated\", \"bg-opacity\", \"text-opacity\", \"ring-opacity\", \"border-opacity\", \"@tailwind base\", \"@tailwind components\", \"@tailwind utilities\", \"upgrade tailwind\", \"tw3 to tw4\", \"breaking changes\", \"@tailwindcss/upgrade\", \"npx @tailwindcss/upgrade\"."
---

# Tailwind CSS 3 → 4 Migration

This skill delegates to the `tailwindcss` agent, which fetches current documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for TW3→TW4 migration.

## Why this skill matters

Tailwind CSS 4 is a major breaking change. Deprecated patterns produce broken output or are silently ignored. The migration involves directives (`@tailwind` → `@import`), theming (`extend` → `@theme`), plugins (`addUtilities` → `@utility`), opacity utilities (separate utilities → modifier syntax), and configuration (`tailwind.config.js` → CSS-first).

Without consulting documentation, answers may mix TW3 and TW4 patterns, use deprecated opacity utilities, or produce hybrid configurations that don't work correctly.

## When to use this skill

Use for ANY request involving:

- Migrating a project from Tailwind CSS 3 to 4
- Fixing deprecated TW3 patterns in existing code
- Converting `tailwind.config.js` to CSS-first `@theme` config
- Replacing deprecated opacity utilities with modifier syntax
- Converting `@tailwind base/components/utilities` to `@import "tailwindcss"`
- Migrating JavaScript plugins to CSS-native `@utility` / `@custom-variant`
- Understanding TW4 breaking changes

## Common patterns

### Directives migration

```css
/* TW3 (deprecated) */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* TW4 */
@import "tailwindcss";
```

### Opacity utilities migration

```html
<!-- TW3 (deprecated) -->
<div class="bg-blue-500 bg-opacity-50">
<div class="text-black text-opacity-75">
<div class="border-red-500 border-opacity-25">

<!-- TW4 -->
<div class="bg-blue-500/50">
<div class="text-black/75">
<div class="border-red-500/25">
```

### Theme migration

```javascript
// TW3 tailwind.config.js (deprecated)
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: { 500: '#3b82f6', 700: '#1d4ed8' },
      },
      spacing: { 18: '4.5rem' },
      fontFamily: { display: ['Cal Sans', 'sans-serif'] },
    },
  },
}
```

```css
/* TW4 @theme */
@theme {
  --color-brand-500: #3b82f6;
  --color-brand-700: #1d4ed8;
  --spacing-18: 4.5rem;
  --font-display: "Cal Sans", sans-serif;
}
```

### Plugin migration

```javascript
// TW3 plugin (deprecated)
const plugin = require('tailwindcss/plugin')
module.exports = plugin(function({ addUtilities, addVariant }) {
  addUtilities({ '.content-auto': { 'content-visibility': 'auto' } })
  addVariant('hocus', ['&:hover', '&:focus'])
})
```

```css
/* TW4 CSS-native */
@utility content-auto {
  content-visibility: auto;
}
@custom-variant hocus (&:hover, &:focus);
```

### Dark mode migration

```javascript
// TW3 config (deprecated)
module.exports = {
  darkMode: 'class',
}
```

```css
/* TW4 */
@variant dark (&:where(.dark, .dark *));
```

### Content sources migration

```javascript
// TW3 config (deprecated)
module.exports = {
  content: ['./src/**/*.{html,js,jsx,tsx}'],
}
```

```css
/* TW4 */
@source "./src/**/*.{html,js,jsx,tsx}";
```

## Before delegating

BEFORE dispatching, use AskUserQuestion to clarify the user's intent. Every question to the user MUST go through AskUserQuestion — never ask as plain text. Common things to clarify:
- Whether they want a full project migration or just fixing specific deprecated patterns
- Whether they can break things (staged migration vs all-at-once)
- Any third-party Tailwind plugins that need attention

## How to use

Dispatch the `frontend:tailwindcss` agent with the user's question or task. Do not answer Tailwind migration questions from general knowledge — the agent fetches current documentation for more accurate answers.

The agent will:
1. Detect whether the project uses TW3 or TW4 (check version, config style)
2. Look up current migration documentation
3. Provide before/after code for each deprecated pattern found
4. Suggest a step-by-step migration path
5. Flag patterns that will silently break in TW4
