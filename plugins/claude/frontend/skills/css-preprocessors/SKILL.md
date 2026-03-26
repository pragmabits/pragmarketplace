---
name: css-preprocessors
description: "This skill should be used when the user asks about CSS preprocessors, \"SCSS\", \"Sass\", \"Less\", \"PostCSS\", \"postcss.config\", \"sass-loader\", \"@use\", \"@forward\", \"@mixin\", \"@include\", \"$variable\", \"nesting\", \"CSS nesting\", \"autoprefixer\", \"postcss-preset-env\", \"CSS Modules\", \".module.css\", \"sass setup\", \"compile scss\", or needs help setting up, configuring, or writing preprocessor code."
---

# CSS Preprocessors

This skill delegates to the `css` agent, which fetches current documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for SCSS, Sass, Less, PostCSS, and native CSS features that overlap with preprocessors.

## Why this skill matters

CSS preprocessors (SCSS/Sass, Less) and PostCSS remain widely used, but native CSS has adopted many features that previously required preprocessors — nesting, custom properties, and color functions. Understanding when to use a preprocessor versus native CSS, and how to set up modern module systems (@use/@forward instead of deprecated @import), prevents outdated patterns and unnecessary toolchain complexity. Without consulting documentation, answers may use Sass's deprecated @import, miss PostCSS plugin configuration, or ignore that native CSS nesting now exists.

## When to use this skill

Use for ANY request involving:

- SCSS/Sass setup and configuration
- Sass module system (@use, @forward)
- Sass mixins, functions, and control flow
- Less variables and mixins
- PostCSS plugin configuration (autoprefixer, postcss-preset-env)
- Native CSS nesting vs preprocessor nesting
- CSS Modules setup (.module.css)
- Migrating from preprocessors to native CSS
- Build tool integration (Vite, Webpack, esbuild)

## Common patterns

### SCSS @use/@forward module system

```scss
// _tokens.scss
$color-primary: #3b82f6;
$spacing-md: 1rem;

// _mixins.scss
@use 'tokens' as t;

@mixin responsive($breakpoint) {
  @media (min-width: $breakpoint) { @content; }
}

// main.scss
@use 'tokens' as t;
@use 'mixins' as m;

.button {
  color: t.$color-primary;
  padding: t.$spacing-md;

  @include m.responsive(768px) {
    padding: t.$spacing-md * 2;
  }
}
```

### PostCSS with autoprefixer

```javascript
// postcss.config.js
export default {
  plugins: {
    autoprefixer: {},
    'postcss-preset-env': {
      stage: 2,
      features: {
        'nesting-rules': true,
      },
    },
  },
};
```

### Native CSS nesting

```css
.card {
  padding: 1rem;

  & .title {
    font-size: 1.25rem;
  }

  &:hover {
    box-shadow: 0 4px 12px rgb(0 0 0 / 0.1);
  }

  @media (min-width: 768px) {
    padding: 2rem;
  }
}
```

### CSS Modules setup

```css
/* Button.module.css */
.button {
  composes: base from './shared.module.css';
  background: var(--color-primary);
}

.primary {
  composes: button;
  font-weight: 600;
}
```

## Before delegating

BEFORE dispatching, use AskUserQuestion to clarify the user's intent. Every question to the user MUST go through AskUserQuestion — never ask as plain text. Common things to clarify:
- Which preprocessor they're using or want to use (SCSS, Sass, Less, PostCSS)
- Whether they're setting up from scratch or migrating
- Build tool context (Vite, Webpack, standalone)

## How to use

Dispatch the `frontend:css` agent with the user's question or task. Do not answer preprocessor questions from general knowledge — the agent fetches current documentation for more accurate answers.

The agent will:
1. Check the user's project for preprocessor files (.scss, .sass, .less, postcss.config)
2. Look up current Sass/Less/PostCSS documentation
3. Recommend modern module patterns (@use/@forward, not @import)
4. Suggest native CSS alternatives when preprocessor features are no longer needed
