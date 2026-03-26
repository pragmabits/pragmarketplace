# How To Add Icons

Source: https://docs.fontawesome.com/web/add-icons/how-to

You can place Font Awesome icons just about anywhere, and icons take on characteristics and blend in with surrounding text naturally.

## Basics

Adding icons requires three pieces of information:

1. The shorthand class name for the desired style
2. The icon name, prefixed with `fa-`
3. The shorthand class name for the family (defaults to Classic if omitted)

**Basic Example:**

```html
<i class="fa-sharp fa-solid fa-user"></i>
```

Alternative syntax using `<span>`:

```html
<span class="fa-sharp fa-solid fa-user"></span>
```

> **Important:** Avoid creating custom classes starting with `fa-` as this can cause missing icons or unwanted behavior.

## Families + Styles

### Classic (Default Family)

| Style | Availability | Class | Font Family | Font Weight |
|-------|-------------|-------|-------------|-------------|
| Solid | Free or Pro | `fa-solid` | Font Awesome 7 Free/Pro | 900 |
| Regular | Free or Pro | `fa-regular` | Font Awesome 7 Free/Pro | 400 |
| Light | Pro only | `fa-light` | Font Awesome 7 Pro | 300 |
| Thin | Pro only | `fa-thin` | Font Awesome 7 Pro | 100 |

### Duotone

| Style | Availability | Class | Font Family | Font Weight |
|-------|-------------|-------|-------------|-------------|
| Solid | Pro only | `fa-duotone fa-solid` | Font Awesome 7 Duotone | 900 |
| Regular | Pro only | `fa-duotone fa-regular` | Font Awesome 7 Duotone | 400 |
| Light | Pro only | `fa-duotone fa-light` | Font Awesome 7 Duotone | 300 |
| Thin | Pro only | `fa-duotone fa-thin` | Font Awesome 7 Duotone | 100 |

### Sharp

| Style | Availability | Class | Font Family | Font Weight |
|-------|-------------|-------|-------------|-------------|
| Solid | Pro only | `fa-sharp fa-solid` | Font Awesome 7 Sharp | 900 |
| Regular | Pro only | `fa-sharp fa-regular` | Font Awesome 7 Sharp | 400 |
| Light | Pro only | `fa-sharp fa-light` | Font Awesome 7 Sharp | 300 |
| Thin | Pro only | `fa-sharp fa-thin` | Font Awesome 7 Sharp | 100 |

### Sharp Duotone

| Style | Availability | Class | Font Family | Font Weight |
|-------|-------------|-------|-------------|-------------|
| Solid | Pro only | `fa-sharp-duotone fa-solid` | Font Awesome 7 Sharp Duotone | 900 |
| Regular | Pro only | `fa-sharp-duotone fa-regular` | Font Awesome 7 Sharp Duotone | 400 |
| Light | Pro only | `fa-sharp-duotone fa-light` | Font Awesome 7 Sharp Duotone | 300 |
| Thin | Pro only | `fa-sharp-duotone fa-thin` | Font Awesome 7 Sharp Duotone | 100 |

### Brands

| Style | Availability | Class | Font Family | Font Weight |
|-------|-------------|-------|-------------|-------------|
| Brands | Free | `fa-brands` | Font Awesome 7 Brands | 400 |

### Small Batch Icon Packs (Pro+ only, ~200 curated icons each)

- **Chisel**: Regular (`fa-chisel fa-regular`, weight 400)
- **Etch**: Solid (`fa-etch fa-solid`, weight 900)
- **Graphite**: Thin (`fa-graphite fa-thin`, weight 100)
- **Jelly**: Regular (`fa-jelly fa-regular`, weight 400), Fill Regular (`fa-jelly-fill fa-regular`, weight 400), Duo Regular (`fa-jelly-duo fa-regular`, weight 400)
- **Notdog**: Solid (`fa-notdog fa-solid`, weight 900), Duo Solid (`fa-notdog-duo fa-solid`, weight 900)
- **Slab**: Regular (`fa-slab fa-regular`, weight 400), Press Regular (`fa-slab-press fa-regular`, weight 400)
- **Thumbprint**: Light (`fa-thumbprint fa-light`, weight 300)
- **Utility**: Semibold (`fa-utility fa-semibold`, weight 600), Fill Semibold (`fa-utility-fill fa-semibold`, weight 600), Duo Semibold (`fa-utility-duo fa-semibold`, weight 600)
- **Whiteboard**: Semibold (`fa-whiteboard fa-semibold`, weight 600)

### Kit-Based Custom Icons

| Style | Availability | Class | Font Family | Font Weight |
|-------|-------------|-------|-------------|-------------|
| Custom Icons | Pro Kits only | `fa-kit` | Font Awesome Kit | 400 |
| Custom Duotone Icons | Pro Kits only | `fa-kit-duotone` | Font Awesome Kit Duotone | 400 |

## Setting Different Families + Styles

```html
<!-- Classic family (default) -->
<i class="fa-solid fa-user"></i>
<i class="fa-regular fa-user"></i>
<i class="fa-light fa-user"></i>
<i class="fa-thin fa-user"></i>

<!-- Classic family (explicit) -->
<i class="fa-classic fa-solid fa-user"></i>
<i class="fa-classic fa-regular fa-user"></i>
<i class="fa-classic fa-light fa-user"></i>
<i class="fa-classic fa-thin fa-user"></i>

<!-- Duotone family -->
<i class="fa-duotone fa-solid fa-user"></i>
<i class="fa-duotone fa-regular fa-user"></i>
<i class="fa-duotone fa-light fa-user"></i>
<i class="fa-duotone fa-thin fa-user"></i>

<!-- Sharp family -->
<i class="fa-sharp fa-solid fa-user"></i>
<i class="fa-sharp fa-regular fa-user"></i>
<i class="fa-sharp fa-light fa-user"></i>
<i class="fa-sharp fa-thin fa-user"></i>

<!-- Sharp Duotone family -->
<i class="fa-sharp-duotone fa-solid fa-user"></i>
<i class="fa-sharp-duotone fa-regular fa-user"></i>
<i class="fa-sharp-duotone fa-light fa-user"></i>
<i class="fa-sharp-duotone fa-thin fa-user"></i>

<!-- Small Batch families -->
<i class="fa-chisel fa-regular fa-user"></i>
<i class="fa-etch fa-solid fa-user"></i>
<i class="fa-jelly fa-regular fa-user"></i>
<i class="fa-jelly-fill fa-regular fa-user"></i>
<i class="fa-jelly-duo fa-regular fa-user"></i>
<i class="fa-notdog fa-solid fa-user"></i>
<i class="fa-notdog-duo fa-solid fa-user"></i>
<i class="fa-slab fa-regular fa-user"></i>
<i class="fa-slab-press fa-regular fa-user"></i>
<i class="fa-thumbprint fa-light fa-user"></i>
<i class="fa-whiteboard fa-semibold fa-user"></i>

<!-- Brands -->
<i class="fa-brands fa-font-awesome"></i>
```

## SVG Framework Note

When using Font Awesome's SVG framework, DOM elements with Font Awesome classes are replaced with injected `<svg>` elements by default. Ensure CSS rules target the appropriate element.

## Aliases

Font Awesome v6 renamed many icons for consistency while maintaining backward compatibility through aliases. Both old and new names work interchangeably.

Supported style aliases: `fas` (Solid), `far` (Regular), `fal` (Light), `fat` (Thin), `fad` (Duotone), `fab` (Brands), `fass` (Sharp Solid), `fasr` (Sharp Regular).

```html
<!-- All render the same Solid icon -->
<i class="fa-solid fa-cutlery"></i>
<i class="fa-solid fa-utensils"></i>
<i class="fas fa-utensils"></i>

<!-- All render the same Sharp Solid icon -->
<i class="fa-sharp fa-solid fa-times"></i>
<i class="fa-sharp fa-solid fa-close"></i>
<i class="fass fa-xmark"></i>
```

## Alternate Ways to Add Icons

- **When using Web Fonts:** Add icons using CSS with pseudo-elements.
- **When using SVGs:** SVG Sprites, bare SVGs, SVG symbols, Unicode values, icon names.
- **Framework Integrations:** Vue, React, WordPress, Squarespace, SCSS/Sass, and more.
