# shadcn/ui Registry System

## Overview

The shadcn/ui registry is a distribution system for code that enables developers to create and share custom components, hooks, pages, configuration, and other resources. Platform-agnostic, works with any project type and framework.

## Key Capabilities

- Distribute custom components across projects
- Share hooks, pages, and configuration files
- Implement authentication for private registries
- Use namespace support for organizing resources
- Integrate with v0 for component customization
- Support MCP servers for AI-assisted development

## Registry Configuration

### In components.json

```json
{
  "registries": {
    "@v0": "https://v0.dev/chat/b/{name}",
    "@acme": "https://registry.acme.com/{name}.json",
    "@internal": "https://internal.company.com/{name}.json"
  }
}
```

The `{name}` placeholder gets replaced with the resource name during installation.

### With Authentication

```json
{
  "registries": {
    "@private": {
      "url": "https://api.company.com/registry/{name}.json",
      "headers": {
        "Authorization": "Bearer ${REGISTRY_TOKEN}",
        "X-API-Key": "${API_KEY}"
      },
      "params": {
        "version": "latest"
      }
    }
  }
}
```

Environment variables in `${VAR_NAME}` format are automatically expanded.

### Installing from Registries

```bash
npx shadcn@latest add @v0/dashboard
npx shadcn@latest add @private/button
npx shadcn@latest add @acme/header @internal/auth-utils
```

## Building a Registry

### Generate registry files

```bash
pnpm dlx shadcn@latest build
pnpm dlx shadcn@latest build --output ./public/registry
```

### registry.json Schema

Defines:
- Available resource namespaces
- Authentication requirements
- Resource metadata and locations
- Integration settings

### registry-item.json

Individual items include:
- Component structure
- Dependencies and requirements
- Installation instructions
- Usage examples

## Design System Presets

Use presets during initialization:

```bash
npx shadcn@latest init --preset <name-or-url>
```

Presets define a complete set of components, theming, and configuration for a design system.

## v0 Integration

Components can be opened in v0 for visual customization:
- "Open in v0" URLs allow editing components in the v0 interface
- Modified components can be imported back via the CLI
