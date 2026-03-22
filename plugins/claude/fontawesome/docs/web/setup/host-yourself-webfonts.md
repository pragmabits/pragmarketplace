# Host Yourself — Web Fonts

Source: https://docs.fontawesome.com/web/setup/host-yourself/webfonts

## File Organization

Downloaded package contains:

- **`/webfonts`** — Typeface files that CSS depends on
- **`/css`** — Core styling and utility classes for all Font Awesome styles

## Implementation Steps

1. Copy asset folders into your project's static assets directory
2. Include core file (`fontawesome.css`) on every page using icons
3. Add style-specific CSS files for needed icon styles
4. Remove unused files to optimize performance

## Icon Styles Available

- **Classic**: Solid, Regular, Light (Pro), Thin (Pro)
- **Duotone**: Solid, Regular, Light, Thin (all Pro)
- **Sharp**: Solid, Regular, Light, Thin (all Pro)
- **Sharp Duotone**: Solid, Regular, Light, Thin (all Pro)
- **Brands**: Free
- **Specialty packs** (Pro+): Chisel, Etch, Graphite, Jelly, Notdog, Slab, Thumbprint, Utility, Whiteboard

## HTML Example

```html
<head>
  <link href="/path-to-fontawesome/css/fontawesome.css" rel="stylesheet" />
  <link href="/path-to-fontawesome/css/solid.css" rel="stylesheet" />
</head>
<body>
  <i class="fa-solid fa-user"></i>
</body>
```

## Important Notes

- Ensure linked stylesheets correctly reference actual file locations.
- `all.css` no longer contains every icon; use only specific style files for better performance.
- The `/webfonts` directory must be accessible relative to the CSS files (CSS references fonts via `../webfonts/` relative path).

## Kit Hosting

Pro subscriptions can download their Kit and self-host it, receiving additional files including custom icon support with dedicated CSS and JavaScript files.

## Version Upgrades

Backward compatibility for most icon name changes and syntax updates between versions.
