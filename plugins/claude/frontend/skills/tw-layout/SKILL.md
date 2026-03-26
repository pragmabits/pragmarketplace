---
name: tw-layout
description: "This skill should be used when the user asks about layouts, flexbox, grid, or container queries in Tailwind CSS. Trigger phrases include \"flex\", \"grid\", \"container\", \"container queries\", \"@container\", \"columns\", \"gap\", \"layout\", \"aspect-ratio\", \"place-\", \"justify-\", \"items-\", \"flexbox layout\", \"grid layout\", \"responsive grid\", \"auto-grid\", \"sidebar layout\", \"holy grail\", \"container query\"."
---

# Tailwind CSS 4 Layout & Container Queries

This skill delegates to the `tailwindcss` agent, which fetches current documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for TW4 layout patterns and container queries.

## Why this skill matters

Tailwind CSS 4 introduces first-class container query support with `@container` and responsive container prefixes (`@sm:`, `@md:`, `@lg:`). These were not available in TW3. Container queries enable component-level responsive design that responds to the container's size rather than the viewport, fundamentally changing how responsive layouts are built.

Without consulting documentation, answers may miss container query syntax, confuse viewport-based `sm:` with container-based `@sm:` prefixes, or use outdated layout patterns.

## When to use this skill

Use for ANY request involving:

- Building flex or grid layouts with Tailwind utilities
- Using container queries (`@container`, `@sm:`, `@md:`)
- Creating responsive grid systems
- Implementing common layout patterns (sidebar, holy grail, dashboard)
- Using gap, place-items, justify-content utilities
- Combining viewport and container responsive breakpoints

## Common patterns

### Flex layout

```html
<div class="flex items-center justify-between gap-4">
  <div class="flex-1">Content</div>
  <div class="flex-shrink-0">Sidebar</div>
</div>
```

### Grid layout

```html
<div class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3">
  <div class="rounded-lg bg-white p-4 shadow">Card 1</div>
  <div class="rounded-lg bg-white p-4 shadow">Card 2</div>
  <div class="rounded-lg bg-white p-4 shadow">Card 3</div>
</div>
```

### Container queries (TW4)

```html
<div class="@container">
  <div class="flex flex-col @sm:flex-row @md:grid @md:grid-cols-3 gap-4">
    <div>Responds to container width, not viewport</div>
    <div>Reusable across different layout contexts</div>
    <div>True component-level responsive design</div>
  </div>
</div>
```

### Named containers

```html
<div class="@container/sidebar">
  <nav class="@sm/sidebar:flex @sm/sidebar:flex-col">
    Named container query
  </nav>
</div>
```

## Before delegating

BEFORE dispatching, use AskUserQuestion to clarify the user's intent. Every question to the user MUST go through AskUserQuestion — never ask as plain text. Common things to clarify:
- Whether they want Flexbox or Grid (or let the agent decide)
- Responsive requirements (viewport breakpoints vs container queries)
- Whether the layout needs to accommodate dynamic content

## How to use

Dispatch the `frontend:tailwindcss` agent with the user's question or task. Do not answer Tailwind layout questions from general knowledge — the agent fetches current documentation for more accurate answers.

The agent will:
1. Check the user's project context for layout patterns
2. Look up current layout and container query documentation
3. Provide layout solutions using modern TW4 utilities
4. Flag when container queries are more appropriate than viewport breakpoints
