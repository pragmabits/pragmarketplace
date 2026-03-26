---
name: vue-ui
description: "This skill should be used when the user asks about reka-ui, lucide-vue-next, vue-sonner, or fontsource in a Vue project. Trigger phrases include \"reka-ui\", \"Reka UI\", \"Radix Vue\", \"headless components\", \"headless UI\", \"lucide\", \"lucide-vue-next\", \"icons\", \"vue-sonner\", \"toast\", \"Sonner\", \"toast notification\", \"fontsource\", \"@fontsource\", \"Roboto Mono\", \"self-hosted font\", \"unstyled components\"."
---

# UI Components — Reka UI, Lucide, Vue Sonner, Fontsource

This skill delegates to the `vuejs` agent, which fetches current documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for reka-ui, lucide-vue-next, vue-sonner, and fontsource.

## Why this skill matters

Reka UI is the successor to Radix Vue — it provides headless, accessible components that pair perfectly with Tailwind CSS. Lucide provides tree-shakeable icons as Vue components. Vue-sonner offers a minimal toast notification system. Fontsource enables self-hosted fonts without external CDN dependencies.

Without consulting documentation, answers may import from the deprecated `radix-vue` package, use incorrect Reka UI composition patterns, or miss the proper setup for vue-sonner's `<Toaster />` component.

## When to use this skill

Use for ANY request involving:

- Reka UI headless components (Dialog, Select, Dropdown, Popover, etc.)
- Lucide icon imports and usage
- Vue-sonner toast notifications
- Fontsource self-hosted font setup
- Headless + Tailwind component styling patterns
- Accessible component composition

## Common patterns

### Reka UI Dialog composition

```vue
<script setup lang="ts">
import {
  DialogRoot, DialogTrigger, DialogPortal,
  DialogOverlay, DialogContent, DialogTitle,
  DialogDescription, DialogClose,
} from 'reka-ui'
</script>

<template>
  <DialogRoot>
    <DialogTrigger as-child>
      <button>Open Dialog</button>
    </DialogTrigger>
    <DialogPortal>
      <DialogOverlay class="fixed inset-0 bg-black/50" />
      <DialogContent class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 rounded-lg bg-white p-6">
        <DialogTitle class="text-lg font-semibold">Dialog Title</DialogTitle>
        <DialogDescription class="text-sm text-muted-foreground">
          Dialog description here.
        </DialogDescription>
        <DialogClose as-child>
          <button>Close</button>
        </DialogClose>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
```

### Reka UI Select composition

```vue
<script setup lang="ts">
import {
  SelectRoot, SelectTrigger, SelectValue,
  SelectPortal, SelectContent, SelectViewport,
  SelectItem, SelectItemText, SelectItemIndicator,
} from 'reka-ui'
</script>

<template>
  <SelectRoot v-model="selected">
    <SelectTrigger class="inline-flex items-center gap-2 rounded border px-3 py-2">
      <SelectValue placeholder="Select an option" />
    </SelectTrigger>
    <SelectPortal>
      <SelectContent class="rounded-md border bg-white shadow-md">
        <SelectViewport class="p-1">
          <SelectItem value="one" class="cursor-pointer rounded px-2 py-1.5 hover:bg-accent">
            <SelectItemText>Option One</SelectItemText>
            <SelectItemIndicator />
          </SelectItem>
        </SelectViewport>
      </SelectContent>
    </SelectPortal>
  </SelectRoot>
</template>
```

### Lucide icon import and usage

```vue
<script setup lang="ts">
import { Search, ChevronDown, X } from 'lucide-vue-next'
</script>

<template>
  <Search :size="20" class="text-muted-foreground" />
  <ChevronDown :size="16" :stroke-width="2" />
  <X :size="16" color="red" />
</template>
```

### Vue-sonner setup and usage

```typescript
// App.vue — add Toaster to root
import { Toaster } from 'vue-sonner'
```

```vue
<!-- App.vue template -->
<template>
  <RouterView />
  <Toaster position="bottom-right" :duration="4000" rich-colors />
</template>
```

```typescript
// Any component — trigger toasts
import { toast } from 'vue-sonner'

toast.success('Changes saved')
toast.error('Something went wrong')
toast('Neutral notification')
toast.promise(saveData(), {
  loading: 'Saving...',
  success: 'Saved!',
  error: 'Failed to save',
})
```

### Fontsource import

```typescript
// main.ts
import '@fontsource/roboto-mono'
import '@fontsource/roboto-mono/400.css'    // specific weight
import '@fontsource/roboto-mono/700.css'    // bold weight
import '@fontsource/roboto-mono/400-italic.css' // italic
```

```css
/* In CSS */
body {
  font-family: 'Roboto Mono', monospace;
}
```

## Before delegating

BEFORE dispatching, use AskUserQuestion to clarify the user's intent. Every question to the user MUST go through AskUserQuestion — never ask as plain text. Common things to clarify:
- Which UI library they're asking about (reka-ui, lucide, vue-sonner, fontsource)
- Whether they need setup instructions or usage patterns
- Whether they're integrating with shadcn/ui or building custom components

## How to use

Dispatch the `frontend:vuejs` agent with the user's question or task. Do not answer UI component questions from general knowledge — the agent fetches current documentation for more accurate answers.

The agent will:
1. Check the user's project context (package.json for installed UI libraries)
2. Look up current reka-ui, lucide, vue-sonner, or fontsource documentation
3. Answer with proper composition patterns and Tailwind styling
4. Flag common pitfalls (radix-vue vs reka-ui, missing Toaster setup)
