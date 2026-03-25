# CSS Animations Quick Reference

## Transitions

| Property | Values | Default |
|----------|--------|---------|
| `transition` | `<property> <duration> <easing> <delay>` | — |
| `transition-property` | `all`, `none`, specific properties | `all` |
| `transition-duration` | `<time>` (e.g., `0.3s`, `300ms`) | `0s` |
| `transition-timing-function` | `ease`, `linear`, `ease-in`, `ease-out`, `ease-in-out`, `cubic-bezier()`, `steps()` | `ease` |
| `transition-delay` | `<time>` | `0s` |
| `transition-behavior` | `normal`, `allow-discrete` | `normal` |

## Keyframe Animations

| Property | Values | Default |
|----------|--------|---------|
| `animation` | `<name> <duration> <easing> <delay> <count> <direction> <fill> <state>` | — |
| `animation-name` | `<keyframe-name>`, `none` | `none` |
| `animation-duration` | `<time>` | `0s` |
| `animation-timing-function` | Same as transition | `ease` |
| `animation-delay` | `<time>` | `0s` |
| `animation-iteration-count` | `<number>`, `infinite` | `1` |
| `animation-direction` | `normal`, `reverse`, `alternate`, `alternate-reverse` | `normal` |
| `animation-fill-mode` | `none`, `forwards`, `backwards`, `both` | `none` |
| `animation-play-state` | `running`, `paused` | `running` |
| `animation-composition` | `replace`, `add`, `accumulate` | `replace` |

## Transforms

| Function | Example | Notes |
|----------|---------|-------|
| `translate()` | `translate(10px, 20px)` | X and Y |
| `translateX()` | `translateX(50%)` | Horizontal |
| `translateY()` | `translateY(-10px)` | Vertical |
| `translateZ()` | `translateZ(100px)` | Depth (needs perspective) |
| `scale()` | `scale(1.5)` | Uniform scale |
| `scaleX()` / `scaleY()` | `scaleX(2)` | Axis scale |
| `rotate()` | `rotate(45deg)` | 2D rotation |
| `rotate3d()` | `rotate3d(1, 0, 0, 45deg)` | 3D rotation |
| `skew()` | `skew(10deg, 5deg)` | Shear |
| `perspective()` | `perspective(800px)` | 3D depth (per-element) |
| `matrix()` | `matrix(a, b, c, d, tx, ty)` | Combined 2D |

### Individual Transform Properties (Modern)

| Property | Example | Notes |
|----------|---------|-------|
| `translate` | `translate: 10px 20px` | Independent from transform |
| `rotate` | `rotate: 45deg` | Can animate independently |
| `scale` | `scale: 1.5` | Can animate independently |

## Easing Functions

| Easing | Cubic-Bezier | Character |
|--------|-------------|-----------|
| `linear` | `cubic-bezier(0, 0, 1, 1)` | Constant speed |
| `ease` | `cubic-bezier(0.25, 0.1, 0.25, 1)` | Quick start, slow end |
| `ease-in` | `cubic-bezier(0.42, 0, 1, 1)` | Slow start |
| `ease-out` | `cubic-bezier(0, 0, 0.58, 1)` | Slow end |
| `ease-in-out` | `cubic-bezier(0.42, 0, 0.58, 1)` | Slow start and end |
| `steps(n)` | `steps(4, jump-start)` | Discrete steps |
| `linear()` | `linear(0, 0.5 25%, 1)` | Custom linear easing |

## Scroll-Driven Animations

| Property | Values |
|----------|--------|
| `animation-timeline` | `scroll()`, `view()`, `<name>` |
| `animation-range` | `entry`, `exit`, `contain`, `cover` |
| `scroll-timeline` | `<name> <axis>` |
| `view-timeline` | `<name> <axis>` |

```css
/* Progress bar tied to page scroll */
.progress {
  animation: grow-width linear both;
  animation-timeline: scroll();
}

@keyframes grow-width {
  from { width: 0; }
  to { width: 100%; }
}

/* Fade in when element enters viewport */
.reveal {
  animation: fade-in linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 100%;
}
```

## Performance Properties

| Property | Purpose | Notes |
|----------|---------|-------|
| `will-change` | Hint browser about upcoming changes | Use sparingly; remove after animation |
| `transform: translateZ(0)` | Force compositing layer (hack) | Prefer `will-change` |
| `contain: layout` | Isolate layout recalculations | |
| `backface-visibility: hidden` | Optimize 3D transforms | |

### Compositor-Only Properties (Cheap to Animate)

- `transform` (translate, rotate, scale)
- `opacity`
- `filter`
- `backdrop-filter`

### Expensive to Animate (Trigger Layout/Paint)

- `width`, `height`, `top`, `left` — trigger layout
- `color`, `background`, `border` — trigger paint
- `box-shadow` — trigger paint (prefer `filter: drop-shadow()`)

## View Transition API

```css
/* Enable view transitions */
@view-transition {
  navigation: auto;
}

/* Name transitioning elements */
.card {
  view-transition-name: card-hero;
}

/* Customize transition animation */
::view-transition-old(card-hero) {
  animation: fade-out 0.3s ease;
}

::view-transition-new(card-hero) {
  animation: fade-in 0.3s ease;
}
```

## Accessibility

```css
/* Always respect user motion preferences */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}

/* Alternative: provide safe defaults */
@media (prefers-reduced-motion: no-preference) {
  .animated {
    animation: slide-in 0.5s ease;
  }
}
```

## Common Pitfalls

- **`animation-fill-mode: forwards`**: Keeps final state but the animation still "runs" — can interfere with hover states
- **`will-change` overuse**: Adding `will-change` to many elements wastes GPU memory; apply only during animation
- **Layout-triggering animations**: Animating `width`/`height` causes reflow every frame; use `transform: scale()` instead
- **`transition: all`**: Transitions every property change — be explicit about which properties to transition
- **Scroll-driven animation browser support**: Check baseline; fallback to IntersectionObserver for broader support
