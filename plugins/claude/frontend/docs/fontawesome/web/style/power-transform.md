# Power Transforms

Source: https://docs.fontawesome.com/web/style/power-transform

Power transforms provide fine-grained control over icon size, position, and rotation. They use the `data-fa-transform` attribute.

> **Important:** Power transforms require the **SVG+JS** version of FontAwesome. They do **NOT** work with the Web Fonts + CSS setup.

## Transform Commands

| Command | Effect |
|---------|--------|
| `shrink-#` | Shrinks icon by # (in 1/16th em units) |
| `grow-#` | Grows icon by # (in 1/16th em units) |
| `up-#` | Moves icon up by # |
| `down-#` | Moves icon down by # |
| `left-#` | Moves icon left by # |
| `right-#` | Moves icon right by # |
| `rotate-#` | Rotates clockwise by # degrees |
| `flip-v` | Flips vertically |
| `flip-h` | Flips horizontally |

## Examples (SVG+JS only)

```html
<i class="fa-solid fa-magic" data-fa-transform="shrink-8"></i>
<i class="fa-solid fa-magic" data-fa-transform="grow-6"></i>
<i class="fa-solid fa-magic" data-fa-transform="rotate-45"></i>
<i class="fa-solid fa-magic" data-fa-transform="up-8 left-6 rotate-45"></i>
```

Multiple transforms can be combined in a single attribute, space-separated.
