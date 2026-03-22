# SVG Async Loading

Source: https://docs.fontawesome.com/web/dig-deeper/svg-async

**Prerequisites:** Font Awesome set up using the SVG+JS implementation method.

## Loading State Classes

Classes added to the `<html>` element:

| State | Class | When |
|-------|-------|------|
| Initial | `fontawesome-i2svg-pending` | Browser begins searching for icons |
| Complete | `fontawesome-i2svg-complete` + `fontawesome-i2svg-active` | Icon replacement finishes |
| Subsequent | Reverts to `pending`, then back to `complete` | Additional icon batches load |

## Practical CSS Applications

### Hide Body Until Icons Load

```css
html:not(.fontawesome-i2svg-active) body {
  opacity: 0;
}
```

### Show Specific Sections Conditionally

```css
.icons-section {
  display: none;
}

html.fontawesome-i2svg-active .icons-section {
  display: block;
}
```

## Note on Layout Stability

While async loading improves initial rendering speed, it can cause page layout shifts if not managed with the provided CSS classes and techniques.
