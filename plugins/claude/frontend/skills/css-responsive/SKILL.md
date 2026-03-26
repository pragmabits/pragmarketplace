---
name: css-responsive
description: "This skill should be used when the user asks about responsive design, \"media query\", \"@media\", \"breakpoint\", \"mobile-first\", \"viewport\", \"clamp()\", \"min()\", \"max()\", \"fluid typography\", \"aspect-ratio\", \"responsive images\", \"container query\", \"responsive grid\", \"responsive layout\", or needs help making pages adapt to different screen sizes and devices."
---

# CSS Responsive Design

This skill delegates to the `css` agent, which fetches current documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for responsive design techniques.

## Why this skill matters

Responsive design has evolved significantly beyond simple media queries. Modern CSS offers fluid sizing with clamp()/min()/max(), container queries for component-level responsiveness, and intrinsic sizing that reduces the need for breakpoints entirely. Without consulting documentation, answers may rely on outdated fixed-breakpoint approaches when intrinsic design patterns or container queries would be more maintainable.

## When to use this skill

Use for ANY request involving:

- Media queries (@media, breakpoints, mobile-first)
- Fluid sizing (clamp(), min(), max())
- Fluid typography
- Viewport units (vw, vh, dvh, svh, lvh)
- Container queries for component responsiveness
- Responsive images (srcset, sizes, object-fit)
- Aspect ratio (aspect-ratio property)
- Responsive grid/flexbox patterns

## Common patterns

### Mobile-first breakpoints

```css
/* Base: mobile */
.container { padding: 1rem; }

/* Tablet */
@media (min-width: 768px) {
  .container { padding: 2rem; }
}

/* Desktop */
@media (min-width: 1024px) {
  .container { max-width: 1200px; margin-inline: auto; }
}
```

### Fluid typography with clamp()

```css
h1 {
  /* Min 1.5rem, preferred 4vw, max 3rem */
  font-size: clamp(1.5rem, 1rem + 2vw, 3rem);
}

p {
  font-size: clamp(1rem, 0.875rem + 0.5vw, 1.25rem);
}
```

### Responsive grid with auto-fit

```css
.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(300px, 100%), 1fr));
  gap: 1.5rem;
}
```

### Container queries for components

```css
.card-wrapper {
  container-type: inline-size;
}

.card {
  display: flex;
  flex-direction: column;
}

@container (min-width: 500px) {
  .card {
    flex-direction: row;
  }
}
```

## How to use

Invoke the `/css` command, passing the user's question or task as the argument:

```
/css <user's question or task>
```

The agent will:
1. Check the user's project context for existing breakpoints and responsive patterns
2. Look up current MDN documentation for responsive features
3. Recommend modern approaches (fluid design, container queries) where appropriate
4. Flag browser support for newer features (container queries, new viewport units)

Responsive design questions should be delegated to the agent rather than answered from general knowledge — the agent fetches current documentation for more accurate, up-to-date answers.
