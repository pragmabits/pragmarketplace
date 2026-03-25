# Media Queries Quick Reference

## Syntax

```css
@media <type> and (<feature>: <value>) {
  /* styles */
}
```

## Media Types

| Type | Description |
|------|-------------|
| `all` | All devices (default) |
| `screen` | Screens |
| `print` | Print preview / printing |

## Width & Height Features

| Feature | Example | Notes |
|---------|---------|-------|
| `width` | `(width: 768px)` | Exact match (rare) |
| `min-width` | `(min-width: 768px)` | Mobile-first breakpoint |
| `max-width` | `(max-width: 767px)` | Desktop-first breakpoint |
| `height` | `(min-height: 600px)` | Viewport height |

### Range Syntax (Modern)

```css
/* Old */
@media (min-width: 768px) and (max-width: 1023px) { }

/* Modern range syntax */
@media (768px <= width < 1024px) { }
@media (width >= 768px) { }
@media (width < 768px) { }
```

## Common Breakpoints

| Name | Min-Width | Target |
|------|-----------|--------|
| Small phone | 320px | iPhone SE |
| Phone | 375px | Most phones |
| Large phone | 480px | Landscape phones |
| Tablet | 768px | iPad portrait |
| Laptop | 1024px | iPad landscape, small laptops |
| Desktop | 1280px | Standard desktops |
| Wide | 1536px | Large monitors |

### Mobile-First Pattern

```css
/* Base: mobile */
.container { padding: 1rem; }

/* Tablet and up */
@media (min-width: 768px) {
  .container { padding: 2rem; max-width: 720px; }
}

/* Desktop and up */
@media (min-width: 1024px) {
  .container { max-width: 960px; }
}

/* Wide screens */
@media (min-width: 1280px) {
  .container { max-width: 1200px; }
}
```

## User Preference Features

| Feature | Values | Purpose |
|---------|--------|---------|
| `prefers-color-scheme` | `light`, `dark` | Color theme |
| `prefers-reduced-motion` | `no-preference`, `reduce` | Motion sensitivity |
| `prefers-contrast` | `no-preference`, `more`, `less`, `custom` | Contrast needs |
| `prefers-reduced-transparency` | `no-preference`, `reduce` | Transparency issues |
| `forced-colors` | `none`, `active` | High-contrast mode (Windows) |
| `prefers-reduced-data` | `no-preference`, `reduce` | Data saving |

```css
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #1a1a2e;
    --text: #e0e0e0;
  }
}

@media (prefers-reduced-motion: reduce) {
  * { animation-duration: 0.01ms !important; }
}

@media (prefers-contrast: more) {
  :root { --border-color: #000; }
}
```

## Display Features

| Feature | Values | Purpose |
|---------|--------|---------|
| `orientation` | `portrait`, `landscape` | Device orientation |
| `aspect-ratio` | `16/9`, range syntax | Display ratio |
| `resolution` | `2dppx`, `192dpi` | Pixel density |
| `display-mode` | `fullscreen`, `standalone`, `minimal-ui`, `browser` | PWA display |
| `dynamic-range` | `standard`, `high` | HDR capability |

```css
@media (orientation: landscape) and (max-height: 500px) {
  .hero { min-height: auto; }
}

@media (resolution >= 2dppx) {
  .logo { background-image: url('logo@2x.png'); }
}

@media (display-mode: standalone) {
  .install-btn { display: none; }
}
```

## Interaction Features

| Feature | Values | Purpose |
|---------|--------|---------|
| `hover` | `none`, `hover` | Primary input can hover |
| `pointer` | `none`, `coarse`, `fine` | Pointer precision |
| `any-hover` | `none`, `hover` | Any input can hover |
| `any-pointer` | `none`, `coarse`, `fine` | Any pointer precision |

```css
/* Larger touch targets on touch devices */
@media (pointer: coarse) {
  .button { min-height: 44px; min-width: 44px; }
}

/* Hover effects only for hover-capable devices */
@media (hover: hover) {
  .card:hover { transform: translateY(-4px); }
}
```

## Container Queries

```css
/* Define containment context */
.card-wrapper {
  container-type: inline-size;
  container-name: card;
}

/* Query container size */
@container card (min-width: 400px) {
  .card { display: grid; grid-template-columns: 1fr 2fr; }
}

@container card (min-width: 600px) {
  .card { grid-template-columns: 1fr 3fr; }
}

/* Container query units */
.card-title {
  font-size: max(1rem, 3cqi); /* 3% of container inline size */
}
```

### Container Query Units

| Unit | Description |
|------|-------------|
| `cqw` | 1% of container width |
| `cqh` | 1% of container height |
| `cqi` | 1% of container inline size |
| `cqb` | 1% of container block size |
| `cqmin` | Smaller of cqi/cqb |
| `cqmax` | Larger of cqi/cqb |

## Logical Operators

| Operator | Example | Purpose |
|----------|---------|---------|
| `and` | `(min-width: 768px) and (orientation: landscape)` | Both must match |
| `,` (or) | `(max-width: 767px), (orientation: portrait)` | Either matches |
| `not` | `not (hover: hover)` | Negation |
| `only` | `only screen and (...)` | Prevent old browser match |

## @supports (Feature Queries)

```css
@supports (container-type: inline-size) {
  .card-wrapper { container-type: inline-size; }
}

@supports not (container-type: inline-size) {
  /* Fallback styles */
}

@supports selector(:has(*)) {
  /* Use :has() selector */
}
```

## Common Pitfalls

- **Overlapping breakpoints**: `max-width: 768px` and `min-width: 768px` both match at exactly 768px; use range syntax or `max-width: 767.98px`
- **`hover: hover` on touch+mouse**: Laptops with touchscreens match `hover: hover`; use `any-hover` for broader detection
- **Print styles**: Always test print layout; `@media print` often needs `background: white`, visible URLs, no navigation
- **Container query containment**: `container-type: inline-size` creates containment that affects child layout; elements inside can't use percentage heights relative to the container
- **Mobile-first vs desktop-first**: Pick one strategy; mixing causes specificity confusion
