# shadcn/ui with Astro

## Quick Start

```bash
pnpm dlx shadcn@latest init -t astro
```

For monorepo setups, add `--monorepo`.

## Adding Components

```bash
pnpm dlx shadcn@latest add button
```

## Usage

```astro
---
import { Button } from "@/components/ui/button"
---

<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width" />
    <title>Astro + shadcn/ui</title>
  </head>
  <body>
    <div class="grid place-items-center h-screen content-center">
      <Button client:load>Button</Button>
    </div>
  </body>
</html>
```

## Island Architecture

Astro uses island architecture for partial hydration. Interactive shadcn/ui components need client directives:

- `client:load` — Hydrate immediately on page load
- `client:idle` — Hydrate when browser is idle
- `client:visible` — Hydrate when component enters viewport

Non-interactive components (e.g., Card, Badge) can render as static HTML without client directives.
