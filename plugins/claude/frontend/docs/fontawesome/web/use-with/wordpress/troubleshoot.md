# Troubleshooting Conflicts (WordPress)

Source: https://docs.fontawesome.com/web/use-with/wordpress/troubleshoot

## Conflict Detection Scanner

The plugin includes a built-in scanner — a blue box appearing in the lower right corner of the browser window (visible only to admins). It runs while you visit any page or area of your site having trouble loading icons correctly, identifying competing Font Awesome versions.

## Detect Conflicts

The scanner monitors pages where icons fail to display properly, documenting any competing Font Awesome installations it discovers.

## Review Active Font Awesome Versions

Two categories:

- **Registered plugins/themes** showing their preferred Font Awesome settings
- **Unidentified versions** found by the scanner, with details about the resource type and loading URL

Users can block detected conflicting versions and decide which plugin settings to prioritize when multiple extensions have different requirements.

## Settings Conflict Warnings

When adjusting CDN or Kit configurations differently from registered plugins' expectations, a settings conflict warning appears. Users retain the ability to override these warnings, though compatibility issues may result.

## Notes

- Conflict results persist until manually cleared
- Users can clear cached scanner results manually and re-scan to verify problem resolution
