# shadcn/ui with Next.js

## Quick Start

```bash
pnpm dlx shadcn@latest init -t next
```

For monorepo projects:
```bash
pnpm dlx shadcn@latest init -t next --monorepo
```

## Adding Components

```bash
pnpm dlx shadcn@latest add button
```

## Usage

```tsx
import { Button } from "@/components/ui/button"

export default function Home() {
  return (
    <div>
      <Button>Click me</Button>
    </div>
  )
}
```

## Key Features

- **Copy-paste components**: Components are copied directly into your project under `@/components/ui/`
- **RSC support**: React Server Components supported via `rsc: true` in components.json
- **Automatic `use client` directives**: Added automatically when `rsc` is enabled
- **App Router patterns**: Works with Next.js App Router layouts and pages
- **Accessibility built-in**: Components follow WAI-ARIA standards

## Available Component Libraries

Two UI foundations:
- **Radix UI**: Pre-built, accessible component primitives (default)
- **Base UI**: Comprehensive set of unstyled, accessible components

## Server vs Client Component Boundaries

When `rsc: true` in components.json:
- Interactive components (Dialog, Sheet, Dropdown) get `"use client"` automatically
- Layout components can be used in Server Components
- Form components require client-side hydration
