# Troubleshooting for Web

Source: https://docs.fontawesome.com/web/troubleshoot/

## Why Isn't My Icon Showing Up?

- **Version availability:** Verify the icon exists in your FA version
- **License tier:** Some icons are Pro/Pro+ exclusive. Confirm subscription level and correct style prefix.
- **Subset limitations:** If using subsetted Kit, ensure icon and style are included
- **File paths:** When self-hosting, verify all files installed and paths in `<head>` are correct
- **Naming errors:** Double-check icon name and prefix
- **Multiple conflicting versions:** CMS/theme/plugin may load its own FA version alongside yours. Use Conflict Detection in Kit settings.

## Wrong Style Showing

Confirm correct style prefix. Version 7 includes many different Icon Families and Styles.

## CMS and Web Publishing Tools

- **WordPress:** Official plugin on WordPress.org
- **Squarespace:** Dedicated instructions
- **Other platforms:** Follow quick start guide if you can access `<head>`

## FA v7 with Theme-Included Versions

Kits include built-in conflict detection. Kits offer v4 compatibility mode. Otherwise, contact theme developer.

## Using FA 7 and Older Versions Together

**Not recommended.** CSS class names, unicode values, and supporting styling overlap heavily. CSS collisions and performance issues would occur.

## Custom Icons

Upload through Kit Icon Upload feature (requires active Pro plan and Pro Kit). Use Icon Wizard to modify existing icons.

## Large File Sizes

Use a Kit with auto-subsetting or create a custom subset. Alternatively, self-host and load only needed styles.

## Custom Icon Upload Issues

- Verify icon preparation recommendations followed
- Confirm project references correct Kit
- Use `fak` style prefix, not `fas`/`far`
- Check dedicated Icon Upload troubleshooting

## Duotone Icons Not Working

Refer to specialized Duotone troubleshooting section.

## Kit Not Working

Ensure Kit embed code is copied exactly. Disable Subresource Integrity (SRI) and Content Security Policy (CSP) — Kits are incompatible with these.

## Style Options Reference

- Icon Packs/Families/Styles
- Styling Options
- Style CheatSheet (CSS custom properties)

## Animated Icons Not Animating

Check system `prefers-reduced-motion` setting.

## Sharp Thin's `.fast` Class Conflict

Older animate.css also uses `fast` class. Fix:

```css
.animated.fast {
  font-family: inherit;
}
```
