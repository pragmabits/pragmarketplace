# shadcn/ui with Laravel

## Quick Start

```bash
pnpm dlx shadcn@latest init -t laravel
```

For monorepo:
```bash
pnpm dlx shadcn@latest init -t laravel --monorepo
```

## Adding Components

```bash
pnpm dlx shadcn@latest add button
```

## Usage with Inertia.js

Laravel typically uses Inertia.js for React integration:

```tsx
// resources/js/Pages/Welcome.tsx
import { Button } from "@/components/ui/button"

export default function Welcome() {
  return (
    <div>
      <Button>Click me</Button>
    </div>
  )
}
```

## Key Notes

- Works with Laravel + Inertia.js + React stack
- Components install relative to your `resources/js/` directory
- Path aliases configured in both `tsconfig.json` and `vite.config.ts`
- Uses Vite as the build tool (Laravel Vite plugin)
