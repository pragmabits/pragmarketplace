# Sass (SCSS) Integration

Source: https://docs.fontawesome.com/web/use-with/scss

## SCSS Files

| File | Purpose |
|------|---------|
| `fontawesome.scss` | Main entry point |
| `_animated.scss` | Animation styles |
| `_bordered.scss` | Border styles |
| `_pulled.scss` | Pull/float styles |
| `_core.scss` | Core styles |
| `_widths.scss` | Width utilities |
| `_icons.scss` | Icon definitions |
| `_list.scss` | List styles |
| `_mixins.scss` | Sass mixins |
| `_rotated-flipped.scss` | Rotation/flip styles |
| `_sizing.scss` | Sizing utilities |
| `_stacked.scss` | Stack styles |
| `_variables.scss` | Variables |
| `_custom-icons.scss` | Custom icon support |

Plus individual style partials (solid, regular, light, thin, brands, etc.).

## Compatibility

Sass and Dart Sass are supported. `node-sass` and `libsass` are officially deprecated.

## Setup Steps

1. Copy `scss` and `webfonts` folders
2. Override `$font-path` via `@use` rule
3. Load core via `@use './fontawesome/fontawesome'` and helpers via `@use './fontawesome/fa' as fa`
4. Load individual styles: `@use './fontawesome/solid' as fa-solid`

## Custom SCSS

Use namespaced `fa` partial for variables, mixins, and individual style icon mixins:

```scss
// Variables
fa.$fw-width

// Mixins
@include fa.fa-size(xl);

// Individual style icon mixins
@include fa-solid.icon(fa.$var-user);
```

## Variables

| Variable | Purpose |
|----------|---------|
| `$css-prefix` | CSS class prefix |
| `$style` | Default style |
| `$family` | Default family |
| `$display` | Display property |
| `$font-display` | Font display strategy |
| `$fw-width` | Fixed width value |
| `$inverse` | Inverse color |
| `$border-color` | Border color |
| `$border-width` | Border width |
| `$border-radius` | Border radius |
| `$border-style` | Border style |
| `$border-padding` | Border padding |
| `$li-margin` | List icon margin |
| `$li-width` | List icon width |
| `$primary-opacity` | Duotone primary opacity |
| `$secondary-opacity` | Duotone secondary opacity |
| `$font-path` | Path to webfonts directory |

## Mixins/Functions

| Mixin/Function | Purpose |
|---------------|---------|
| `fa-icon()` | Core icon mixin |
| `fa-size()` | Size mixin |
| `fa-content()` | Content mixin |
| `icon()` | Individual style partials |

## Downloaded Kit Support

Custom icons via `_custom-icons.scss` and `custom-icons.woff2`.
