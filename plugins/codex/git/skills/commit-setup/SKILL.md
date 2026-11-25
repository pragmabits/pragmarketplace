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

If the user asks to apply setup, use the Codex structured question tool exposed
by the client (`request_user_input_async` or `request_user_input`) to ask whether to keep normal
approval prompts or enable automatic execution for the Git command forms used by
the workflow. Explain in the question that an `allow` rule may let those commands
run outside the sandbox without a prompt. This is a choice about the project's
setup, separate from authorizing any particular staging action or commit.

Apply with `--git-mutations prompt` or `--git-mutations allow` only after the
user selects that option. For an asynchronous question, wait for the answer
before applying the selected policy. If the client cannot present the question,
leave that choice pending, report it, and run the installer without the flag.
The installer preserves an existing choice and defaults to prompts on a new setup.

For example, with the normal approval policy:

```bash
python3 <plugin-root>/scripts/install_hooks.py --apply --git-mutations prompt
```

If the user asks for every native git hook:

```bash
python3 <plugin-root>/scripts/install_hooks.py --apply --all
```

If a specific set is requested:

```bash
python3 <plugin-root>/scripts/install_hooks.py --apply --hooks commit-msg,pre-commit
```

Add the selected approval flag to the same invocation when the user has answered.
Use `--force` only when the user explicitly agrees to replace a third-party git hook.

## Behavior

- The default `--apply` installs `commit-msg` plus Codex rules and hooks.
- Existing plugin-installed hooks are updated in place.
- Existing third-party hooks are skipped unless `--force` is provided.
- Existing locally edited rules and explicit hook settings are preserved.
- Codex discovers project hooks from `.codex/hooks.json`. Use the client's hook
  management UI to verify their trust status. Project rules also require a trusted project.
- The installer prints a summary of created, updated, skipped, and unchanged files.

## Verification

After applying setup, run:

```bash
python3 <plugin-root>/scripts/install_hooks.py --check
codex execpolicy check --pretty --rules .codex/rules/git-commit.rules -- git commit --no-verify
```

Expected: exec-policy reports `forbidden` for `git commit --no-verify`. Verify
that the hook definitions are trusted in the client. The file check does not
establish client trust or guarantee that a particular command skips approval.
