# Dialog Component Reference

## Installation

```bash
pnpm dlx shadcn@latest add dialog
```

## Usage

```tsx
import {
  Dialog, DialogContent, DialogDescription,
  DialogHeader, DialogTitle, DialogTrigger,
} from "@/components/ui/dialog"
```

## Basic Example

```tsx
<Dialog>
  <DialogTrigger>Open</DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Are you absolutely sure?</DialogTitle>
      <DialogDescription>
        This action cannot be undone.
      </DialogDescription>
    </DialogHeader>
  </DialogContent>
</Dialog>
```

## Sub-Components

- **Dialog** — Root container managing state
- **DialogTrigger** — Activation button/element
- **DialogContent** — Modal container
- **DialogHeader** — Title section
- **DialogTitle** — Heading text (required for accessibility)
- **DialogDescription** — Body description
- **DialogFooter** — Action buttons section
- **DialogClose** — Close button

## Patterns

### No Close Button
```tsx
<DialogContent showCloseButton={false}>
  {/* Content */}
</DialogContent>
```

### Scrollable Content
Long content automatically scrolls while header stays visible.

### Sticky Footer
Structure layout to separate scrollable content from fixed footer.

## Accessibility

Built on Radix UI Dialog primitive. Provides:
- Focus trapping
- Escape key dismissal
- Aria attributes
- Screen reader announcements

## API Reference

See [Radix UI Dialog](https://www.radix-ui.com/docs/primitives/components/dialog#api-reference) for complete props.
