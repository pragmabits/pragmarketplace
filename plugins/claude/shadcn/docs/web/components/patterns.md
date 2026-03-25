# shadcn/ui Component Patterns

## Core Concepts

### Not a Component Library

shadcn/ui is a code distribution system. Components are copied into your project — you own the source code and can modify them freely. There is no npm package to install for the components themselves.

### Compound Components

Most shadcn/ui components follow a compound component pattern using sub-components:

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

### asChild Pattern

The `asChild` prop (from Radix UI) allows rendering a different element while keeping the component's behavior:

```tsx
<Button asChild>
  <Link href="/login">Login</Link>
</Button>
```

### data-icon Attribute

Use `data-icon="inline-start"` or `data-icon="inline-end"` for proper icon spacing:

```tsx
<Button>
  <IconGitBranch data-icon="inline-start" />
  New Branch
</Button>
```

---

## Component Categories

### Form Components
- **Button** — Variants: default, outline, secondary, ghost, destructive, link. Sizes: xs, sm, default, lg, icon
- **Input** — Text input with variants
- **Textarea** — Multi-line text input
- **Select** — Dropdown selection
- **Checkbox** — Toggle with label
- **Radio Group** — Single selection from options
- **Switch** — Toggle switch
- **Slider** — Range input
- **Date Picker** — Calendar-based date selection (uses Popover + Calendar)
- **Combobox** — Searchable select (uses Popover + Command)
- **Form** — React Hook Form integration with Zod validation

### Layout Components
- **Card** — Container with header, content, footer
- **Separator** — Visual divider
- **Aspect Ratio** — Maintain width-to-height ratio
- **Scroll Area** — Custom scrollbar container
- **Resizable** — Resizable panel groups

### Data Display
- **Table** — Data table (pairs with TanStack Table)
- **Badge** — Status/category labels
- **Avatar** — User profile images
- **Calendar** — Date display/selection
- **Chart** — Data visualization (uses Recharts)
- **Carousel** — Scrollable content (uses Embla)

### Navigation
- **Navigation Menu** — Top-level navigation
- **Breadcrumb** — Path navigation
- **Tabs** — Tabbed interfaces
- **Pagination** — Page navigation
- **Sidebar** — Collapsible side navigation
- **Command** — Command palette (cmdk)

### Overlay / Feedback
- **Dialog** — Modal window
- **Sheet** — Side panel (slide-out)
- **Drawer** — Bottom drawer (uses Vaul)
- **Alert Dialog** — Confirmation dialog
- **Popover** — Floating content
- **Tooltip** — Hover information
- **Hover Card** — Rich hover preview
- **Toast** — Notification messages (uses Sonner)
- **Alert** — Inline feedback messages
- **Progress** — Progress indicator
- **Skeleton** — Loading placeholder
- **Spinner** — Loading animation

### Menus
- **Dropdown Menu** — Actions menu
- **Context Menu** — Right-click menu
- **Menubar** — Application menu bar

### Misc
- **Accordion** — Expandable sections
- **Collapsible** — Toggle visibility
- **Toggle** — Two-state button
- **Toggle Group** — Group of toggles

---

## Key Patterns

### Button Variants

```tsx
<Button variant="default">Default</Button>
<Button variant="outline">Outline</Button>
<Button variant="secondary">Secondary</Button>
<Button variant="ghost">Ghost</Button>
<Button variant="destructive">Destructive</Button>
<Button variant="link">Link</Button>
```

### Loading State

```tsx
<Button disabled>
  <Spinner data-icon="inline-start" />
  Loading...
</Button>
```

### Dialog with Form

```tsx
<Dialog>
  <DialogTrigger asChild>
    <Button>Edit Profile</Button>
  </DialogTrigger>
  <DialogContent>
    <DialogHeader>
      <DialogTitle>Edit profile</DialogTitle>
      <DialogDescription>Make changes to your profile.</DialogDescription>
    </DialogHeader>
    <form>
      <Input placeholder="Name" />
      <Button type="submit">Save</Button>
    </form>
  </DialogContent>
</Dialog>
```

### Data Table with TanStack Table

```tsx
import { useReactTable, getCoreRowModel, flexRender } from "@tanstack/react-table"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"

// See data-table.md for full implementation
```

### Form with React Hook Form + Zod

```tsx
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"

const formSchema = z.object({
  username: z.string().min(2).max(50),
})

function ProfileForm() {
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: { username: "" },
  })

  function onSubmit(values: z.infer<typeof formSchema>) {
    console.log(values)
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)}>
        <FormField
          control={form.control}
          name="username"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Username</FormLabel>
              <FormControl>
                <Input placeholder="shadcn" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit">Submit</Button>
      </form>
    </Form>
  )
}
```

### Dark Mode Toggle

```tsx
import { Moon, Sun } from "lucide-react"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { useTheme } from "@/components/theme-provider"

export function ModeToggle() {
  const { setTheme } = useTheme()
  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon">
          <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme("light")}>Light</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")}>Dark</DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("system")}>System</DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
```

---

## Customization Approaches

1. **Modify source directly** — Edit the component file in `components/ui/`
2. **Extend via props** — Add new variants using `cva()` (class-variance-authority)
3. **Compose** — Wrap components in higher-order components
4. **Override styles** — Use className prop with Tailwind classes

### Adding a Custom Variant

```tsx
// In components/ui/button.tsx
const buttonVariants = cva("...", {
  variants: {
    variant: {
      default: "...",
      // Add your custom variant:
      success: "bg-green-500 text-white hover:bg-green-600",
    },
  },
})
```
