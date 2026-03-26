# Material Design 3 — Color System Quick Reference

> Official docs: [m3.material.io/styles/color](https://m3.material.io/styles/color/overview)

## Key Concepts

- Colors are derived from **key colors** through the **HCT color space** (Hue, Chroma, Tone)
- **5 key color roles** generate tonal palettes: Primary, Secondary, Tertiary, Neutral, Neutral Variant
- Each key color produces a **tonal palette of 13 tones**: 0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 100
- Tone 0 = pure black; Tone 100 = pure white

## Color Roles — Complete Token List

### Accent Colors (Primary / Secondary / Tertiary — same pattern)

| Token | Light Tone | Dark Tone |
|---|---|---|
| `--md-sys-color-primary` | P-40 | P-80 |
| `--md-sys-color-on-primary` | P-100 | P-20 |
| `--md-sys-color-primary-container` | P-90 | P-30 |
| `--md-sys-color-on-primary-container` | P-10 | P-90 |
| `--md-sys-color-primary-fixed` | P-90 | P-90 |
| `--md-sys-color-primary-fixed-dim` | P-80 | P-80 |
| `--md-sys-color-on-primary-fixed` | P-10 | P-10 |
| `--md-sys-color-on-primary-fixed-variant` | P-30 | P-30 |

Replace `primary` with `secondary` (S-tones) or `tertiary` (T-tones) for those roles.

### Error Colors

| Token | Light Tone | Dark Tone |
|---|---|---|
| `--md-sys-color-error` | E-40 | E-80 |
| `--md-sys-color-on-error` | E-100 | E-20 |
| `--md-sys-color-error-container` | E-90 | E-30 |
| `--md-sys-color-on-error-container` | E-10 | E-90 |

### Surface Colors

| Token | Light Tone | Dark Tone |
|---|---|---|
| `--md-sys-color-surface` | N-99 | N-10 |
| `--md-sys-color-on-surface` | N-10 | N-90 |
| `--md-sys-color-surface-variant` | NV-90 | NV-30 |
| `--md-sys-color-on-surface-variant` | NV-30 | NV-80 |
| `--md-sys-color-surface-dim` | N-87 | N-6 |
| `--md-sys-color-surface-bright` | N-98 | N-24 |
| `--md-sys-color-surface-container-lowest` | N-100 | N-4 |
| `--md-sys-color-surface-container-low` | N-96 | N-10 |
| `--md-sys-color-surface-container` | N-94 | N-12 |
| `--md-sys-color-surface-container-high` | N-92 | N-17 |
| `--md-sys-color-surface-container-highest` | N-90 | N-22 |
| `--md-sys-color-surface-tint` | P-40 | P-80 |

P = Primary, N = Neutral, NV = Neutral Variant

### Utility Colors

| Token | Light Tone | Dark Tone |
|---|---|---|
| `--md-sys-color-outline` | NV-50 | NV-60 |
| `--md-sys-color-outline-variant` | NV-80 | NV-30 |
| `--md-sys-color-shadow` | N-0 | N-0 |
| `--md-sys-color-scrim` | N-0 | N-0 |
| `--md-sys-color-inverse-surface` | N-20 | N-90 |
| `--md-sys-color-inverse-on-surface` | N-95 | N-20 |
| `--md-sys-color-inverse-primary` | P-80 | P-40 |

## Baseline Theme Default Values (Light)

| Token | Hex |
|---|---|
| `--md-sys-color-primary` | `#6750A4` |
| `--md-sys-color-on-primary` | `#FFFFFF` |
| `--md-sys-color-primary-container` | `#EADDFF` |
| `--md-sys-color-on-primary-container` | `#21005D` |
| `--md-sys-color-secondary` | `#625B71` |
| `--md-sys-color-on-secondary` | `#FFFFFF` |
| `--md-sys-color-secondary-container` | `#E8DEF8` |
| `--md-sys-color-on-secondary-container` | `#1D192B` |
| `--md-sys-color-tertiary` | `#7D5260` |
| `--md-sys-color-on-tertiary` | `#FFFFFF` |
| `--md-sys-color-tertiary-container` | `#FFD8E4` |
| `--md-sys-color-on-tertiary-container` | `#31111D` |
| `--md-sys-color-error` | `#B3261E` |
| `--md-sys-color-on-error` | `#FFFFFF` |
| `--md-sys-color-error-container` | `#F9DEDC` |
| `--md-sys-color-on-error-container` | `#410E0B` |
| `--md-sys-color-surface` | `#FFFBFE` |
| `--md-sys-color-on-surface` | `#1C1B1F` |
| `--md-sys-color-surface-variant` | `#E7E0EC` |
| `--md-sys-color-on-surface-variant` | `#49454F` |
| `--md-sys-color-outline` | `#79747E` |
| `--md-sys-color-outline-variant` | `#CAC4D0` |

## Dynamic Color

### HCT Color Space

- **H** (Hue): 0-360, circular color spectrum
- **C** (Chroma): 0-~120, color purity/saturation
- **T** (Tone): 0-100, lightness (0 = black, 100 = white)

### Tonal Palette Generation from Source Color

1. Convert source color to HCT
2. Generate 5 palettes:
   - **Primary**: source hue, chroma capped at 48
   - **Secondary**: source hue, chroma set to 16
   - **Tertiary**: source hue + 60 degrees, chroma set to 24
   - **Neutral**: source hue, chroma set to 4
   - **Neutral Variant**: source hue, chroma set to 8
3. Each palette: 13 tone stops (0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 95, 99, 100)
4. Map tones to color roles using the light/dark table above

### Implementation Library

`@material/material-color-utilities` (npm) — TypeScript, Dart, Java. Provides `Hct`, `SchemeContent`, `SchemeMonochrome`, `SchemeTonalSpot`, etc.

## CSS Usage

```css
:root {
  --md-sys-color-primary: #6750A4;
  --md-sys-color-on-primary: #FFFFFF;
  --md-sys-color-primary-container: #EADDFF;
  /* ... all tokens ... */
}

/* Dark theme override */
[data-theme="dark"],
.dark {
  --md-sys-color-primary: #D0BCFF;
  --md-sys-color-on-primary: #381E72;
  --md-sys-color-primary-container: #4F378B;
  /* ... dark values ... */
}

/* Using prefers-color-scheme */
@media (prefers-color-scheme: dark) {
  :root {
    --md-sys-color-primary: #D0BCFF;
    /* ... */
  }
}
```
