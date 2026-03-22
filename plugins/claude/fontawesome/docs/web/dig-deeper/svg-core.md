# SVG Core

Source: https://docs.fontawesome.com/web/dig-deeper/svg-core

The `@fortawesome/fontawesome-svg-core` package is for specialized scenarios:

- **Icon subsetting**: Reduce bundle size by including only icons you use
- **Foundation for integrations**: Base for React, Angular, Vue, and Ember components
- **Module bundling**: Works with Webpack, Rollup, and Parcel
- **Module loaders**: Compatible with RequireJS and similar systems

Supports ES6 modules and **tree shaking**.

## Comparing Basic Packages vs SVG Core

### Basic Packages (`@fortawesome/fontawesome-free` and `@fortawesome/fontawesome-pro`)

- Quick integration without deep technical knowledge
- Automatic behavior with minimal configuration
- Automatically replaces `<i>` tags with `<svg>` tags

### SVG Core Package

- Built for specialized use cases and advanced scenarios
- No automatic behavior or side-effects
- Requires explicit configuration and control
- Powers Font Awesome's official framework components

## Key Difference — DOM Replacement

With the core package, you must manually configure icon rendering:

```javascript
import { library, dom } from '@fortawesome/fontawesome-svg-core'
import { faUserAstronaut } from '@fortawesome/free-solid-svg-icons'

library.add(faUserAstronaut)
dom.watch()
```

`dom.watch()` establishes a MutationObserver to continuously replace tags as the DOM changes.
