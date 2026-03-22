# Duotone Icons

Source: https://docs.fontawesome.com/web/style/duotone

Duotone icons have two layers (primary and secondary) that can be styled independently.

> **Important:** Duotone icons are a **FontAwesome Pro** feature. They are not available in the free set.

## Style Prefix

`fa-duotone` (also `fa-duotone fa-solid`, `fa-duotone fa-regular` in newer versions)

```html
<i class="fa-duotone fa-solid fa-camera"></i>
```

## CSS Custom Properties

| Property | Default | Purpose |
|----------|---------|---------|
| `--fa-primary-color` | currentColor | Primary layer color |
| `--fa-secondary-color` | currentColor | Secondary layer color |
| `--fa-primary-opacity` | 1 | Primary layer opacity |
| `--fa-secondary-opacity` | 0.4 | Secondary layer opacity |

## Swap Opacity

| Class | Effect |
|-------|--------|
| `fa-swap-opacity` | Swaps primary/secondary opacity values |

## Examples

```html
<!-- Swap opacity (make secondary layer dominant) -->
<i class="fa-duotone fa-solid fa-camera fa-swap-opacity"></i>

<!-- Custom colors -->
<i class="fa-duotone fa-solid fa-camera"
   style="--fa-primary-color: gold; --fa-secondary-color: navy;"></i>

<!-- Custom opacity -->
<i class="fa-duotone fa-solid fa-camera"
   style="--fa-secondary-opacity: 1.0;"></i>
```

## Global Styling via CSS

```css
:root {
  --fa-primary-color: dodgerblue;
  --fa-secondary-color: gold;
  --fa-secondary-opacity: 0.6;
}
```
