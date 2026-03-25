# shadcn/ui CLI Complete Reference

## Overview

The shadcn CLI is a command-line tool for managing components in shadcn/ui projects. It enables initialization, component installation, registry management, and project migrations.

## Core Commands

### init

Initialize configuration and dependencies for a new project. Installs dependencies, adds the `cn` utility, and configures CSS variables.

```bash
pnpm dlx shadcn@latest init
```

**Options:**
- `-t, --template`: Project template (next, vite, start, react-router, laravel, astro)
- `-b, --base`: Component library (radix, base)
- `-p, --preset`: Use preset configuration by name, URL, or code
- `-n, --name`: Name for new project
- `-d, --defaults`: Use default configuration
- `-y, --yes`: Skip confirmation prompts
- `-f, --force`: Force overwrite existing configuration
- `--monorepo`: Scaffold monorepo project
- `--rtl`: Enable RTL support
- `--css-variables`: Use CSS variables for theming (default: true)

**Alias:** `create`

---

### add

Add components and dependencies to your project.

```bash
pnpm dlx shadcn@latest add [component]
```

**Options:**
- `-y, --yes`: Skip confirmation
- `-o, --overwrite`: Overwrite existing files
- `-c, --cwd`: Working directory
- `-a, --all`: Add all available components
- `-p, --path`: Custom installation path
- `-s, --silent`: Mute output
- `--dry-run`: Preview changes without writing
- `--diff [path]`: Show file differences
- `--view [path]`: Display file contents

---

### view

View registry items before installing.

```bash
pnpm dlx shadcn@latest view [item]
```

Examples:
```bash
pnpm dlx shadcn@latest view button card dialog
pnpm dlx shadcn@latest view @acme/auth @v0/dashboard
```

---

### search / list

Search items across registries.

```bash
pnpm dlx shadcn@latest search [registry]
```

**Options:**
- `-c, --cwd`: Working directory
- `-q, --query`: Search query string
- `-l, --limit`: Results per registry (default: 100)
- `-o, --offset`: Number to skip (default: 0)

Examples:
```bash
pnpm dlx shadcn@latest search @shadcn -q "button"
pnpm dlx shadcn@latest search @shadcn @v0 @acme
```

---

### build

Generate registry JSON files.

```bash
pnpm dlx shadcn@latest build
```

**Options:**
- `-o, --output`: Destination directory (default: ./public/r)
- `-c, --cwd`: Working directory

---

### docs

Fetch documentation and API references for components.

```bash
pnpm dlx shadcn@latest docs [component]
```

**Options:**
- `-c, --cwd`: Working directory
- `-b, --base`: Base to use (radix or base)
- `--json`: Output as JSON

---

### info

Get information about your project.

```bash
pnpm dlx shadcn@latest info
```

**Options:**
- `-c, --cwd`: Working directory
- `--json`: Output as JSON

---

### migrate

Run migrations on your project.

```bash
pnpm dlx shadcn@latest migrate [migration]
```

**Options:**
- `-c, --cwd`: Working directory
- `-l, --list`: List all available migrations
- `-y, --yes`: Skip confirmation

#### migrate rtl

Transforms components to support right-to-left languages. Updates physical CSS properties to logical equivalents (e.g., `ml-4` → `ms-4`).

```bash
pnpm dlx shadcn@latest migrate rtl
npx shadcn@latest migrate rtl src/components/ui/button.tsx
npx shadcn@latest migrate rtl "src/components/ui/**"
```

#### migrate radix

Updates imports from individual `@radix-ui/react-*` packages to unified `radix-ui` package.

```bash
pnpm dlx shadcn@latest migrate radix
```

**Before:**
```typescript
import * as DialogPrimitive from "@radix-ui/react-dialog"
import * as SelectPrimitive from "@radix-ui/react-select"
```

**After:**
```typescript
import { Dialog as DialogPrimitive, Select as SelectPrimitive } from "radix-ui"
```

---

## Global Options

Most commands support:
- `-c, --cwd`: Specify working directory (defaults to current)
- `-h, --help`: Display command help
