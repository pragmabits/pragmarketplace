# Set Up with WordPress

Source: https://docs.fontawesome.com/web/use-with/wordpress

The official Font Awesome plugin enables WordPress users to incorporate icons into pages, posts, and templates.

## Use a Kit (Recommended)

1. Set up a Kit at fontawesome.com/kits or use an existing one
2. Get Your Font Awesome API Token from your account page
3. Add Your Token to WordPress plugin settings, select "Use a Kit"
4. Select Your Kit from the list and save

Kits use an API Token to securely get your Kits in WordPress without sharing FA credentials with your WordPress server.

## Use the Font Awesome CDN (Default)

- Font Awesome 7 Pro is **NOT** available on the Font Awesome CDN. Version 7 requires either a Kit or self-hosting.
- Font Awesome 5 remains the latest CDN-supported version.
- Defaults: FA v5, Free Icons, Web Font format, FA CDN.

## Plugin Settings

- **Free vs. Pro**: All Free icons work without setup. Pro/Pro+ available via Kit.
- **SVG vs. Web Font**: SVG enables Power Transforms, Masks, and Layering. Web Font cannot do those but works with pseudo-elements.
- **Versions**: `latest` provides newest icons. Specific versions can be pinned. Kits using `latest` auto-update.
- **Older Version Compatibility**: Kits auto-handle v7 backwards compatibility. Plugin settings include v4 compatibility feature.

## Manual Installation (Advanced)

Modify WordPress `functions.php` file. Requires advanced knowledge and awareness of potential plugin conflicts.

## For Plugin and Theme Developers

The official plugin functions as a composer package for proper integration while avoiding user-site conflicts.
