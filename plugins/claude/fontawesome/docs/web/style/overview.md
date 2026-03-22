# Styling with Font Awesome

Source: https://docs.fontawesome.com/web/style/

FontAwesome icons inherit the `font-size` and `color` of their parent container by default. This means you can style them with CSS or utility classes (like Tailwind) naturally.

## Basic Usage

```html
<i class="fa-solid fa-camera"></i>
```

## Changing Color and Size with CSS

```html
<i class="fa-solid fa-camera" style="font-size: 3em; color: tomato;"></i>
```

## With Tailwind CSS

```html
<i class="fa-solid fa-camera text-primary text-2xl"></i>
```

## Key Points

- Icons are inline elements by default.
- They inherit `color` and `font-size` from the parent.
- Width is set to a fixed value so icons of different shapes align well (`fa-fw` for fixed width).

## Utility Classes

### Fixed Width

The `fa-fw` class forces a fixed width (useful in lists, nav items, or anywhere alignment matters):

```html
<i class="fa-solid fa-home fa-fw"></i> Home
<i class="fa-solid fa-cog fa-fw"></i> Settings
```

### Border

The `fa-border` class adds a border around the icon:

```html
<i class="fa-solid fa-quote-left fa-border"></i>
```

### Inverse

The `fa-inverse` class sets the icon color to white (useful when stacking on dark backgrounds):

```html
<span class="fa-stack">
  <i class="fa-solid fa-circle fa-stack-2x"></i>
  <i class="fa-solid fa-home fa-stack-1x fa-inverse"></i>
</span>
```

## Feature Compatibility: Web Fonts + CSS vs SVG + JS

| Feature | Web Fonts + CSS | SVG + JS |
|---------|-----------------|----------|
| **Sizing** (`fa-xs` through `fa-10x`) | Yes | Yes |
| **Animations** (`fa-spin`, `fa-beat`, `fa-bounce`, etc.) | Yes | Yes |
| **Rotate** (`fa-rotate-90/180/270`, `fa-rotate-by`) | Yes | Yes |
| **Flip** (`fa-flip-horizontal/vertical/both`) | Yes | Yes |
| **Pull** (`fa-pull-left/right`) | Yes | Yes |
| **Stacking** (`fa-stack`, `fa-stack-1x/2x`) | Yes | Yes |
| **Fixed Width** (`fa-fw`) | Yes | Yes |
| **Border** (`fa-border`) | Yes | Yes |
| **Inverse** (`fa-inverse`) | Yes | Yes |
| **Layers** (`fa-layers`) | Partial | Yes |
| **Power Transforms** (`data-fa-transform`) | No | Yes |
| **Masking** (`data-fa-mask`) | No | Yes |
| **Duotone** | No (Pro only) | Pro only |
