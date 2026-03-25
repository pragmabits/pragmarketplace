---
name: vue-component
description: "This skill should be used when the user asks to create, modify, or understand Vue 3 components. Trigger phrases include \"create a Vue component\", \"Vue SFC\", \"Single File Component\", \"script setup\", \"defineProps\", \"defineEmits\", \"defineModel\", \"Composition API\", \"composable\", \"ref()\", \"reactive()\", \"computed()\", \"provide/inject\", \"slots\", \"Teleport\", \"Suspense\", \"KeepAlive\", \"Transition\", or any Vue 3 component or reactivity API question."
---

# Vue 3 Component Development

This skill delegates to the `vuejs` agent, which fetches current Vue 3 documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers — especially for Vue 3-specific features like `<script setup>` macros, reactivity system nuances, and TypeScript integration.

## Why this skill matters

Vue 3's Composition API and `<script setup>` syntax represent a fundamental shift from Vue 2:

- Components use `<script setup>` macros (`defineProps`, `defineEmits`, `defineModel`) not `export default`
- Reactivity uses `ref()` and `reactive()` not `data()` return objects
- Logic reuse uses composables not mixins
- TypeScript integration is first-class with generic props and emits
- New built-in components (`Suspense`, improved `Transition`) have specific usage patterns

Without consulting documentation, answers may use deprecated Options API patterns, miss TypeScript generics for props/emits, or provide Vue 2-era guidance.

## When to use this skill

Use for ANY request involving Vue 3 component development, including but not limited to:

- Creating new components with `<script setup lang="ts">`
- Defining typed props with `defineProps<T>()`
- Defining typed events with `defineEmits<T>()`
- Two-way binding with `defineModel()`
- Composable creation and usage patterns
- Reactivity system (`ref`, `reactive`, `computed`, `watch`, `watchEffect`)
- Lifecycle hooks (`onMounted`, `onUnmounted`, etc.)
- Provide/inject for dependency injection
- Template refs and `defineExpose()`
- Slots, scoped slots, and `useSlots()`
- Built-in components (`Transition`, `KeepAlive`, `Teleport`, `Suspense`)
- Dynamic and async components
- Render functions and JSX

## Common patterns

### Typed props with defaults

```vue
<script setup lang="ts">
const props = withDefaults(defineProps<{
  title: string
  count?: number
}>(), {
  count: 0,
})
</script>
```

### Two-way binding (Vue 3.4+)

```vue
<script setup lang="ts">
const modelValue = defineModel<string>({ required: true })
const selected = defineModel<number>('selected')
</script>
```

### Basic composable

```typescript
export function useCounter(initial = 0) {
  const count = ref(initial)
  const increment = () => count.value++
  const decrement = () => count.value--
  return { count: readonly(count), increment, decrement }
}
```

### Expose public API

```vue
<script setup lang="ts">
const validate = () => { /* ... */ return true }
defineExpose({ validate })
</script>
```

### Provide/inject with TypeScript

```typescript
// keys.ts
const ThemeKey: InjectionKey<Ref<'light' | 'dark'>> = Symbol('theme')

// Provider: provide(ThemeKey, theme)
// Consumer: const theme = inject(ThemeKey)
```

## How to use

Invoke the `/vuejs` command, passing the user's question or task as the argument:

```
/vuejs <user's question or task>
```

The agent will:
1. Check the user's project context (package.json, tsconfig.json, vite.config.*)
2. Look up current Vue 3 documentation via context7 MCP or WebSearch
3. Answer with TypeScript-first, Composition API code examples
4. Flag version-specific features and common pitfalls
5. Suggest related composables or patterns

Vue 3 component questions should be delegated to the agent rather than answered from general knowledge — the agent fetches current documentation for more accurate, up-to-date answers.
