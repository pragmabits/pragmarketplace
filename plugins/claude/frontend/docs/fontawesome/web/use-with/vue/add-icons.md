# Add Icons in Vue

Source: https://docs.fontawesome.com/web/use-with/vue/add-icons

## Kit Package Methods

### By Prefix and Name

```javascript
import { byPrefixAndName } from '@awesome.me/kit-KIT_CODE/icons'
```

```html
<FontAwesomeIcon :icon="byPrefixAndName.fas['house']" />
```

### Individual Icons (Best for tree-shaking)

Enables tree-shaking, allows aliasing for multi-style icons using camelCase.

### Whole Styles

Loads entire style packages but prevents tree-shaking.

### Library (Centralized Registration)

Register in `main.ts`/`main.js` with simplified template syntax (string or array formats).

## SVG Icon Packages

For projects unable to use Kit packages.

> **Note:** Pro+ and Custom icons aren't available with SVG Packages.

Methods include individual icon imports with library registration, whole style imports for Free packages, and multiple style combinations.

## Troubleshooting

- Missing icons when not in Kit subsets
- Hyphenated names requiring PascalCase conversion
- Self-closing tag considerations for inline/HTML templates
- Support for computed/component properties
