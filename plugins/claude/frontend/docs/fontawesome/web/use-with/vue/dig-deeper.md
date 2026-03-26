# Dig Deeper with Vue

Source: https://docs.fontawesome.com/web/use-with/vue/dig-deeper

## Setting Default Styles

### Kit-Based

```javascript
import { library, config } from '@fortawesome/fontawesome-svg-core'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { all } from '@awesome.me/kit-KIT_CODE'
library.add(...all)
config.familyDefault = 'classic'
config.styleDefault = 'duotone'
```

### Package-Based

```javascript
import { config } from '@fortawesome/fontawesome-svg-core'
config.familyDefault = 'classic'
config.styleDefault = 'duotone'
```

## Tree Shaking

Keeping bundles small when using `import { faCoffee }` relies on tree-shaking. For tools lacking automatic tree-shaking, use explicit file paths:

```javascript
import { faCoffee } from '@fortawesome/free-solid-svg-icons/faCoffee'
```

Full style imports possible but warned: "use with caution as it can be thousands of icons."

## Advanced Patterns

Computed properties for dynamic icons, alternative component properties for conditional rendering.
