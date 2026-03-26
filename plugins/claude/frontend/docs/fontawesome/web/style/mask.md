# Masking

Source: https://docs.fontawesome.com/web/style/mask

Masking combines two icons where one acts as the outer mask and the other as the inner icon. The inner icon is clipped to the shape of the outer icon.

> **Important:** Like power transforms, masking requires the **SVG+JS** version. It does **NOT** work with Web Fonts + CSS.

## Usage (SVG+JS only)

```html
<i class="fa-solid fa-pencil" data-fa-transform="shrink-10 up-.5"
   data-fa-mask="fa-solid fa-comment"></i>
```

This renders a pencil icon clipped inside the shape of a comment bubble.

```html
<i class="fa-solid fa-phone" data-fa-transform="shrink-10"
   data-fa-mask="fa-solid fa-circle"></i>
```

Phone icon masked inside a circle.

## How It Works

- The main class defines the inner (foreground) icon.
- `data-fa-mask` defines the outer (mask/clipping) icon.
- `data-fa-transform` is typically used to shrink/position the inner icon so it fits well inside the mask shape.
- The result uses SVG clipping paths.

## Common Mask Shapes

- `fa-circle`
- `fa-square`
- `fa-comment`
- `fa-bookmark`
- `fa-heart`
