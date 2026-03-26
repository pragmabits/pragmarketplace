---
name: md3-theming
description: "This skill should be used when the user asks about Material Design 3 theming, \"MD3 dark mode\", \"MD3 light dark theme\", \"MD3 custom theme\", \"MD3 dynamic color\", \"Material Design color scheme\", \"MD3 theme generation\", \"Material You theme\", \"@material/material-color-utilities\", \"HCT color space\", \"tonal spot scheme\", \"MD3 theme CSS variables\", \"MD3 theme switching\", \"prefers-color-scheme Material\", \"Material Design custom palette\", or any question about generating, customizing, or switching MD3 themes."
---

This skill provides guidance on Material Design 3 theming — generating color schemes, implementing light/dark mode, creating custom themes, and dynamic color — for framework-agnostic web implementation.

## Design System Detection

Before applying MD3 theming, verify the project uses Material Design 3. Check for `--md-sys-*` tokens, `@material/web` in package.json, or MD3 theme files. If not found, warn the user and offer to set up MD3 theming from scratch or adapt to the project's existing system.

## Theme Generation

### From a Source Color

MD3 generates complete themes from a single source color using the HCT color space:

1. Convert source color to HCT (Hue, Chroma, Tone)
2. Generate 5 tonal palettes:
   - **Primary**: source hue, chroma capped at 48
   - **Secondary**: source hue, chroma 16
   - **Tertiary**: source hue + 60°, chroma 24
   - **Neutral**: source hue, chroma 4
   - **Neutral Variant**: source hue, chroma 8
3. Each palette: 13 tone stops (0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 100)
4. Map tones to color roles for light and dark themes

### Using @material/material-color-utilities

```javascript
import {
  argbFromHex,
  themeFromSourceColor,
  applyTheme,
  hexFromArgb
} from '@material/material-color-utilities';

// Generate theme from source color
const theme = themeFromSourceColor(argbFromHex('#6750A4'));

// Access scheme colors
const lightScheme = theme.schemes.light;
const darkScheme = theme.schemes.dark;

// Convert to hex for CSS
const primaryHex = hexFromArgb(lightScheme.primary); // #6750A4
```

### Manual CSS Theme Definition

```css
:root,
[data-theme="light"] {
  color-scheme: light;

  /* Primary */
  --md-sys-color-primary: #6750A4;
  --md-sys-color-on-primary: #FFFFFF;
  --md-sys-color-primary-container: #EADDFF;
  --md-sys-color-on-primary-container: #21005D;

  /* Secondary */
  --md-sys-color-secondary: #625B71;
  --md-sys-color-on-secondary: #FFFFFF;
  --md-sys-color-secondary-container: #E8DEF8;
  --md-sys-color-on-secondary-container: #1D192B;

  /* Tertiary */
  --md-sys-color-tertiary: #7D5260;
  --md-sys-color-on-tertiary: #FFFFFF;
  --md-sys-color-tertiary-container: #FFD8E4;
  --md-sys-color-on-tertiary-container: #31111D;

  /* Error */
  --md-sys-color-error: #B3261E;
  --md-sys-color-on-error: #FFFFFF;
  --md-sys-color-error-container: #F9DEDC;
  --md-sys-color-on-error-container: #410E0B;

  /* Surface */
  --md-sys-color-surface: #FFFBFE;
  --md-sys-color-on-surface: #1C1B1F;
  --md-sys-color-surface-variant: #E7E0EC;
  --md-sys-color-on-surface-variant: #49454F;
  --md-sys-color-surface-container-lowest: #FFFFFF;
  --md-sys-color-surface-container-low: #F7F2FA;
  --md-sys-color-surface-container: #F3EDF7;
  --md-sys-color-surface-container-high: #ECE6F0;
  --md-sys-color-surface-container-highest: #E6E0E9;
  --md-sys-color-surface-tint: #6750A4;

  /* Utility */
  --md-sys-color-outline: #79747E;
  --md-sys-color-outline-variant: #CAC4D0;
  --md-sys-color-shadow: #000000;
  --md-sys-color-scrim: #000000;
  --md-sys-color-inverse-surface: #313033;
  --md-sys-color-inverse-on-surface: #F4EFF4;
  --md-sys-color-inverse-primary: #D0BCFF;
}
```

## Light/Dark Theme Switching

### Method 1: `prefers-color-scheme` (OS-Automatic)

```css
@media (prefers-color-scheme: dark) {
  :root {
    color-scheme: dark;
    --md-sys-color-primary: #D0BCFF;
    --md-sys-color-on-primary: #381E72;
    --md-sys-color-primary-container: #4F378B;
    --md-sys-color-on-primary-container: #EADDFF;
    --md-sys-color-surface: #1C1B1F;
    --md-sys-color-on-surface: #E6E1E5;
    /* ... all dark tokens ... */
  }
}
```

### Method 2: `data-theme` Attribute (User Toggle)

```css
[data-theme="dark"] {
  color-scheme: dark;
  --md-sys-color-primary: #D0BCFF;
  --md-sys-color-on-primary: #381E72;
  /* ... all dark tokens ... */
}
```

```javascript
// Toggle theme
function toggleTheme() {
  const current = document.documentElement.dataset.theme;
  document.documentElement.dataset.theme = current === 'dark' ? 'light' : 'dark';
}

// Respect OS preference as default
if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
  document.documentElement.dataset.theme = 'dark';
}
```

### Method 3: `light-dark()` CSS Function (Modern)

```css
:root {
  color-scheme: light dark;
  --md-sys-color-primary: light-dark(#6750A4, #D0BCFF);
  --md-sys-color-on-primary: light-dark(#FFFFFF, #381E72);
  --md-sys-color-surface: light-dark(#FFFBFE, #1C1B1F);
  /* ... */
}
```

## Custom Theme from Brand Color

To create a custom MD3 theme from a brand color:

1. Choose the brand color as the source/seed color
2. Generate tonal palettes using the HCT algorithm (or the Material Theme Builder tool at [material-foundation.github.io/material-theme-builder](https://material-foundation.github.io/material-theme-builder/))
3. Map tones to all color roles
4. Verify accessibility: every `on-*` token must achieve 4.5:1 contrast against its paired surface

### Quick Custom Theme Pattern

```css
/* Override just the key system colors — components inherit automatically */
:root {
  --md-sys-color-primary: #006D3B;       /* Brand green */
  --md-sys-color-on-primary: #FFFFFF;
  --md-sys-color-primary-container: #9CF5B0;
  --md-sys-color-on-primary-container: #00210E;
  /* ... generate remaining tokens from brand color ... */
}
```

## Scoped Theme Overrides

Apply different themes to sections of the page:

```css
.marketing-section {
  --md-sys-color-primary: #FF5722;
  --md-sys-color-on-primary: #FFFFFF;
  --md-sys-color-surface: #FBE9E7;
  --md-sys-color-on-surface: #3E2723;
}

.admin-panel {
  --md-sys-color-primary: #1565C0;
  --md-sys-color-on-primary: #FFFFFF;
}
```

CSS custom properties cascade naturally — scoped overrides affect all children.

## Tailwind CSS Integration

For projects using Tailwind CSS, map MD3 tokens to the Tailwind theme:

```css
/* Tailwind CSS 4 with @theme */
@theme {
  --color-primary: var(--md-sys-color-primary);
  --color-on-primary: var(--md-sys-color-on-primary);
  --color-primary-container: var(--md-sys-color-primary-container);
  --color-surface: var(--md-sys-color-surface);
  --color-on-surface: var(--md-sys-color-on-surface);
  /* ... map all needed tokens ... */
  --radius-sm: var(--md-sys-shape-corner-small);
  --radius-md: var(--md-sys-shape-corner-medium);
  --radius-lg: var(--md-sys-shape-corner-large);
  --radius-full: var(--md-sys-shape-corner-full);
}
```

Then use: `bg-primary text-on-primary rounded-md`.

## Documentation Resources

Consult `${CLAUDE_PLUGIN_ROOT}/docs/material-design/web/color-system.md` for the complete color role list, tone mappings, and baseline hex values.

### External Resources

- **Material Theme Builder**: [material-foundation.github.io/material-theme-builder](https://material-foundation.github.io/material-theme-builder/)
- **@material/material-color-utilities**: [npm](https://www.npmjs.com/package/@material/material-color-utilities)
- **Official theming docs**: [material-web.dev/theming](https://material-web.dev/theming/material-theming/)
