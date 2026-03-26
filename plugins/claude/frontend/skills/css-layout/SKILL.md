---
name: css-layout
description: "This skill should be used when the user asks about CSS layout techniques, \"flexbox\", \"CSS Grid\", \"display flex\", \"justify-content\", \"align-items\", \"gap\", \"grid-template\", \"place-items\", \"centering\", \"center a div\", \"layout\", \"box model\", \"position\", \"z-index\", \"stacking context\", \"float\", \"columns\", \"container queries\", \"@container\", or needs help building page layouts, aligning elements, understanding CSS positioning, or debugging layout bugs and unexpected element placement."
---

# CSS Layout

This skill delegates to the `css` agent, which fetches current documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for CSS layout techniques.

## Why this skill matters

CSS layout is one of the most complex areas of web development, with multiple competing systems (Flexbox, Grid, positioning, floats) that each have specific use cases. Modern CSS has introduced powerful new features like container queries and subgrid that change layout best practices. Without consulting documentation, answers may use outdated patterns (float-based layouts, clearfix hacks) or miss modern alternatives (gap instead of margins, place-items shorthand, container queries).

## When to use this skill

Use for ANY request involving:

- Flexbox alignment and distribution (justify-content, align-items, flex-wrap)
- CSS Grid layout (grid-template, grid-area, subgrid, auto-fill/auto-fit)
- Centering elements (horizontal, vertical, both)
- Positioning (relative, absolute, fixed, sticky)
- Z-index and stacking contexts
- Box model (margin, padding, border-box)
- Container queries (@container)
- Multi-column layouts

## Common patterns

### Flexbox centering

```css
.centered {
  display: flex;
  justify-content: center;
  align-items: center;
}
```

### CSS Grid 12-column layout

```css
.grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 1rem;
}

.span-6 {
  grid-column: span 6;
}
```

### Holy Grail layout with Grid

```css
.layout {
  display: grid;
  grid-template:
    "header header header" auto
    "nav    main   aside"  1fr
    "footer footer footer" auto
    / 200px 1fr    200px;
  min-height: 100dvh;
}
```

### Container queries

```css
.card-container {
  container-type: inline-size;
  container-name: card;
}

@container card (min-width: 400px) {
  .card {
    display: grid;
    grid-template-columns: 1fr 2fr;
  }
}
```

## How to use

Invoke the `/css` command, passing the user's question or task as the argument:

```
/css <user's question or task>
```

The agent will:
1. Check the user's project context (existing CSS methodology, framework)
2. Look up current MDN documentation for layout properties
3. Answer with modern, standards-compliant patterns
4. Flag browser compatibility concerns for newer features (subgrid, container queries)

Layout questions should be delegated to the agent rather than answered from general knowledge — the agent fetches current documentation for more accurate, up-to-date answers.
