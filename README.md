# Pragmatic

A curated collection of Claude Code plugins by [Pragmabits](https://github.com/pragmabits).

## Overview

Pragmatic provides ready-to-install plugins that extend Claude Code with specialized knowledge, tools, and workflows. Each plugin is focused on a specific domain — from git commit strategy to frontend framework expertise — and integrates directly into Claude Code's slash command system.

## Plugins

| Plugin | Version | Category | Slash Commands | Description |
|--------|---------|----------|----------------|-------------|
| **git** | 3.0.1 | Tools | `/commit`, `/commit-setup` | Semantic commits, whole-file staging, hook-validated messages, native git hooks, and safety hooks |
| **frontend** | 1.8.0 | Frontend | `/frontend`, `/css`, `/tailwindcss`, `/vuejs`, `/nuxt`, `/shadcn`, `/fontawesome` | Cross-domain orchestrator bundling CSS, Tailwind CSS 4, Vue/Nuxt, shadcn/ui, and Font Awesome specialists |
| **review** | 1.0.1 | Tools | `/codex-review` | Independent Codex-based code review of the current `git diff` — verdict, summary, and findings |
| **session** | 2.1.1 | Tools | `/report`, `/recall` | Session handoff reports with fixed-numbered pending items (`/report`); list, filter, grep, resume, and read back prior reports via five `/recall` subcommands (`list`, `filter`, `grep`, `resume`, `last`) |
| **pragmatic** | 1.0.1 | Output | — | Output style for evidence-driven engineering — user-governed material decisions, batched `AskUserQuestion` prompts, evidence-cited claims, terse responses |

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
/commit-setup    # Configure permission rules for prompt-free commits
/frontend        # Cross-domain frontend orchestrator
/css             # CSS expert guidance
/tailwindcss     # Tailwind CSS 4 guidance
/vuejs           # Vue.js ecosystem guidance
/nuxt            # Nuxt 3 guidance
/shadcn          # shadcn/ui component guidance
/fontawesome     # Font Awesome icon guidance
/codex-review    # Independent Codex-based review of the current git diff
/report          # Generate a session handoff report
/recall          # List, filter, grep, or resume prior session reports
```

The **pragmatic** plugin has no slash command — it provides an output style that shapes how Claude formats responses when active.

## Author

Built by **Leonardo Leoncio** at [Pragmabits](https://github.com/pragmabits).

## License

MIT
