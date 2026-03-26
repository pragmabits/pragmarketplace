# Rotate Icons

Source: https://docs.fontawesome.com/web/style/rotate

Static rotation classes apply a fixed rotation transform.

## Rotation Classes

| Class | Rotation |
|-------|----------|
| `fa-rotate-90` | 90 degrees |
| `fa-rotate-180` | 180 degrees |
| `fa-rotate-270` | 270 degrees |

## Examples

```html
<i class="fa-solid fa-snowboarding"></i>
<i class="fa-solid fa-snowboarding fa-rotate-90"></i>
<i class="fa-solid fa-snowboarding fa-rotate-180"></i>
<i class="fa-solid fa-snowboarding fa-rotate-270"></i>
```

## Arbitrary Rotation

You can use the `fa-rotate-by` class with a CSS custom property for arbitrary angles:

```html
<i class="fa-solid fa-snowboarding fa-rotate-by" style="--fa-rotate-angle: 45deg;"></i>
```
