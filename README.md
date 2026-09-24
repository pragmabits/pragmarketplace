# Pragmatic

A curated collection of Claude Code plugins by [Pragmabits](https://github.com/pragmabits).

## Overview

Pragmatic provides ready-to-install plugins that extend Claude Code with specialized knowledge, tools, and workflows. Each plugin is focused on a specific domain — commit strategy, code review, session handoff, the axio library — and reaches Claude Code through the slash command system, through a session hook in `pragma`'s case, or through skills Claude loads when the work calls for them in `axio`'s case.

## Plugins

| Plugin | Version | Category | Slash Commands | Description |
|--------|---------|----------|----------------|-------------|
| **git** | 3.0.1 | Tools | `/commit`, `/commit-setup` | Semantic commits, whole-file staging, hook-validated messages, native git hooks, and safety hooks |
| **review** | 1.0.1 | Tools | `/codex-review` | Independent Codex-based code review of the current `git diff` — verdict, summary, and findings |
| **session** | 2.3.1 | Tools | `/report`, `/recall` | Session handoff reports with fixed-numbered pending items (`/report`); list, filter, grep, resume, and read back prior reports via five `/recall` subcommands (`list`, `filter`, `grep`, `resume`, `last`) |
| **pragma** | 0.2.0 | Output | — | Standing working directives injected at session start — verify before conceding, a complaint is not a work order, a dominated option is not an option, verify before claiming |
| **axio** | 0.4.0 | Development | — | Skills for the [axio](https://github.com/pragmabits/axio) Go logging library: an entry skill for the whole API and a migration skill for code on `log`, `slog`, logrus, zerolog, zap or apex/log. Its source lives in the axio repository |

## Installation

Add the marketplace once, then install any plugin from it:

```bash
claude plugin marketplace add pragmabits/pragmarketplace
claude plugin install <plugin-name>@pragmatic
```

For example, to install the git plugin:

```bash
claude plugin install git@pragmatic
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

The **axio** plugin has no slash command either: its `axio` skill loads when the work involves axio, and its `migration` skill when code moves to axio from another logging library.

## Author

Built by **Leonardo Leoncio** at [Pragmabits](https://github.com/pragmabits).

## License

MIT
