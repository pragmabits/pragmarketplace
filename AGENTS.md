# AGENTS.md

Guidance for Codex agents working in `pragmabits/pragmarketplace`.

## Project Identity

This repository is a plugin marketplace. It publishes Claude Code plugins under `plugins/claude/`, registered in `.claude-plugin/marketplace.json`, and Codex plugins under `plugins/codex/`, registered in `.agents/plugins/marketplace.json`. There is no application code, build pipeline or package manager workflow. The only in-repo tests are script suites:

- the `session` plugins': `bash plugins/claude/session/tests/run.sh` (it also exercises the Codex scripts and checks that both readers agree) and `python3 -I plugins/codex/session/tests/test_session.py`;
- the `git` plugins' guards: `bash plugins/claude/git/tests/run.sh` and `python3 -I plugins/codex/git/tests/test_git_command_policy.py`;
- the `pragma` review gate's: `python3 -B -I plugins/claude/pragma/tests/test_gate.py` (deterministic), and `plugins/claude/pragma/tests/behavior.py`, which calls the model.

Codex-specific work belongs outside the Claude plugin space. Use `AGENTS.md`, `.codex/`, and `plugins/codex/` for Codex instructions, rules, experiments, and future Codex plugin content.

## Hard Boundary: Claude Plugin Space Is Read-Only

Codex agents may read, inspect, summarize, validate, and review the Claude plugin space, but must never create, edit, move, delete, format, or mechanically rewrite anything under these paths:

- `plugins/claude/`
- `.claude-plugin/`
- `.claude/`
- `CLAUDE.md`

This includes manifests, commands, skills, agents, hooks, scripts, references, docs, output styles, marketplace metadata, and session files. If a user asks for a change to the Claude plugin space, explain that this Codex configuration treats those paths as read-only and ask them to switch to the Claude workflow or explicitly change the repository policy first.

Do not use shell redirection, `tee`, `sed -i`, ad hoc scripts, formatters, code generators, `git checkout`, `git restore`, or any other workaround to modify those paths. The local Codex filesystem permission profile in `.codex/config.toml` enforces read-only access for the same boundary.

## Repo Layout

- `.claude-plugin/marketplace.json`: central Claude plugin registry and published version source of truth.
- `plugins/claude/<plugin>/.claude-plugin/plugin.json`: per-plugin Claude manifest.
- `plugins/codex/<plugin>/.codex-plugin/plugin.json`: per-plugin Codex manifest. Current Codex plugins: `git` `0.2.0` and `session` `0.2.0`.
- `.agents/plugins/marketplace.json`: Codex marketplace metadata for repo-local Codex plugins.
- `.harness/sessions/`: session handoff reports, shared by the Claude Code and Codex `session` plugins. This belongs to the user project, not to Claude, Codex, `.agents`, or any plugin runtime.
- `.codex/config.toml`: project-local Codex configuration and filesystem permission profile.
- `.codex/rules/*.rules`: project-local Codex exec approval rules.
- `CLAUDE.md`: Claude Code instructions. Read-only for Codex agents.

## Registered Claude Plugins

Current marketplace entries:

- `git` `3.1.0`: semantic commit workflow, Conventional Commits validation, native git hooks, safety hooks.
- `review` `1.0.1`: `/codex-review`, backed by `codex-review.sh` and the external Codex CLI.
- `session` `3.0.0`: `/report` and `/recall` handoff reports for Claude Code.
- `pragma` `0.3.2`: standing working directives injected by a `SessionStart` hook, plus a review gate on `AskUserQuestion` and turn ends. No slash entry.
- `axio` `0.4.0`: `axio` and `migration` skills for the axio Go logging library. No slash entry; sourced by `git-subdir` from `pragmabits/axio` (`plugin/`), not from `plugins/claude/`.

Treat those entries as read-only inventory unless the project policy changes.

## Validation

For Codex-side changes, keep verification structural and local:

```bash
git status --short
python3 -c 'import pathlib, tomllib; tomllib.loads(pathlib.Path(".codex/config.toml").read_text())'
codex execpolicy check --pretty --rules .codex/rules/claude-readonly.rules -- rm -rf plugins/claude/git
```

`jq` is for JSON only; do not run it on TOML.

## Working Conventions

- Prefer `rg` and `rg --files` for discovery.
- Keep Codex edits scoped to Codex-owned files unless the user explicitly changes the read-only boundary.
- Store session handoff reports under root `.harness/sessions/`; never write session reports under `.codex/`, `.agents/`, or `.claude/`.
- Do not introduce build tooling or dependency files unless the task specifically requires it.
- Keep plugin marketplace facts synchronized with `.claude-plugin/marketplace.json` when documenting inventory, but do not edit that registry from Codex.
- When a request touches both Claude and Codex concerns, implement only the Codex-owned side and clearly name any Claude-side change that remains blocked by policy.
