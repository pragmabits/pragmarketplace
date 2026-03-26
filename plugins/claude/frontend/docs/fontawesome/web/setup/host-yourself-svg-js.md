# Host Yourself — SVG + JS

Source: https://docs.fontawesome.com/web/setup/host-yourself/svg-js

## File Organization

Copy core `fontawesome.js` loader and style-specific `.js` files from the `/js` folder into your project's static assets directory.

## Implementation Example

```html
<head>
  <script defer src="/your-path-to-fontawesome/js/fontawesome.js"></script>
  <script defer src="/your-path-to-fontawesome/js/brands.js"></script>
  <script defer src="/your-path-to-fontawesome/js/solid.js"></script>
</head>
<body>
  <i class="fa-solid fa-user"></i>
</body>
```

## Available Icon Styles

Classic, Duotone, Sharp, Brands, Chisel, Etch, Graphite, Jelly, Notdog, Slab, Thumbprint, Utility, and Whiteboard families, noting Free vs Pro availability.

## Important Notes

- `all.js` doesn't include 'all' icons anymore — include only specific styles needed
- Custom icons from downloaded Pro Kits are supported
- Backward compatibility handles older icon naming conventions automatically
- Verify file paths point to correct locations
- Use the `defer` attribute on script tags to prevent blocking page render
