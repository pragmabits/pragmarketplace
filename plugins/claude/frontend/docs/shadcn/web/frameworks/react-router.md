# shadcn/ui with React Router

## Quick Start

```bash
pnpm dlx shadcn@latest init -t react-router
```

For monorepo setups:
```bash
pnpm dlx shadcn@latest init -t react-router --monorepo
```

## Adding Components

```bash
pnpm dlx shadcn@latest add button
```

## Usage

```typescript
// app/routes/home.tsx
import { Button } from "@/components/ui/button"
import type { Route } from "./+types/home"

export function meta({}: Route.MetaArgs) {
  return [
    { title: "New React Router App" },
    { name: "description", content: "Welcome to React Router!" },
  ]
}

export default function Home() {
  return (
    <div className="flex min-h-svh flex-col items-center justify-center">
      <Button>Click me</Button>
    </div>
  )
}
```

## Key Notes

- Works with React Router v7+ file-based routing
- Supports loader/action patterns for data fetching
- Components install to the configured `@/components/ui/` path
