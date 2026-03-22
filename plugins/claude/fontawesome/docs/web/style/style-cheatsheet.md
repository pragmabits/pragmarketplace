# Style Cheatsheet

Source: https://docs.fontawesome.com/web/style/style-cheatsheet

Complete reference of all Font Awesome CSS classes and custom properties.

## General

| Class | Details |
|-------|---------|
| `fa-inverse` | Inverts the color of an icon to white |

| CSS Custom Property | Details | Accepted Values |
|---------------------|---------|-----------------|
| `--fa-family` | Set Font Awesome icon family | Any valid Font Awesome family's `font-family` |
| `--fa-style` | Set Font Awesome icon style | Any valid Font Awesome style's `font-weight` |
| `--fa-display` | Set display of an icon | Any valid CSS `display` value |
| `--fa-inverse` | Set color of an inverted icon | Any valid CSS `color` value |

## Sizing Icons

| Class | Details |
|-------|---------|
| `fa-1x` | `font-size` to 1em |
| `fa-2x` | `font-size` to 2em |
| `fa-3x` | `font-size` to 3em |
| `fa-4x` | `font-size` to 4em |
| `fa-5x` | `font-size` to 5em |
| `fa-6x` | `font-size` to 6em |
| `fa-7x` | `font-size` to 7em |
| `fa-8x` | `font-size` to 8em |
| `fa-9x` | `font-size` to 9em |
| `fa-10x` | `font-size` to 10em |
| `fa-2xs` | `font-size` to 0.625em (~10px), vertically aligns |
| `fa-xs` | `font-size` to 0.75em (~12px), vertically aligns |
| `fa-sm` | `font-size` to 0.875em (~14px), vertically aligns |
| `fa-lg` | `font-size` to 1.25em (~20px), vertically aligns |
| `fa-xl` | `font-size` to 1.5em (~24px), vertically aligns |
| `fa-2xl` | `font-size` to 2em (~32px), vertically aligns |

## Icon Canvas + Widths

| Class | Details |
|-------|---------|
| `fa-width-auto` | Set icon width to only its symbol, not the entire Icon Canvas |

| CSS Custom Property | Details | Accepted Values |
|---------------------|---------|-----------------|
| `--fa-width` | Set the width of an icon | Any valid CSS `width` value |

## Icons in a List

| Class | Details |
|-------|---------|
| `fa-ul` | Used on `<ul>` or `<ol>` to style icons as list bullets |
| `fa-li` | Used on individual `<li>` elements for icon bullets |

| CSS Custom Property | Details | Accepted Values |
|---------------------|---------|-----------------|
| `--fa-li-margin` | Set margin around icon | Any valid CSS `margin` value |
| `--fa-li-width` | Set inline-size of icon | Any valid CSS `width` value |

## Rotating Icons

| Class | Details |
|-------|---------|
| `fa-rotate-90` | Rotates 90 degrees |
| `fa-rotate-180` | Rotates 180 degrees |
| `fa-rotate-270` | Rotates 270 degrees |
| `fa-flip-horizontal` | Mirrors horizontally |
| `fa-flip-vertical` | Mirrors vertically |
| `fa-flip-both` | Mirrors both vertically and horizontally |
| `fa-rotate-by` | Rotates by specific degree (requires `--fa-rotate-angle`) |

| CSS Custom Property | Details | Accepted Values |
|---------------------|---------|-----------------|
| `--fa-rotate-angle` | Set rotation angle of `.fa-rotate-by` | Any valid CSS `transform` rotate value |

## Animating Icons

| Class | Details |
|-------|---------|
| `fa-spin` | Spin 360 degrees clockwise |
| `fa-spin-pulse` | Spin 360 degrees clockwise in 8 incremental steps |
| `fa-spin-reverse` | With `fa-spin`/`fa-spin-pulse`, spin counter-clockwise |
| `fa-beat` | Scale up and down |
| `fa-fade` | Fade in and out using `opacity` |
| `fa-beat-fade` | Combine beat and fade |
| `fa-bounce` | Bounce up and down |
| `fa-flip` | Rotate about the Y axis |
| `fa-shake` | Shake left and right |

| CSS Custom Property | Details | Accepted Values |
|---------------------|---------|-----------------|
| `--fa-animation-delay` | Initial delay | Any valid CSS `animation-delay` value |
| `--fa-animation-direction` | Direction | Any valid CSS `animation-direction` value |
| `--fa-animation-duration` | Duration | Any valid CSS `animation-duration` value |
| `--fa-animation-iteration-count` | Iterations | Any valid CSS `animation-iteration-count` value |
| `--fa-animation-timing` | Timing function | Any valid CSS `animation-timing-function` value |
| `--fa-beat-scale` | Max scale for `fa-beat` | Any valid CSS number |
| `--fa-fade-opacity` | Lowest opacity for `fa-fade` | `0` to `1.0` |
| `--fa-beat-fade-opacity` | Lowest opacity for `fa-beat-fade` | `0` to `1.0` |
| `--fa-beat-fade-scale` | Max scale for `fa-beat-fade` | Any valid value |
| `--fa-flip-x` | X-axis rotation vector | `0` to `1` |
| `--fa-flip-y` | Y-axis rotation vector | `0` to `1` |
| `--fa-flip-z` | Z-axis rotation vector | `0` to `1` |
| `--fa-flip-angle` | Flip angle | Any valid CSS angle value |
| `--fa-bounce-height` | Bounce height | Any valid CSS length |
| `--fa-bounce-rebound` | Rebound amount | Any valid CSS length |
| `--fa-bounce-start-scale-x` | Starting horizontal scale | Any valid number |
| `--fa-bounce-start-scale-y` | Starting vertical scale | Any valid number |
| `--fa-bounce-jump-scale-x` | Mid-air horizontal scale | Any valid number |
| `--fa-bounce-jump-scale-y` | Mid-air vertical scale | Any valid number |
| `--fa-bounce-land-scale-x` | Landing horizontal scale | Any valid number |
| `--fa-bounce-land-scale-y` | Landing vertical scale | Any valid number |
| `--fa-shake-angle` | Shake angle | Any valid CSS angle value |

## Bordered Icons

| Class | Details |
|-------|---------|
| `fa-border` | Creates border with border-radius and padding around icon |

| CSS Custom Property | Details | Accepted Values |
|---------------------|---------|-----------------|
| `--fa-border-color` | Border color | Any valid CSS `border-color` value |
| `--fa-border-padding` | Padding around icon | Any valid CSS `padding` value |
| `--fa-border-radius` | Border radius | Any valid CSS `border-radius` value |
| `--fa-border-style` | Border style | Any valid CSS `border-style` value |
| `--fa-border-width` | Border width | Any valid CSS `border-width` value |

## Pulled Icons

| Class | Details |
|-------|---------|
| `fa-pull-start` | Float `inline-start` with `margin-inline-end` |
| `fa-pull-end` | Float `inline-end` with `margin-inline-start` |

| CSS Custom Property | Details | Accepted Values |
|---------------------|---------|-----------------|
| `--fa-pull-margin` | Set margin around icon | Any valid CSS `margin` value |

## Stacking Icons

| Class | Details |
|-------|---------|
| `fa-stack` | Parent element of two stacked icons |
| `fa-stack-1x` | Base size icon when stacked |
| `fa-stack-2x` | Larger icon when stacked |
| `fa-inverse` | Invert color of base-size stacked icon |

| CSS Custom Property | Details | Accepted Values |
|---------------------|---------|-----------------|
| `--fa-stack-z-index` | z-index of stacked icon | Any valid CSS `z-index` value |
| `--fa-inverse` | Color of inverted stacked icon | Any valid CSS `color` value |

## Duotone Icons

| Class | Details |
|-------|---------|
| `fa-swap-opacity` | Swap default opacity of duotone layers |

| CSS Custom Property | Details | Accepted Values |
|---------------------|---------|-----------------|
| `--fa-primary-color` | Primary layer color | Any valid CSS `color` value |
| `--fa-primary-opacity` | Primary layer opacity | `0` to `1.0` |
| `--fa-secondary-color` | Secondary layer color | Any valid CSS `color` value |
| `--fa-secondary-opacity` | Secondary layer opacity | `0` to `1.0` |

## Power Transforms (SVG+JS only)

| HTML `data-` Attribute | Details |
|------------------------|---------|
| `data-fa-transform="shrink-[value]"` | Shrinks icon |
| `data-fa-transform="grow-[value]"` | Grows icon |
| `data-fa-transform="up-[value]"` | Moves icon up |
| `data-fa-transform="right-[value]"` | Moves icon right |
| `data-fa-transform="down-[value]"` | Moves icon down |
| `data-fa-transform="left-[value]"` | Moves icon left |
| `data-fa-transform="rotate-[angle]"` | Rotates icon (negative numbers allowed) |
| `data-fa-transform="flip-h"` | Mirrors horizontally |
| `data-fa-transform="flip-v"` | Mirrors vertically |

Units are `1/16em` each. Accepts arbitrary values including decimals.

## Pseudo-elements CSS Custom Properties

| CSS Custom Property | Family + Style |
|---------------------|---------------|
| `--fa-font-solid` | Classic Solid |
| `--fa-font-regular` | Classic Regular |
| `--fa-font-light` | Classic Light |
| `--fa-font-thin` | Classic Thin |
| `--fa-font-duotone` | Duotone Solid |
| `--fa-font-duotone-regular` | Duotone Regular |
| `--fa-font-duotone-light` | Duotone Light |
| `--fa-font-duotone-thin` | Duotone Thin |
| `--fa-font-brands` | Brands Regular |
| `--fa-font-sharp-solid` | Sharp Solid |
| `--fa-font-sharp-regular` | Sharp Regular |
| `--fa-font-sharp-light` | Sharp Light |
| `--fa-font-sharp-thin` | Sharp Thin |
| `--fa-font-sharp-duotone-solid` | Sharp Duotone Solid |
| `--fa-font-sharp-duotone-regular` | Sharp Duotone Regular |
| `--fa-font-sharp-duotone-light` | Sharp Duotone Light |
| `--fa-font-sharp-duotone-thin` | Sharp Duotone Thin |
