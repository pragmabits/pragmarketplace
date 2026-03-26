---
name: css-selectors
description: "This skill should be used when the user asks about CSS selectors, \"specificity\", \":has()\", \":is()\", \":where()\", \":not()\", \"pseudo-class\", \"pseudo-element\", \"::before\", \"::after\", \"nth-child\", \"combinators\", \"cascade\", \"@layer\", \"cascade layers\", \"custom properties\", \"var()\", \"CSS variables\", \":focus-visible\", \"selector specificity\", or needs help understanding how CSS selectors work, calculating specificity, or organizing stylesheets with cascade layers."
---

# CSS Selectors & Cascade

This skill delegates to the `css` agent, which fetches current documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for CSS selectors, specificity, and cascade management.

## Why this skill matters

The CSS cascade, specificity, and modern selector features like :has(), :is(), :where(), and @layer fundamentally changed how stylesheets are organized. Cascade layers (@layer) provide explicit control over specificity ordering, while :has() enables parent selection that was previously impossible without JavaScript. Without consulting documentation, answers may miss zero-specificity selectors (:where()), incorrect specificity calculations, or the power of cascade layers for managing third-party CSS conflicts.

## When to use this skill

Use for ANY request involving:

- Selector syntax (combinators, attribute selectors, pseudo-classes)
- Specificity calculation and conflicts
- Modern selectors (:has(), :is(), :where(), :not())
- Pseudo-elements (::before, ::after, ::marker, ::placeholder)
- Cascade layers (@layer)
- Custom properties (CSS variables, var(), fallbacks)
- :focus-visible vs :focus
- :nth-child() and :nth-of-type() patterns

## Common patterns

### :has() parent selector

```css
/* Style a card that contains an image */
.card:has(img) {
  padding: 0;
}

/* Style a form group with an invalid input */
.form-group:has(:invalid) {
  border-color: red;
}
```

### Cascade layers for specificity control

```css
@layer reset, base, components, utilities;

@layer reset {
  * { margin: 0; padding: 0; box-sizing: border-box; }
}

@layer components {
  .button { padding: 0.5em 1em; }
}

@layer utilities {
  .hidden { display: none; }
}
```

### Custom properties with fallbacks

```css
:root {
  --color-primary: #3b82f6;
  --spacing-md: 1rem;
  --radius-md: 0.5rem;
}

.button {
  background: var(--color-primary, #0066cc);
  padding: var(--spacing-md);
  border-radius: var(--radius-md);
}
```

### :is() and :where() grouping

```css
/* :is() — takes highest specificity of its arguments */
:is(h1, h2, h3) { line-height: 1.2; }

/* :where() — zero specificity, easily overridable */
:where(h1, h2, h3) { margin-block: 0.5em; }
```

## How to use

Invoke the `/css` command, passing the user's question or task as the argument:

```
/css <user's question or task>
```

The agent will:
1. Check the user's project context for CSS methodology (BEM, Modules, utility-first)
2. Look up current MDN documentation for selectors and specificity
3. Recommend modern cascade management techniques where appropriate
4. Flag browser support for newer selectors (:has(), @layer)

Selector and cascade questions should be delegated to the agent rather than answered from general knowledge — the agent fetches current documentation for more accurate, up-to-date answers.
