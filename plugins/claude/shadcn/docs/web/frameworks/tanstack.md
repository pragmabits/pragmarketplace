# shadcn/ui with TanStack Start

## Quick Start

```bash
pnpm dlx shadcn@latest init -t start
```

For monorepo:
```bash
pnpm dlx shadcn@latest init -t start --monorepo
```

## Adding Components

```bash
pnpm dlx shadcn@latest add button
```

## Usage

```typescript
// app/routes/index.tsx
import { Button } from "@/components/ui/button"

function App() {
  return (
    <div>
      <Button>Click me</Button>
    </div>
  )
}
```

## Key Notes

- Full-stack type-safe framework
- Works with all standard package managers (pnpm, npm, yarn, bun)
- Supports TanStack Router file-based routing
