# Prep Icons for Upload

Source: https://docs.fontawesome.com/web/add-icons/upload-icons/prep-icons

## Valid SVGs

Font Awesome accepts only SVG files. Required parameters include:

- A `viewBox` attribute with height and width values (defines the icon's canvas/artboard)
- **Monotone icons**: One (1) `path` element
- **Duotone icons**: Two (2) `path` elements (one with < 100% opacity)

Example of a valid SVG:

```xml
<svg viewBox="0 0 512 512">
  <path d="M0 256a256 256 0 1 1 512 0 256 256 0 1 1 -512 0z" />
</svg>
```

## Avoiding Rasters

Raster (pixel-based) images like PNGs, JPGs, and GIFs do not scale well. Embedded raster images in SVGs cause file bloat and rendering issues.

## ViewBox Specifications

The `viewBox` attribute acts as the icon's canvas. All path data must remain completely within viewBox boundaries — any points outside are ignored during upload. Design software artboard dimensions translate directly to `viewBox` values.

## Wide Custom Icons

Icons exceeding the 20-pixel canvas width display differently depending on format:

- **Font Awesome Web Software**: Scaled to standard width (unless using `fa-width-auto`)
- **Raw SVG Assets**: Height scaled to standard canvas; width scales proportionally
- **Full SVGs**: Scaled down to fit the fixed 20-pixel canvas while maintaining aspect ratio

## Color Handling

The system ignores color attributes during upload to expedite processing. Apply colors through Font Awesome's styling support after uploading.

## Monotone Icons Setup

Multiple shapes must be combined into a single compound path:

- **Illustrator**: Use "Object > Compound Path > Make"
- **Figma**: Use boolean operations to create one vector node

Combined example:

```xml
<svg viewBox="0 0 20 20">
  <path
    d="M3,5c0-.553.447-1,1-1h12c.553,0,1,.447,1,1s-.447,1-1,1H4c-.553,0-1-.447-1-1ZM3,10c0-.553.447-1,1-1h12c.553,0,1,.447,1,1s-.447,1-1,1H4c-.553,0-1-.447-1-1ZM17,15c0,.553-.447,1-1,1H4c-.553,0-1-.447-1-1s.447-1,1-1h12c.553,0,1,.447,1,1Z" />
</svg>
```

## Duotone Icons Setup

Duotone icons require two separate compound paths or nodes with opacity differentiation:

- **Primary layer**: 100% opacity
- **Secondary layer**: < 100% opacity (will be set to 40% after upload)

**Critical consideration**: The primary layer is subtracted from overlapping secondary layer portions. Ensure either:
- Layers don't overlap, OR
- Overlapping secondary portions can be safely removed

Example duotone SVG:

```xml
<svg viewBox="0 0 20 20">
  <path d="M7 4H11V2H13V4H16V8.36426L9.08496 15.2793L8.79785 17H2V4H5V2H7V4ZM5 13.5H9V12H5V13.5ZM5 10.5H11V9H5V10.5Z" />
  <path
    d="M17.1445 14.3513L13 18.4958L10 18.9958L10.5 15.9958L14.6445 11.8513L17.1445 14.3513ZM19.5 11.9958L17.8516 13.6443L15.3516 11.1443L17 9.49585L19.5 11.9958Z"
    opacity=".4" />
</svg>
```

## Adobe Illustrator Export Process

1. Create icon designs in individual artboards
2. Outline strokes via "Object > Path > Outline Stroke" and text via "Type > Create Outlines"
3. Combine using "Object > Compound Path > Make"
4. Export via "File > Export > Export for Screens" as SVG with these settings:
   - Styling: Presentation Attributes
   - Font: Convert to Outlines
   - Object IDs: Minimal
   - Decimal: 3
   - Enable "Minify"
   - Disable "Responsive"
5. Upload to a Font Awesome Kit

## Figma Export Process

1. Create designs in individual frames
2. Outline text and strokes (unless part of boolean groups)
3. Apply boolean operations to combine elements
4. Select frames and export as SVG from the right sidebar
5. Upload to a Font Awesome Kit
