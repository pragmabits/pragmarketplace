# Install Manually

Source: https://docs.fontawesome.com/web/use-with/wordpress/install-manually

How to manually install Font Awesome in WordPress by modifying the theme's `functions.php` file. Designed for advanced WordPress developers who cannot use the official plugin.

## Key Prerequisites

- Write access to the WordPress theme's `functions.php` file
- Knowledge of how to edit this file safely
- Comfort making code modifications

## Kit Installation

Create a PHP function that enqueues your Font Awesome Kit across three WordPress contexts: the front-end, admin panel, and login screen. Replace `yourkitcode.js` with your actual Kit token.

```php
function enqueue_font_awesome() {
  wp_enqueue_script(
    'font-awesome-kit',
    'https://kit.fontawesome.com/yourkitcode.js',
    array(),
    null,
    false
  );
}
add_action('wp_enqueue_scripts', 'enqueue_font_awesome');
add_action('admin_enqueue_scripts', 'enqueue_font_awesome');
add_action('login_enqueue_scripts', 'enqueue_font_awesome');
```

## CDN Alternative (Limited)

Font Awesome 7 Pro is **not** available on the Font Awesome CDN. Users requiring v7 must either use a Kit or self-host. Version 5 remains the latest CDN-supported release.

## Conflict Resolution

Since WordPress themes and plugins often bundle their own Font Awesome versions, conflicts frequently occur.

### Steps

1. Use the conflict detector tool to identify problematic instances
2. Implement a blocklist function to dequeue conflicting resources
3. Remove specific MD5 hashes representing conflicting assets

## Version Compatibility Notes

When removing v4 conflicts, Kit setup automatically provides compatibility for renamed icons between versions (v4 compatibility shim), eliminating manual migration work for most scenarios.
