# Icons in a List

Source: https://docs.fontawesome.com/web/style/lists

## Overview

Font Awesome provides utility styling for replacing default HTML list bullets with decorative icons using the `fa-ul` and `fa-li` classes.

## CSS Classes

| Class | Purpose |
|-------|---------|
| `fa-ul` | Applied to `<ul>` or `<ol>` to enable icon bullets |
| `fa-li` | Wraps the icon inside `<li>` elements |

## Basic Implementation

### Unordered Lists

```html
<ul class="fa-ul">
  <li>
    <span class="fa-li"><i class="fa-solid fa-check-square"></i></span>List icons can
  </li>
  <li>
    <span class="fa-li"><i class="fa-solid fa-check-square"></i></span>be used to
  </li>
  <li>
    <span class="fa-li"><i class="fa-solid fa-spinner fa-pulse"></i></span>replace bullets
  </li>
  <li>
    <span class="fa-li"><i class="fa-regular fa-square"></i></span>in lists
  </li>
</ul>
```

### Ordered Lists

The same approach works with `<ol>` elements while maintaining semantic ordering:

```html
<ol class="fa-ul">
  <li>
    <span class="fa-li"><i class="fa-solid fa-check-square"></i></span>List icons can
  </li>
</ol>
```

## Customization via CSS Custom Properties

| Property | Function | Values |
|----------|----------|--------|
| `--fa-li-margin` | Adjusts spacing around icons | Any valid CSS margin value |
| `--fa-li-width` | Sets icon width | Any valid CSS width value |

### Custom Width

```html
<ul class="fa-ul" style="--fa-li-width: 3em;">
  <li>
    <span class="fa-li"><i class="fa-solid fa-check-square"></i></span>List item
  </li>
</ul>
```

### Custom Margin

```html
<ul class="fa-ul" style="--fa-li-margin: 4em;">
  <li>
    <span class="fa-li"><i class="fa-solid fa-check-square"></i></span>List item
  </li>
</ul>
```

Properties can be overridden at the individual list or item level for granular control.

## Technical Notes

The implementation uses CSS Logical Properties to support multiple writing modes and languages, ensuring broader compatibility across different text directions and scripts.
