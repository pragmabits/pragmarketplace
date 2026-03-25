# CSS Grid Quick Reference

## Container Properties

| Property | Values | Default |
|----------|--------|---------|
| `display` | `grid`, `inline-grid` | — |
| `grid-template-columns` | `<track-list>` | `none` |
| `grid-template-rows` | `<track-list>` | `none` |
| `grid-template-areas` | `"<string>"` | `none` |
| `grid-template` | `<rows> / <columns>` | — |
| `gap` | `<row-gap> <col-gap>` | `0` |
| `justify-items` | `start`, `end`, `center`, `stretch` | `stretch` |
| `align-items` | `start`, `end`, `center`, `stretch` | `stretch` |
| `place-items` | `<align> <justify>` | — |
| `justify-content` | `start`, `end`, `center`, `space-between`, `space-around`, `space-evenly` | `start` |
| `align-content` | Same as justify-content | `start` |
| `place-content` | `<align> <justify>` | — |
| `grid-auto-columns` | `<track-size>` | `auto` |
| `grid-auto-rows` | `<track-size>` | `auto` |
| `grid-auto-flow` | `row`, `column`, `dense` | `row` |

## Item Properties

| Property | Values |
|----------|--------|
| `grid-column` | `<start> / <end>` |
| `grid-row` | `<start> / <end>` |
| `grid-area` | `<name>` or `<row-start> / <col-start> / <row-end> / <col-end>` |
| `justify-self` | `start`, `end`, `center`, `stretch` |
| `align-self` | `start`, `end`, `center`, `stretch` |
| `place-self` | `<align> <justify>` |

## Track Sizing Functions

| Function | Example | Purpose |
|----------|---------|---------|
| `fr` | `1fr 2fr` | Fractional unit |
| `minmax()` | `minmax(200px, 1fr)` | Min/max constraint |
| `repeat()` | `repeat(3, 1fr)` | Repeat tracks |
| `auto-fill` | `repeat(auto-fill, minmax(250px, 1fr))` | Fill with tracks |
| `auto-fit` | `repeat(auto-fit, minmax(250px, 1fr))` | Fit to content |
| `min-content` | `min-content` | Smallest without overflow |
| `max-content` | `max-content` | Widest without wrapping |
| `fit-content()` | `fit-content(300px)` | Clamp to max |

## Grid Area Diagram

```
grid-template-areas:
  "header  header  header"
  "sidebar main    aside"
  "footer  footer  footer";

┌────────────────────────────────┐
│          header                │
├────────┬───────────┬──────────┤
│sidebar │   main    │  aside   │
│        │           │          │
├────────┴───────────┴──────────┤
│          footer                │
└────────────────────────────────┘
```

## auto-fill vs auto-fit

```
Container: 900px wide, items: minmax(200px, 1fr)

auto-fill: Creates tracks even if empty
┌──────┐┌──────┐┌──────┐┌──────┐
│ Item ││ Item ││      ││      │  ← Empty tracks preserved
└──────┘└──────┘└──────┘└──────┘

auto-fit: Collapses empty tracks
┌───────────┐┌───────────┐
│   Item    ││   Item    │  ← Items stretch to fill
└───────────┘└───────────┘
```

## Common Patterns

### Responsive card grid

```css
.cards {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(300px, 100%), 1fr));
  gap: 1.5rem;
}
```

### Holy Grail layout

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

.header { grid-area: header; }
.nav    { grid-area: nav; }
.main   { grid-area: main; }
.aside  { grid-area: aside; }
.footer { grid-area: footer; }
```

### 12-column system

```css
.grid { display: grid; grid-template-columns: repeat(12, 1fr); gap: 1rem; }
.col-1  { grid-column: span 1; }
.col-2  { grid-column: span 2; }
.col-3  { grid-column: span 3; }
.col-4  { grid-column: span 4; }
.col-6  { grid-column: span 6; }
.col-12 { grid-column: span 12; }
```

### Subgrid

```css
.parent {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.child {
  grid-column: span 3;
  display: grid;
  grid-template-columns: subgrid; /* Inherits parent columns */
}
```

### Masonry-like with auto-flow dense

```css
.masonry {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  grid-auto-rows: 100px;
  grid-auto-flow: dense;
  gap: 1rem;
}

.tall { grid-row: span 2; }
.wide { grid-column: span 2; }
```

## Common Pitfalls

- **`auto-fill` vs `auto-fit`**: `auto-fill` keeps empty tracks; `auto-fit` collapses them — use `auto-fit` for responsive stretching
- **`1fr` and `min-content`**: `1fr` minimum is `min-content` by default; use `minmax(0, 1fr)` to allow items to shrink below content
- **Subgrid support**: Available in all modern browsers (2023+); check if your baseline supports it
- **`gap` not `grid-gap`**: `grid-gap` is the old name, now deprecated; use `gap`
- **Implicit vs explicit**: Items placed beyond `grid-template` create implicit tracks sized by `grid-auto-rows`/`grid-auto-columns`
