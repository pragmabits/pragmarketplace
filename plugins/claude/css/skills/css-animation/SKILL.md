---
name: css-animation
description: "This skill should be used when the user asks about CSS animations, \"transition\", \"keyframes\", \"@keyframes\", \"transform\", \"translate\", \"rotate\", \"scale\", \"ease\", \"cubic-bezier\", \"animation-timeline\", \"scroll-driven animation\", \"will-change\", \"prefers-reduced-motion\", \"view transitions\", \"View Transition API\", or needs help creating motion effects, hover transitions, loading spinners, or animated UI elements."
---

# CSS Animation

This skill delegates to the `css` agent, which fetches current documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for CSS animations and transitions.

## Why this skill matters

CSS animation encompasses transitions, keyframe animations, scroll-driven animations, and the View Transition API — each with different use cases and performance characteristics. Modern CSS has introduced scroll-driven animations and view transitions that eliminate the need for JavaScript-based scroll libraries. Without consulting documentation, answers may miss performance best practices (compositing-only properties), accessibility requirements (prefers-reduced-motion), or use outdated JavaScript-heavy approaches.

## When to use this skill

Use for ANY request involving:

- CSS transitions (hover effects, state changes)
- Keyframe animations (@keyframes, animation properties)
- Transform functions (translate, rotate, scale, skew)
- Easing functions (cubic-bezier, steps, linear())
- Scroll-driven animations (animation-timeline, scroll())
- View Transition API
- Performance (will-change, composite layers)
- Accessibility (prefers-reduced-motion)

## Common patterns

### Fade-in transition

```css
.element {
  opacity: 0;
  transition: opacity 0.3s ease;
}

.element.visible {
  opacity: 1;
}
```

### Keyframe animation

```css
@keyframes slide-in {
  from {
    transform: translateX(-100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.animated {
  animation: slide-in 0.5s ease-out forwards;
}
```

### Scroll-driven animation

```css
@keyframes fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.reveal {
  animation: fade-in linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 100%;
}
```

### Respecting motion preferences

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

## How to use

Invoke the `/css` command, passing the user's question or task as the argument:

```
/css <user's question or task>
```

The agent will:
1. Check the user's project context for existing animation patterns
2. Look up current MDN documentation for animation properties
3. Answer with performant, accessible animation patterns
4. Flag browser support for newer features (scroll-driven animations, view transitions)

Animation questions should be delegated to the agent rather than answered from general knowledge — the agent fetches current documentation for more accurate, up-to-date answers.
