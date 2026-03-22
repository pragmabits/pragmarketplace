# SVG Sprites

Source: https://docs.fontawesome.com/web/add-icons/svg-sprites

## Two SVG Sprite Format Options

### SVG Format (`/sprites`)
Cropped viewbox dimensions matching interior symbol boundaries, minimal whitespace.

### Full SVG Format (`/sprites-full`)
Standardized square viewboxes based on Icon Canvas spec, consistent rendering with padding.

## Available Sprite Files

- **Classic**: Solid, Regular, Light (Pro), Thin (Pro)
- **Duotone**: Solid, Regular, Light, Thin (all Pro)
- **Sharp**: Solid, Regular, Light, Thin (all Pro)
- **Sharp Duotone**: Solid, Regular, Light, Thin (all Pro)
- **Brands**: Free
- **Specialty packs** (Pro+): Chisel, Etch, Graphite, Jelly, Notdog, Slab, Thumbprint, Utility, Whiteboard

## Implementation

1. Obtain sprite file from Font Awesome package
2. Store alongside other static assets
3. Reference icons using `<svg><use href>` syntax

```html
<svg>
  <use href="/path-to/fa-solid.svg#user"></use>
</svg>

<svg>
  <use href="/path-to/fa-brands.svg#github"></use>
</svg>
```

## Critical Technical Considerations

### Same Origin Policy

`href` URLs require same-domain loading due to cross-origin protection. The sprite file must be served from the same origin as the page.

### Visual Cropping

Icons may appear cut off if icon paths extend beyond Icon Canvas grid height. Solutions:
- Use Full SVG assets (`/sprites-full`)
- Use inline bare SVG with `overflow: visible`
