---
name: css-performance
description: "This skill should be used when the user asks about CSS performance, \"paint\", \"layout thrashing\", \"contain\", \"content-visibility\", \"will-change\", \"critical CSS\", \"above-the-fold\", \"render blocking\", \"font-display\", \"preload\", \"reflow\", \"repaint\", \"composite layer\", \"CSS optimization\", or needs help improving stylesheet loading times, reducing layout shifts, or optimizing rendering performance."
---

# CSS Performance

This skill delegates to the `css` agent, which fetches current documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for CSS performance optimization.

## Why this skill matters

CSS performance directly impacts Core Web Vitals (LCP, CLS, INP) and user experience. Poorly optimized CSS causes render-blocking, layout shifts, excessive repaints, and janky animations. Modern CSS offers powerful containment and visibility features that can dramatically improve rendering performance, but misuse of properties like will-change can actually hurt performance. Without consulting documentation, answers may suggest outdated optimization techniques or miss newer APIs like content-visibility and CSS containment.

## When to use this skill

Use for ANY request involving:

- Critical CSS extraction and inline strategies
- Render-blocking stylesheet optimization
- CSS containment (contain property)
- Content-visibility for off-screen content
- will-change usage and misuse
- Reflow/repaint minimization
- Composite layer optimization
- Font loading strategies (font-display)
- Layout shift prevention (CLS)

## Common patterns

### content-visibility for long pages

```css
.below-fold-section {
  content-visibility: auto;
  contain-intrinsic-size: auto 500px;
}
```

### CSS containment

```css
.widget {
  contain: layout style;
}

.isolated-component {
  contain: strict; /* layout + style + paint + size */
}
```

### Font loading strategy

```css
@font-face {
  font-family: 'Custom';
  src: url('/fonts/custom.woff2') format('woff2');
  font-display: swap;
  unicode-range: U+0000-00FF;
}
```

### Preventing layout shifts

```css
img, video {
  max-width: 100%;
  height: auto;
  aspect-ratio: 16 / 9;
}

@keyframes shimmer {
  to { background-position: -200% 0; }
}

.skeleton {
  min-height: 200px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
```

## How to use

Invoke the `/css` command, passing the user's question or task as the argument:

```
/css <user's question or task>
```

The agent will:
1. Check the user's project context for build tools and CSS loading strategy
2. Look up current MDN documentation for performance APIs
3. Recommend measurable optimizations backed by documentation
4. Flag tradeoffs (e.g., content-visibility breaking find-in-page, will-change memory cost)

Performance questions should be delegated to the agent rather than answered from general knowledge — the agent fetches current documentation for more accurate, up-to-date answers.
