# Tailwind CSS Quick Reference

## 4. TW4 Core Quick Reference

### CSS-First Configuration

| TW3 Pattern | TW4 Pattern |
|-------------|-------------|
| `@tailwind base;` `@tailwind components;` `@tailwind utilities;` | `@import "tailwindcss";` |
| `tailwind.config.js` `theme.extend` | `@theme { ... }` block in CSS |
| `plugins: [addUtilities()]` | `@utility name { ... }` in CSS |
| `plugins: [addVariant()]` | `@custom-variant name { ... }` in CSS |
| `content: ['./src/**/*.{html,js}']` | `@source "./src/**/*.{html,js}";` |

### @theme Block (Design Tokens)

Define design tokens that compile to CSS custom properties:

```css
@import "tailwindcss";

@theme {
  --color-primary: #3b82f6;
  --color-primary-light: #60a5fa;
  --color-primary-dark: #2563eb;

  --font-sans: "Inter", sans-serif;
  --font-mono: "Fira Code", monospace;

  --spacing-18: 4.5rem;

  --breakpoint-3xl: 120rem;

  --radius-pill: 9999px;
}
```

Usage: `bg-primary`, `text-primary-dark`, `font-sans`, `rounded-pill`

### @utility (Custom Utilities)

```css
@utility text-shadow-sm {
  text-shadow: 0 1px 2px rgb(0 0 0 / 0.2);
}

@utility text-shadow-md {
  text-shadow: 0 2px 4px rgb(0 0 0 / 0.3);
}

@utility content-auto {
  content-visibility: auto;
}
```

Usage: `text-shadow-sm`, `hover:text-shadow-md`, `lg:content-auto`

### @custom-variant

```css
@custom-variant pointer-coarse (@media (pointer: coarse));
@custom-variant theme-midnight (&:where([data-theme="midnight"], [data-theme="midnight"] *));
```

Usage: `pointer-coarse:text-lg`, `theme-midnight:bg-slate-900`

### @source (Content Sources)

```css
@source "./src/**/*.{html,vue,jsx,tsx,svelte,astro}";
@source "../shared/components/**/*.{html,js}";
```

### @layer (CSS Organization)

```css
@layer base {
  html {
    font-family: var(--font-sans);
  }
}

@layer components {
  .card {
    @apply rounded-lg bg-white p-6 shadow-md;
  }
}
```

### Opacity Modifiers

| TW3 (deprecated) | TW4 (current) |
|-------------------|---------------|
| `bg-black bg-opacity-50` | `bg-black/50` |
| `text-blue-500 text-opacity-75` | `text-blue-500/75` |
| `border-red-500 border-opacity-25` | `border-red-500/25` |

### Dark Mode

Default (media strategy): use `dark:` prefix directly.

Custom class strategy:

```css
@custom-variant dark (&:where(.dark, .dark *));
```

Usage: `dark:bg-slate-900`, `dark:text-white`

### Responsive Breakpoints (Mobile-First)

| Prefix | Minimum width | CSS |
|--------|--------------|-----|
| `sm:` | 40rem (640px) | `@media (width >= 40rem)` |
| `md:` | 48rem (768px) | `@media (width >= 48rem)` |
| `lg:` | 64rem (1024px) | `@media (width >= 64rem)` |
| `xl:` | 80rem (1280px) | `@media (width >= 80rem)` |
| `2xl:` | 96rem (1536px) | `@media (width >= 96rem)` |

Usage: `text-sm md:text-base lg:text-lg`

### Container Queries

Mark a container:

```html
<div class="@container">
  <div class="@sm:flex @md:grid @md:grid-cols-2 @lg:grid-cols-3">
    <!-- responsive to container, not viewport -->
  </div>
</div>
```

Named containers:

```html
<div class="@container/sidebar">
  <div class="@sm/sidebar:flex">...</div>
</div>
```

Container query breakpoints:

| Prefix | Minimum width |
|--------|--------------|
| `@xs:` | 20rem (320px) |
| `@sm:` | 24rem (384px) |
| `@md:` | 28rem (448px) |
| `@lg:` | 32rem (512px) |
| `@xl:` | 36rem (576px) |
| `@2xl:` | 42rem (672px) |

## 5. TW3 to TW4 Migration Reference

| TW3 | TW4 | Notes |
|-----|-----|-------|
| `@tailwind base; @tailwind components; @tailwind utilities;` | `@import "tailwindcss";` | Single import replaces three directives |
| `bg-opacity-50` | `bg-black/50` | Opacity modifier syntax |
| `tailwind.config.js` `extend.colors` | `@theme { --color-*: ... }` | CSS-first theming |
| `plugins: [addUtilities()]` | `@utility { ... }` | CSS-based custom utilities |
| `plugins: [addVariant()]` | `@custom-variant name { ... }` | CSS-based custom variants |
| `theme('colors.blue.500')` | `var(--color-blue-500)` | CSS custom properties |
| `content: ['./src/**/*.{html,js}']` | `@source "./src/**/*.{html,js}";` | Content source declaration |
| `darkMode: 'class'` | `@custom-variant dark (&:where(.dark, .dark *));` | Custom dark mode variant |
| `screens: { '3xl': '1920px' }` | `@theme { --breakpoint-3xl: 120rem; }` | Custom breakpoints in @theme |
| `@apply bg-blue-500 hover:bg-blue-700` | `@apply bg-blue-500 hover:bg-blue-700` | @apply still works in TW4 |
| `@screen md { ... }` | `@media (width >= 48rem) { ... }` | Native CSS media queries |
| PostCSS plugin (`tailwindcss`) | `@tailwindcss/postcss` or `@tailwindcss/vite` | New package names |

### Migration Steps

1. Update `package.json`: `tailwindcss` v3 to v4, add `@tailwindcss/vite` or `@tailwindcss/postcss`
2. Replace CSS directives: `@tailwind base/components/utilities` with `@import "tailwindcss"`
3. Move theme config: `tailwind.config.js` `theme.extend` to `@theme { ... }` in CSS
4. Convert plugins: `addUtilities` to `@utility`, `addVariant` to `@custom-variant`
5. Update opacity: `bg-opacity-*` / `text-opacity-*` to `/XX` modifier syntax
6. Update content: `content` array to `@source` declarations
7. Update dark mode: `darkMode: 'class'` to `@custom-variant dark (...)`
8. Update Vite config: replace PostCSS plugin with `@tailwindcss/vite`
9. Remove `tailwind.config.js` if fully migrated
10. Test all pages for visual regressions

