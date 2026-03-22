# The Icon Canvas

Source: https://docs.fontawesome.com/web/style/icon-canvas

## Introduction

Icons are designed using a square 20 pixel grid functioning as an "Icon Canvas" that determines proportions and positioning.

## Fixed Width (Default)

All Font Awesome icons display at fixed width by default, filling the entire Icon Canvas with visual centering and balanced whitespace.

**Benefits:**
- Easy alignment in lists or vertical lines
- Consistent, uniform width when placed horizontally (navigation, controls)

### Vertical Alignment Example

```html
<div>
  <div><i class="fa-solid fa-bread-slice"></i> Bread</div>
  <div><i class="fa-solid fa-egg"></i> Eggs</div>
  <div><i class="fa-solid fa-cow"></i> Milk</div>
  <div><i class="fa-solid fa-apple-whole"></i> Apples</div>
  <div><i class="fa-solid fa-broccoli"></i> Broccoli</div>
</div>
```

### Horizontal Controls Example

```html
<div class="fa-3x" style="display: flex; gap: 0.5rem;">
  <i class="fa-solid fa-backward"></i>
  <i class="fa-solid fa-play"></i>
  <i class="fa-solid fa-forward"></i>
  <i class="fa-solid fa-volume-xmark"></i>
  <i class="fa-solid fa-volume-low"></i>
  <i class="fa-solid fa-volume-high"></i>
  <i class="fa-solid fa-sliders"></i>
</div>
```

## Automatic Width

Add the `fa-width-auto` class to render icons using only the interior symbol and not the entire Icon Canvas. This removes extra whitespace, ideal for inline text insertion.

```html
<div class="fa-3x" style="display: flex; gap: 0.5rem;">
  <i class="fa-solid fa-exclamation fa-width-auto"></i>
  <i class="fa-solid fa-circle-check fa-width-auto"></i>
  <i class="fa-solid fa-input-numeric fa-width-auto"></i>
  <i class="fa-solid fa-ruler-vertical fa-width-auto"></i>
  <i class="fa-solid fa-ruler-horizontal fa-width-auto"></i>
  <i class="fa-solid fa-airplay fa-width-auto"></i>
</div>
```

## Automatic Width by Default

### Set the Automatic Width Class

Apply `fa-width-auto` to a parent element for nested icons to inherit the rule:

```html
<!-- All icons on the page will render using Automatic Width -->
<body class="fa-width-auto">
  ...
</body>
```

```html
<!-- All icons in this section will render using Automatic Width -->
<section class="fa-width-auto">...</section>
```

### Using CSS Custom Properties

```css
/* Project-wide */
:root {
  --fa-width: auto;
}

/* Scoped to a section */
.my-section {
  --fa-width: auto;
}
```

> **Warning:** Default fixed width equals approximately 20 pixels (based on 16px browser default). Custom `--fa-width` values may introduce rendering issues; verify results carefully.

## Icon Height and Visual Padding

**Rendering Height:** Icons display and vertically center in elements with base height of `1em` (default 16px in most browsers), facilitating easy text alignment.

**Visual Grid Extension:** Some icons utilize additional visual grid space with parts extending beyond base rendering height (example: `-slash` icons).

### Cropping Issues with Icon Padding

Visual cropping occurs when:
1. Icon sits inside an equally tall HTML element
2. `overflow: hidden` applied via CSS to parent element

**Solution:** Increase element's computed height via larger `line-height` or `padding-top`/`padding-bottom`.

```html
<!-- Icon Padding is visually cut off -->
<div style="font-size: 48px; line-height: 1; overflow: hidden;">
  <i class="fa-solid fa-file-slash"></i>
</div>

<!-- Fix with extra line-height -->
<div style="font-size: 48px; line-height: 1; overflow: hidden;">
  <i class="fa-solid fa-file-slash" style="line-height: 1.2;"></i>
</div>

<!-- Fix with vertical padding -->
<div style="font-size: 48px; line-height: 1; overflow: hidden;">
  <i class="fa-solid fa-file-slash" style="padding-top: 0.1em; padding-bottom: 0.1em"></i>
</div>
```

**Other Cropping Cases:** Similar visual cropping may occur with SVG Sprites, Bare SVGs, or Animating Icons in Safari.
