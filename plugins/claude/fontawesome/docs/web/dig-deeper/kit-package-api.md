# Kit Package API

Source: https://docs.fontawesome.com/web/dig-deeper/kit-package-api

## Prerequisites

- Project setup using a modern package manager
- Configured access to Font Awesome packages
- A Kit with Package Installation enabled for Pro+ icons

## Package Contents

| Directory | Contents |
|-----------|----------|
| `css/*` | Stylesheets for modern browsers |
| `scss/*` | Sass files for webfont directory |
| `webfonts/*` | WOFF2 font files |
| `js/*` | Auto-loading SVG + JS technology files |
| `modules/*` | ESM & CommonJS modules (SVG Core-compatible) |
| `sprites/*` | Sprite sheets for all icons |
| `svg/*` | Individual SVG files |
| `metadata/*` | JSON and YAML icon metadata |

## JavaScript API Methods

### `byPrefixAndName[prefix][iconName]`

Accesses icons by prefix and name:

```javascript
byPrefixAndName.fas['house']
// Returns: { prefix, iconName, icon array, Unicode value, SVG path data }
```

## Icon Prefixes by Pack

| Pack | Style | Prefix | Availability |
|------|-------|--------|-------------|
| Kit Custom | Custom | `fak` | — |
| Kit Custom | Duotone | `fakd` | — |
| Classic | Solid | `fas` | Free |
| Classic | Regular | `far` | Pro |
| Classic | Light | `fal` | Pro |
| Classic | Thin | `fat` | Pro |
| Duotone | Solid | `fad` | Pro |
| Duotone | Regular | `fadr` | Pro |
| Duotone | Light | `fadl` | Pro |
| Duotone | Thin | `fadt` | Pro |
| Sharp | Solid | `fass` | Pro |
| Sharp | Regular | `fasr` | Pro |
| Sharp | Light | `fasl` | Pro |
| Sharp | Thin | `fast` | Pro |
| Sharp Duotone | Solid | `fasds` | Pro |
| Sharp Duotone | Regular | `fasdr` | Pro |
| Sharp Duotone | Light | `fasdl` | Pro |
| Sharp Duotone | Thin | `fasdt` | Pro |
| Brands | Brands | `fab` | Free |

### Pro+ Small Batch Packs

Chisel Regular (`facr`), Etch Solid (`faes`), Jelly Regular (`fajr`), Jelly Fill Regular (`fajfr`), Jelly Duo Regular (`fajdr`), Notdog Solid (`fans`), Notdog Duo Solid (`fands`), Slab Regular (`faslr`), Slab Press Regular (`faslpr`), Thumbprint Light (`fatl`), Whiteboard Semibold (`fawsb`)

## Import Examples

### By Pack

```javascript
import { fas, far, fal } from '@awesome.me/kit-KIT_CODE/icons'
import { fass, fasr, fasl } from '@awesome.me/kit-KIT_CODE/icons'
import { fab } from '@awesome.me/kit-KIT_CODE/icons'
import { fak } from '@awesome.me/kit-KIT_CODE/icons'
```

### Individual Icons (for tree-shaking)

```javascript
import { faUser } from '@awesome.me/kit-KIT_CODE/icons/classic/solid'
import { faUser } from '@awesome.me/kit-KIT_CODE/icons/classic/regular'
import { faUser } from '@awesome.me/kit-KIT_CODE/icons/classic/light'
import { faUser } from '@awesome.me/kit-KIT_CODE/icons/sharp/solid'
import { faUser } from '@awesome.me/kit-KIT_CODE/icons/sharp/regular'
import { faUser } from '@awesome.me/kit-KIT_CODE/icons/sharp/light'
import { faFontAwesome } from '@awesome.me/kit-KIT_CODE/icons/brands'
import { faMyIcon } from '@awesome.me/kit-KIT_CODE/icons/kit/custom'
```

### `all[]` Array

An array containing every icon in a Kit, best used with custom-subsetted Kits. Works well paired with the SVG Core Library for registration.

## TypeScript Configuration

Required `tsconfig.json` `moduleResolution` settings:

| Setting | Status |
|---------|--------|
| `nodenext` | Recommended |
| `bundler` | Supported alternative |
| `node16` | Supported but not recommended |
| `node`, `classic`, `node10` | Unsupported |

### Module Augmentation for SVG Core APIs (custom icons)

```typescript
import { icon, findIconDefinition } from "@fortawesome/fontawesome-svg-core"
import type { IconLookup, IconName } from "@awesome.me/kit-KIT_CODE/icons"
import type { IconDefinition } from "@fortawesome/fontawesome-common-types"

declare module "@fortawesome/fontawesome-svg-core" {
  export function icon(icon: IconName | IconLookup, params?: IconParams): Icon
  export function findIconDefinition(iconLookup: IconLookup): IconDefinition
}
```

## Troubleshooting

- **404 Error**: Run update before install:
  ```bash
  npm update '@awesome.me/kit-KIT_CODE'
  npm install --save '@awesome.me/kit-KIT_CODE@latest'
  ```
- **Windows NPM Issues**: Use double quotes:
  ```bash
  npm install --save "@awesome.me/kit-[KIT_CODE]@latest"
  ```
- **Tree-Shaking**: Using `all` and icon packs prevents tree-shaking. Custom-subsetted Kits provide similar benefits without technical complexity.
