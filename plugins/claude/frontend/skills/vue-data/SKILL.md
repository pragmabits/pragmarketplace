---
name: vue-data
description: "This skill should be used when the user asks about TanStack Query, vue-query, or @internationalized/date in a Vue project. Trigger phrases include \"TanStack Query\", \"vue-query\", \"@tanstack/vue-query\", \"useQuery\", \"useMutation\", \"useQueryClient\", \"QueryClient\", \"VueQueryPlugin\", \"query invalidation\", \"server state\", \"cache management\", \"@internationalized/date\", \"CalendarDate\", \"CalendarDateTime\", \"ZonedDateTime\"."
---

# TanStack Query + @internationalized/date

This skill delegates to the `vuejs` agent, which fetches current documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for @tanstack/vue-query and @internationalized/date.

## Why this skill matters

TanStack Query separates server state from client state — a fundamentally different approach from putting API data in Pinia stores. It provides automatic caching, background refetching, deduplication, and optimistic updates. `@internationalized/date` provides locale-aware date objects used by UI date pickers (Reka UI DatePicker, etc.).

Without consulting documentation, answers may conflate server state with Pinia client state, use React Query API patterns instead of the Vue adapter, or forget the `VueQueryPlugin` setup.

## When to use this skill

Use for ANY request involving:

- Setting up TanStack Query in a Vue project
- `useQuery()` for data fetching with caching
- `useMutation()` for data mutations
- Query invalidation and cache management
- `useQueryClient()` for programmatic cache control
- `@internationalized/date` CalendarDate operations
- Server state vs client state architecture decisions

## Common patterns

### VueQueryPlugin setup

```typescript
// main.ts
import { createApp } from 'vue'
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'
import App from './App.vue'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 1000 * 60 * 5, // 5 minutes
      retry: 1,
    },
  },
})

const app = createApp(App)
app.use(VueQueryPlugin, { queryClient })
app.mount('#app')
```

### useQuery for data fetching

```vue
<script setup lang="ts">
import { useQuery } from '@tanstack/vue-query'

interface User {
  id: number
  name: string
  email: string
}

const { data, isLoading, isError, error } = useQuery({
  queryKey: ['users'],
  queryFn: async (): Promise<User[]> => {
    const response = await fetch('/api/users')
    if (!response.ok) throw new Error('Failed to fetch users')
    return response.json()
  },
})
</script>

<template>
  <div v-if="isLoading">Loading...</div>
  <div v-else-if="isError">Error: {{ error?.message }}</div>
  <ul v-else>
    <li v-for="user in data" :key="user.id">{{ user.name }}</li>
  </ul>
</template>
```

### useMutation with cache invalidation

```typescript
import { useMutation, useQueryClient } from '@tanstack/vue-query'

const queryClient = useQueryClient()

const { mutate, isPending } = useMutation({
  mutationFn: async (newUser: { name: string; email: string }) => {
    const response = await fetch('/api/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(newUser),
    })
    if (!response.ok) throw new Error('Failed to create user')
    return response.json()
  },
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['users'] })
  },
})
```

### useQueryClient for cache control

```typescript
const queryClient = useQueryClient()

// Invalidate specific queries
queryClient.invalidateQueries({ queryKey: ['users'] })

// Set data directly
queryClient.setQueryData(['users', userId], updatedUser)

// Prefetch data
queryClient.prefetchQuery({
  queryKey: ['users', userId],
  queryFn: () => fetchUser(userId),
})
```

### CalendarDate creation and comparison

```typescript
import { CalendarDate, CalendarDateTime, ZonedDateTime, today, getLocalTimeZone } from '@internationalized/date'

// Create dates
const date = new CalendarDate(2024, 3, 15) // March 15, 2024
const dateTime = new CalendarDateTime(2024, 3, 15, 10, 30)
const todayDate = today(getLocalTimeZone())

// Compare dates
if (date.compare(todayDate) < 0) {
  console.log('Date is in the past')
}

// Arithmetic
const nextWeek = todayDate.add({ weeks: 1 })
const lastMonth = todayDate.subtract({ months: 1 })
```

## Before delegating

BEFORE dispatching, use AskUserQuestion to clarify the user's intent. Every question to the user MUST go through AskUserQuestion — never ask as plain text. Common things to clarify:
- Whether they're asking about TanStack Query or @internationalized/date
- Whether they need setup or usage patterns
- Their caching/invalidation requirements

## How to use

Dispatch the `frontend:vuejs` agent with the user's question or task. Do not answer data management questions from general knowledge — the agent fetches current documentation for more accurate answers.

The agent will:
1. Check the user's project context (package.json for @tanstack/vue-query)
2. Look up current TanStack Query Vue or @internationalized/date documentation
3. Answer with Vue-specific API patterns (not React Query patterns)
4. Flag common pitfalls (missing VueQueryPlugin, React vs Vue API differences)
