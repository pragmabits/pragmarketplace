# Git Commit Workflow for Codex

Codex-native git commit workflow for semantic, hook-validated commits.

The workflow uses:

- Agent skills for reusable workflows: `commit` and `commit-setup`
- Project-local Codex exec-policy rules generated into `.codex/rules/git-commit.rules`
- Project-local Codex lifecycle hooks generated into `.codex/hooks.json`
- Native Git hooks installed at the active path reported by Git
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

Git commands run from the repository root. When the session directory is below the root, the workflow gives each command the root as its `workdir`, never a `cd <root> &&` prefix, which the Codex hook blocks.

## Setup

The setup skill runs `scripts/install_hooks.py` with Python 3.11 or later.

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
- `commit-msg` validates the message format and rejects supported attribution trailers.
- Optional `pre-commit` checks size, paths, and newly added secrets or markers. Session reports skip the marker check.
- Optional `prepare-commit-msg` drafts the subject from the staged paths.

Existing third-party git hooks are not overwritten unless `--force` is passed.
The Codex setup question offers keeping approval prompts or allowing the
workflow's Git command forms without prompts. The latter can run those commands
outside the sandbox. Project-local rules require a trusted project. Check
hook trust in the Codex client, since an installed hook can still be inactive.

## Design Notes

The plugin keeps the model responsible for semantic analysis and commit grouping, while deterministic checks live in Codex rules, Codex hooks, and native git hooks. This gives Codex room to reason about intent without trusting the model to enforce command safety or commit-message syntax by memory.

The commit skill runs Git from the repository root. The command hook blocks a
`cd` before Git in a single call. Ordinary commands such as `git status`
remain available from subdirectories.

Tests: `python3 -I plugins/codex/git/tests/test_git_command_policy.py`.
