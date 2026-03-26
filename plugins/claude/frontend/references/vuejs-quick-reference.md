# Vue.js Ecosystem Quick Reference

## 4. Vue 3 Core Quick Reference

### Reactivity API

| API | Purpose | Import |
|-----|---------|--------|
| `ref()` | Primitive/object reactive reference | `vue` |
| `reactive()` | Deep reactive object | `vue` |
| `computed()` | Derived reactive value | `vue` |
| `watch()` | Watch specific sources | `vue` |
| `watchEffect()` | Auto-track dependencies | `vue` |
| `toRef()` / `toRefs()` | Convert reactive to refs | `vue` |
| `shallowRef()` | Shallow reactive reference | `vue` |
| `triggerRef()` | Force trigger shallow ref | `vue` |
| `readonly()` | Read-only proxy | `vue` |

### Component API (`<script setup>`)

| Macro/API | Purpose |
|-----------|---------|
| `defineProps<T>()` | Type-safe props declaration |
| `defineEmits<T>()` | Type-safe event declaration |
| `defineModel()` | Two-way binding (v-model) |
| `defineExpose()` | Expose public instance properties |
| `defineOptions()` | Component options (name, inheritAttrs) |
| `defineSlots()` | Type-safe slot definitions |
| `useSlots()` | Access slots programmatically |
| `useAttrs()` | Access fallthrough attributes |

### Lifecycle Hooks

| Hook | Timing |
|------|--------|
| `onBeforeMount()` | Before DOM mount |
| `onMounted()` | After DOM mount |
| `onBeforeUpdate()` | Before DOM update |
| `onUpdated()` | After DOM update |
| `onBeforeUnmount()` | Before unmount |
| `onUnmounted()` | After unmount |
| `onErrorCaptured()` | Error from descendant |
| `onActivated()` | KeepAlive activated |
| `onDeactivated()` | KeepAlive deactivated |

### Built-in Directives

`v-if`, `v-else`, `v-else-if`, `v-show`, `v-for`, `v-on` (`@`), `v-bind` (`:`), `v-model`, `v-slot` (`#`), `v-pre`, `v-once`, `v-memo`, `v-cloak`

### Built-in Components

`<Transition>`, `<TransitionGroup>`, `<KeepAlive>`, `<Teleport>`, `<Suspense>`

## 5. Vite Quick Reference

### Key Config Options

| Option | Description |
|--------|-------------|
| `plugins` | Vite plugins array (e.g., `@vitejs/plugin-vue`) |
| `resolve.alias` | Path aliases (`@` → `./src`) |
| `server.port` | Dev server port |
| `server.proxy` | API proxy configuration |
| `build.target` | Browser target |
| `define` | Global constant replacements |
| `css.preprocessorOptions` | Sass/Less options |
| `envPrefix` | Env variable prefix (default: `VITE_`) |

### Environment Variables

- `import.meta.env.VITE_*` — Client-exposed variables
- `import.meta.env.MODE` — Current mode
- `import.meta.env.DEV` / `import.meta.env.PROD` — Boolean flags
- `import.meta.env.SSR` — SSR flag

## 6. Nuxt 3 Quick Reference

### Auto-Imports

Nuxt auto-imports from: `vue`, `vue-router`, `composables/`, `utils/`, `server/utils/`

### Key Composables

| Composable | Purpose |
|------------|---------|
| `useFetch()` | Data fetching with SSR support |
| `useAsyncData()` | Async data with key-based caching |
| `useLazyFetch()` | Non-blocking fetch |
| `useHead()` | Head/meta management |
| `useSeoMeta()` | SEO-focused meta tags |
| `useRuntimeConfig()` | Runtime configuration access |
| `useAppConfig()` | App configuration access |
| `useState()` | SSR-safe shared state |
| `useRoute()` | Current route object |
| `useRouter()` | Router instance |
| `useCookie()` | Cookie management |
| `useError()` | Error handling |
| `navigateTo()` | Programmatic navigation |

### Directory Conventions

| Directory | Purpose |
|-----------|---------|
| `pages/` | File-based routing |
| `components/` | Auto-imported components |
| `composables/` | Auto-imported composables |
| `layouts/` | Page layouts |
| `middleware/` | Route middleware |
| `plugins/` | App plugins |
| `server/api/` | API routes (Nitro) |
| `server/routes/` | Server routes |
| `server/middleware/` | Server middleware |
| `public/` | Static assets |
| `assets/` | Build-processed assets |

### Page Meta & Middleware

```typescript
definePageMeta({
  layout: 'custom',
  middleware: ['auth'],
  keepalive: true,
})
```

### Server Routes (Nitro)

```typescript
// server/api/hello.get.ts
export default defineEventHandler((event) => {
  return { hello: 'world' }
})
```

## 7. Pinia Quick Reference

### Store Definition (Setup Syntax)

```typescript
export const useCounterStore = defineStore('counter', () => {
  const count = ref(0)
  const doubleCount = computed(() => count.value * 2)
  function increment() { count.value++ }
  return { count, doubleCount, increment }
})
```

### Store Usage

```typescript
const store = useCounterStore()
const { count, doubleCount } = storeToRefs(store)
store.increment()
store.$reset()
store.$patch({ count: 10 })
```

## 8. Vue Router Quick Reference

### Router Setup

```typescript
const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', component: Home },
    { path: '/user/:id', component: User, props: true },
    { path: '/:pathMatch(.*)*', component: NotFound },
  ],
})
```

### Navigation Guards

| Guard | Scope |
|-------|-------|
| `router.beforeEach()` | Global before |
| `router.afterEach()` | Global after |
| `beforeEnter` | Per-route |
| `onBeforeRouteUpdate()` | In-component |
| `onBeforeRouteLeave()` | In-component |

### Composables

```typescript
const route = useRoute()    // reactive route object
const router = useRouter()  // router instance
router.push('/path')
router.replace('/path')
router.go(-1)
```

## 9. VueUse Quick Reference

### Popular Composables

| Composable | Category | Purpose |
|------------|----------|---------|
| `useStorage()` | State | Reactive localStorage/sessionStorage |
| `useDark()` | Browser | Dark mode toggle |
| `useToggle()` | State | Boolean toggle |
| `useFetch()` | Network | Fetch API wrapper |
| `useDebounce()` | Utilities | Debounced ref |
| `useThrottleFn()` | Utilities | Throttled function |
| `useIntersectionObserver()` | Sensors | Intersection observer |
| `useResizeObserver()` | Sensors | Element resize |
| `useClipboard()` | Browser | Clipboard API |
| `useEventListener()` | Browser | Auto-cleanup event listener |
| `useLocalStorage()` | State | Typed localStorage |
| `onClickOutside()` | Sensors | Click outside detection |
| `useMediaQuery()` | Browser | Responsive breakpoints |
| `useVModel()` | Component | v-model shorthand |

Always look up the specific composable documentation for current API details.

## 9a. Tailwind CSS + Styling Quick Reference

### cn() Utility (clsx + tailwind-merge)

```typescript
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

### CVA (Class Variance Authority)

```typescript
import { cva, type VariantProps } from 'class-variance-authority'

const buttonVariants = cva('inline-flex items-center rounded-md font-medium', {
  variants: {
    variant: {
      default: 'bg-primary text-primary-foreground',
      destructive: 'bg-destructive text-destructive-foreground',
      outline: 'border border-input bg-background',
    },
    size: {
      default: 'h-10 px-4 py-2',
      sm: 'h-9 px-3',
      lg: 'h-11 px-8',
    },
  },
  defaultVariants: {
    variant: 'default',
    size: 'default',
  },
})

type ButtonVariants = VariantProps<typeof buttonVariants>
```

### @tailwindcss/vite Setup

```typescript
// vite.config.ts
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [vue(), tailwindcss()],
})
```

```css
/* main.css */
@import "tailwindcss";
```

## 9b. vee-validate + Zod Quick Reference

### useForm with toTypedSchema

```typescript
import { useForm } from 'vee-validate'
import { toTypedSchema } from '@vee-validate/zod'
import { z } from 'zod'

const schema = toTypedSchema(
  z.object({
    email: z.string().email(),
    password: z.string().min(8),
  })
)

const { handleSubmit, errors } = useForm({ validationSchema: schema })
const onSubmit = handleSubmit((values) => { /* values is typed */ })
```

### useField

```typescript
const { value, errorMessage } = useField<string>('email')
```

### handleSubmit

```vue
<form @submit="onSubmit">
  <input v-model="email" />
  <span>{{ errors.email }}</span>
  <button type="submit">Submit</button>
</form>
```

## 9c. TanStack Query Quick Reference

### VueQueryPlugin Setup

```typescript
// main.ts
import { VueQueryPlugin, QueryClient } from '@tanstack/vue-query'

const queryClient = new QueryClient()
app.use(VueQueryPlugin, { queryClient })
```

### useQuery

```typescript
import { useQuery } from '@tanstack/vue-query'

const { data, isLoading, error } = useQuery({
  queryKey: ['users'],
  queryFn: () => fetch('/api/users').then(r => r.json()),
})
```

### useMutation with Invalidation

```typescript
import { useMutation, useQueryClient } from '@tanstack/vue-query'

const queryClient = useQueryClient()

const { mutate } = useMutation({
  mutationFn: (newUser: User) => fetch('/api/users', {
    method: 'POST',
    body: JSON.stringify(newUser),
  }),
  onSuccess: () => {
    queryClient.invalidateQueries({ queryKey: ['users'] })
  },
})
```

## 9d. Reka UI Quick Reference

### Component Composition Pattern

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
    <DialogTrigger>Open</DialogTrigger>
    <DialogPortal>
      <DialogOverlay class="fixed inset-0 bg-black/50" />
      <DialogContent class="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
        <DialogTitle>Title</DialogTitle>
        <DialogDescription>Description</DialogDescription>
        <DialogClose>Close</DialogClose>
      </DialogContent>
    </DialogPortal>
  </DialogRoot>
</template>
```

**Key imports:** Always import from `reka-ui`, never from `radix-vue` (Reka UI is the successor).

## 9e. Motion Quick Reference

### Basic Animation

```vue
<script setup lang="ts">
import { Motion, AnimatePresence } from 'motion/vue'
</script>

<template>
  <Motion
    :initial="{ opacity: 0, y: 20 }"
    :animate="{ opacity: 1, y: 0 }"
    :transition="{ duration: 0.5 }"
  >
    <div>Animated content</div>
  </Motion>
</template>
```

### Spring Animation

```vue
<Motion
  :animate="{ scale: 1.2 }"
  :transition="{ type: 'spring', stiffness: 300, damping: 20 }"
>
  <div>Spring animation</div>
</Motion>
```

### AnimatePresence (Exit Animations)

```vue
<AnimatePresence>
  <Motion
    v-if="show"
    :initial="{ opacity: 0 }"
    :animate="{ opacity: 1 }"
    :exit="{ opacity: 0 }"
  >
    <div>Appears and disappears</div>
  </Motion>
</AnimatePresence>
```

## 10. Vitest Quick Reference

### Test Structure

```typescript
import { describe, it, expect, vi, beforeEach } from 'vitest'

describe('MyComponent', () => {
  beforeEach(() => { /* setup */ })
  it('should work', () => { expect(1 + 1).toBe(2) })
})
```

### Vue Test Utils Integration

```typescript
import { mount, shallowMount } from '@vue/test-utils'
import MyComponent from './MyComponent.vue'

const wrapper = mount(MyComponent, {
  props: { title: 'Hello' },
  global: {
    plugins: [createPinia()],
    stubs: { RouterLink: true },
  },
})

expect(wrapper.text()).toContain('Hello')
await wrapper.find('button').trigger('click')
expect(wrapper.emitted('update')).toHaveLength(1)
```

### Mocking

```typescript
vi.mock('./api', () => ({ fetchData: vi.fn() }))
vi.spyOn(store, 'increment')
vi.useFakeTimers()
vi.stubGlobal('fetch', vi.fn())
```

