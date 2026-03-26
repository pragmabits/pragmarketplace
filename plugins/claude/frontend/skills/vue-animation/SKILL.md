---
name: vue-animation
description: "This skill should be used when the user asks about the motion library (motion.dev) for Vue animations. Trigger phrases include \"motion\", \"motion.dev\", \"motion-vue\", \"animate\", \"useMotion\", \"useAnimate\", \"spring animation\", \"animation library\", \"AnimatePresence\", \"motion/vue\", \"scroll animation\", \"gesture animation\"."
---

# Motion (motion.dev) Animations

This skill delegates to the `vuejs` agent, which fetches current documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for the motion library (motion.dev) in Vue.

## Why this skill matters

Motion provides declarative, spring-physics-based animations for Vue that go beyond what Vue's built-in `<Transition>` component offers. It handles complex animation scenarios like layout animations, scroll-triggered effects, gesture interactions, and exit animations via `AnimatePresence` — all with a declarative API.

Without consulting documentation, answers may use incorrect import paths, miss the `motion/vue` entry point, or try to use React-specific motion APIs in Vue.

## When to use this skill

Use for ANY request involving:

- Entrance and exit animations
- Spring-based physics animations
- Scroll-triggered animations
- Gesture-based animations (hover, tap, drag)
- `AnimatePresence` for exit animations
- Motion component from `motion/vue`
- Complex animation sequences

## Common patterns

### Motion component import

```vue
<script setup lang="ts">
import { Motion, AnimatePresence } from 'motion/vue'
</script>
```

### Basic entrance animation

```vue
<template>
  <Motion
    :initial="{ opacity: 0, y: 20 }"
    :animate="{ opacity: 1, y: 0 }"
    :transition="{ duration: 0.5 }"
  >
    <div class="card">Content fades in and slides up</div>
  </Motion>
</template>
```

### Spring configuration

```vue
<template>
  <Motion
    :initial="{ scale: 0 }"
    :animate="{ scale: 1 }"
    :transition="{
      type: 'spring',
      stiffness: 300,
      damping: 20,
      mass: 1,
    }"
  >
    <div>Springs into view</div>
  </Motion>
</template>
```

### AnimatePresence for exit animations

```vue
<script setup lang="ts">
import { Motion, AnimatePresence } from 'motion/vue'
import { ref } from 'vue'

const show = ref(true)
</script>

<template>
  <button @click="show = !show">Toggle</button>

  <AnimatePresence>
    <Motion
      v-if="show"
      :initial="{ opacity: 0, scale: 0.9 }"
      :animate="{ opacity: 1, scale: 1 }"
      :exit="{ opacity: 0, scale: 0.9 }"
      :transition="{ duration: 0.3 }"
    >
      <div class="panel">Appears and disappears smoothly</div>
    </Motion>
  </AnimatePresence>
</template>
```

### Scroll-triggered animations

```vue
<template>
  <Motion
    :initial="{ opacity: 0, y: 50 }"
    :in-view="{ opacity: 1, y: 0 }"
    :transition="{ duration: 0.6 }"
  >
    <div>Animates when scrolled into view</div>
  </Motion>
</template>
```

### Hover and tap gestures

```vue
<template>
  <Motion
    :while-hover="{ scale: 1.05 }"
    :while-tap="{ scale: 0.95 }"
    :transition="{ type: 'spring', stiffness: 400, damping: 17 }"
  >
    <button>Interactive button</button>
  </Motion>
</template>
```

## Before delegating

BEFORE dispatching, use AskUserQuestion to clarify the user's intent. Every question to the user MUST go through AskUserQuestion — never ask as plain text. Common things to clarify:
- Whether they want motion.dev or Vue's built-in Transition/TransitionGroup
- Type of animation (entrance, exit, scroll-triggered, gesture)
- Performance requirements (spring vs tween, reduced motion support)

## How to use

Dispatch the `frontend:vuejs` agent with the user's question or task. Do not answer Vue animation questions from general knowledge — the agent fetches current documentation for more accurate answers.

The agent will:
1. Check the user's project context (package.json for motion)
2. Look up current motion.dev documentation for Vue
3. Answer with Vue-specific patterns (not React motion patterns)
4. Flag common pitfalls (import path, React vs Vue API differences)
