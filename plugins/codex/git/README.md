# Git Commit Workflow for Codex

Codex-native git commit workflow for semantic, hook-validated commits.

This plugin adapts the existing Claude git workflow to Codex instead of copying it. The Codex version uses:

- Agent skills for reusable workflows: `commit` and `commit-setup`
- Project-local Codex exec-policy rules generated into `.codex/rules/git-commit.rules`
- Project-local Codex lifecycle hooks generated into `.codex/hooks.json`
- Native git hooks installed into `.git/hooks/`
- Python scripts with only standard-library dependencies

## Skills

Use the skill selector or mention the skill in a prompt:

```text
$commit
$commit split by concern
$commit amend the last commit with the config change
$commit-setup --show
$commit-setup --apply
```

## Commit Convention

Subjects use:

```text
type: description
```

Valid types are `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, and `perf`.

The workflow stages whole files only. It does not use hunk staging, interactive patch mode, `git -C`, `git config user.name`, `git config user.email`, or `git commit --no-verify`.

## Setup

The setup skill runs `scripts/install_hooks.py`.

Default setup:

```bash
python3 plugins/codex/git/scripts/install_hooks.py --apply
```

Full setup with optional native hooks:

```bash
python3 plugins/codex/git/scripts/install_hooks.py --apply --all
```

Installed artifacts in the consumer repository:

- `.codex/rules/git-commit.rules`
- `.codex/hooks/git_command_policy.py`
- `.codex/hooks.json`
- `.codex/config.toml` with `[features].codex_hooks = true`
- `.git/hooks/commit-msg`
- Optional: `.git/hooks/pre-commit`
- Optional: `.git/hooks/prepare-commit-msg`

Existing third-party git hooks are not overwritten unless `--force` is passed.

## Design Notes

The plugin keeps the model responsible for semantic analysis and commit grouping, while deterministic checks live in Codex rules, Codex hooks, and native git hooks. This gives Codex room to reason about intent without trusting the model to enforce command safety or commit-message syntax by memory.
