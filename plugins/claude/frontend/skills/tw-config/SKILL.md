---
name: tw-config
description: "This skill should be used when the user asks about Tailwind CSS setup, installation, or configuration. Trigger phrases include \"@import tailwindcss\", \"PostCSS\", \"setup tailwind\", \"install tailwind\", \"vite tailwind\", \"@tailwindcss/vite\", \"@tailwindcss/postcss\", \"@tailwindcss/cli\", \"@layer\", \"@source\", \"content configuration\", \"main.css\", \"tailwind setup\", \"postcss.config\", \"CSS entry point\", \"configure tailwind\", \"next.js tailwind\", \"nuxt tailwind\", \"astro tailwind\", \"remix tailwind\"."
---

# Tailwind CSS 4 Configuration & Setup

This skill delegates to the `tailwindcss` agent, which fetches current documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for TW4 setup and configuration.

## Why this skill matters

Tailwind CSS 4 fundamentally changed the setup process. The `@tailwindcss/vite` plugin replaces the PostCSS approach for Vite projects. The CSS entry point uses `@import "tailwindcss"` instead of `@tailwind` directives. The `@source` directive replaces the `content` array in JavaScript config. The `@layer` directive organizes custom CSS within the Tailwind cascade.

Without consulting documentation, answers may use the outdated PostCSS setup for Vite projects, generate `@tailwind base/components/utilities` directives, or create `tailwind.config.js` files when CSS-first config is preferred.

## When to use this skill

Use for ANY request involving:

- Installing Tailwind CSS 4 in a new project
- Setting up `@tailwindcss/vite` for Vite-based projects
- Configuring `@tailwindcss/postcss` for non-Vite projects
- Writing the CSS entry point (`@import "tailwindcss"`)
- Specifying content sources with `@source`
- Organizing custom CSS with `@layer`
- Migrating from `tailwind.config.js` to CSS-first config

## Common patterns

### Vite setup (@tailwindcss/vite)

```typescript
// vite.config.ts
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [tailwindcss()],
})
```

```css
/* main.css */
@import "tailwindcss";
```

### PostCSS setup (@tailwindcss/postcss)

```javascript
// postcss.config.mjs
export default {
  plugins: {
    '@tailwindcss/postcss': {},
  },
}
```

### Content sources with @source

```css
@import "tailwindcss";
@source "../node_modules/@my-company/ui-lib/src/**/*.{html,js}";
@source "./content/**/*.md";
```

### Layer organization

```css
@import "tailwindcss";

@layer base {
  html {
    font-family: var(--font-sans);
  }
}

@layer components {
  .card {
    @apply rounded-lg bg-white p-6 shadow-md;
  }
}

@layer utilities {
  .content-auto {
    content-visibility: auto;
  }
}
```

## Before delegating

BEFORE dispatching, use AskUserQuestion to clarify the user's intent. Every question to the user MUST go through AskUserQuestion — never ask as plain text. Common things to clarify:
- Which framework they're using (Vite, Next.js, Nuxt, Astro)
- Whether they're doing a fresh setup or reconfiguring an existing project
- Tailwind version (v3 or v4)

## How to use

Dispatch the `frontend:tailwindcss` agent with the user's question or task. Do not answer Tailwind setup questions from general knowledge — the agent fetches current documentation for more accurate answers.

The agent will:
1. Check the user's project context (package.json, vite.config.*, postcss.config.*)
2. Look up current Tailwind CSS 4 setup documentation
3. Provide framework-appropriate installation and configuration steps
4. Flag deprecated setup patterns (PostCSS in Vite projects, @tailwind directives)
