# Layering Text & Counters

Source: https://docs.fontawesome.com/web/style/layer

Layers are a more flexible alternative to stacking. They let you combine icons, text, and counters in a single container.

> **Important:** Layers work fully with the **SVG+JS** version of FontAwesome. With the **Web Fonts + CSS** version, layers have **limited support** — basic layering works but `data-fa-transform` and `fa-layers-counter`/`fa-layers-text` require the JavaScript framework. For CSS-only setups, **stacking** (`fa-stack`) is the more reliable approach.

## Key Classes

| Class | Purpose |
|-------|---------|
| `fa-layers` | Container for layered icons |
| `fa-layers-counter` | Positions a counter badge (top-right by default) |
| `fa-layers-text` | Positions text over the icon |
| `fa-layers-bottom-left` | Positions element at bottom-left |
| `fa-layers-bottom-right` | Positions element at bottom-right |
| `fa-layers-top-left` | Positions element at top-left |
| `fa-layers-top-right` | Positions element at top-right |

> **Important:** `fa-fw` (fixed width) is strongly recommended on the `fa-layers` container to ensure consistent sizing.

## Basic Structure

```html
<span class="fa-layers fa-fw">
  <i class="fa-solid fa-circle"></i>
  <i class="fa-solid fa-check fa-inverse" data-fa-transform="shrink-6"></i>
</span>
```

## Examples (SVG+JS)

### Counter Badge

```html
<span class="fa-layers fa-fw" style="font-size: 3em;">
  <i class="fa-solid fa-envelope"></i>
  <span class="fa-layers-counter" style="background: tomato;">1,419</span>
</span>
```

### Text on Icon

```html
<span class="fa-layers fa-fw" style="font-size: 3em;">
  <i class="fa-solid fa-certificate"></i>
  <span class="fa-layers-text fa-inverse" data-fa-transform="shrink-11.5 rotate--30"
        style="font-weight: 900;">NEW</span>
</span>
```
