---
name: tw-utility
description: "This skill should be used when the user asks about creating custom Tailwind CSS utilities, variants, or extending Tailwind with new classes. Trigger phrases include \"@utility\", \"@custom-variant\", \"custom utility\", \"extend tailwind\", \"plugin\", \"addUtilities\", \"addVariant\", \"custom class\", \"arbitrary variant\", \"create utility\", \"new tailwind class\", \"tailwind plugin\", \"custom variant\", \"functional utility\", \"dynamic utility\"."
---

# Tailwind CSS 4 Custom Utilities & Variants

This skill delegates to the `tailwindcss` agent, which fetches current documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for TW4 custom utilities and variants.

## Why this skill matters

Tailwind CSS 4 replaced JavaScript-based `addUtilities()` and `addVariant()` plugin functions with CSS-native `@utility` and `@custom-variant` directives. This is a breaking change — the old plugin API no longer works. Custom utilities defined with `@utility` automatically support variants, responsive prefixes, and arbitrary values.

Without consulting documentation, answers may use the deprecated JavaScript plugin API, miss the `@utility` block syntax, or create custom variants that don't integrate with the TW4 variant system.

## When to use this skill

Use for ANY request involving:

- Creating custom utility classes with `@utility`
- Defining custom variants with `@custom-variant`
- Migrating JavaScript `addUtilities()` / `addVariant()` to CSS-native syntax
- Using arbitrary values `[value]` with custom utilities
- Building component-level utility abstractions
- Understanding how `@utility` differs from `@layer utilities`

## Common patterns

### @utility block syntax

```css
@utility tab-size-* {
  tab-size: --value(--tab-size-*);
}

@utility content-auto {
  content-visibility: auto;
}

@utility scrollbar-hidden {
  scrollbar-width: none;
  &::-webkit-scrollbar {
    display: none;
  }
}
```

### @custom-variant definition

```css
@custom-variant pointer-coarse (@media (pointer: coarse));
@custom-variant theme-dark (&:where(.dark, .dark *));
@custom-variant hocus (&:hover, &:focus);
```

```html
<!-- Usage -->
<button class="pointer-coarse:p-4 hocus:bg-blue-500">
  Adaptive button
</button>
```

### Arbitrary values with custom utilities

```html
<div class="tab-size-[8]">
  Code with custom tab size
</div>
```

## How to use

Invoke the `/tailwindcss` command, passing the user's question or task as the argument:

```
/tailwindcss <user's question or task>
```

The agent will:
1. Check the user's project context for existing custom utilities
2. Look up current `@utility` and `@custom-variant` documentation
3. Provide CSS-native utility definitions with proper syntax
4. Flag deprecated patterns (JavaScript addUtilities/addVariant plugin API)

Custom utility and variant questions should be delegated to the agent rather than answered from general knowledge — the agent fetches current documentation for more accurate, up-to-date answers.
