# Sizing Icons

Source: https://docs.fontawesome.com/web/style/size

FontAwesome provides relative and literal sizing classes.

## Relative Sizing Classes

These scale relative to the parent element's font-size (using `em` units):

| Class | Size |
|-------|------|
| `fa-2xs` | 0.625em |
| `fa-xs` | 0.75em |
| `fa-sm` | 0.875em |
| (default) | 1em |
| `fa-lg` | 1.25em |
| `fa-xl` | 1.5em |
| `fa-2xl` | 2em |

## Literal Sizing Classes

These set the font-size to an exact multiple of the base (1em = parent font-size):

| Class | Size |
|-------|------|
| `fa-1x` | 1em |
| `fa-2x` | 2em |
| `fa-3x` | 3em |
| `fa-4x` | 4em |
| `fa-5x` | 5em |
| `fa-6x` | 6em |
| `fa-7x` | 7em |
| `fa-8x` | 8em |
| `fa-9x` | 9em |
| `fa-10x` | 10em |

## Examples

```html
<i class="fa-solid fa-camera fa-xs"></i>
<i class="fa-solid fa-camera fa-sm"></i>
<i class="fa-solid fa-camera fa-lg"></i>
<i class="fa-solid fa-camera fa-xl"></i>
<i class="fa-solid fa-camera fa-2xl"></i>

<i class="fa-solid fa-camera fa-1x"></i>
<i class="fa-solid fa-camera fa-5x"></i>
<i class="fa-solid fa-camera fa-10x"></i>
```

> **Note:** When using Tailwind CSS, you can also use `text-xs`, `text-sm`, `text-lg`, etc. directly since icons inherit font-size.
