# shadcn/ui Reference

## 4. CLI Reference

### init (alias: create)
```bash
npx shadcn@latest init
```
| Flag | Description |
|------|-------------|
| `-t, --template` | Framework: next, vite, start, react-router, laravel, astro |
| `-b, --base` | Component library: radix, base |
| `-p, --preset` | Preset config by name, URL, or code |
| `-n, --name` | Project name |
| `-d, --defaults` | Use default config |
| `-y, --yes` | Skip confirmation |
| `-f, --force` | Force overwrite |
| `--monorepo` | Scaffold monorepo |
| `--rtl` | Enable RTL support |
| `--css-variables` | Use CSS variables (default: true) |

### add
```bash
npx shadcn@latest add [component]
```
| Flag | Description |
|------|-------------|
| `-y, --yes` | Skip confirmation |
| `-o, --overwrite` | Overwrite existing files |
| `-a, --all` | Add all components |
| `-p, --path` | Custom install path |
| `-s, --silent` | Mute output |
| `--dry-run` | Preview changes |
| `--diff [path]` | Show file differences |
| `--view [path]` | Display file contents |

### Other Commands
- **view**: `npx shadcn@latest view [item]` — Preview registry items
- **search**: `npx shadcn@latest search [registry] -q "query"` — Search registries
- **build**: `npx shadcn@latest build` — Generate registry JSON files
- **docs**: `npx shadcn@latest docs [component]` — Fetch component docs
- **info**: `npx shadcn@latest info` — Show project config
- **migrate**: `npx shadcn@latest migrate [migration]` — Run migrations (rtl, radix)

## 5. Configuration (components.json)

```json
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "new-york",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.js",
    "css": "app/globals.css",
    "baseColor": "neutral",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "ui": "@/components/ui",
    "utils": "@/lib/utils",
    "lib": "@/lib",
    "hooks": "@/hooks"
  },
  "registries": {
    "@v0": "https://v0.dev/chat/b/{name}"
  }
}
```

### Key Fields
- **style**: `"new-york"` (default style deprecated, use new-york)
- **rsc**: React Server Components — adds `"use client"` to client components
- **tsx**: `true` for TypeScript, `false` for JavaScript
- **tailwind.baseColor**: neutral, stone, zinc, slate, gray, mauve, olive, mist, taupe
- **tailwind.cssVariables**: Use CSS variables for theming (immutable after init)
- **aliases**: Must match tsconfig.json paths

## 6. Component Catalog

### Categories

| Category | Components |
|----------|-----------|
| **Form** | Button, Input, Textarea, Select, Checkbox, Radio Group, Switch, Slider, Date Picker, Combobox, Form |
| **Layout** | Card, Separator, Aspect Ratio, Scroll Area, Resizable |
| **Data Display** | Table, Badge, Avatar, Calendar, Chart, Carousel |
| **Navigation** | Navigation Menu, Breadcrumb, Tabs, Pagination, Sidebar, Command |
| **Overlay/Feedback** | Dialog, Sheet, Drawer, Alert Dialog, Popover, Tooltip, Hover Card, Toast, Alert, Progress, Skeleton, Spinner |
| **Menus** | Dropdown Menu, Context Menu, Menubar |
| **Misc** | Accordion, Collapsible, Toggle, Toggle Group |

### Composition Patterns

**Compound components** — Most use sub-component composition:
```tsx
<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Title</DialogTitle>
      <DialogDescription>Description</DialogDescription>
    </DialogHeader>
  </DialogContent>
</Dialog>
```

**asChild pattern** — Render different element, keep behavior:
```tsx
<Button asChild>
  <Link href="/login">Login</Link>
</Button>
```

**data-icon attribute** — Proper icon spacing:
```tsx
<Button>
  <Icon data-icon="inline-start" />
  Label
</Button>
```

### Customization Approaches
1. **Modify source directly** — Edit `components/ui/*.tsx`
2. **Add variants** — Extend `cva()` definitions
3. **Compose** — Wrap in higher-order components
4. **Override styles** — Use className prop with Tailwind

## 7. Theming System

### CSS Variable Convention
Background + foreground pairs. The `background` suffix is omitted:
- `--primary` → `bg-primary`
- `--primary-foreground` → `text-primary-foreground`

### Core Variables
```
--background, --foreground
--card, --card-foreground
--popover, --popover-foreground
--primary, --primary-foreground
--secondary, --secondary-foreground
--muted, --muted-foreground
--accent, --accent-foreground
--destructive, --destructive-foreground
--border, --input, --ring, --radius
--chart-1 through --chart-5
--sidebar-*, --sidebar-*-foreground (sidebar theming)
```

### OKLCH Format
```css
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --primary: oklch(0.205 0 0);
}

.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --primary: oklch(0.922 0 0);
}
```

### Adding Custom Colors
```css
:root {
  --warning: oklch(0.84 0.16 84);
  --warning-foreground: oklch(0.28 0.07 46);
}

@theme inline {
  --color-warning: var(--warning);
  --color-warning-foreground: var(--warning-foreground);
}
```
Use: `bg-warning text-warning-foreground`

### Base Colors
Available at init: Neutral, Stone, Zinc, Slate, Gray, Mauve, Olive, Mist, Taupe

### Dark Mode

**Next.js** — Use `next-themes`:
```bash
pnpm add next-themes
```
1. Create ThemeProvider wrapping NextThemesProvider
2. Wrap root layout with `<ThemeProvider attribute="class" defaultTheme="system" enableSystem>`
3. Add ModeToggle component

**Vite** — Custom provider with React Context:
1. Create ThemeProvider using createContext + localStorage
2. Manage light/dark/system on document root classList
3. Add ModeToggle with useTheme hook

## 8. Framework-Specific Guidance

### Next.js
```bash
npx shadcn@latest init -t next
```
- RSC support via `rsc: true` — auto-adds `"use client"` directives
- App Router: layouts, pages, server/client boundaries
- Interactive components (Dialog, Sheet, Dropdown) = client components
- Layout components (Card, Badge) = can be server components

### Vite
```bash
npx shadcn@latest init -t vite
```
- Configure path aliases in `vite.config.ts`
- Must match `tsconfig.json` and `components.json` aliases

### Astro
```bash
npx shadcn@latest init -t astro
```
- Island architecture: interactive components need client directives
- `client:load` — Hydrate immediately
- `client:idle` — Hydrate when idle
- `client:visible` — Hydrate when visible
- Non-interactive components render as static HTML

### React Router
```bash
npx shadcn@latest init -t react-router
```
- Works with React Router v7+ file-based routing
- Supports loader/action patterns

### TanStack Start
```bash
npx shadcn@latest init -t start
```
- Full-stack type-safe framework
- TanStack Router file-based routing

### Laravel
```bash
npx shadcn@latest init -t laravel
```
- Works with Laravel + Inertia.js + React
- Path aliases in both `tsconfig.json` and `vite.config.ts`

## 9. Registry & Distribution

### Custom Registry in components.json
```json
{
  "registries": {
    "@v0": "https://v0.dev/chat/b/{name}",
    "@acme": "https://registry.acme.com/{name}.json",
    "@private": {
      "url": "https://api.company.com/registry/{name}.json",
      "headers": {
        "Authorization": "Bearer ${REGISTRY_TOKEN}"
      }
    }
  }
}
```

### Install from Registry
```bash
npx shadcn@latest add @v0/dashboard
npx shadcn@latest add @acme/header
```

### Build Registry
```bash
npx shadcn@latest build --output ./public/registry
```

### Design System Presets
```bash
npx shadcn@latest init --preset <name-or-url>
```

