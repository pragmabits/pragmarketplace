# Accessibility

Source: https://docs.fontawesome.com/web/dig-deeper/accessibility

Nearly 10% of the global population experiences sight impairments, and over 5% live with disabling hearing loss. Font Awesome icons are hidden from assistive technology by default.

## Decorative Icons

Icons used alongside descriptive text require no additional accessibility configuration.

### Web Fonts

No additional configuration needed — automatically ignored by assistive technology:

```html
<button type="submit"><i class="fa-solid fa-envelope"></i> Email Us!</button>
```

### SVG

Automatically receives `aria-hidden="true"`:

```html
<button type="submit">
  <svg aria-hidden="true" class="svg-inline--fa fa-envelope" role="img" viewBox="0 0 512 512">
    <path d="..."></path>
  </svg>
  Email Us!
</button>
```

## Semantic Icons in Interactive Elements

Add `aria-label` to the interactive element (not the icon):

### Web Fonts

```html
<button type="submit" aria-label="Email us!">
  <i class="fa-solid fa-envelope"></i>
</button>
```

### SVG

```html
<button type="submit" aria-label="Email us!">
  <svg aria-hidden="true" class="svg-inline--fa fa-envelope" role="img" viewBox="0 0 512 512">
    <path d="..."></path>
  </svg>
</button>
```

### SVG Sprites

```html
<button type="submit" aria-label="Email us!">
  <svg aria-hidden="true" role="img">
    <use href="fa-solid.svg#envelope"></use>
  </svg>
</button>
```

## Semantic Icons in Content

Place `aria-label` directly on the icon. For web fonts, add `role="img"`:

### Web Fonts

```html
We <i class="fa-solid fa-heart" aria-label="love" role="img"></i> pizza!
```

### SVG

```html
We
  <svg aria-label="love" aria-hidden="false" class="svg-inline--fa fa-heart" role="img" viewBox="0 0 512 512">
    <path d="..."></path>
  </svg>
  pizza!
```

### SVG Sprites

```html
We
  <svg aria-label="love" aria-hidden="false" role="img">
    <use href="fa-solid.svg#heart"></use>
  </svg>
  pizza!
```

## Animating Icons and Accessibility

Font Awesome animations support `prefers-reduced-motion` CSS media feature:
- **Default:** Animations render normally.
- **With `prefers-reduced-motion: reduce`:** Animations disable for users with vestibular motion disorders.

## Additional Resources

- Accessible Icon Buttons
- Accessible SVGs: Perfect Patterns For Screen Reader Users
- Aria-label Does Not Translate
- Contrast Ratio Checker from Lea Verou
