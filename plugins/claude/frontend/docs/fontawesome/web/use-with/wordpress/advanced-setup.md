# Advanced Setup Without Kits CDN

Source: https://docs.fontawesome.com/web/use-with/wordpress/advanced-setup

Want your web site pages to load icons without hitting the Font Awesome CDN? Read on.

Starting with Version 5 of the WordPress plugin, icons are added as inline SVGs through the Icon Chooser. The full `<svg>` elements are embedded directly in post content, eliminating the need to load from a Kit or CDN when visitors view the site.

## Is This for You?

This method targets sites needing to limit third-party resource loading like CDNs for end users. The standard WordPress plugin setup is recommended for simpler implementations.

## Set Up

**Step 1:** Select a Kit in plugin settings. The plugin fetches the CSS stylesheet from Font Awesome Kits CDN and stores it in the uploads directory, serving it directly from the WordPress site rather than the CDN.

**Step 2:** Skip loading the Kit by adding this filter to `functions.php`:

```php
add_filter( 'font_awesome_skip_enqueue_kit', '__return_true' );
```

**Step 3:** Add icons using the Icon Chooser in the Block Editor, which embeds icons as SVGs.

After setup, visitor browsers won't communicate with the Font Awesome CDN.

## Limitation: Embedded SVG Icons Only

In this mode, because the Kit will not be loaded on the page, it will not render icons for `<i>` tags, `[icon]` shortcodes, or CSS pseudo-elements.

## Working with Other Font Awesome Versions

Themes or plugins loading their own Font Awesome versions typically use `<i>` tags or CSS pseudo-elements. If you use the conflict detector to block Font Awesome assets from other sources, their icons won't load without an asset to render them.

## Admin and Editor CDN Usage

While frontend visitors avoid CDN communication, the Icon Chooser still uses the CDN for fetching SVGs and the GraphQL API for Kit information and searches. These requests occur only in the admin or editor interface.
