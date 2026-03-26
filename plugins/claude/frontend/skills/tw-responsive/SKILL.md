---
name: tw-responsive
description: "This skill should be used when the user asks about responsive design, breakpoints, or dark mode in Tailwind CSS. Trigger phrases include \"breakpoints\", \"dark mode\", \"sm:\", \"md:\", \"lg:\", \"xl:\", \"2xl:\", \"prefers-color-scheme\", \"media query\", \"@variant dark\", \"@custom-variant print\", \"@custom-variant motion\", \"dark:\", \"responsive\", \"mobile-first\", \"responsive design\", \"dark theme\", \"light theme\", \"color scheme\", \"custom breakpoint\", \"print styles\", \"reduced motion\"."
---

# Tailwind CSS 4 Responsive Design & Dark Mode

This skill delegates to the `tailwindcss` agent, which fetches current documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for TW4 responsive patterns and dark mode.

## Why this skill matters

Tailwind CSS 4 changes how dark mode and custom variants are configured. Dark mode now uses `@variant dark { ... }` for custom configurations instead of `darkMode: 'class'` in JavaScript config. Custom breakpoints are defined in `@theme` instead of `screens` in config. The `@custom-variant` directive enables print styles, reduced motion, and other media-query-based variants.

Without consulting documentation, answers may use `darkMode: 'class'` in config, miss the `@variant dark` syntax, or define breakpoints in the wrong location.

## When to use this skill

Use for ANY request involving:

- Responsive breakpoints (`sm:`, `md:`, `lg:`, `xl:`, `2xl:`)
- Dark mode implementation (`dark:` variant)
- Custom dark mode configuration with `@variant dark`
- Custom media query variants (print, reduced-motion)
- Mobile-first responsive patterns
- Custom breakpoint definitions in `@theme`
- Combining responsive and state variants

## Common patterns

### Mobile-first responsive design

```html
<div class="px-4 md:px-8 lg:px-16">
  <h1 class="text-2xl md:text-4xl lg:text-6xl font-bold">
    Responsive heading
  </h1>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
    <!-- Cards -->
  </div>
</div>
```

### Dark mode

```html
<div class="bg-white text-gray-900 dark:bg-gray-900 dark:text-white">
  <p class="text-gray-600 dark:text-gray-300">
    Adapts to color scheme
  </p>
</div>
```

### Custom dark mode variant (TW4)

```css
@import "tailwindcss";
@variant dark (&:where(.dark, .dark *));
```

### Custom breakpoints in @theme

```css
@theme {
  --breakpoint-xs: 480px;
  --breakpoint-3xl: 1920px;
}
```

```html
<div class="xs:flex 3xl:grid 3xl:grid-cols-6">
  Custom breakpoint layout
</div>
```

### Custom media query variants

```css
@custom-variant print (@media print);
@custom-variant motion-safe (@media (prefers-reduced-motion: no-preference));
@custom-variant motion-reduce (@media (prefers-reduced-motion: reduce));
```

```html
<div class="motion-safe:animate-bounce print:hidden">
  Animated content, hidden in print
</div>
```

## Before delegating

BEFORE dispatching, use AskUserQuestion to clarify the user's intent. Every question to the user MUST go through AskUserQuestion — never ask as plain text. Common things to clarify:
- Dark mode strategy (media query vs class-based toggle)
- Custom breakpoint requirements
- Whether they're adding responsive behavior to existing components or building new ones

## How to use

Dispatch the `frontend:tailwindcss` agent with the user's question or task. Do not answer Tailwind responsive/dark mode questions from general knowledge — the agent fetches current documentation for more accurate answers.

The agent will:
1. Check the user's project context for responsive and dark mode patterns
2. Look up current breakpoint and dark mode documentation
3. Provide mobile-first responsive solutions with TW4 syntax
4. Flag deprecated patterns (darkMode in config, screens in config)
