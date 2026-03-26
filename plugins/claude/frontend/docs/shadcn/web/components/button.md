# Button Component Reference

## Installation

```bash
pnpm dlx shadcn@latest add button
```

## Usage

```tsx
import { Button } from "@/components/ui/button"
```

## Variants

| Variant | Description |
|---------|-------------|
| `default` | Standard button |
| `outline` | Bordered, transparent background |
| `secondary` | Alternative styling |
| `ghost` | Minimal, no background/border |
| `destructive` | Alert/danger action |
| `link` | Appears as hyperlink |

## Sizes

| Size | Description |
|------|-------------|
| `xs` | Extra small |
| `sm` | Small |
| `default` | Standard |
| `lg` | Large |
| `icon` | Square for icon-only |
| `icon-xs`, `icon-sm`, `icon-lg` | Icon size variants |

## Props

| Prop | Type | Default |
|------|------|---------|
| `variant` | `"default" \| "outline" \| "ghost" \| "destructive" \| "secondary" \| "link"` | `"default"` |
| `size` | `"default" \| "xs" \| "sm" \| "lg" \| "icon"` | `"default"` |
| `asChild` | `boolean` | `false` |

## Examples

### With Icon
```tsx
<Button>
  <IconGitBranch data-icon="inline-start" />
  New Branch
</Button>
```

### Icon Only
```tsx
<Button size="icon">
  <CircleFadingArrowUpIcon />
</Button>
```

### As Link
```tsx
<Button asChild>
  <Link href="/login">Login</Link>
</Button>
```

### Loading
```tsx
<Button disabled>
  <Spinner data-icon="inline-start" />
  Loading...
</Button>
```

### Rounded
```tsx
<Button className="rounded-full">Rounded</Button>
```

## Cursor Note

Tailwind CSS v4 changed default button cursor from `pointer` to `default`. To restore:

```css
@layer base {
  button:not(:disabled),
  [role="button"]:not(:disabled) {
    cursor: pointer;
  }
}
```
