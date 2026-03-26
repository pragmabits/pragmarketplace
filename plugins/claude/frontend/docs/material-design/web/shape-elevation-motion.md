# Material Design 3 — Shape, Elevation & Motion Quick Reference

## Shape System

> Official docs: [m3.material.io/styles/shape](https://m3.material.io/styles/shape/overview)

### Shape Scale Tokens

| Token | Default Value | Typical Usage |
|---|---|---|
| `--md-sys-shape-corner-none` | 0px | Full-bleed images, backgrounds |
| `--md-sys-shape-corner-extra-small` | 4px | Chips, small controls |
| `--md-sys-shape-corner-small` | 8px | Text fields, menus |
| `--md-sys-shape-corner-medium` | 12px | Cards, dialogs |
| `--md-sys-shape-corner-large` | 16px | FAB, navigation drawers |
| `--md-sys-shape-corner-extra-large` | 28px | Large sheets, expanded FAB |
| `--md-sys-shape-corner-full` | 9999px | Pills, circular buttons |

### Top-Only Variants

Some components use top-only rounding (e.g., bottom sheets):

```css
.bottom-sheet {
  border-radius: var(--md-sys-shape-corner-extra-large) var(--md-sys-shape-corner-extra-large) 0 0;
}
```

### CSS Usage

```css
:root {
  --md-sys-shape-corner-none: 0px;
  --md-sys-shape-corner-extra-small: 4px;
  --md-sys-shape-corner-small: 8px;
  --md-sys-shape-corner-medium: 12px;
  --md-sys-shape-corner-large: 16px;
  --md-sys-shape-corner-extra-large: 28px;
  --md-sys-shape-corner-full: 9999px;
}

.card {
  border-radius: var(--md-sys-shape-corner-medium);
}
```

---

## Elevation System

> Official docs: [m3.material.io/styles/elevation](https://m3.material.io/styles/elevation/overview)

### Elevation Levels

| Level | dp | Surface Tint Opacity | Usage |
|---|---|---|---|
| 0 | 0dp | 0% | Filled buttons, outlined cards |
| 1 | 1dp | 5% | Elevated cards, navigation drawer, top app bar (scrolled) |
| 2 | 3dp | 8% | Tonal/elevated buttons, navigation bar, bottom app bar |
| 3 | 6dp | 11% | FAB, dialogs, search bar, modal bottom sheets |
| 4 | 8dp | 12% | Hover states |
| 5 | 12dp | 14% | Drag states |

### Two Elevation Methods

1. **Tonal elevation** (primary in MD3): Surface tint color overlay from `--md-sys-color-surface-tint`
2. **Shadow elevation**: Traditional drop shadows

### Box-Shadow CSS Values

```css
:root {
  --md-sys-elevation-level0: none;
  --md-sys-elevation-level1: 0 1px 2px 0 rgba(0,0,0,0.3), 0 1px 3px 1px rgba(0,0,0,0.15);
  --md-sys-elevation-level2: 0 1px 2px 0 rgba(0,0,0,0.3), 0 2px 6px 2px rgba(0,0,0,0.15);
  --md-sys-elevation-level3: 0 4px 8px 3px rgba(0,0,0,0.15), 0 1px 3px 0 rgba(0,0,0,0.3);
  --md-sys-elevation-level4: 0 6px 10px 4px rgba(0,0,0,0.15), 0 2px 3px 0 rgba(0,0,0,0.3);
  --md-sys-elevation-level5: 0 8px 12px 6px rgba(0,0,0,0.15), 0 4px 4px 0 rgba(0,0,0,0.3);
}
```

### Tonal Elevation with Surface Tint

```css
/* Surface tint overlay for tonal elevation */
.elevated-surface {
  background-color: var(--md-sys-color-surface);
  position: relative;
}

.elevated-surface::after {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background-color: var(--md-sys-color-surface-tint);
  opacity: 0.05; /* Level 1 = 5% */
  pointer-events: none;
}
```

---

## Motion System

> Official docs: [m3.material.io/styles/motion](https://m3.material.io/styles/motion/overview)

### Easing Tokens

| Token | CSS cubic-bezier | Use |
|---|---|---|
| `--md-sys-motion-easing-standard` | `cubic-bezier(0.2, 0, 0, 1)` | Default transitions |
| `--md-sys-motion-easing-standard-decelerate` | `cubic-bezier(0, 0, 0, 1)` | Elements entering |
| `--md-sys-motion-easing-standard-accelerate` | `cubic-bezier(0.3, 0, 1, 1)` | Elements exiting |
| `--md-sys-motion-easing-emphasized` | `cubic-bezier(0.2, 0, 0, 1)` | High-emphasis primary transitions |
| `--md-sys-motion-easing-emphasized-decelerate` | `cubic-bezier(0.05, 0.7, 0.1, 1)` | Incoming emphasized elements |
| `--md-sys-motion-easing-emphasized-accelerate` | `cubic-bezier(0.3, 0, 0.8, 0.15)` | Outgoing emphasized elements |
| `--md-sys-motion-easing-linear` | `cubic-bezier(0, 0, 1, 1)` | Color fades, progress indicators |

### Duration Tokens

| Token | Value | Use |
|---|---|---|
| `--md-sys-motion-duration-short1` | 50ms | Micro-interactions (ripple start) |
| `--md-sys-motion-duration-short2` | 100ms | Quick feedback (icon toggle) |
| `--md-sys-motion-duration-short3` | 150ms | Small element transitions |
| `--md-sys-motion-duration-short4` | 200ms | Small to medium transitions |
| `--md-sys-motion-duration-medium1` | 250ms | Medium element transitions |
| `--md-sys-motion-duration-medium2` | 300ms | Default component transitions |
| `--md-sys-motion-duration-medium3` | 350ms | Moderate complexity |
| `--md-sys-motion-duration-medium4` | 400ms | Medium to large transitions |
| `--md-sys-motion-duration-long1` | 450ms | Large element transitions |
| `--md-sys-motion-duration-long2` | 500ms | Complex layout changes |
| `--md-sys-motion-duration-long3` | 550ms | Full-screen transitions |
| `--md-sys-motion-duration-long4` | 600ms | Complex full-screen transitions |
| `--md-sys-motion-duration-extra-long1` | 700ms | Page-level transitions |
| `--md-sys-motion-duration-extra-long2` | 800ms | Complex page transitions |
| `--md-sys-motion-duration-extra-long3` | 900ms | Multi-element orchestrations |
| `--md-sys-motion-duration-extra-long4` | 1000ms | Maximum duration transitions |

### CSS Usage

```css
:root {
  --md-sys-motion-easing-standard: cubic-bezier(0.2, 0, 0, 1);
  --md-sys-motion-easing-emphasized-decelerate: cubic-bezier(0.05, 0.7, 0.1, 1);
  --md-sys-motion-easing-emphasized-accelerate: cubic-bezier(0.3, 0, 0.8, 0.15);
  --md-sys-motion-duration-medium2: 300ms;
}

.card {
  transition: transform var(--md-sys-motion-duration-medium2) var(--md-sys-motion-easing-standard),
              opacity var(--md-sys-motion-duration-short4) var(--md-sys-motion-easing-standard);
}

/* Enter animation */
.dialog-enter {
  animation: dialog-in var(--md-sys-motion-duration-medium2) var(--md-sys-motion-easing-emphasized-decelerate);
}

/* Exit animation */
.dialog-exit {
  animation: dialog-out var(--md-sys-motion-duration-short4) var(--md-sys-motion-easing-emphasized-accelerate);
}

/* Respect user preferences */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```
