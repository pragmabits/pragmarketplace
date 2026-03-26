---
name: md3-components
description: "This skill should be used when the user asks about Material Design 3 component token styling, \"MD3 buttons\", \"MD3 cards\", \"MD3 FAB\", \"MD3 chips\", \"MD3 dialog\", \"MD3 text field\", \"MD3 app bar\", \"MD3 bottom sheet\", \"--md-comp-*\", \"md-filled-button\", \"MD3 state layers\", \"MD3 disabled state\", or any MD3 component implementation pattern. Covers component token mapping, state layers, and applying system tokens to custom components."
---

This skill provides token-level guidance for implementing Material Design 3 component patterns using CSS custom properties. It focuses on how system tokens map to components — not full component implementations, which are framework-specific.

## Design System Detection

Before applying MD3 component patterns, verify the project uses MD3. Check for `--md-sys-*` tokens, `@material/web` in package.json, `md-*` custom elements, or `@angular/material` with M3 theme. If not found, warn the user and offer alternatives.

## Component Token Pattern

MD3 components consume system tokens through component-level tokens:

```css
/* System tokens define the palette */
:root {
  --md-sys-color-primary: #6750A4;
  --md-sys-color-on-primary: #FFFFFF;
  --md-sys-shape-corner-full: 9999px;
}

/* Component tokens map system tokens to specific parts */
md-filled-button,
.md3-filled-button {
  --md-comp-filled-button-container-color: var(--md-sys-color-primary);
  --md-comp-filled-button-label-text-color: var(--md-sys-color-on-primary);
  --md-comp-filled-button-container-shape: var(--md-sys-shape-corner-full);
}
```

## Component Categories & Token Mapping

### Buttons

| Variant | Container Color | Label Color | Shape |
|---|---|---|---|
| Filled | `primary` | `on-primary` | `corner-full` |
| Filled tonal | `secondary-container` | `on-secondary-container` | `corner-full` |
| Outlined | `transparent` | `primary` | `corner-full` |
| Elevated | `surface-container-low` | `primary` | `corner-full` |
| Text | `transparent` | `primary` | `corner-full` |

### Cards

| Variant | Container Color | Shape | Elevation |
|---|---|---|---|
| Elevated | `surface-container-low` | `corner-medium` | Level 1 |
| Filled | `surface-container-highest` | `corner-medium` | Level 0 |
| Outlined | `surface` + outline border | `corner-medium` | Level 0 |

### FAB (Floating Action Button)

| Variant | Container Color | Icon Color | Shape |
|---|---|---|---|
| FAB | `primary-container` | `on-primary-container` | `corner-large` |
| Small FAB | `primary-container` | `on-primary-container` | `corner-medium` |
| Large FAB | `primary-container` | `on-primary-container` | `corner-extra-large` |

### Text Fields

| Variant | Container Color | Label Color | Shape |
|---|---|---|---|
| Filled | `surface-container-highest` | `on-surface-variant` | top corners `corner-extra-small` |
| Outlined | `transparent` + outline | `on-surface-variant` | `corner-extra-small` |

### Navigation

| Component | Container | Active Indicator | Shape |
|---|---|---|---|
| Navigation bar | `surface-container` | `secondary-container` | `corner-full` indicator |
| Navigation rail | `surface` | `secondary-container` | `corner-full` indicator |
| Navigation drawer | `surface-container-low` | `secondary-container` | `corner-full` indicator |

## State Layers

All interactive MD3 components use semi-transparent overlays for feedback:

| State | Opacity | Color Source |
|---|---|---|
| Hover | 8% | Content color (`on-*` token) |
| Focus | 10% | Content color |
| Pressed | 10% | Content color |
| Dragged | 16% | Content color |

### CSS State Layer Pattern

```css
.md3-interactive {
  position: relative;
  overflow: hidden;
}

.md3-interactive::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  background-color: currentColor; /* Inherits the content color */
  opacity: 0;
  transition: opacity var(--md-sys-motion-duration-short3, 150ms)
              var(--md-sys-motion-easing-standard, cubic-bezier(0.2, 0, 0, 1));
  pointer-events: none;
}

.md3-interactive:hover::before { opacity: 0.08; }
.md3-interactive:focus-visible::before { opacity: 0.1; }
.md3-interactive:active::before { opacity: 0.1; }
```

## Disabled States

| Property | Value |
|---|---|
| Container opacity | 12% of `on-surface` |
| Content opacity | 38% of `on-surface` |
| No elevation | Level 0 |
| No state layer | No hover/focus/press feedback |

```css
.md3-component:disabled,
.md3-component[aria-disabled="true"] {
  opacity: 1; /* Don't use whole-element opacity */
  pointer-events: none;
}

.md3-component:disabled .container {
  background-color: color-mix(in srgb, var(--md-sys-color-on-surface) 12%, transparent);
}

.md3-component:disabled .label {
  color: color-mix(in srgb, var(--md-sys-color-on-surface) 38%, transparent);
}
```

## Applying MD3 Tokens to Custom Components

To style a custom component following MD3:

1. Choose the appropriate system tokens for each part (container, content, icon)
2. Apply shape tokens for border-radius
3. Use elevation tokens for depth
4. Add state layers for interactivity
5. Handle disabled state with opacity patterns above

```css
.custom-card {
  background-color: var(--md-sys-color-surface-container-low);
  color: var(--md-sys-color-on-surface);
  border-radius: var(--md-sys-shape-corner-medium);
  box-shadow: var(--md-sys-elevation-level1);
  padding: 16px;
}

.custom-card .title {
  font-family: var(--md-sys-typescale-title-medium-font);
  font-size: var(--md-sys-typescale-title-medium-size);
  line-height: var(--md-sys-typescale-title-medium-line-height);
  font-weight: var(--md-sys-typescale-title-medium-weight);
  letter-spacing: var(--md-sys-typescale-title-medium-tracking);
  color: var(--md-sys-color-on-surface);
}

.custom-card .body {
  font-family: var(--md-sys-typescale-body-medium-font);
  font-size: var(--md-sys-typescale-body-medium-size);
  line-height: var(--md-sys-typescale-body-medium-line-height);
  color: var(--md-sys-color-on-surface-variant);
}
```

## Documentation Resources

Consult bundled docs at `${CLAUDE_PLUGIN_ROOT}/docs/material-design/web/` for exact token values. For component-specific token lists, search the `@material/web` source on GitHub: `github.com/material-components/material-web/tree/main/tokens`.

### WebSearch Fallback

```
site:material-web.dev components/<component-name>
site:m3.material.io components/<component-name>
```
