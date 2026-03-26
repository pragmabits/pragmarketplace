# Flexbox Quick Reference

## Container Properties

| Property | Values | Default |
|----------|--------|---------|
| `display` | `flex`, `inline-flex` | — |
| `flex-direction` | `row`, `row-reverse`, `column`, `column-reverse` | `row` |
| `flex-wrap` | `nowrap`, `wrap`, `wrap-reverse` | `nowrap` |
| `justify-content` | `flex-start`, `flex-end`, `center`, `space-between`, `space-around`, `space-evenly` | `flex-start` |
| `align-items` | `stretch`, `flex-start`, `flex-end`, `center`, `baseline` | `stretch` |
| `align-content` | `flex-start`, `flex-end`, `center`, `space-between`, `space-around`, `stretch` | `stretch` |
| `gap` | `<length>` | `0` |
| `row-gap` | `<length>` | `0` |
| `column-gap` | `<length>` | `0` |

## Item Properties

| Property | Values | Default |
|----------|--------|---------|
| `flex` | `<grow> <shrink> <basis>` | `0 1 auto` |
| `flex-grow` | `<number>` | `0` |
| `flex-shrink` | `<number>` | `1` |
| `flex-basis` | `<length>`, `auto`, `content` | `auto` |
| `align-self` | `auto`, `flex-start`, `flex-end`, `center`, `baseline`, `stretch` | `auto` |
| `order` | `<integer>` | `0` |

## Axis Diagram

```
flex-direction: row
┌─────────────────────────────────────┐
│  Main Axis →                        │
│  ┌───┐ ┌───┐ ┌───┐                │
│  │ 1 │ │ 2 │ │ 3 │  ↕ Cross Axis  │
│  └───┘ └───┘ └───┘                │
└─────────────────────────────────────┘

flex-direction: column
┌──────────┐
│ Main Axis│
│    ↓     │
│  ┌───┐   │
│  │ 1 │   │
│  └───┘   │
│  ┌───┐   │
│  │ 2 │ ↔ Cross Axis
│  └───┘   │
│  ┌───┐   │
│  │ 3 │   │
│  └───┘   │
└──────────┘
```

## Common Patterns

### Center everything

```css
.center {
  display: flex;
  justify-content: center;
  align-items: center;
}
```

### Space between with gap

```css
.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}
```

### Wrap with equal-width items

```css
.grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.grid > * {
  flex: 1 1 300px; /* Grow, shrink, min 300px */
}
```

### Push last item to the end

```css
.bar {
  display: flex;
  gap: 1rem;
}

.bar > :last-child {
  margin-inline-start: auto;
}
```

### Sticky footer

```css
body {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
}

main {
  flex: 1; /* Grows to fill space */
}
```

## flex Shorthand

| Shorthand | Equivalent | Use Case |
|-----------|-----------|----------|
| `flex: 1` | `flex: 1 1 0%` | Equal sizing |
| `flex: auto` | `flex: 1 1 auto` | Size by content, grow/shrink |
| `flex: none` | `flex: 0 0 auto` | Fixed size, no flex |
| `flex: 0 1 auto` | Default | Shrink only |

## Common Pitfalls

- **`flex-basis` vs `width`**: `flex-basis` defines initial size along main axis; it overrides `width` in row direction
- **`min-width: auto`**: Flex items won't shrink below content size by default; set `min-width: 0` to allow
- **`gap` vs `margin`**: Prefer `gap` — it only applies between items, not on edges
- **`flex: 1` on images**: Images need `min-width: 0` and `object-fit` to prevent overflow
- **Alignment with wrapping**: `align-content` controls spacing between wrapped rows; `align-items` controls items within each row
