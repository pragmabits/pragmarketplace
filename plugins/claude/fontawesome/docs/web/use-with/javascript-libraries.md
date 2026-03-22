# JavaScript Libraries

Source: https://docs.fontawesome.com/web/use-with/javascript-libraries

For SVG+JS method with JavaScript libraries (jQuery, etc.).

## Nested SVG Tags

Main solution: use `data-auto-replace-svg="nest"`:

```html
<script src="https://kit.fontawesome.com/YOUR-KIT-ID.js"
  data-auto-replace-svg="nest"></script>
```

## Critical Issue

Since elements are replaced, any bindings to the element will be lost! Solutions:

- Use event delegation on parent elements
- Target rendered SVGs with `[data-fa-i2svg]` selector
- Don't store references to icon elements

## Dynamic Swapping

```javascript
$(this).find('[data-fa-i2svg]')
  .toggleClass('fa-angle-down')
  .toggleClass('fa-angle-right')
```
