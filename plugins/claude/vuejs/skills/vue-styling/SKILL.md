---
name: vue-styling
description: "This skill should be used when the user asks about Tailwind CSS, CVA, clsx, or tailwind-merge in a Vue project. Trigger phrases include \"Tailwind\", \"tailwindcss\", \"@tailwindcss/vite\", \"Tailwind CSS\", \"CVA\", \"class-variance-authority\", \"cva()\", \"cn()\", \"clsx\", \"tailwind-merge\", \"twMerge\", \"utility classes\", \"conditional classes\", \"variant styling\"."
---

# Tailwind CSS + Styling Utilities

This skill delegates to the `vuejs` agent, which fetches current documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for Tailwind CSS v4, CVA, clsx, and tailwind-merge.

## Why this skill matters

Tailwind CSS v4 introduces a new Vite-native plugin (`@tailwindcss/vite`) that replaces the PostCSS approach. The `cn()` utility (clsx + tailwind-merge) has become the de facto standard for conditional class merging in component libraries. CVA provides type-safe variant definitions that pair perfectly with TypeScript Vue components.

Without consulting documentation, answers may use the outdated PostCSS setup, miss the `cn()` pattern, or produce CVA variants without proper TypeScript integration.

## When to use this skill

Use for ANY request involving:

- Setting up Tailwind CSS in a Vite + Vue project
- Creating the `cn()` utility function
- Defining component variants with CVA
- Conditional class application with clsx
- Merging conflicting Tailwind classes with tailwind-merge
- `@tailwindcss/vite` plugin configuration
- `VariantProps` type extraction from CVA definitions

## Common patterns

### cn() utility function (clsx + tailwind-merge)

```typescript
// lib/utils.ts
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### CVA variant definition with VariantProps

```typescript
import { cva, type VariantProps } from 'class-variance-authority'
import { cn } from '@/lib/utils'

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input bg-background hover:bg-accent hover:text-accent-foreground',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
      },
      size: {
        default: 'h-10 px-4 py-2',
        sm: 'h-9 rounded-md px-3',
        lg: 'h-11 rounded-md px-8',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
)

type ButtonVariants = VariantProps<typeof buttonVariants>
```

### @tailwindcss/vite setup

```typescript
// vite.config.ts
import vue from '@vitejs/plugin-vue'
import tailwindcss from '@tailwindcss/vite'
import { defineConfig } from 'vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
})
```

```css
/* src/assets/main.css */
@import "tailwindcss";
```

### Component using cn() + CVA together

```vue
<script setup lang="ts">
import { cn } from '@/lib/utils'
import { cva, type VariantProps } from 'class-variance-authority'

const buttonVariants = cva('inline-flex items-center rounded-md font-medium', {
  variants: {
    variant: {
      default: 'bg-primary text-primary-foreground',
      outline: 'border border-input bg-background',
    },
    size: {
      default: 'h-10 px-4 py-2',
      sm: 'h-9 px-3',
    },
  },
  defaultVariants: { variant: 'default', size: 'default' },
})

type Props = VariantProps<typeof buttonVariants> & { class?: string }
const props = defineProps<Props>()
</script>

<template>
  <button :class="cn(buttonVariants({ variant, size }), props.class)">
    <slot />
  </button>
</template>
```

## How to use

Invoke the `/vuejs` command, passing the user's question or task as the argument:

```
/vuejs <user's question or task>
```

The agent will:
1. Check the user's project context (package.json, vite.config.*, CSS files)
2. Look up current Tailwind CSS, CVA, clsx, and tailwind-merge documentation
3. Answer with TypeScript-first code examples using modern patterns
4. Flag common pitfalls (PostCSS vs Vite plugin, missing tailwind-merge)

Tailwind CSS and styling questions should be delegated to the agent rather than answered from general knowledge — the agent fetches current documentation for more accurate, up-to-date answers.
