# CSS Pseudo-elements

Source: https://docs.fontawesome.com/web/add-icons/pseudo-elements

CSS pseudo-elements allow adding Font Awesome icons using only CSS, without modifying HTML. Uses `::before` pseudo-element to inject icon content.

> **Important:** "Working with pseudo-elements is not for the faint of fa-heart." More error-prone than standard HTML; requires solid CSS knowledge.

## Step 1: Common CSS for All Icons

```css
.icon::before {
  display: inline-block;
  text-rendering: auto;
  -webkit-font-smoothing: antialiased;
}
```

## Step 2: Reference Individual Icons

Each icon requires:
1. `::before` pseudo-element
2. A font CSS custom property matching the desired style
3. The icon's Unicode value as the content

```css
.ghost::before {
  font: var(--fa-font-solid);
  content: '\f6e2';
}
```

## Style Reference Chart — CSS Custom Properties

### Classic Family

| Style | CSS Custom Property |
|-------|-------------------|
| Solid | `--fa-font-solid` |
| Regular | `--fa-font-regular` |
| Light | `--fa-font-light` |
| Thin | `--fa-font-thin` |

### Duotone Family

| Style | CSS Custom Property |
|-------|-------------------|
| Duotone Solid | `--fa-font-duotone` |
| Duotone Regular | `--fa-font-duotone-regular` |
| Duotone Light | `--fa-font-duotone-light` |
| Duotone Thin | `--fa-font-duotone-thin` |

### Sharp Family

| Style | CSS Custom Property |
|-------|-------------------|
| Sharp Solid | `--fa-font-sharp-solid` |
| Sharp Regular | `--fa-font-sharp-regular` |
| Sharp Light | `--fa-font-sharp-light` |
| Sharp Thin | `--fa-font-sharp-thin` |

### Brands

| Style | CSS Custom Property |
|-------|-------------------|
| Brands | `--fa-font-brands` |

## Duotone Icons with Pseudo-elements

Duotone icons require both `::before` and `::after` pseudo-elements with additional positioning and opacity styling.

The `::after` pseudo-element uses `font-feature-settings: 'ss01'` for the secondary layer.

```css
.duotone-icon {
  position: relative;
}

.duotone-icon::before {
  font: var(--fa-font-duotone);
  content: '\f6e2';
}

.duotone-icon::after {
  font: var(--fa-font-duotone);
  content: '\f6e2';
  font-feature-settings: 'ss01';
  position: absolute;
  left: 0;
  opacity: var(--fa-secondary-opacity, 0.4);
}
```

## SVG+JS Framework

When using the SVG+JS version, enable pseudo-elements with `data-search-pseudo-elements` attribute on the script tag, then hide the CSS-rendered pseudo-element using `display: none`:

```html
<script defer data-search-pseudo-elements src="/your-path-to-fontawesome/js/all.js"></script>
```
