---
name: nuxt
description: "This skill should be used when the user asks about Nuxt 3 development. Trigger phrases include \"Nuxt\", \"Nuxt 3\", \"nuxt.config\", \"useFetch\", \"useAsyncData\", \"server routes\", \"Nitro\", \"file-based routing\", \"auto-imports\", \"SSR\", \"SSG\", \"hybrid rendering\", \"Nuxt modules\", \"definePageMeta\", \"Nuxt middleware\", \"Nuxt layouts\", or any Nuxt 3 composable or API question."
---

# Nuxt 3 Development

This skill delegates to the `vuejs` agent with Nuxt 3 focus. The agent fetches current Nuxt 3 documentation at runtime via context7 MCP and WebSearch, providing documentation-backed answers for Nuxt-specific features like auto-imports, server routes, and rendering modes.

## Why this skill matters

Nuxt 3 is a complete rewrite from Nuxt 2 with fundamentally different patterns:

- Auto-imports for Vue APIs, composables, and components (no manual imports)
- File-based routing with `definePageMeta` instead of router configuration
- Server routes via Nitro engine (not serverMiddleware)
- `useFetch`/`useAsyncData` replace `asyncData`/`fetch` hooks
- Hybrid rendering with per-route rules (SSR, SSG, SPA, ISR)
- TypeScript-first with auto-generated types

Without current documentation, answers risk using Nuxt 2 patterns that don't work in Nuxt 3.

## When to use this skill

Use for ANY request involving Nuxt 3, including but not limited to:

- Project setup and configuration (`nuxt.config.ts`)
- File-based routing and page meta
- Data fetching (`useFetch`, `useAsyncData`, `useLazyFetch`)
- Server routes and API endpoints (Nitro)
- Middleware (route and server)
- Layouts and error handling
- Modules and plugins
- SSR/SSG/SPA rendering modes and hybrid rendering
- Runtime config and app config
- Auto-imports and directory conventions
- SEO and head management (`useHead`, `useSeoMeta`)
- Deployment and hosting (Vercel, Netlify, Cloudflare, Node)

## Common patterns

### Data fetching with SSR

```vue
<script setup lang="ts">
const { data, pending, error } = await useFetch('/api/users')
</script>

<template>
  <div v-if="pending">Loading...</div>
  <div v-else-if="error">Error: {{ error.message }}</div>
  <ul v-else>
    <li v-for="user in data" :key="user.id">{{ user.name }}</li>
  </ul>
</template>
```

### Server API route

```typescript
// server/api/users.get.ts
export default defineEventHandler(async (event) => {
  const query = getQuery(event)
  return { users: await fetchUsers(query) }
})
```

### Route middleware

```typescript
// middleware/auth.ts
export default defineNuxtRouteMiddleware((to, from) => {
  const { authenticated } = useAuthState() // your auth composable
  if (!authenticated.value) return navigateTo('/login')
})
```

### Page with meta

```vue
<script setup lang="ts">
definePageMeta({
  layout: 'dashboard',
  middleware: ['auth'],
})

const { data } = await useFetch('/api/dashboard')
</script>
```

### Runtime config

```typescript
// nuxt.config.ts
export default defineNuxtConfig({
  runtimeConfig: {
    secretKey: '', // server-only, from NUXT_SECRET_KEY
    public: {
      apiBase: '/api', // client + server, from NUXT_PUBLIC_API_BASE
    },
  },
})
```

## How to use

Invoke the `/nuxt` command for Nuxt-focused guidance (preferred):

```
/nuxt <user's question or task>
```

Or use `/vuejs` for general Vue ecosystem questions that also involve Nuxt:

```
/vuejs <user's question involving Nuxt>
```

The agent will:
1. Check the user's project for `nuxt.config.ts` and directory structure
2. Look up current Nuxt 3 documentation via context7 MCP or WebSearch
3. Answer with Nuxt 3 patterns (auto-imports, composables, Nitro)
4. Flag SSR considerations and hydration pitfalls
5. Suggest relevant Nuxt modules when applicable

Nuxt 3 questions should be delegated to the agent rather than answered from general knowledge — the agent fetches current documentation for more accurate, up-to-date answers.
