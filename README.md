# Pragmatic

A curated collection of Claude Code plugins by [Pragmabits](https://github.com/pragmabits).

## Overview

Pragmatic provides ready-to-install plugins that extend Claude Code with specialized knowledge, tools, and workflows. Each plugin is focused on a specific domain — from git commit strategy to frontend framework expertise — and integrates directly into Claude Code's slash command system.

## Plugins

| Plugin | Version | Category | Slash Commands | Description |
|--------|---------|----------|----------------|-------------|
| **git** | 2.2.0 | Tools | `/commit`, `/tag-it`, `/commit-setup` | Semantic commits, hunk-level staging, validation, version tagging, and safety hooks |
| **guideline** | 1.0.0 | Output | — | Output style formatting via predefined rules and standards |
| **pragma-statusline** | 1.0.0 | Tools | `/pragma-status` | Custom Claude Code statusline with git and context metrics |
| **fontawesome** | 1.1.0 | Design | `/fontawesome` | Font Awesome 7 icon selection, animation, styling, and integration |
| **shadcn** | 1.1.0 | Design | `/shadcn` | shadcn/ui component setup, CLI, theming, and framework integration |
| **tailwindcss** | 1.0.0 | Frontend | `/tailwindcss` | Tailwind CSS 4 utility authoring, theming, and TW3-to-TW4 migration |
| **css** | 1.1.0 | Frontend | `/css` | Layouts, animations, responsive design, selectors, and preprocessors |
| **vuejs** | 1.1.0 | Frontend | `/vuejs`, `/nuxt` | Vue 3, Nuxt 3, Pinia, testing, forms, styling, and animation |
| **frontend** | 1.0.0 | Frontend | `/frontend` | Cross-domain orchestrator — coordinates CSS, Tailwind, Vue, shadcn, FA specialists |

## Installation

Install any plugin directly from the marketplace:

```bash
claude plugin add pragmabits/pragmarketplace --plugin <plugin-name>
```

For example, to install the git plugin:

```bash
claude plugin add pragmabits/pragmarketplace --plugin git
```

## Usage

Once installed, plugins are available through slash commands in Claude Code:

```
/commit          # Strategic git commit with semantic analysis
/tag-it          # Suggest and create version tags
/commit-setup    # Configure permission rules for prompt-free commits
/pragma-status   # Install custom statusline
/fontawesome     # Font Awesome icon guidance
/shadcn          # shadcn/ui component guidance
/tailwindcss     # Tailwind CSS 4 guidance
/css             # CSS expert guidance
/vuejs           # Vue.js ecosystem guidance
/nuxt            # Nuxt 3 guidance
/frontend        # Cross-domain frontend orchestrator
```

The **guideline** plugin has no slash command — it provides output style rules that shape how Claude formats responses when active.

## Author

Built by **Leonardo Leoncio** at [Pragmabits](https://github.com/pragmabits).

## License

MIT
