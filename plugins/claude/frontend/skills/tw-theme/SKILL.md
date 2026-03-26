---
name: tw-theme
description: "This skill should be used when the user asks about Tailwind CSS theming, design tokens, or CSS custom properties. Trigger phrases include \"@theme\", \"design tokens\", \"CSS custom properties\", \"CSS variables\", \"colors\", \"spacing\", \"typography\", \"font\", \"--color-\", \"--spacing-\", \"--font-\", \"custom colors\", \"color palette\", \"theme configuration\", \"extend colors\", \"brand colors\", \"design system tokens\"."
---

# Tailwind CSS 4 Theming & Design Tokens

This skill delegates to the `tailwindcss` agent, which fetches current documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for TW4 theming with `@theme`.

## Why this skill matters

Tailwind CSS 4 replaced `tailwind.config.js extend.colors/spacing/fonts` with CSS-native `@theme` blocks that compile to CSS custom properties. This is a fundamental shift — the old JavaScript-based theming no longer applies. Design tokens defined in `@theme` are accessible both as utility classes and as `var(--token-name)` in custom CSS.

Without consulting documentation, answers may use `extend: { colors: {} }` in JavaScript config, miss the `@theme` syntax, or produce tokens that don't generate the expected CSS custom properties.

## When to use this skill

Use for ANY request involving:

- Defining custom colors, spacing, or typography in TW4
- Creating a design token system with `@theme`
- Referencing theme values via CSS custom properties
- Migrating from `tailwind.config.js` theme to `@theme`
- Overriding or extending default Tailwind theme values
- Building a multi-theme or brand-specific color system

## Common patterns

### Full @theme block with colors, spacing, fonts

```css
@import "tailwindcss";

@theme {
  --color-brand-50: #eff6ff;
  --color-brand-100: #dbeafe;
  --color-brand-500: #3b82f6;
  --color-brand-700: #1d4ed8;
  --color-brand-900: #1e3a5f;

  --color-surface: #ffffff;
  --color-surface-alt: #f8fafc;

  --spacing-18: 4.5rem;
  --spacing-128: 32rem;

  --font-display: "Cal Sans", sans-serif;
  --font-body: "Inter", sans-serif;

  --radius-card: 0.75rem;
}
```

### Using theme tokens in utilities and custom CSS

```html
<!-- As utility classes -->
<div class="bg-brand-500 text-white font-display p-18 rounded-card">
  Brand card
</div>
```

```css
/* As CSS custom properties */
.custom-element {
  background: var(--color-brand-500);
  font-family: var(--font-display);
  padding: var(--spacing-18);
}
```

### Overriding default theme values

```css
@theme {
  --color-blue-500: #2563eb;
  --breakpoint-sm: 640px;
  --font-sans: "Inter", sans-serif;
}
```

## How to use

Invoke the `/tailwindcss` command, passing the user's question or task as the argument:

```
/tailwindcss <user's question or task>
```

The agent will:
1. Check the user's project context for existing theme configuration
2. Look up current `@theme` documentation
3. Provide design token definitions with proper `@theme` syntax
4. Flag deprecated patterns (JavaScript extend.colors, theme() function)

Theming questions should be delegated to the agent rather than answered from general knowledge — the agent fetches current documentation for more accurate, up-to-date answers.
