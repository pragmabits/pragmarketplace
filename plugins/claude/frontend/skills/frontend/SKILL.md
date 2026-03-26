---
name: frontend
description: |
  This skill should be used when the user asks for cross-domain frontend development tasks that involve 2 or more specialist areas. Trigger phrases include "build a page", "create a dashboard", "landing page with", "responsive layout with icons", "Vue component with Tailwind and shadcn", "frontend project", "full-stack frontend", or any request that combines CSS, Tailwind CSS, Vue.js, Nuxt, shadcn/ui, Font Awesome, or frontend design work.

  Do NOT use this skill for single-domain questions. Those should go directly to the relevant specialist:
  - Pure CSS questions → css agent
  - Tailwind-only questions → tailwindcss agent
  - Vue/Nuxt-only questions → vuejs agent
  - shadcn/ui-only questions → shadcn agent
  - Font Awesome-only questions → fontawesome agent
---

The frontend orchestrator coordinates multiple specialist agents for cross-domain frontend tasks. It does not implement code directly — it delegates to specialists.

## Why this skill matters

Frontend tasks often span multiple technology domains. Building a dashboard might involve Vue components, Tailwind styling, shadcn UI primitives, Font Awesome icons, and CSS animations. Without orchestration, these domains are handled in isolation, leading to inconsistent patterns and missed integration opportunities.

The frontend orchestrator ensures:
- All relevant specialist domains are identified upfront
- Codebase exploration covers all technology layers
- Architecture proposals consider cross-domain interactions
- Implementation is coordinated across specialists
- Quality review checks cross-domain consistency

## When to use

**Use this skill when the task involves 2+ of these domains:**
- CSS (layouts, animations, selectors, performance, preprocessors)
- Tailwind CSS (utilities, theming, responsive, dark mode)
- Vue.js / Nuxt (components, routing, state, SSR, testing)
- shadcn/ui (component library, theming, CLI)
- Font Awesome (icons, animation, styling)
- Frontend design (aesthetics, UX, visual identity)

**Examples of tasks that need orchestration:**
- "Build a settings page with form validation, dark mode, and icon navigation"
- "Create a responsive landing page with hero, features, and contact form"
- "Build a Vue 3 dashboard with sidebar, charts, and notification system"
- "Redesign the admin panel with shadcn components and Tailwind theming"

**Examples that do NOT need orchestration (use specialist directly):**
- "How do I center a div?" → `/css`
- "Set up Tailwind dark mode" → `/tailwindcss`
- "Create a Pinia store" → `/vuejs`
- "Add a date picker" → `/shadcn`
- "Which icon for a delete button?" → `/fontawesome`

## How to use

```
/frontend <task description>
```

The orchestrator will:
1. Analyze the task and identify needed specialist domains
2. Launch parallel exploration agents for codebase context
3. Ask clarifying questions about underspecified aspects
4. Dispatch architecture agents with different approaches
5. Present the proposed approach for user approval
6. Coordinate specialist agents for implementation
7. Run quality review across all domains
8. Summarize results and next steps
