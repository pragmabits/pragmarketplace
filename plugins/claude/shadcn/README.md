# shadcn Plugin

shadcn/ui expert plugin for Claude Code — component setup, CLI guidance, theming, and framework integration powered by official documentation.

## Features

- **CLI Guidance**: `npx shadcn@latest init`, `add`, `diff`, `info`, `docs` command reference
- **Component Setup**: Selection, addition, and customization of shadcn/ui components
- **Theming**: CSS variables, base colors, dark mode, theme customization
- **Framework Integration**: Next.js, Vite, Astro, React Router, TanStack, Laravel
- **Registry**: Custom registries, design system presets, v0 integration
- **Configuration**: components.json management, path aliases, Tailwind config

## Components

| Component | Type | Purpose |
|-----------|------|---------|
| `agents/shadcn.md` | Agent | Expert agent with bundled documentation access |
| `commands/shadcn.md` | Command | Gateway command (`/shadcn`) |
| `skills/shadcn/SKILL.md` | Skill | Trigger-based skill delegation |
| `docs/web/` | Documentation | Bundled official shadcn/ui docs |

## Usage

### Via command
```
/shadcn how do I set up shadcn/ui in my Next.js project?
```

### Via agent (automatic)
Mention shadcn/ui, components.json, `npx shadcn`, or any shadcn component name and the agent triggers automatically.

## Documentation

The `docs/web/` directory contains bundled official documentation from https://ui.shadcn.com/docs/ organized by topic:

- `getting-started/` — Installation, init, overview
- `cli/` — CLI commands reference
- `components/` — Component patterns and usage
- `configuration/` — components.json, path aliases
- `theming/` — CSS variables, colors, dark mode
- `frameworks/` — Per-framework setup guides
- `registry/` — Custom registries, presets
- `blocks/` — Pre-built block patterns
