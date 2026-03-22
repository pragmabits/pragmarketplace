# Animating Icons

Source: https://docs.fontawesome.com/web/style/animate

FontAwesome provides built-in animation utility classes. All animations are CSS-driven and work with both Web Fonts + CSS and SVG + JS.

## Animation Classes

| Class | Effect |
|-------|--------|
| `fa-beat` | Scales up and down (pulsing/heartbeat effect) |
| `fa-fade` | Fades in and out |
| `fa-beat-fade` | Combines beat and fade |
| `fa-bounce` | Bounces up and down |
| `fa-flip` | Flips along the Y axis in 3D (not the same as the static flip classes) |
| `fa-shake` | Shakes left and right |
| `fa-spin` | Continuous 360-degree rotation (clockwise) |
| `fa-spin-reverse` | Continuous 360-degree rotation (counter-clockwise) |
| `fa-spin-pulse` | Rotates in 8 discrete steps (like a loading spinner) |

## Examples

```html
<i class="fa-solid fa-heart fa-beat"></i>
<i class="fa-solid fa-triangle-exclamation fa-fade"></i>
<i class="fa-solid fa-heart fa-beat-fade"></i>
<i class="fa-solid fa-basketball fa-bounce"></i>
<i class="fa-solid fa-compact-disc fa-flip"></i>
<i class="fa-solid fa-bell fa-shake"></i>
<i class="fa-solid fa-spinner fa-spin"></i>
<i class="fa-solid fa-spinner fa-spin-pulse"></i>
<i class="fa-solid fa-spinner fa-spin fa-spin-reverse"></i>
```

## CSS Custom Properties for Fine-Tuning

Each animation exposes CSS custom properties for customization.

### fa-beat

| Property | Default | Purpose |
|----------|---------|---------|
| `--fa-beat-scale` | `1.25` | Maximum scale |

### fa-fade

| Property | Default | Purpose |
|----------|---------|---------|
| `--fa-fade-opacity` | `0.4` | Minimum opacity |

### fa-beat-fade

| Property | Default | Purpose |
|----------|---------|---------|
| `--fa-beat-fade-scale` | `1.125` | Maximum scale |
| `--fa-beat-fade-opacity` | `0.4` | Minimum opacity |

### fa-bounce

| Property | Default | Purpose |
|----------|---------|---------|
| `--fa-bounce-start-scale-x` | `1.1` | Starting horizontal scale |
| `--fa-bounce-start-scale-y` | `0.9` | Starting vertical scale |
| `--fa-bounce-jump-scale-x` | `0.9` | Mid-air horizontal scale |
| `--fa-bounce-jump-scale-y` | `1.1` | Mid-air vertical scale |
| `--fa-bounce-land-scale-x` | `1.05` | Landing horizontal scale |
| `--fa-bounce-land-scale-y` | `0.95` | Landing vertical scale |
| `--fa-bounce-height` | `-0.5em` | Bounce height |
| `--fa-bounce-rebound` | `-0.125em` | Rebound amount |

### fa-flip (animated)

| Property | Default | Purpose |
|----------|---------|---------|
| `--fa-flip-x` | `0` | X rotation amount |
| `--fa-flip-y` | `1` | Y rotation amount |
| `--fa-flip-z` | `0` | Z rotation amount |
| `--fa-flip-angle` | `-180deg` | Flip angle |

### fa-shake

| Property | Default | Purpose |
|----------|---------|---------|
| `--fa-shake-angle` | `15deg` | Rotation angle |

### fa-spin

| Property | Default | Purpose |
|----------|---------|---------|
| `--fa-animation-duration` | `2s` | Duration |
| `--fa-animation-iteration-count` | `infinite` | Iteration count |
| `--fa-animation-timing` | `linear` (for spin), `ease-in-out` (for others) | Easing function |

## Customization Examples

```html
<i class="fa-solid fa-heart fa-beat" style="--fa-beat-scale: 2.0;"></i>
<i class="fa-solid fa-heart fa-fade" style="--fa-fade-opacity: 0.1;"></i>
<i class="fa-solid fa-spinner fa-spin" style="--fa-animation-duration: 0.5s;"></i>
```

## Accessibility

Font Awesome animations support `prefers-reduced-motion` CSS media feature. When `prefers-reduced-motion: reduce` is set, animations are disabled for users with vestibular motion disorders.
