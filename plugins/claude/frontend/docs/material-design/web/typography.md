# Material Design 3 — Typography Quick Reference

> Official docs: [m3.material.io/styles/typography](https://m3.material.io/styles/typography/overview)

## Type Scale (5 roles x 3 sizes = 15 styles)

Token pattern: `--md-sys-typescale-<role>-<size>-<property>`

Properties: `font`, `size`, `line-height`, `weight`, `tracking`

### Complete Type Scale Values

| Role + Size | Font Size | Line Height | Weight | Tracking |
|---|---|---|---|---|
| display-large | 57px / 3.5625rem | 64px / 4rem | 400 | -0.25px |
| display-medium | 45px / 2.8125rem | 52px / 3.25rem | 400 | 0px |
| display-small | 36px / 2.25rem | 44px / 2.75rem | 400 | 0px |
| headline-large | 32px / 2rem | 40px / 2.5rem | 400 | 0px |
| headline-medium | 28px / 1.75rem | 36px / 2.25rem | 400 | 0px |
| headline-small | 24px / 1.5rem | 32px / 2rem | 400 | 0px |
| title-large | 22px / 1.375rem | 28px / 1.75rem | 400 | 0px |
| title-medium | 16px / 1rem | 24px / 1.5rem | 500 | 0.15px |
| title-small | 14px / 0.875rem | 20px / 1.25rem | 500 | 0.1px |
| body-large | 16px / 1rem | 24px / 1.5rem | 400 | 0.5px |
| body-medium | 14px / 0.875rem | 20px / 1.25rem | 400 | 0.25px |
| body-small | 12px / 0.75rem | 16px / 1rem | 400 | 0.4px |
| label-large | 14px / 0.875rem | 20px / 1.25rem | 500 | 0.1px |
| label-medium | 12px / 0.75rem | 16px / 1rem | 500 | 0.5px |
| label-small | 11px / 0.6875rem | 16px / 1rem | 500 | 0.5px |

### Role Usage Guidelines

| Role | Purpose |
|---|---|
| **Display** | Hero text, large numerals. Short, impactful content only. |
| **Headline** | Section headings. High emphasis, brief text. |
| **Title** | Component headers (cards, dialogs, app bars). Medium emphasis. |
| **Body** | Paragraph text, long-form content. |
| **Label** | Buttons, chips, tabs, navigation items, captions. |

## Typeface Tokens

| Token | Purpose | Default |
|---|---|---|
| `--md-ref-typeface-brand` | Branded/display typeface | Roboto |
| `--md-ref-typeface-plain` | Body/utility typeface | Roboto |

## CSS Token Examples

```css
:root {
  /* Typeface references */
  --md-ref-typeface-brand: 'Google Sans', Roboto, system-ui, sans-serif;
  --md-ref-typeface-plain: Roboto, system-ui, sans-serif;

  /* Body Large tokens */
  --md-sys-typescale-body-large-font: var(--md-ref-typeface-plain);
  --md-sys-typescale-body-large-size: 1rem;
  --md-sys-typescale-body-large-line-height: 1.5rem;
  --md-sys-typescale-body-large-weight: 400;
  --md-sys-typescale-body-large-tracking: 0.031rem;

  /* Display Large tokens */
  --md-sys-typescale-display-large-font: var(--md-ref-typeface-brand);
  --md-sys-typescale-display-large-size: 3.5625rem;
  --md-sys-typescale-display-large-line-height: 4rem;
  --md-sys-typescale-display-large-weight: 400;
  --md-sys-typescale-display-large-tracking: -0.016rem;
}

/* Usage in components */
.headline {
  font-family: var(--md-sys-typescale-headline-large-font);
  font-size: var(--md-sys-typescale-headline-large-size);
  line-height: var(--md-sys-typescale-headline-large-line-height);
  font-weight: var(--md-sys-typescale-headline-large-weight);
  letter-spacing: var(--md-sys-typescale-headline-large-tracking);
}
```

## Weights Used

MD3 uses only two weights:
- **400 (Regular)**: Display, Headline, Title Large, Body
- **500 (Medium)**: Title Medium/Small, Label

## Accessibility Notes

- Support text scaling up to at least 200%
- Use `rem` units for font-size to respect user preferences
- Ensure minimum 4.5:1 contrast ratio for normal text (WCAG AA)
- Ensure minimum 3:1 contrast ratio for large text (>=18px regular or >=14px bold)
