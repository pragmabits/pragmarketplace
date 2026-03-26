# Sidebar Block Pattern

## Overview

The Sidebar is a composable, themeable, and customizable component for application navigation.

## Core Components

- **SidebarProvider** — Manages collapsible state
- **Sidebar** — Main container
- **SidebarHeader / SidebarFooter** — Sticky top/bottom
- **SidebarContent** — Scrollable content area
- **SidebarGroup** — Sectional organization
- **SidebarTrigger** — Toggle mechanism

## Configuration

### SidebarProvider Props
- `defaultOpen` (boolean) — Initial open state
- `open` (boolean) — Controlled state
- `onOpenChange` — State callback

### Sidebar Props
- **side**: `"left"` | `"right"`
- **variant**: `"sidebar"` | `"floating"` | `"inset"`
- **collapsible**: `"offcanvas"` | `"icon"` | `"none"`

## Width

```
SIDEBAR_WIDTH = "16rem"
SIDEBAR_WIDTH_MOBILE = "18rem"
```

Customizable via CSS variables: `--sidebar-width` and `--sidebar-width-mobile`

## Menu Components

- **SidebarMenu** — Container for menu items
- **SidebarMenuItem** — Individual menu entry
- **SidebarMenuButton** — Interactive button (supports `asChild`, `isActive`)
- **SidebarMenuAction** — Action elements within items
- **SidebarMenuSub** — Nested submenu structure
- **SidebarMenuBadge** — Badge display
- **SidebarMenuSkeleton** — Loading placeholder

## useSidebar Hook

```typescript
const { state, open, setOpen, openMobile, setOpenMobile, isMobile, toggleSidebar } = useSidebar()
```

- `state` — `"expanded"` | `"collapsed"`
- `toggleSidebar()` — Universal toggle

## Keyboard Shortcut

Default: `Cmd+B` (Mac) / `Ctrl+B` (Windows)

## Theming Variables

- `--sidebar-background`, `--sidebar-foreground`
- `--sidebar-primary`, `--sidebar-primary-foreground`
- `--sidebar-accent`, `--sidebar-accent-foreground`
- `--sidebar-border`, `--sidebar-ring`

## Collapsible Groups

Wrap `SidebarGroup` in `Collapsible` with `CollapsibleTrigger` for expandable sections.

## Basic Usage

```tsx
import {
  Sidebar, SidebarContent, SidebarGroup, SidebarGroupContent,
  SidebarGroupLabel, SidebarMenu, SidebarMenuButton, SidebarMenuItem,
  SidebarProvider, SidebarTrigger,
} from "@/components/ui/sidebar"

export function AppSidebar() {
  return (
    <SidebarProvider>
      <Sidebar>
        <SidebarContent>
          <SidebarGroup>
            <SidebarGroupLabel>Application</SidebarGroupLabel>
            <SidebarGroupContent>
              <SidebarMenu>
                <SidebarMenuItem>
                  <SidebarMenuButton asChild>
                    <a href="/dashboard">Dashboard</a>
                  </SidebarMenuButton>
                </SidebarMenuItem>
              </SidebarMenu>
            </SidebarGroupContent>
          </SidebarGroup>
        </SidebarContent>
      </Sidebar>
      <main>
        <SidebarTrigger />
        {/* Page content */}
      </main>
    </SidebarProvider>
  )
}
```
