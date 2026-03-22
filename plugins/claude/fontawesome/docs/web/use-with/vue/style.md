# Style Icons in Vue

Source: https://docs.fontawesome.com/web/use-with/vue/style

The entire Font Awesome styling toolkit is available in Vue with Vue-specific syntax.

## Size

T-shirt sizes (`2xs` to `2xl`) and literal (`1x` to `10x`):

```html
<font-awesome-icon icon="fa-solid fa-coffee" size="xs" />
<font-awesome-icon icon="fa-solid fa-coffee" size="6x" />
```

## Automatic Width

```html
<font-awesome-icon icon="fa-solid fa-coffee" widthAuto />
```

## Icons in a List

No Vue-specific syntax; use `fa-ul` and `fa-li` as usual.

## Rotate and Flip

```html
<font-awesome-icon icon="fa-solid fa-coffee" rotation="90" />
<font-awesome-icon icon="fa-solid fa-coffee" flip="horizontal" />
<font-awesome-icon icon="fa-solid fa-coffee" flip="both" />
```

### Custom Rotation

`rotateBy` boolean + `--fa-rotate-angle` CSS custom property:

```html
<font-awesome-icon icon="fa-solid fa-coffee" rotateBy style="--fa-rotate-angle: 329deg" />
```

## Animate Icons

```html
<font-awesome-icon icon="fa-solid fa-heart" beat />
<font-awesome-icon icon="fa-solid fa-circle-info" beat-fade />
<font-awesome-icon icon="fa-solid fa-basketball" bounce />
<font-awesome-icon icon="fa-solid fa-exclamation-triangle" fade />
<font-awesome-icon icon="fa-solid fa-compact-disc" flip />
<font-awesome-icon icon="fa-solid fa-bell" shake />
<font-awesome-icon icon="fa-solid fa-cog" spin />
<font-awesome-icon icon="fa-solid fa-compass" spin spin-reverse />
<font-awesome-icon icon="fa-solid fa-spinner" spin-pulse />
```

## Bordered and Pulled

`border` prop for borders. `pull="left"` / `pull="right"` for floated icons.

## Power Transforms

```html
<font-awesome-icon icon="fa-solid fa-coffee" transform="shrink-6 left-4" />
```

## Mask

```html
<font-awesome-icon icon="fa-solid fa-coffee" transform="shrink-7" mask="fa-solid fa-circle" />
```

## Duotone

`swap-opacity` prop to swap layer opacities.

## Layers

Requires importing `FontAwesomeLayers` and `FontAwesomeLayersText` components. Supports layering icons, text overlays, counters (positions: `bottom-left`, `bottom-right`, `top-left`, default `top-right`), and inversion (`inverse` prop).
