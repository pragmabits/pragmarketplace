# CSS Quick Reference

## 4. CSS Quick Reference

### Box Model & Layout

| Property | Values / Pattern | Purpose |
|----------|-----------------|---------|
| `display` | `block`, `inline`, `flex`, `grid`, `inline-flex`, `inline-grid`, `contents`, `none` | Element display type |
| `box-sizing` | `border-box`, `content-box` | Box model calculation |
| `position` | `static`, `relative`, `absolute`, `fixed`, `sticky` | Positioning scheme |
| `float` | `left`, `right`, `none`, `inline-start`, `inline-end` | Float (legacy layout) |
| `overflow` | `visible`, `hidden`, `scroll`, `auto`, `clip` | Overflow handling |
| `contain` | `none`, `layout`, `paint`, `size`, `content`, `strict` | Containment |
| `container-type` | `inline-size`, `size`, `normal` | Container query target |
| `content-visibility` | `auto`, `visible`, `hidden` | Rendering optimization |

### Flexbox

| Property | Context | Values |
|----------|---------|--------|
| `display: flex` | Container | Establishes flex context |
| `flex-direction` | Container | `row`, `column`, `row-reverse`, `column-reverse` |
| `flex-wrap` | Container | `nowrap`, `wrap`, `wrap-reverse` |
| `justify-content` | Container | `start`, `end`, `center`, `space-between`, `space-around`, `space-evenly` |
| `align-items` | Container | `stretch`, `start`, `end`, `center`, `baseline` |
| `align-content` | Container | Same as justify-content (multi-line) |
| `gap` | Container | `<length>` or `<row> <column>` |
| `flex` | Item | `<grow> <shrink> <basis>` shorthand |
| `flex-grow` | Item | `<number>` (default: 0) |
| `flex-shrink` | Item | `<number>` (default: 1) |
| `flex-basis` | Item | `<length>`, `auto`, `content` |
| `align-self` | Item | Overrides `align-items` for single item |
| `order` | Item | `<integer>` (default: 0) |

### Grid

| Property | Context | Values |
|----------|---------|--------|
| `display: grid` | Container | Establishes grid context |
| `grid-template-columns` | Container | Track sizes, `repeat()`, `fr`, `minmax()`, `auto-fill`, `auto-fit` |
| `grid-template-rows` | Container | Same as columns |
| `grid-template-areas` | Container | Named area strings |
| `grid-auto-flow` | Container | `row`, `column`, `dense` |
| `grid-auto-rows` | Container | Implicit row sizing |
| `grid-auto-columns` | Container | Implicit column sizing |
| `gap` | Container | `<row> <column>` |
| `grid-column` | Item | `<start> / <end>`, `span <n>` |
| `grid-row` | Item | `<start> / <end>`, `span <n>` |
| `grid-area` | Item | `<name>` or `<row-start> / <col-start> / <row-end> / <col-end>` |
| `subgrid` | Item (as container) | `grid-template-columns: subgrid` |
| `place-items` | Container | `<align> <justify>` shorthand |
| `place-content` | Container | `<align> <justify>` shorthand |
| `place-self` | Item | `<align> <justify>` shorthand |

### Common Grid Patterns

```css
/* Responsive auto-fill grid */
.grid-auto {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(min(250px, 100%), 1fr));
  gap: 1rem;
}

/* Holy grail layout */
.layout {
  display: grid;
  grid-template: "header header header" auto
                 "nav    main   aside" 1fr
                 "footer footer footer" auto
               / 200px  1fr    200px;
  min-height: 100dvh;
}

/* Centering */
.center {
  display: grid;
  place-items: center;
}
```

### Selectors

| Selector | Specificity | Example |
|----------|-------------|---------|
| Universal `*` | (0,0,0) | `*` |
| Type | (0,0,1) | `div`, `p` |
| Class | (0,1,0) | `.card` |
| Attribute | (0,1,0) | `[type="text"]` |
| Pseudo-class | (0,1,0) | `:hover`, `:first-child` |
| ID | (1,0,0) | `#main` |
| Pseudo-element | (0,0,1) | `::before`, `::after` |
| `:is()` | Highest in list | `:is(.a, #b)` → (1,0,0) |
| `:where()` | (0,0,0) always | `:where(.a, #b)` → (0,0,0) |
| `:has()` | Highest in argument | `:has(.active)` → (0,1,0) |
| `:not()` | Highest in argument | `:not(#id)` → (1,0,0) |
| `@layer` | Lower than unlayered | Layered styles yield to unlayered |

### Specificity Rules Summary

1. Inline styles beat everything (except `!important`)
2. `!important` reverses the cascade — layered `!important` beats unlayered `!important`
3. ID > Class/Attribute/Pseudo-class > Type/Pseudo-element
4. `:where()` always contributes zero specificity — use for resettable defaults
5. `:is()` and `:not()` take the specificity of their most specific argument
6. Later rules win when specificity is equal (source order)
7. `@layer` establishes explicit cascade priority — unlayered styles always win over layered ones

### Cascade Layers

```css
/* Declare layer order (first = lowest priority) */
@layer reset, base, components, utilities;

@layer reset {
  *, *::before, *::after {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
}

@layer base {
  body { font-family: system-ui, sans-serif; }
  a { color: var(--link-color); }
}

@layer components {
  .card { /* component styles */ }
  .button { /* component styles */ }
}

@layer utilities {
  .sr-only { /* screen reader only */ }
  .visually-hidden { /* visually hidden */ }
}

/* Unlayered styles always beat layered styles */
.override { color: red; }
```

### Custom Properties (CSS Variables)

| Pattern | Example |
|---------|---------|
| Declaration | `--color-primary: oklch(0.6 0.2 260);` |
| Usage | `color: var(--color-primary);` |
| Fallback | `color: var(--color-primary, blue);` |
| Scoped | `.dark { --color-primary: oklch(0.8 0.15 260); }` |
| Inherited | Custom properties inherit by default |
| @property | `@property --hue { syntax: "<angle>"; inherits: false; initial-value: 0deg; }` |
| Calculation | `calc(var(--spacing) * 2)` |
| Conditional | Toggle patterns with `--flag: ;` or `--flag: initial;` |

### @property Registration

```css
@property --gradient-angle {
  syntax: "<angle>";
  inherits: false;
  initial-value: 0deg;
}

.animated-gradient {
  --gradient-angle: 0deg;
  background: conic-gradient(from var(--gradient-angle), red, blue, red);
  transition: --gradient-angle 1s;
}

.animated-gradient:hover {
  --gradient-angle: 360deg;
}
```

### Colors

| Function | Example | Notes |
|----------|---------|-------|
| `oklch()` | `oklch(0.7 0.15 250)` | Perceptually uniform, recommended |
| `lch()` | `lch(70% 50 250)` | CIE perceptual |
| `oklab()` | `oklab(0.7 -0.1 0.1)` | Perceptual, lab-based |
| `hsl()` | `hsl(250 50% 70%)` | Legacy but familiar |
| `rgb()` | `rgb(100 150 200)` | Classic, space-separated |
| `color-mix()` | `color-mix(in oklch, var(--a) 70%, var(--b))` | Mix two colors |
| `light-dark()` | `light-dark(white, black)` | Auto dark mode |
| `color()` | `color(display-p3 1 0 0)` | Wide gamut |

### Responsive Design

| Feature | Syntax | Use Case |
|---------|--------|----------|
| Media query (width) | `@media (min-width: 768px)` | Viewport breakpoints |
| Media query (range) | `@media (768px <= width < 1024px)` | Modern range syntax |
| Media query (preference) | `@media (prefers-color-scheme: dark)` | Dark mode |
| Media query (motion) | `@media (prefers-reduced-motion: reduce)` | Accessibility |
| Media query (contrast) | `@media (prefers-contrast: more)` | High contrast |
| Container query (size) | `@container (min-inline-size: 400px)` | Component-level |
| Container query (style) | `@container style(--theme: dark)` | Style-based |
| `clamp()` | `font-size: clamp(1rem, 2.5vw, 2rem)` | Fluid values |
| `min()` | `width: min(100%, 600px)` | Constrained max |
| `max()` | `width: max(300px, 50%)` | Constrained min |
| Viewport units | `dvh`, `svh`, `lvh`, `dvw`, `svw`, `lvw` | Dynamic viewport |
| Container units | `cqi`, `cqb`, `cqw`, `cqh`, `cqmin`, `cqmax` | Relative to container |

### Container Queries

```css
/* Define a container */
.card-wrapper {
  container-type: inline-size;
  container-name: card;
}

/* Query the container */
@container card (min-inline-size: 400px) {
  .card {
    display: grid;
    grid-template-columns: 200px 1fr;
  }
}

@container card (min-inline-size: 600px) {
  .card {
    grid-template-columns: 300px 1fr;
    gap: 2rem;
  }
}

/* Style queries */
@container style(--variant: compact) {
  .card { padding: 0.5rem; }
}
```

### Animations & Transitions

| Property | Values | Purpose |
|----------|--------|---------|
| `transition` | `<property> <duration> <easing> <delay>` | Shorthand |
| `transition-property` | `all`, specific props, `none` | What to animate |
| `transition-duration` | `0.3s`, `300ms` | How long |
| `transition-timing-function` | `ease`, `linear`, `ease-in-out`, `cubic-bezier()`, `linear()` | Easing |
| `transition-behavior` | `allow-discrete` | Animate discrete properties (display, overlay) |
| `animation` | `<name> <duration> <easing> <delay> <count> <direction> <fill> <play-state>` | Shorthand |
| `animation-timeline` | `scroll()`, `view()`, `auto` | Scroll-driven |
| `@starting-style` | Block of initial styles | Entry animations |
| `@keyframes` | `from/to` or `%` steps | Define animation |

### @starting-style (Entry Animations)

```css
.dialog {
  opacity: 1;
  transform: scale(1);
  transition: opacity 0.3s, transform 0.3s, display 0.3s allow-discrete;

  @starting-style {
    opacity: 0;
    transform: scale(0.95);
  }
}

/* Exit state */
.dialog[hidden] {
  opacity: 0;
  transform: scale(0.95);
}
```

### Scroll-Driven Animations

```css
@keyframes fade-in {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}

/* Scroll progress on the page */
.progress-bar {
  animation: grow-width linear;
  animation-timeline: scroll(root block);
}

/* View timeline — animate as element enters viewport */
.reveal {
  animation: fade-in linear both;
  animation-timeline: view();
  animation-range: entry 0% entry 100%;
}
```

### View Transitions

```css
/* Opt in to view transitions */
@view-transition {
  navigation: auto;
}

/* Name elements for cross-page transitions */
.hero-image {
  view-transition-name: hero;
}

/* Customize the transition */
::view-transition-old(hero) {
  animation: fade-out 0.3s ease-out;
}
::view-transition-new(hero) {
  animation: fade-in 0.3s ease-in;
}
```

### Typography

| Property | Values | Purpose |
|----------|--------|---------|
| `font-family` | Named fonts, `system-ui`, `sans-serif` | Font stack |
| `font-size` | `<length>`, `clamp()`, `rem`, `em` | Size |
| `font-weight` | `100`-`900`, `normal`, `bold` | Weight |
| `font-variation-settings` | `"wght" 600, "wdth" 75` | Variable fonts |
| `font-optical-sizing` | `auto`, `none` | Optical sizing |
| `line-height` | Unitless `1.5` preferred | Leading |
| `letter-spacing` | `<length>` | Tracking |
| `text-wrap` | `balance`, `pretty`, `stable`, `nowrap` | Text wrapping |
| `text-overflow` | `ellipsis`, `clip` | Overflow text |
| `overflow-wrap` | `break-word`, `anywhere` | Word breaking |
| `word-break` | `break-all`, `keep-all` | Word breaking |
| `hyphens` | `auto`, `manual`, `none` | Hyphenation |
| `font-display` | `swap`, `fallback`, `optional` | @font-face loading |

### Modern Text Patterns

```css
/* Fluid typography */
body {
  font-size: clamp(1rem, 0.875rem + 0.5vw, 1.25rem);
}

/* Balance headings */
h1, h2, h3 {
  text-wrap: balance;
}

/* Pretty paragraph wrapping */
p {
  text-wrap: pretty;
}

/* Truncate with ellipsis */
.truncate {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Multi-line truncation */
.line-clamp {
  display: -webkit-box;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 3;
  overflow: hidden;
}
```

### Visual Effects

| Property | Values | Purpose |
|----------|--------|---------|
| `filter` | `blur()`, `brightness()`, `contrast()`, `grayscale()`, `saturate()`, `drop-shadow()` | Element filters |
| `backdrop-filter` | Same functions as filter | Background filters |
| `mix-blend-mode` | `multiply`, `screen`, `overlay`, `darken`, `lighten` | Blending |
| `clip-path` | `circle()`, `ellipse()`, `polygon()`, `inset()`, `path()` | Clipping |
| `mask-image` | `url()`, `linear-gradient()` | Masking |
| `box-shadow` | `<offset-x> <offset-y> <blur> <spread> <color>` | Box shadows |
| `text-shadow` | `<offset-x> <offset-y> <blur> <color>` | Text shadows |
| `outline` | `<width> <style> <color>` | Outline (no layout) |
| `outline-offset` | `<length>` | Offset from border |
| `border-image` | `source slice width outset repeat` | Image borders |
| `background-clip` | `text` | Text fill with background |
| `paint-order` | `stroke fill markers` | SVG/text paint order |

### Scroll Behavior

| Property | Values | Purpose |
|----------|--------|---------|
| `scroll-behavior` | `smooth`, `auto` | Smooth scrolling |
| `scroll-snap-type` | `x mandatory`, `y proximity`, `both` | Snap scrolling |
| `scroll-snap-align` | `start`, `center`, `end` | Snap points |
| `scroll-snap-stop` | `always`, `normal` | Force stop |
| `scroll-padding` | `<length>` | Scroll padding |
| `scroll-margin` | `<length>` | Snap margin |
| `overscroll-behavior` | `auto`, `contain`, `none` | Overscroll |
| `scrollbar-width` | `auto`, `thin`, `none` | Scrollbar width |
| `scrollbar-color` | `<thumb> <track>` | Scrollbar colors |
| `scrollbar-gutter` | `stable`, `stable both-edges` | Reserve scrollbar space |

### Scroll Snap Pattern

```css
.carousel {
  display: flex;
  overflow-x: auto;
  scroll-snap-type: x mandatory;
  scrollbar-width: none; /* Hide scrollbar */
  gap: 1rem;
}

.carousel > * {
  scroll-snap-align: start;
  flex: 0 0 min(300px, 80%);
}
```

### Logical Properties

| Physical | Logical | Direction |
|----------|---------|-----------|
| `margin-left` | `margin-inline-start` | Start of inline axis |
| `margin-right` | `margin-inline-end` | End of inline axis |
| `margin-top` | `margin-block-start` | Start of block axis |
| `margin-bottom` | `margin-block-end` | End of block axis |
| `padding-left` | `padding-inline-start` | Inline start |
| `width` | `inline-size` | Inline dimension |
| `height` | `block-size` | Block dimension |
| `min-width` | `min-inline-size` | Min inline |
| `max-height` | `max-block-size` | Max block |
| `top` | `inset-block-start` | Block start |
| `left` | `inset-inline-start` | Inline start |
| `border-left` | `border-inline-start` | Inline start border |
| `text-align: left` | `text-align: start` | Start alignment |

### Anchor Positioning

```css
/* Define an anchor */
.trigger {
  anchor-name: --tooltip-anchor;
}

/* Position relative to anchor */
.tooltip {
  position: fixed;
  position-anchor: --tooltip-anchor;
  inset-area: top center;
  margin-block-end: 0.5rem;

  /* Fallback if not enough space */
  position-try-fallbacks: bottom center, right center;
}
```

### Popover API + CSS

```css
[popover] {
  &:popover-open {
    opacity: 1;
    transform: scale(1);
  }

  opacity: 0;
  transform: scale(0.95);
  transition: opacity 0.2s, transform 0.2s, display 0.2s allow-discrete;

  @starting-style {
    &:popover-open {
      opacity: 0;
      transform: scale(0.95);
    }
  }
}

/* Backdrop */
[popover]::backdrop {
  background: oklch(0 0 0 / 0.3);
  transition: background 0.2s;
}
```

### Native CSS Nesting

```css
.card {
  padding: 1rem;
  border: 1px solid var(--border);

  .title {
    font-size: 1.25rem;
    font-weight: 600;
  }

  .content {
    margin-block-start: 0.5rem;
  }

  &:hover {
    border-color: var(--border-hover);
  }

  &.highlighted {
    background: var(--highlight);
  }

  @media (min-width: 768px) {
    padding: 2rem;
  }
}
```

### :has() Relational Selector

```css
/* Parent has a checked input */
.form-group:has(input:checked) {
  border-color: var(--success);
}

/* Card with image gets different layout */
.card:has(> img) {
  grid-template-rows: 200px 1fr;
}

/* Form is valid when all required fields are valid */
form:has(:required:invalid) .submit-btn {
  opacity: 0.5;
  pointer-events: none;
}

/* Previous sibling selector (combined with ~) */
.item:has(~ .item:hover) {
  opacity: 0.7;
}

/* Quantity queries */
.grid:has(> :nth-child(4)) {
  grid-template-columns: repeat(2, 1fr);
}
```

## 5. Preprocessor Guidance

### SCSS/Sass Patterns

#### Variables and Maps

```scss
// Design tokens
$colors: (
  "primary": oklch(0.6 0.2 260),
  "secondary": oklch(0.7 0.15 150),
  "danger": oklch(0.6 0.22 25),
);

$spacing: (
  "xs": 0.25rem,
  "sm": 0.5rem,
  "md": 1rem,
  "lg": 1.5rem,
  "xl": 2rem,
);

// Access with map-get
.box {
  padding: map-get($spacing, "md");
  color: map-get($colors, "primary");
}
```

#### Mixins

```scss
// Responsive mixin
@mixin respond-to($breakpoint) {
  $breakpoints: (
    "sm": 640px,
    "md": 768px,
    "lg": 1024px,
    "xl": 1280px,
  );

  @media (min-width: map-get($breakpoints, $breakpoint)) {
    @content;
  }
}

// Usage
.container {
  padding: 1rem;

  @include respond-to("md") {
    padding: 2rem;
  }
}

// Visually hidden mixin
@mixin visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip-path: inset(50%);
  white-space: nowrap;
  border: 0;
}
```

#### Functions

```scss
// Strip units
@function strip-unit($value) {
  @return $value / ($value * 0 + 1);
}

// Fluid value generator
@function fluid($min, $max, $min-vw: 320px, $max-vw: 1200px) {
  $slope: ($max - $min) / ($max-vw - $min-vw);
  $intercept: $min - $slope * $min-vw;
  @return clamp(#{$min}, #{$intercept} + #{$slope * 100}vw, #{$max});
}

// Usage
h1 {
  font-size: fluid(1.5rem, 3rem);
}
```

#### Module System (@use / @forward)

```scss
// _tokens.scss
$primary: oklch(0.6 0.2 260);
$radius: 0.5rem;

// _mixins.scss
@use "tokens";

@mixin card {
  border-radius: tokens.$radius;
  border: 1px solid oklch(0 0 0 / 0.1);
}

// main.scss
@use "tokens";
@use "mixins";

.card {
  @include mixins.card;
  color: tokens.$primary;
}
```

**Important**: Always prefer `@use` and `@forward` over `@import`. Sass `@import` is deprecated and will be removed.

### Less Patterns

#### Variables and Mixins

```less
// Variables
@primary: oklch(0.6 0.2 260);
@spacing-md: 1rem;
@border-radius: 0.5rem;

// Mixin
.card() {
  border-radius: @border-radius;
  padding: @spacing-md;
}

// Parametric mixin
.respond-to(@breakpoint) {
  @media (min-width: @breakpoint) {
    @content();
  }
}

// Usage
.card {
  .card();
  color: @primary;
}
```

#### When Guards

```less
.color-variant(@color) when (lightness(@color) > 50%) {
  color: black;
  background: @color;
}

.color-variant(@color) when (lightness(@color) <= 50%) {
  color: white;
  background: @color;
}
```

### PostCSS Plugin Setup

#### Common PostCSS Configuration

```javascript
// postcss.config.js
module.exports = {
  plugins: {
    'postcss-preset-env': {
      stage: 2,
      features: {
        'nesting-rules': true,
        'custom-media-queries': true,
        'media-query-ranges': true,
      },
      autoprefixer: { grid: 'autoplace' },
    },
    'cssnano': process.env.NODE_ENV === 'production' ? {} : false,
  },
};
```

#### Popular PostCSS Plugins

| Plugin | Purpose |
|--------|---------|
| `autoprefixer` | Add vendor prefixes automatically |
| `postcss-preset-env` | Use future CSS today (polyfills) |
| `cssnano` | Minification and optimization |
| `postcss-import` | Inline @import statements |
| `postcss-nesting` | CSS nesting (spec-compliant) |
| `postcss-custom-media` | Custom media queries |
| `postcss-mixins` | Sass-like mixins in CSS |
| `postcss-functions` | Custom functions |
| `postcss-pxtorem` | Convert px to rem |
| `stylelint` | CSS linting (via postcss) |

#### Vite + SCSS Setup

```typescript
// vite.config.ts
import { defineConfig } from 'vite';

export default defineConfig({
  css: {
    preprocessorOptions: {
      scss: {
        // Modern API (Dart Sass)
        api: 'modern-compiler',
        // Shared variables/mixins (injected into every SCSS file)
        additionalData: `@use "@/styles/tokens" as *;`,
      },
    },
    devSourcemap: true,
  },
});
```

```bash
# Install Sass
pnpm add -D sass-embedded
# or
pnpm add -D sass
```

#### Vite + Less Setup

```typescript
// vite.config.ts
export default defineConfig({
  css: {
    preprocessorOptions: {
      less: {
        math: 'always',
        globalVars: {
          primaryColor: '#1890ff',
        },
      },
    },
  },
});
```

#### Vite + PostCSS Setup

```typescript
// vite.config.ts
export default defineConfig({
  css: {
    postcss: './postcss.config.js',
    // or inline:
    postcss: {
      plugins: [
        autoprefixer(),
      ],
    },
  },
});
```

### CSS Modules

```css
/* Button.module.css */
.button {
  padding: 0.5rem 1rem;
  border-radius: 0.25rem;
}

.primary {
  composes: button;
  background: var(--primary);
  color: var(--primary-foreground);
}
```

```typescript
// Usage (framework-dependent)
import styles from './Button.module.css';
// styles.button, styles.primary
```

#### Vite CSS Modules Configuration

```typescript
// vite.config.ts
export default defineConfig({
  css: {
    modules: {
      localsConvention: 'camelCase',
      scopeBehaviour: 'local',
      generateScopedName: '[name]__[local]___[hash:base64:5]',
    },
  },
});
```

