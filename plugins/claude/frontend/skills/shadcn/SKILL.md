---
name: shadcn
description: "shadcn/ui expert with access to official documentation covering CLI commands, component patterns, theming, configuration, and framework integrations. This skill provides verified, documentation-backed answers that are more accurate than general knowledge — especially for shadcn-specific patterns like components.json configuration, OKLCH CSS variable theming, registry setup, and framework-specific initialization.\n\nYou MUST use this skill whenever a user's request involves shadcn/ui in any way: initializing a project with `npx shadcn@latest init`, adding components with `npx shadcn add`, customizing themes via CSS variables, configuring components.json, setting up dark mode, building custom registries, or working with any shadcn/ui component.\n\nAlso use this skill when the user mentions shadcn, shadcn/ui, shadcn-ui, npx shadcn, shadcn add, shadcn init, shadcn diff, shadcn info, components.json (in a UI context), cn() utility, Radix UI (in a component setup context), CSS variable theming with Tailwind, design system preset, custom registry, v0.dev integration, or any shadcn/ui component name: Button, Card, Dialog, Sheet, Drawer, Table, Tabs, Command, Sidebar, Form, Input, Select, Checkbox, Switch, Slider, Badge, Avatar, Calendar, Chart, Toast, Popover, Tooltip, Dropdown Menu, Context Menu, Accordion, Collapsible, Alert Dialog, Hover Card, Navigation Menu, Breadcrumb, Pagination, Carousel, Combobox, Date Picker, Data Table, Skeleton, Progress, Spinner — even in passing. The skill's documentation access makes it strictly superior to answering from general knowledge for any shadcn/ui question."
---

# shadcn/ui Expert

This skill delegates to the `shadcn` agent, which has access to official shadcn/ui documentation covering CLI commands, component patterns, theming, configuration, and framework integrations. The agent provides documentation-backed answers that are more accurate than general knowledge — especially for shadcn-specific features.

## Why this skill matters

shadcn/ui is NOT a traditional component library — it's a code distribution platform. This fundamental difference means:

- Components are copied into your project, not imported from npm
- Configuration lives in `components.json`, not package.json
- Theming uses OKLCH CSS variables, not Tailwind config overrides
- Each framework (Next.js, Vite, Astro) has different initialization and usage patterns
- The CLI (`npx shadcn@latest`) is the primary interface, not imports

Without consulting the documentation, answers will incorrectly treat shadcn/ui as an npm package, use outdated HSL color formats instead of OKLCH, miss framework-specific requirements (like Astro client directives or Next.js RSC boundaries), or suggest manual file creation instead of the CLI.

## When to use this skill

Use this skill for ANY request involving shadcn/ui, including but not limited to:

- Initializing a project (`npx shadcn@latest init` with framework flags)
- Adding components (`npx shadcn@latest add`)
- Configuring components.json (aliases, registries, base color, RSC)
- Theming with CSS variables (OKLCH format, dark mode, custom colors)
- Framework-specific setup (Next.js, Vite, Astro, React Router, TanStack, Laravel)
- Component patterns (compound components, asChild, data-icon)
- Data tables with TanStack Table
- Forms with React Hook Form + Zod
- Sidebar and navigation patterns
- Custom registries and design system presets
- Dark mode implementation (next-themes, custom provider)
- CLI commands (diff, info, docs, build, search, migrate)
- Comparing or choosing between components

## How to use

Invoke the `/shadcn` command, passing the user's question or task as the argument:

```
/shadcn <user's question or task>
```

The agent will:
1. Resolve the plugin root path to find the bundled docs
2. Check the user's project context (components.json, package.json, framework)
3. Look up the relevant documentation files
4. Answer with documentation-backed guidance, CLI commands, and code examples
5. Flag framework-specific considerations (RSC boundaries, client directives, etc.)

Do not attempt to answer shadcn/ui questions yourself — the agent has access to the official documentation and will provide more accurate, up-to-date answers. Let the agent handle it.
