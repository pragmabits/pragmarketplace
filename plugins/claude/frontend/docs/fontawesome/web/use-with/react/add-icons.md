# Add Icons in React

Source: https://docs.fontawesome.com/web/use-with/react/add-icons

## Kit Package Approaches

### By Prefix and Name

```javascript
import { byPrefixAndName } from '@awesome.me/kit-KIT_CODE/icons'

<FontAwesomeIcon icon={byPrefixAndName.fas['house']} />
```

### Specific Icons (Best for tree-shaking)

```javascript
import { faHouse } from '@awesome.me/kit-KIT_CODE/icons/classic/solid'
```

### Library (Centralized Registration)

```javascript
import { library } from '@fortawesome/fontawesome-svg-core'
import { all } from '@awesome.me/kit-KIT_CODE/icons'
library.add(...all)
```

## SVG Package Methods

```javascript
import { faEnvelope } from '@fortawesome/free-solid-svg-icons'
const element = <FontAwesomeIcon icon={faEnvelope} />
```

> **Note:** Pro+ and Custom icons aren't available with SVG Packages. Custom icons with TypeScript require `@ts-ignore`. Hyphenated names convert to PascalCase (`circle-user` becomes `faCircleUser`).
