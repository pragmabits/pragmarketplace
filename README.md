# Pragmatic

A curated collection of Claude Code plugins by [Pragmabits](https://github.com/pragmabits).

## Overview

Pragmatic provides ready-to-install plugins that extend Claude Code with specialized knowledge, tools, and workflows. Each plugin is focused on a specific domain — commit strategy, code review, session handoff — and reaches Claude Code either through the slash command system or, in `pragma`'s case, through a session hook.

## Plugins

| Plugin | Version | Category | Slash Commands | Description |
|--------|---------|----------|----------------|-------------|
| **git** | 3.0.1 | Tools | `/commit`, `/commit-setup` | Semantic commits, whole-file staging, hook-validated messages, native git hooks, and safety hooks |
| **review** | 1.0.1 | Tools | `/codex-review` | Independent Codex-based code review of the current `git diff` — verdict, summary, and findings |
| **session** | 2.3.1 | Tools | `/report`, `/recall` | Session handoff reports with fixed-numbered pending items (`/report`); list, filter, grep, resume, and read back prior reports via five `/recall` subcommands (`list`, `filter`, `grep`, `resume`, `last`) |
| **pragma** | 0.1.0 | Output | — | Standing working directives injected at session start — currently one rule: verify a disputed claim before conceding it, and say so when the user is wrong |

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
/codex-review    # Independent Codex-based review of the current git diff
/report          # Generate a session handoff report
/recall          # List, filter, grep, or resume prior session reports
```

The **pragma** plugin has no slash command and nothing to invoke — a `SessionStart` hook injects its directives as session context, so they are in force before the first answer.

## Author

Built by **Leonardo Leoncio** at [Pragmabits](https://github.com/pragmabits).

## License

MIT
