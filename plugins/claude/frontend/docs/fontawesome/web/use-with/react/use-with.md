# Use With Next.js / TypeScript

Source: https://docs.fontawesome.com/web/use-with/react/use-with

## Next.js

Must configure CSS imports. Without correct setup, icons appear huge because they are missing the accompanying CSS.

```javascript
import '@fortawesome/fontawesome-svg-core/styles.css'
import { config } from '@fortawesome/fontawesome-svg-core'
config.autoAddCss = false
```

Newer Next.js versions may require:

```javascript
import '../node_modules/@fortawesome/fontawesome-svg-core/styles.css'
```

> **Note:** Duotone icons appearing as solid = FA CSS not installed (CSS sets secondary layer opacity).

## TypeScript

Type definitions included. Key types:

- `IconLookup` from `@fortawesome/fontawesome-svg-core`
- `IconDefinition` from `@fortawesome/fontawesome-svg-core`
