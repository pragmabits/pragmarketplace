# shadcn/ui Documentation

Official documentation sourced from https://ui.shadcn.com/docs/.

## Directory Structure

```
docs/web/
├── getting-started/
│   ├── introduction.md          # Core concepts, philosophy
│   └── installation.md          # Installation overview, framework options
├── cli/
│   └── cli-reference.md         # Complete CLI commands (init, add, view, search, build, docs, info, migrate)
├── components/
│   ├── patterns.md              # Component catalog, composition patterns, customization
│   ├── button.md                # Button variants, sizes, props, examples
│   ├── dialog.md                # Dialog compound component pattern
│   ├── form.md                  # Form with React Hook Form + Zod
│   └── data-table.md            # TanStack Table integration (sorting, filtering, pagination)
├── configuration/
│   └── components-json.md       # components.json schema (style, tailwind, aliases, registries)
├── theming/
│   ├── theming.md               # CSS variables, OKLCH format, color naming, base colors
│   └── dark-mode.md             # Dark mode (Next.js with next-themes, Vite custom provider, toggle)
├── frameworks/
│   ├── nextjs.md                # Next.js setup (App Router, RSC)
│   ├── vite.md                  # Vite setup (path aliases)
│   ├── astro.md                 # Astro setup (island architecture, client directives)
│   ├── react-router.md          # React Router setup
│   ├── tanstack.md              # TanStack Start setup
│   └── laravel.md               # Laravel + Inertia.js setup
├── registry/
│   └── registry.md              # Custom registries, authentication, v0 integration, presets
├── blocks/
│   └── sidebar.md               # Sidebar component (collapsible, theming, useSidebar hook)
└── skills/                      # Reserved for agent-optimized context
```

## Fetching Notes

- Documentation fetched from https://ui.shadcn.com/docs/
- Focus: CLI, configuration, theming, frameworks, and composition patterns
- Individual component pages are NOT bundled (70+ components) — agent uses WebFetch for specific component details
- Last updated: 2026-03-24
