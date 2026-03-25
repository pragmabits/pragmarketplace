# CSS Properties Quick Reference

## Display

| Value | Purpose |
|-------|---------|
| `block` | Full-width block element |
| `inline` | Inline flow element |
| `inline-block` | Inline with block properties |
| `flex` | Flexbox container |
| `inline-flex` | Inline flexbox container |
| `grid` | Grid container |
| `inline-grid` | Inline grid container |
| `none` | Remove from layout |
| `contents` | Remove box, keep children |

## Box Model

| Property | Values | Notes |
|----------|--------|-------|
| `box-sizing` | `content-box`, `border-box` | Use `border-box` globally |
| `margin` | `<length>`, `auto`, `0` | `auto` for centering |
| `padding` | `<length>` | No negative values |
| `border` | `<width> <style> <color>` | Shorthand |
| `outline` | `<width> <style> <color>` | Doesn't affect layout |
| `outline-offset` | `<length>` | Can be negative |

## Logical Properties

| Physical | Logical | Axis |
|----------|---------|------|
| `margin-top/bottom` | `margin-block` | Block |
| `margin-left/right` | `margin-inline` | Inline |
| `padding-top/bottom` | `padding-block` | Block |
| `padding-left/right` | `padding-inline` | Inline |
| `width` | `inline-size` | Inline |
| `height` | `block-size` | Block |
| `top` | `inset-block-start` | Block |
| `left` | `inset-inline-start` | Inline |

## Sizing

| Property | Common Values | Notes |
|----------|--------------|-------|
| `width` / `inline-size` | `<length>`, `%`, `auto`, `fit-content`, `min-content`, `max-content` | |
| `min-width` | `<length>`, `0`, `min-content` | |
| `max-width` | `<length>`, `none`, `100%` | |
| `aspect-ratio` | `16 / 9`, `1`, `auto` | Maintains proportions |

## Typography

| Property | Common Values |
|----------|--------------|
| `font-family` | `system-ui`, `sans-serif`, `serif`, `monospace` |
| `font-size` | `<length>`, `clamp()`, `rem`, `em` |
| `font-weight` | `100`–`900`, `normal`, `bold` |
| `line-height` | `1.5`, `<number>`, `<length>` |
| `letter-spacing` | `<length>`, `normal` |
| `text-align` | `start`, `center`, `end`, `justify` |
| `text-decoration` | `none`, `underline`, `line-through` |
| `text-transform` | `none`, `uppercase`, `lowercase`, `capitalize` |
| `text-wrap` | `balance`, `pretty`, `stable` |
| `overflow-wrap` | `break-word`, `anywhere` |
| `text-overflow` | `ellipsis`, `clip` |
| `white-space` | `nowrap`, `pre`, `pre-wrap` |

## Colors

| Format | Example | Notes |
|--------|---------|-------|
| Named | `red`, `transparent` | Limited palette |
| Hex | `#3b82f6`, `#3b82f680` | With optional alpha |
| RGB | `rgb(59 130 246)` | Modern space syntax |
| HSL | `hsl(217 91% 60%)` | Hue/saturation/lightness |
| OKLCH | `oklch(0.62 0.2 264)` | Perceptually uniform |
| `color-mix()` | `color-mix(in oklch, #3b82f6 70%, white)` | Mix colors |
| `currentColor` | Inherits from `color` | Useful for borders/SVGs |

## Overflow

| Property | Values |
|----------|--------|
| `overflow` | `visible`, `hidden`, `clip`, `scroll`, `auto` |
| `overflow-x` / `overflow-y` | Same as above |
| `text-overflow` | `ellipsis`, `clip` |
| `scrollbar-gutter` | `stable`, `stable both-edges` |

## Common Pitfalls

- **Margin collapse**: Vertical margins collapse between siblings and parent-child; use `display: flow-root` or padding to prevent
- **Percentage heights**: Require explicit parent height or use `dvh` units
- **Outline vs border**: Outline doesn't affect layout — prefer for focus styles
- **`overflow: hidden`**: Creates a new stacking context and clips absolutely positioned children
- **`box-sizing`**: Always set `border-box` globally via `*, *::before, *::after { box-sizing: border-box; }`
