---
name: md3-layout
description: "This skill should be used when the user asks about Material Design 3 layout, \"MD3 responsive layout\", \"MD3 breakpoints\", \"MD3 grid\", \"MD3 window size classes\", \"compact medium expanded\", \"MD3 canonical layouts\", \"list-detail layout\", \"supporting pane\", \"MD3 responsive navigation patterns\", \"Material Design responsive\", \"MD3 columns margins gutters\", \"8dp grid\", or any Material Design 3 responsive design and layout structure question. For responsive navigation switching (which nav component at which breakpoint), not component token styling."
---

This skill provides guidance on Material Design 3 responsive layout system — window size classes, column grids, canonical layouts, and navigation patterns — for framework-agnostic web implementation.

## Design System Detection

Before applying MD3 layout patterns, verify the project uses Material Design 3. Check for `--md-sys-*` tokens, `@material/web` in package.json, or MD3-specific layout classes. If not found, warn the user and offer to adapt guidance to the project's existing layout system.

## Window Size Classes

MD3 defines 5 breakpoints replacing traditional arbitrary pixel values:

| Class | Width | Columns | Margins | Gutters | CSS Media Query |
|---|---|---|---|---|---|
| Compact | 0–599px | 4 | 16px | 8px | Default (mobile-first) |
| Medium | 600–839px | 8 | 24px | 24px | `@media (min-width: 600px)` |
| Expanded | 840–1199px | 12 | 24px | 24px | `@media (min-width: 840px)` |
| Large | 1200–1599px | 12 | 24px | 24px | `@media (min-width: 1200px)` |
| Extra-large | 1600px+ | 12 | 24px | 24px | `@media (min-width: 1600px)` |

### CSS Media Queries

Note: MD3 does not define official breakpoint CSS tokens. Use the literal pixel values from the table above in media queries directly.

## Column Grid System

Based on an **8px baseline grid**:

```css
.md3-grid {
  display: grid;
  gap: 8px;
  grid-template-columns: repeat(4, 1fr);
  padding-inline: 16px;
  max-width: 1440px;
  margin-inline: auto;
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

## Canonical Layouts

MD3 defines four adaptive layout patterns:

### 1. List-Detail

Two-pane master-detail view. Single pane on compact, side-by-side on expanded+.

```css
.list-detail {
  display: grid;
  grid-template-columns: 1fr;
}

@media (min-width: 840px) {
  .list-detail {
    grid-template-columns: 360px 1fr;
    gap: 24px;
  }
}

@media (min-width: 1200px) {
  .list-detail {
    grid-template-columns: 400px 1fr;
  }
}
```

### 2. Supporting Pane

Main content area with an auxiliary side panel.

```css
.supporting-pane {
  display: grid;
  grid-template-columns: 1fr;
}

@media (min-width: 840px) {
  .supporting-pane {
    grid-template-columns: 1fr 360px;
    gap: 24px;
  }
}
```

### 3. Feed

Scrolling content grid that adapts column count.

```css
.feed {
  display: grid;
  grid-template-columns: 1fr;
  gap: 8px;
}

@media (min-width: 600px) {
  .feed {
    grid-template-columns: repeat(2, 1fr);
    gap: 24px;
  }
}

@media (min-width: 1200px) {
  .feed {
    grid-template-columns: repeat(3, 1fr);
  }
}
```

### 4. Hero

Single focused content, full-width on all sizes.

```css
.hero {
  display: grid;
  grid-template-columns: 1fr;
  max-width: 840px;
  margin-inline: auto;
  padding-inline: 16px;
}

@media (min-width: 600px) {
  .hero {
    padding-inline: 24px;
  }
}
```

## Navigation Patterns per Breakpoint

| Breakpoint | Primary Navigation | Secondary |
|---|---|---|
| Compact | Bottom navigation bar | Hamburger → modal drawer |
| Medium | Navigation rail (side) | Modal drawer overlay |
| Expanded | Navigation rail (side) | Persistent drawer |
| Large+ | Persistent navigation drawer | — |

### Navigation Transition Pattern

```css
.nav-rail {
  display: none;
}

.nav-bar {
  display: flex;
  position: fixed;
  inset-inline: 0;
  inset-block-end: 0;
}

@media (min-width: 600px) {
  .nav-bar { display: none; }
  .nav-rail {
    display: flex;
    flex-direction: column;
    position: fixed;
    inset-block: 0;
    inset-inline-start: 0;
    width: 80px;
  }
}

@media (min-width: 1200px) {
  .nav-rail { width: 360px; } /* Expands to drawer */
}
```

## Spacing Scale (8px Grid)

MD3 spacing follows an 8px baseline grid:

| Usage | Values |
|---|---|
| Tight spacing | 4px, 8px |
| Component padding | 12px, 16px, 24px |
| Section spacing | 32px, 40px, 48px |
| Layout spacing | 64px, 80px, 96px, 128px |
| Touch targets | Minimum 48x48px |

## Documentation Resources

Consult `${CLAUDE_PLUGIN_ROOT}/docs/material-design/web/layout-accessibility.md` for full breakpoint tables, grid details, and canonical layout guidance.

### WebSearch Fallback

```
site:m3.material.io foundations/layout <topic>
site:m3.material.io foundations/layout/canonical-layouts
```
