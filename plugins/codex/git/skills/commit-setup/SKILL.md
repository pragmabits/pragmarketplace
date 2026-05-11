---
name: commit-setup
description: Use when the user wants to install or inspect the Codex git commit workflow setup, including Codex exec-policy rules, Codex lifecycle hooks, and native git hooks for commit validation.
---

# Commit Setup

Install or inspect the deterministic pieces used by the `commit` skill.

## Native Codex Setup

This setup is intentionally Codex-native. It does not write Claude settings and does not depend on Claude commands.

It can install:

- `.codex/rules/git-commit.rules` for Codex exec-policy decisions
- `.codex/hooks/git_command_policy.py` for Codex hook command checks
- `.codex/hooks.json` entries for `PreToolUse` and `PermissionRequest`
- `.codex/config.toml` with `[features].codex_hooks = true`
- `.git/hooks/commit-msg` for Conventional Commit validation
- Optional `.git/hooks/pre-commit` for secret and file guards
- Optional `.git/hooks/prepare-commit-msg` for native message drafting

## How to Run

Resolve this skill directory from the skill file path. The installer is two directories up:

```text
../../scripts/install_hooks.py
```

If the user asks to inspect setup, run:

```bash
python3 <plugin-root>/scripts/install_hooks.py --show
```

If the user asks to apply the recommended setup, run:

```bash
python3 <plugin-root>/scripts/install_hooks.py --apply
```

If the user asks for every native git hook:

```bash
python3 <plugin-root>/scripts/install_hooks.py --apply --all
```

If a specific set is requested:

```bash
python3 <plugin-root>/scripts/install_hooks.py --apply --hooks commit-msg,pre-commit
```

Use `--force` only when the user explicitly agrees to replace a third-party git hook.

## Behavior

- The default `--apply` installs `commit-msg` plus Codex rules and hooks.
- Existing plugin-installed hooks are updated in place.
- Existing third-party hooks are skipped unless `--force` is provided.
- The installer prints a summary of created, updated, skipped, and unchanged files.

## Verification

After applying setup, run:

```bash
python3 <plugin-root>/scripts/install_hooks.py --check
codex execpolicy check --pretty --rules .codex/rules/git-commit.rules -- git commit --no-verify
```

Expected: the check command reports `forbidden` for `git commit --no-verify`.
