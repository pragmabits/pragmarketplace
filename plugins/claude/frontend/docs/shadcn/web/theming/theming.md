# shadcn/ui Theming Guide

## Overview

shadcn/ui provides theming through CSS variables and color utilities, with support for both light and dark modes using the OKLCH color format.

## CSS Variables Setup

Enable CSS variables in `components.json`:

```json
{
  "tailwind": {
    "cssVariables": true
  }
}
```

## Color Naming Convention

The library follows a "background and foreground" pattern:
- `background` variables define component backgrounds
- `foreground` variables define text colors
- The `background` suffix is omitted in utility class names

Example: `--primary` and `--primary-foreground` become `bg-primary` and `text-primary-foreground`.

## Core CSS Variables

### Layout & Structure
- `--radius`: Border radius (0.625rem)
- `--border`, `--input`, `--ring`

### Color Variables
- `--background`, `--foreground`
- `--card`, `--card-foreground`
- `--popover`, `--popover-foreground`
- `--primary`, `--primary-foreground`
- `--secondary`, `--secondary-foreground`
- `--muted`, `--muted-foreground`
- `--accent`, `--accent-foreground`
- `--destructive`, `--destructive-foreground`

### Chart Colors
- `--chart-1` through `--chart-5`

### Sidebar Variables
- `--sidebar`, `--sidebar-foreground`
- `--sidebar-primary`, `--sidebar-primary-foreground`
- `--sidebar-accent`, `--sidebar-accent-foreground`
- `--sidebar-border`, `--sidebar-ring`

## Light Mode (Default)

Variables use OKLCH format:
```css
:root {
  --background: oklch(1 0 0);
  --foreground: oklch(0.145 0 0);
  --primary: oklch(0.205 0 0);
}
```

## Dark Mode

The `.dark` class applies alternate values:
```css
.dark {
  --background: oklch(0.145 0 0);
  --foreground: oklch(0.985 0 0);
  --primary: oklch(0.922 0 0);
}
```

Dark mode uses transparency for borders: `oklch(1 0 0 / 10%)`.

## Adding Custom Colors

```css
:root {
  --warning: oklch(0.84 0.16 84);
  --warning-foreground: oklch(0.28 0.07 46);
}

.dark {
  --warning: oklch(0.41 0.11 46);
  --warning-foreground: oklch(0.99 0.02 95);
}

@theme inline {
  --color-warning: var(--warning);
  --color-warning-foreground: var(--warning-foreground);
}
```

Use via utility classes: `bg-warning text-warning-foreground`

## Base Color Options

Available base colors for project initialization:
- Neutral
- Stone
- Zinc
- Mauve
- Olive
- Mist
- Taupe

Set via `components.json`: `"baseColor": "neutral"`

## Theme Detection

Includes automatic theme detection via JavaScript:
- Checks localStorage for user preference
- Falls back to system preference via `prefers-color-scheme`
- Updates meta theme-color attribute accordingly
