---
name: vue-test
description: "This skill should be used when the user asks about testing Vue.js applications. Trigger phrases include \"Vitest\", \"@vue/test-utils\", \"mount()\", \"shallowMount()\", \"vi.mock\", \"vi.fn\", \"test Vue component\", \"test composable\", \"test Pinia store\", \"@testing-library/vue\", \"component testing\", \"test coverage\", \"mock router\", or any Vitest or Vue Test Utils API question."
---

# Vitest & Vue Test Utils

This skill delegates to the `vuejs` agent for testing guidance. The agent fetches current Vitest and Vue Test Utils documentation at runtime, providing documentation-backed answers for test setup, component testing, mocking, and coverage configuration.

## Why this skill matters

Testing Vue 3 applications requires specific knowledge:

- **Vitest** is the Vite-native test runner — shares Vite config, supports ESM, HMR in watch mode
- **Vue Test Utils** (`@vue/test-utils`) provides `mount`/`shallowMount` with Vue 3-specific APIs
- **Testing Library Vue** (`@testing-library/vue`) offers user-centric testing as an alternative
- Component tests need proper plugin injection (Pinia, Router) via `global.plugins`
- Composable testing requires wrapper components or `renderHook` patterns
- Nuxt testing uses `@nuxt/test-utils` with its own setup patterns

Without current documentation, answers may use Jest patterns instead of Vitest, Vue 2 Test Utils API, or miss proper Pinia/Router plugin injection.

## When to use this skill

Use for ANY request involving testing Vue applications, including but not limited to:

- **Vitest**: Configuration, test structure, assertions, mocking (`vi.mock`, `vi.fn`, `vi.spyOn`), fake timers, coverage, workspace config
- **Vue Test Utils**: `mount`/`shallowMount`, finding elements, triggering events, checking emitted events, props, slots, stubs, global plugins injection
- **Testing Library Vue**: `render`, `screen` queries, `userEvent`, accessibility testing
- **Component testing**: Props, events, slots, async behavior, lifecycle
- **Composable testing**: Testing custom composables in isolation
- **Store testing**: Testing Pinia stores with `createTestingPinia`
- **Router testing**: Mocking routes, testing navigation guards
- **Nuxt testing**: `@nuxt/test-utils`, `mountSuspended`, server testing

## Common patterns

### Component test with Pinia and Router

```typescript
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { createRouter, createMemoryHistory } from 'vue-router'
import UserList from './UserList.vue'

const router = createRouter({
  history: createMemoryHistory(),
  routes: [{ path: '/', component: { template: '<div />' } }],
})

const wrapper = mount(UserList, {
  global: {
    plugins: [
      createTestingPinia({ initialState: { users: { list: mockUsers } } }),
      router,
    ],
  },
})
```

### Testing a composable (wrapper component pattern)

```typescript
import { mount } from '@vue/test-utils'
import { useCounter } from './useCounter'

function withSetup<T>(composable: () => T) {
  let result!: T
  mount({ setup() { result = composable(); return () => null } })
  return result
}

it('increments counter', () => {
  const { count, increment } = withSetup(() => useCounter())
  expect(count.value).toBe(0)
  increment()
  expect(count.value).toBe(1)
})
```

### Mocking API calls

```typescript
import { vi } from 'vitest'
import { flushPromises } from '@vue/test-utils'

vi.mock('./api', () => ({
  fetchUsers: vi.fn().mockResolvedValue([{ id: 1, name: 'Alice' }]),
}))

it('loads users on mount', async () => {
  const wrapper = mount(UserList)
  await flushPromises()
  expect(wrapper.findAll('li')).toHaveLength(1)
})
```

### Testing emitted events

```typescript
it('emits submit with form data', async () => {
  const wrapper = mount(LoginForm)
  await wrapper.find('input[name="email"]').setValue('test@example.com')
  await wrapper.find('form').trigger('submit')
  expect(wrapper.emitted('submit')?.[0]).toEqual([{ email: 'test@example.com' }])
})
```

## Before delegating

BEFORE dispatching, use AskUserQuestion to clarify the user's intent. Every question to the user MUST go through AskUserQuestion — never ask as plain text. Common things to clarify:
- What they're testing (component, composable, store, utility)
- Whether they want unit tests or integration tests
- Whether they already have a test setup or need to configure from scratch

## How to use

Dispatch the `frontend:vuejs` agent with the user's question or task. Do not answer Vue testing questions from general knowledge — the agent fetches current documentation for more accurate answers.

The agent will:
1. Check the user's project for test configuration (`vitest.config.*`, test files)
2. Look up current Vitest/Vue Test Utils documentation via context7 MCP or WebSearch
3. Answer with proper test patterns (plugin injection, mocking, async handling)
4. Flag common pitfalls (missing `flushPromises`, improper store injection)
5. Suggest testing patterns (component, composable, store, e2e)
