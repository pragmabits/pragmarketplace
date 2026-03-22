# Bare SVGs on the Web

Source: https://docs.fontawesome.com/web/add-icons/svg-bare

## SVG Formats Available

### SVG Format
Cropped viewbox fitting the icon's interior symbol. Minimal whitespace.

### Full SVG Format
Standard square viewbox based on Icon Canvas spec. Consistent rendering with padding.

## Usage

Bare SVGs can be embedded directly in HTML or referenced as `<img>` sources:

### Inline SVG

```html
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <path d="M0 256a256 256 0 1 1 512 0A256 256 0 1 1 0 256z"/>
</svg>
```

### Image Reference

```html
<img src="/path-to/circle-check.svg" alt="Check mark" />
```

## Styling

Standard CSS can style inline SVGs:

```css
svg {
  fill: currentColor;
  width: 1em;
  height: 1em;
}
```

## Notes

- No Font Awesome JavaScript or CSS framework needed
- Full control over SVG markup and styling
- Must handle sizing, color, and accessibility manually
- Best for projects requiring minimal dependencies or full SVG control
