# Material Design 3 — Layout & Accessibility Quick Reference

## Responsive Layout

> Official docs: [m3.material.io/foundations/layout](https://m3.material.io/foundations/layout/understanding-layout/overview)

### Window Size Classes

| Class | Width Range | Columns | Margins | Gutters |
|---|---|---|---|---|
| Compact | 0–599px | 4 | 16px | 8px |
| Medium | 600–839px | 8 | 24px | 24px |
| Expanded | 840–1199px | 12 | 24px | 24px |
| Large | 1200–1599px | 12 | 24px | 24px |
| Extra-large | 1600px+ | 12 | 24px | 24px |

### Grid System

- Based on an **8px baseline grid**
- Margins and gutters: 8, 16, 24, or 40px
- Content max-width: typically 1440px on extra-large screens

### CSS Breakpoints

```css
/* MD3 Window Size Classes as CSS media queries */
/* Compact: default (mobile-first) */
/* Medium */
@media (min-width: 600px) { }
/* Expanded */
@media (min-width: 840px) { }
/* Large */
@media (min-width: 1200px) { }
/* Extra-large */
@media (min-width: 1600px) { }
```

### Canonical Layouts

MD3 defines four adaptive layout patterns:

| Layout | Description | Breakpoint Behavior |
|---|---|---|
| **List-detail** | Master list + detail pane | Single pane on compact, side-by-side on expanded+ |
| **Supporting pane** | Main content + auxiliary panel | Panel hidden/overlay on compact, visible on expanded+ |
| **Feed** | Scrolling content grid | 1 column compact, 2-3 columns expanded+ |
| **Hero** | Single focused content area | Full-width on all sizes, content scales |

### Grid CSS Pattern

```css
.md3-grid {
  display: grid;
  gap: 8px;                               /* Compact gutter */
  grid-template-columns: repeat(4, 1fr);   /* Compact: 4 columns */
  padding-inline: 16px;                    /* Compact margin */
}

@media (min-width: 600px) {
  .md3-grid {
    gap: 24px;
    grid-template-columns: repeat(8, 1fr);
    padding-inline: 24px;
  }
}

@media (min-width: 840px) {
  .md3-grid {
    grid-template-columns: repeat(12, 1fr);
  }
}
```

### Spacing Scale (8px grid)

| Token Pattern | Values |
|---|---|
| Spacing increments | 4, 8, 12, 16, 24, 32, 40, 48, 64, 80, 96, 128px |
| Touch targets | Minimum 48x48px |
| Icon sizes | 18, 20, 24, 36, 40, 48px |

---

## Accessible Design

> Official docs: [m3.material.io/foundations/accessible-design](https://m3.material.io/foundations/accessible-design/overview)

### Color Contrast

| Content Type | Minimum Ratio (WCAG AA) |
|---|---|
| Normal text (<18px regular, <14px bold) | 4.5:1 |
| Large text (>=18px regular, >=14px bold) | 3:1 |
| UI components and graphics | 3:1 |
| Focus indicators | 3:1 against adjacent colors |

MD3's `on-*` tokens are designed to meet these ratios automatically against their paired surface.

### Touch Targets

- Minimum interactive area: **48 x 48px** (approximately 9mm physical)
- Visual element can be smaller (e.g., 24x24px icon) but total clickable area must reach 48px
- Use padding to extend touch targets beyond visual bounds

```css
.icon-button {
  /* Visual: 24x24 icon */
  width: 24px;
  height: 24px;
  /* Touch target: 48x48 via padding */
  padding: 12px;
  /* Or use min-width/min-height */
  min-width: 48px;
  min-height: 48px;
}
```

### Focus Indicators

- Visible focus ring with at least 3:1 contrast ratio
- Use `--md-sys-color-secondary` or a high-contrast outline
- Never remove focus outlines without providing an alternative

```css
:focus-visible {
  outline: 2px solid var(--md-sys-color-secondary);
  outline-offset: 2px;
}
```

### Motion Accessibility

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

### Text Scaling

- Support text scaling up to at least 200%
- Use `rem` units for font sizes (not `px`)
- Ensure layouts reflow gracefully at larger text sizes
- Do not use `max-height` with `overflow: hidden` on text containers

### State Layers

MD3 uses semi-transparent overlays for interactive states:

| State | Opacity |
|---|---|
| Hover | 8% of content color |
| Focus | 10% of content color |
| Pressed | 10% of content color |
| Dragged | 16% of content color |
| Disabled container | 12% of on-surface |
| Disabled content | 38% of on-surface |

```css
.interactive-element {
  position: relative;
}

.interactive-element::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background-color: var(--md-sys-color-on-surface);
  opacity: 0;
  transition: opacity 150ms;
  pointer-events: none;
}

.interactive-element:hover::before {
  opacity: 0.08;
}

.interactive-element:focus-visible::before {
  opacity: 0.1;
}

.interactive-element:active::before {
  opacity: 0.1;
}
```

## Design Token Architecture

> Official docs: [m3.material.io/foundations/design-tokens](https://m3.material.io/foundations/design-tokens/overview)

### Three-Tier Token System

| Tier | Prefix | Description | Example |
|---|---|---|---|
| Reference | `--md-ref-*` | Raw concrete values (hex, px, font names) | `--md-ref-typeface-brand: 'Google Sans'` |
| System | `--md-sys-*` | Semantic roles and decisions | `--md-sys-color-primary: #6750A4` |
| Component | `--md-comp-*` | Element-specific attributes | `--md-comp-filled-button-container-color` |

### Token Resolution Chain

```
Component Token → System Token → Reference Token → Concrete Value

--md-comp-filled-button-container-color
  → --md-sys-color-primary
    → --md-ref-palette-primary40
      → #6750A4
```

### Applying Themes via CSS Scope

```css
/* Global theme */
:root {
  --md-sys-color-primary: #6750A4;
}

/* Scoped theme override */
.brand-section {
  --md-sys-color-primary: #006D3B;
}

/* Component-level override */
.special-button {
  --md-comp-filled-button-container-color: #FF5722;
}
```
