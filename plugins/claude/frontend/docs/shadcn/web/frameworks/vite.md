# shadcn/ui with Vite

## Quick Start

```bash
pnpm dlx shadcn@latest init -t vite
```

For monorepo projects:
```bash
pnpm dlx shadcn@latest init -t vite --monorepo
```

Alternative package managers:
- `npm dlx shadcn@latest init -t vite`
- `yarn dlx shadcn@latest init -t vite`
- `bun dlx shadcn@latest init -t vite`

## Adding Components

```bash
pnpm dlx shadcn@latest add button
```

## Usage

```typescript
import { Button } from "@/components/ui/button"

export default function App() {
  return (
    <div>
      <Button>Click me</Button>
    </div>
  )
}
```

## Path Aliases

Vite requires path alias configuration in `vite.config.ts`:

```typescript
import path from "path"
import { defineConfig } from "vite"

export default defineConfig({
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
```

Must match the aliases in `components.json` and `tsconfig.json`.
