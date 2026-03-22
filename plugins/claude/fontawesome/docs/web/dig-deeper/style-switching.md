# Fast Style Switching

Source: https://docs.fontawesome.com/web/dig-deeper/style-switching

## Basic Requirement

Use only the `fa` class on icon elements, omitting style-specific classes:

```html
<i class="fa fa-mask"></i>
```

## Web Fonts Implementation

Two CSS custom properties control style switching:

- `--fa-family`: Controls icon family (Classic, Duotone, Sharp, Sharp Duotone)
- `--fa-style`: Controls weight/style via font-weight values (100, 300, 400, 900)

### Example: Sharp Solid Icons

```css
:root {
  --fa-family: var(--fa-family-sharp);
  --fa-style: 900;
}
```

### Font-Weight Values by Style

| Style | Font Weight |
|-------|------------|
| Solid | 900 |
| Regular | 400 |
| Light | 300 |
| Thin | 100 |

## Override Methods

1. Setting new CSS custom property values on specific elements
2. Adding style class attributes directly to HTML elements (takes precedence)

## Duotone Families

Setting Duotone as the default requires using Sass with Font Awesome's Sass assets. The process involves compiling with appropriate imports and using `@extend` to apply Duotone CSS to the general `.fa` class.

## SVG+JS Approach

Configuration uses `data-style-default` and `data-family-default` attributes on script tags or a `FontAwesomeConfig` object created before script loading:

```html
<script defer
  data-style-default="solid"
  data-family-default="sharp"
  src="/your-path-to-fontawesome/js/fontawesome.js">
</script>
```

Or via JavaScript configuration object:

```javascript
window.FontAwesomeConfig = {
  styleDefault: 'solid',
  familyDefault: 'sharp'
}
```
