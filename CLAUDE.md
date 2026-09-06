# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

A Claude Code **plugin marketplace** (`pragmabits/pragmarketplace`). It contains no application code, no build, no test runner. The product is a tree of plugins (markdown + JSON + Bash) that other Claude Code instances install. Per-plugin install: `claude plugin add pragmabits/pragmarketplace --plugin <name>`.

## Repo layout

- `.claude-plugin/marketplace.json` — central plugin registry. Source of truth for what's published.
- `plugins/claude/<plugin>/.claude-plugin/plugin.json` — per-plugin manifest. Each carries its own `version`.
- `.claude/settings.json` — project permission allowlist. Belongs to the user; do not modify unless explicitly asked.

## Registered plugins

| Plugin | Version | Slash entries | What it is |
|--------|---------|--------------|-----|
| `git` | 3.0.1 | `/commit` (skill), `/commit-setup` (command) | Inline commit workflow + Conventional Commits validation. Native git hooks installed by `/commit-setup --apply`. |
| `review` | 1.0.1 | `/codex-review` (skill) | Wraps `scripts/codex-review.sh`. Requires the external `codex` CLI plus `jq`. |
| `session` | 2.3.1 | `/report`, `/recall` (skills) | Writes/reads handoff reports under `<repo>/.claude/sessions/`. `/report` auto-commits the new file by running `git add -- <path>` (so the brand-new file becomes tracked) then `git commit -m "chore: …" -- <path>` (partial commit; other staged work untouched); pass `--no-commit` to skip. The `/recall` `last` and `resume` subcommands return file pointers; the agent uses `Read` to ingest reports rather than dumping them into the chat. |
| `pragma` | 0.1.0 | — | Standing working directives. No slash entry and nothing to invoke: a `SessionStart` hook emits `instructions.md` as session context. Ships one rule — verify a disputed claim before conceding it. |

## Slash entries: commands vs skills

Both `commands/*.md` and `skills/*/SKILL.md` files can serve as slash entry points. In this repo:

- `/commit-setup` is a command (`plugins/claude/git/commands/commit-setup.md`).
- `/commit` is a skill (`plugins/claude/git/skills/commit/SKILL.md`) — the workflow runs inline in the main context, no sub-agent.
- `/codex-review` is a skill with `disable-model-invocation: true` (slash-only, not auto-discovered).
- `/report` and `/recall` are skills.

Frontmatter that affects behavior: `name`, `description` (drives skill auto-discovery matching — keywords matter), `argument-hint`, `allowed-tools`, `disable-model-invocation`, `model`, `color`, `memory`, `tools`.

Path expansions inside command/skill bodies:
- `${CLAUDE_PLUGIN_ROOT}` — plugin absolute root. Used in commands and `hooks/hooks.json`.
- `${CLAUDE_SKILL_DIR}` — skill absolute root. Used inside SKILL.md bodies (e.g., `review/skills/codex-review/SKILL.md`).
- `!`-prefixed fenced blocks inside a SKILL.md are shell-executed at render time and the output is substituted into the prompt (e.g., `session/skills/report/SKILL.md` injects git metadata this way; `session/scripts/ensure-sessions-dir.sh` resolves the sessions directory via `$CLAUDE_PROJECT_DIR` → `git rev-parse --show-toplevel` → `pwd`).

## Validation hooks

Plugin-level hooks declared in `<plugin>/hooks/hooks.json`. Hook scripts deny a tool call by writing JSON to stderr and exiting non-zero:

```
{"hookSpecificOutput": {"permissionDecision": "deny"}, "systemMessage": "..."}
```

They depend on `jq`. One is wired in this repo:

- `git/hooks/validate-git-command.sh` — PreToolUse on Bash. Blocks `git add -p`, `git -C`, and `git config user.{name,email}`.

Hook entries set `"timeout": 5` (seconds).

Not every hook validates. `pragma/hooks/session-start.sh` is a `SessionStart` hook
(`matcher: "startup|clear|compact"`) that injects context instead of gating a tool
call: it emits `instructions.md` on stdout as
`hookSpecificOutput.additionalContext`, letting `jq --rawfile` do the JSON
escaping. It exits non-zero when `instructions.md` or `jq` is missing rather than
emitting nothing — a context hook that silently produces empty output is
indistinguishable from a plugin that was never enabled.

## Native git hooks

Installed by `/commit-setup --apply` into the consumer repo's `.git/hooks/`. Each script carries a marker comment used by `commit-setup` to detect plugin-installed hooks vs third-party hooks; preserve those comments verbatim when editing.

- `commit-msg` — enforces `type: description` (`feat|fix|docs|style|refactor|test|chore|perf`), lowercase/digit first char, the explicit allowed-character set (Unicode letters, digits, spaces, and `, . / + - : ' # >`), single blank line before any body, and a Trojan-Source / CVE-2021-42574 ban on bidi/zero-width/control codepoints in the body. Skips merge / revert / squash / cherry-pick / `fixup!` / `squash!` / `amend!` messages.
- `pre-commit` — blocks staged secrets, files >1MB, and blocklisted file types (`.pyc`, `.pyo`, `.DS_Store`, `.swp`, `.swo`, `.env`).
- `prepare-commit-msg` — drafts a Conventional Commits subject from staged files. Type detection is path-pattern only and falls back to `feat:` whenever staged files don't all match a single non-feat category — drafts can mis-classify and are intended to be edited.

## Working in this repo

There is no build/test pipeline. Verification is structural:

```bash
# Validate the marketplace JSON
jq . .claude-plugin/marketplace.json

# Validate any plugin manifest
jq . plugins/claude/<plugin>/.claude-plugin/plugin.json

# Smoke-test a hook with a fake tool input on stdin
echo '{"tool_input":{"command":"git add -p ."}}' | bash plugins/claude/git/hooks/validate-git-command.sh

# Install a plugin from the local checkout
claude plugin add ./plugins/claude/<plugin>
```

For commits, use `/commit`. The user drives commit boundaries — do not propose splits or messages proactively; let the skill ask via `AskUserQuestion` when ambiguous.

Skill `evals/evals.json` files are test-case definitions only — there is no in-repo runner. Treat them as the contract a skill is meant to satisfy, not an executable suite.

## Releasing

Two version fields move together for any plugin change:

1. `plugins/claude/<plugin>/.claude-plugin/plugin.json` → `version`
2. `.claude-plugin/marketplace.json` → `plugins[<n>].version` for that plugin

If the marketplace itself changed (added/removed a plugin, registry-level metadata), also bump `.claude-plugin/marketplace.json` → `metadata.version`.

## Conventions

- File naming: kebab-case throughout (commands, skills, scripts).
- Every user-facing decision in commands/skills goes through `AskUserQuestion`, never plain text questions.
- No plugin here ships agents any more. If one does again, it fetches live docs at runtime via the `context7` MCP server and `WebSearch` rather than carrying pre-baked snippets, and dispatch is `subagent_type: "<plugin>:<agent>"`.
- Skill `description:` frontmatter is the trigger contract for auto-discovery — keywords and example phrases in there matter. Edit deliberately.
- Project allow rules in `.claude/settings.json` are designed so each `git` invocation runs as a separate Bash call (one rule each). The `/commit` skill explicitly tells the model to run `git status`, `git diff HEAD`, `git diff --cached`, and `git log` as parallel Bash calls — do not chain them with `&&`.
