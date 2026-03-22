# Styling Basics

Source: https://docs.fontawesome.com/web/style/basics

## Overview

Font Awesome icons automatically inherit CSS size and color and blend in with text inline wherever you put them. The framework applies minimal styling rules to ensure proper rendering in context.

**Prerequisites:** Setup with Font Awesome in your project and familiarity with adding Font Awesome icons.

## Code Examples

### Inline Size and Color (em units)

```html
<span style="font-size: 3em; color: Tomato;">
  <i class="fa-solid fa-camera"></i>
</span>
```

### Pixel-Based Sizing

```html
<span style="font-size: 48px; color: Dodgerblue;">
  <i class="fa-solid fa-camera"></i>
</span>
```

### Nested Styling (rem units)

```html
<span style="font-size: 3rem;">
  <span style="color: Mediumslateblue;">
    <i class="fa-solid fa-camera"></i>
  </span>
</span>
```

## Additional Resources

The documentation references broader styling utilities available for sizing, alignment, rotation, transformation, and animation, plus custom CSS approaches for extended customization.
