---
name: vue-state
description: "This skill should be used when the user asks about state management or routing in Vue.js applications. Trigger phrases include \"Pinia\", \"defineStore\", \"storeToRefs\", \"state management\", \"Vuex migration\", \"Vue Router\", \"useRoute\", \"useRouter\", \"navigation guards\", \"beforeEach\", \"dynamic routes\", \"nested routes\", \"lazy loading routes\", or any Pinia or Vue Router API question."
---

# Pinia & Vue Router

This skill delegates to the `vuejs` agent for state management and routing guidance. The agent fetches current Pinia and Vue Router documentation at runtime, providing documentation-backed answers for store patterns, routing configuration, and navigation guards.

## Why this skill matters

Pinia and Vue Router have specific patterns that differ from older alternatives:

- **Pinia** is the official Vue 3 store (not Vuex). Uses Composition API-style `defineStore` with `ref`/`computed`/functions instead of state/getters/mutations/actions
- **`storeToRefs()`** is required when destructuring stores — a common source of bugs
- **Vue Router 4** uses `createRouter()` with explicit history mode, not `new VueRouter()`
- Navigation guards have different signatures and can return values instead of calling `next()`
- Both integrate deeply with TypeScript for type-safe params, queries, and store state

Without current documentation, answers may use Vuex patterns, call `next()` in guards (deprecated pattern), or miss `storeToRefs()` requirements.

## When to use this skill

Use for ANY request involving Pinia or Vue Router, including but not limited to:

- **Pinia**: Store creation (setup and options syntax), store composition, `storeToRefs`, `$patch`, `$reset`, `$subscribe`, plugins, SSR state hydration, testing stores, persisted state
- **Vue Router**: Router setup, route definitions, dynamic/nested routes, navigation guards (`beforeEach`, `beforeEnter`, `onBeforeRouteUpdate`), lazy loading, route meta, named views, transitions, scroll behavior, hash vs history mode

## Common patterns

### Pinia store (setup syntax)

```typescript
export const useCartStore = defineStore('cart', () => {
  const items = ref<CartItem[]>([])
  const total = computed(() =>
    items.value.reduce((sum, item) => sum + item.price * item.qty, 0)
  )
  function addItem(item: CartItem) { items.value.push(item) }
  function removeItem(id: string) {
    items.value = items.value.filter(i => i.id !== id)
  }
  return { items, total, addItem, removeItem }
})
```

### Using store with storeToRefs

```vue
<script setup lang="ts">
const store = useCartStore()
const { items, total } = storeToRefs(store) // reactive refs
store.addItem(newItem) // actions called directly
</script>
```

### Router with lazy loading

```typescript
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: () => import('./views/Home.vue') },
    {
      path: '/dashboard',
      component: () => import('./views/Dashboard.vue'),
      children: [
        { path: 'settings', component: () => import('./views/Settings.vue') },
      ],
      meta: { requiresAuth: true },
    },
  ],
})
```

### Navigation guard (modern — no next())

```typescript
router.beforeEach((to) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
})
```

### Store composition

```typescript
export const useUserStore = defineStore('user', () => {
  const auth = useAuthStore() // use another store directly
  const profile = ref<UserProfile | null>(null)

  async function loadProfile() {
    if (!auth.isLoggedIn) return
    profile.value = await api.getProfile(auth.userId)
  }
  return { profile, loadProfile }
})
```

## How to use

Invoke the `/vuejs` command:

```
/vuejs <user's question about Pinia or Vue Router>
```

The agent will:
1. Check the user's project for existing store and router patterns
2. Look up current Pinia/Vue Router documentation via context7 MCP or WebSearch
3. Answer with Composition API-style store definitions and TypeScript-first router config
4. Flag common pitfalls (missing `storeToRefs`, deprecated `next()` in guards)
5. Suggest related patterns (store composition, route middleware)

Pinia and Vue Router questions should be delegated to the agent rather than answered from general knowledge — the agent fetches current documentation for more accurate, up-to-date answers.
