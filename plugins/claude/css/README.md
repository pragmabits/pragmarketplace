# CSS Expert Plugin

General-purpose CSS expert toolkit for Claude Code — providing guidance on layouts, animations, responsive design, selectors, performance optimization, and preprocessor integration.

## Features

- **CSS Layout** — Flexbox, CSS Grid, positioning, container queries, centering patterns
- **CSS Animation** — Transitions, keyframes, scroll-driven animations, View Transition API
- **CSS Responsive** — Media queries, fluid typography, container queries, mobile-first design
- **CSS Selectors** — Specificity, :has(), cascade layers, custom properties, pseudo-classes
- **CSS Performance** — Critical CSS, containment, content-visibility, font loading, Core Web Vitals
- **CSS Preprocessors** — SCSS/Sass, Less, PostCSS, native CSS nesting, CSS Modules

## Installation

Add to your Claude Code plugins configuration:

```json
{
  "plugins": ["plugins/claude/css"]
}
```

Or install from the marketplace:

```
/install css
```

## Usage

### Slash Command

```
/css center a div both horizontally and vertically
/css set up SCSS with Vite
/css how do cascade layers work?
/css optimize CSS for Core Web Vitals
```

### Automatic Triggering

The CSS agent triggers automatically when your questions involve CSS topics — layouts, animations, responsive design, selectors, performance, or preprocessors. The 6 skills provide specific triggers for each domain.

## Documentation Strategy

This plugin uses a hybrid documentation approach:

1. **Bundled quick-reference tables** in `docs/web/` — compact property references, value tables, and ASCII diagrams for common patterns
2. **Runtime documentation lookup** via context7 MCP (MDN Web Docs, Sass, Less, PostCSS) and WebSearch fallback — ensuring always up-to-date answers for detailed specifications

The agent consults current documentation before answering, rather than relying solely on training data.

## Technologies Covered

- Pure CSS (modern standards)
- SCSS / Sass
- Less
- PostCSS (autoprefixer, postcss-preset-env)
- CSS Modules
- Native CSS features (nesting, container queries, cascade layers, :has())
