# Troubleshoot Uploads

Source: https://docs.fontawesome.com/web/add-icons/upload-icons/troubleshoot

## File Format Problems

Only SVG files (`.svg` extension) are accepted. Other formats like PNG, PDF, and GIF cannot be uploaded.

## Typography Issues

Occurs when text remains as editable typefaces rather than outlines in your SVG. Convert all text to paths/outlines before exporting.

## Embedded Images

Raster images (PNG, GIF, JPG) don't scale properly and should be removed. Use vector alternatives instead.

## Sizing Problems

Check:
- Viewbox dimensions match icon height requirements
- Artboard dimensions in design software like Adobe Illustrator
- Icon scaling relative to the visual canvas
- No extra paths or points on the artboard

## Wide Icon Behavior

Wide icons (significantly wider than tall) render differently depending on context:

- **Web Fonts/SVG + JS**: Scaled to fixed width unless `fa-width-auto` class is applied
- **SVG assets**: Viewbox height of 512 with proportional width
- **Full SVG assets**: Scaled to fit 640x640 viewbox, vertically centered

## Warning and Error Messages

Common messages users may encounter:
- SVG parsing failures
- Multiple objects requiring joining
- Bitmap image conflicts
- Text outline requirements
- Overlapping paths
- Objects extending beyond viewbox boundaries

## Display Issues

For uploaded icons not appearing in projects, verify:

1. Font Awesome Pro Services access
2. Kit contains the uploaded icons
3. Proper domain authorization
4. Kit embed code in HTML `<head>`
5. Correct syntax: `<i class="fak fa-[uploadedIconName]"></i>`
6. Use `fak` prefix, not other Font Awesome style prefixes

## Resources

Use official Font Awesome Icon Design Templates for Adobe Illustrator and Figma to ensure successful uploads.
