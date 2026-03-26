---
name: shadcn
description: "This skill should be used when the user asks about shadcn/ui — setup, CLI commands (npx shadcn add/init/diff), theming, components.json config, dark mode, custom registries, or any shadcn/ui component (Button, Card, Dialog, Form, Table, Tabs, etc.). Also triggers on: shadcn, cn() utility, Radix UI setup context, or any shadcn component bug/issue. Provides documentation-backed answers via bundled reference files."
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

## Before delegating

BEFORE dispatching, use AskUserQuestion to clarify the user's intent. Every question to the user MUST go through AskUserQuestion — never ask as plain text. Common things to clarify:
- Which framework they're using (Next.js, Vite, Astro, etc.)
- Whether they want to add a component, customize theming, or fix an issue
- Whether they have shadcn/ui already initialized or need setup

## How to use

Dispatch the `frontend:shadcn` agent with the user's question or task. Do not answer shadcn/ui questions from general knowledge — the agent has access to official documentation for more accurate answers.

The agent will:
1. Resolve the plugin root path to find the bundled docs
2. Check the user's project context (components.json, package.json, framework)
3. Look up the relevant documentation files
4. Answer with documentation-backed guidance, CLI commands, and code examples
5. Flag framework-specific considerations (RSC boundaries, client directives, etc.)
