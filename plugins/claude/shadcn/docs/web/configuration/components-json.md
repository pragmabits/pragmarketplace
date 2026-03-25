# components.json Configuration Reference

## Overview

The `components.json` file configures your shadcn/ui project. It's **optional** if you're using copy-paste, but **required** for CLI-based component installation.

Create it by running: `pnpm dlx shadcn@latest init`

## Schema

```json
{
  "$schema": "https://ui.shadcn.com/schema.json"
}
```

## Core Configuration Fields

### style

Specifies component design style. **Cannot be changed after initialization.**

```json
{
  "style": "new-york"
}
```

*Note: The `default` style is deprecated; use `new-york` instead.*

### tailwind

#### tailwind.config
Path to your Tailwind configuration file. Leave blank for Tailwind CSS v4.

```json
{
  "tailwind": {
    "config": "tailwind.config.js"
  }
}
```

#### tailwind.css
Path to your CSS file importing Tailwind.

```json
{
  "tailwind": {
    "css": "styles/global.css"
  }
}
```

#### tailwind.baseColor
Default color palette. **Immutable after initialization.**

Options: `gray`, `neutral`, `slate`, `stone`, `zinc`, `mauve`, `olive`, `mist`, `taupe`

```json
{
  "tailwind": {
    "baseColor": "neutral"
  }
}
```

#### tailwind.cssVariables
Toggle CSS variables vs utility classes for theming. **Cannot be changed after init.** Requires component reinstallation to switch.

```json
{
  "tailwind": {
    "cssVariables": true
  }
}
```

#### tailwind.prefix
Utility class prefix for generated components.

```json
{
  "tailwind": {
    "prefix": "tw-"
  }
}
```

## Component Settings

### rsc
Enables React Server Components support. Automatically adds `use client` directives to client components.

```json
{
  "rsc": true
}
```

### tsx
Choose TypeScript or JavaScript output. Set to `false` for `.jsx` files.

```json
{
  "tsx": true
}
```

## Path Aliases

Must match `tsconfig.json` or `jsconfig.json` `paths` configuration.

```json
{
  "aliases": {
    "utils": "@/lib/utils",
    "components": "@/components",
    "ui": "@/app/ui",
    "lib": "@/lib",
    "hooks": "@/hooks"
  }
}
```

## Registries

Configure multiple resource registries for components from various sources.

### Basic Configuration

```json
{
  "registries": {
    "@v0": "https://v0.dev/chat/b/{name}",
    "@acme": "https://registry.acme.com/{name}.json",
    "@internal": "https://internal.company.com/{name}.json"
  }
}
```

### Advanced Configuration with Authentication

```json
{
  "registries": {
    "@private": {
      "url": "https://api.company.com/registry/{name}.json",
      "headers": {
        "Authorization": "Bearer ${REGISTRY_TOKEN}",
        "X-API-Key": "${API_KEY}"
      },
      "params": {
        "version": "latest"
      }
    }
  }
}
```

Environment variables in `${VAR_NAME}` format are automatically expanded.

### Installation from Namespaced Registries

```bash
npx shadcn@latest add @v0/dashboard
npx shadcn@latest add @private/button
npx shadcn@latest add @acme/header @internal/auth-utils
```
