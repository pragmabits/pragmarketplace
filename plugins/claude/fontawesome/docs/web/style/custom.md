# Customizing Icons

Source: https://docs.fontawesome.com/web/style/custom

## CSS Custom Properties

Font Awesome offers extensive CSS custom properties organized by feature category.

### Core Properties

| Property | Purpose |
|----------|---------|
| `--fa-family` | Sets icon family |
| `--fa-style` | Sets icon style (font-weight) |
| `--fa-display` | Controls display value |
| `--fa-inverse` | Sets inverted icon color |

### Animation Properties

| Property | Purpose |
|----------|---------|
| `--fa-animation-delay` | Initial delay for animation |
| `--fa-animation-direction` | Direction for animation |
| `--fa-animation-duration` | Duration for animation |
| `--fa-animation-iteration-count` | Number of iterations |
| `--fa-animation-timing` | Animation timing function |
| `--fa-beat-scale` | Max scale for `fa-beat` |
| `--fa-fade-opacity` | Lowest opacity for `fa-fade` |
| `--fa-beat-fade-opacity` | Lowest opacity for `fa-beat-fade` |

### Transform Properties

| Property | Purpose |
|----------|---------|
| `--fa-rotate-angle` | Rotation for `.fa-rotate-by` |
| `--fa-flip-x` | X-coordinate of flip axis |
| `--fa-flip-y` | Y-coordinate of flip axis |
| `--fa-flip-z` | Z-coordinate of flip axis |
| `--fa-flip-angle` | Flip angle |

### Bounce Properties

| Property | Purpose |
|----------|---------|
| `--fa-bounce-height` | Bounce height |
| `--fa-bounce-rebound` | Rebound amount |
| `--fa-bounce-start-scale-x` | Starting horizontal scale |
| `--fa-bounce-start-scale-y` | Starting vertical scale |
| `--fa-bounce-jump-scale-x` | Mid-air horizontal scale |
| `--fa-bounce-jump-scale-y` | Mid-air vertical scale |
| `--fa-bounce-land-scale-x` | Landing horizontal scale |
| `--fa-bounce-land-scale-y` | Landing vertical scale |

### Border Properties

| Property | Purpose |
|----------|---------|
| `--fa-border-color` | Border color |
| `--fa-border-width` | Border width |
| `--fa-border-radius` | Border radius |
| `--fa-border-style` | Border style |
| `--fa-border-padding` | Padding inside border |

### Duotone Properties

| Property | Purpose |
|----------|---------|
| `--fa-primary-color` | Primary layer color |
| `--fa-secondary-color` | Secondary layer color |
| `--fa-primary-opacity` | Primary layer opacity |
| `--fa-secondary-opacity` | Secondary layer opacity |

### Counter Properties

| Property | Purpose |
|----------|---------|
| `--fa-counter-background-color` | Counter badge background |
| `--fa-counter-padding` | Counter badge padding |

### List and Positioning

| Property | Purpose |
|----------|---------|
| `--fa-li-margin` | List icon margin |
| `--fa-li-width` | List icon width |
| `--fa-top` | Top position |
| `--fa-right` | Right position |
| `--fa-bottom` | Bottom position |
| `--fa-left` | Left position |

### Family Switching

| Property | Purpose |
|----------|---------|
| `--fa-family-classic` | Classic family font-family value |
| `--fa-family-sharp` | Sharp family font-family value |
| `--fa-family-duotone` | Duotone family font-family value |

## Implementation Methods

### CSS :root Level

Defines properties globally affecting all icons:

```css
:root {
  --fa-family: var(--fa-family-classic);
  --fa-style: 400;
  --fa-border-color: red;
  --fa-primary-color: green;
  --fa-secondary-color: red;
}
```

### Project-Based CSS Rules

Scopes properties to specific selectors:

```css
.ye-olde-icon-dropcap {
  --fa-border-color: WhiteSmoke;
  --fa-border-padding: 2em;
  --fa-border-radius: 0.25em;
  --fa-pull-margin: 2em;
  font-size: 8em;
}

.track-quick-spin {
  --fa-spin-duration: 0.25s;
  --fa-spin-iteration-count: 1;
  --fa-spin-timing: ease-out;
}

.theme-slytherin {
  --fa-primary-color: darkgreen;
  --fa-secondary-color: silver;
}

.theme-sharp {
  font: var(--fa-font-sharp-solid);
}
```

### Inline Styles

Best for one-off customizations:

```html
<i class="fa-solid fa-bomb fa-rotate-by" style="--fa-rotate-angle: 45deg;"></i>
<i class="fa-duotone fa-solid fa-crow" style="--fa-primary-color: dodgerblue; --fa-secondary-color: gold;"></i>
```

> **Important:** Custom properties redefined in more specific selectors override `:root` definitions due to CSS cascade rules.

## Custom CSS Styling

Beyond custom properties, standard CSS can target icons through recommended selectors.

### Target Icons by Style

```css
.fa-solid { ... }
.fa-regular { ... }
.fa-light { ... }
.fa-thin { ... }
.fa-duotone { ... }
.fa-brands { ... }
.fa-sharp-solid { ... }
```

### Target Specific Icons

```css
.fa-user { ... }
.fa-font-awesome { ... }
```

### Practical Example

```css
.fa-solid,
.fa-brands,
.fa-sharp-solid {
  background-color: papayawhip;
  border-radius: 0.2em;
  padding: 0.3em;
}

.fa-fish {
  color: salmon;
}

.fa-frog {
  color: green;
}

.fa-user-ninja.vanished {
  opacity: 0.2;
}

.fa-facebook {
  color: rgb(59, 91, 152);
}
```

## Important Note for SVG + JS Framework

When using Font Awesome's SVG framework, the original `<i>` elements are replaced with `<svg>` elements by default. CSS rules must target the appropriate elements accordingly.
