---
name: commit
description: Use when the user asks Codex to commit changes, create semantic commits, split staged or unstaged work into coherent commits, amend the most recent commit, or follow Conventional Commits. Do not trigger for ordinary code edits unless the user explicitly asks to commit.
---

# Strategic Git Commit

Create semantic git commits from the current repository state.

## Core Rules

- One commit represents one semantic change.
- Stage whole files only with `git add -- <files>`.
- Never use `git add -p`, `git add --patch`, `git -C`, `git config user.name`, `git config user.email`, `git commit --no-verify`, or `git commit -n`.
- Keep the user's existing git identity and config unchanged.
- Do not sign, attribute, or add generated-by metadata.
- Match the dominant language of recent commit subjects from `git log --oneline -10`.
- Ask the user a concise question only when the diff leaves more than one materially valid strategy.

## Commit Message Format

Use:

```text
type: description
```

Allowed types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`.

Rules:

- No scope. Parenthesized scopes are not used.
- The description starts with a lowercase letter or digit.
- Description characters are limited to Unicode letters, digits, spaces, and `, . / + - : ' # >`.
- A breaking change may use `!` after the type, for example `feat!: remove legacy API`.
- Optional bodies must be separated from the subject by one blank line.
- Do not add co-author footers or model attribution.

## Initial Analysis

Run independent read-only commands separately. Use parallel tool calls when the active Codex client supports them. Do not chain with `&&` or shell wrappers.

Recommended analysis commands:

```bash
git status --short
git diff --stat HEAD
git diff HEAD
git diff --cached --stat
git diff --cached
git log --oneline -10
test -x .git/hooks/commit-msg
```

If the working tree and index are clean, report that there is nothing to commit and stop.

If `.git/hooks/commit-msg` is missing or not executable, warn:

```text
Commit message hooks are not installed. Run $commit-setup --apply to install them. Proceeding without hook validation.
```

## Strategy

Determine file groups by intent, not by file count.

Separate commits when changes have different reasons to exist, for example:

- Behavior change versus refactor
- Feature versus bug fix
- Runtime code versus unrelated docs
- Tests for a feature versus unrelated test maintenance
- Dependency or config maintenance versus product behavior

Group files when they explain one coherent change, even if many files are involved.

If unrelated concerns are mixed inside the same file, do not split hunks. Commit the file under the dominant change type, or ask the user which concern should own the file when dominance is unclear.

## Merge, Revert, and Cherry-pick States

Before rewriting a message, check whether git is already driving the commit:

```bash
git rev-parse --git-dir
```

If `MERGE_HEAD`, `REVERT_HEAD`, `CHERRY_PICK_HEAD`, or `SQUASH_MSG` exists in the git dir and the user asks to finish that operation, prefer the native git message:

```bash
git commit --no-edit
```

Do not force a Conventional Commits subject onto git-generated merge, revert, cherry-pick, or squash messages.

## Commit Execution

For each planned commit:

1. Stage files with one command:

   ```bash
   git add -- path/to/file another/file
   ```

2. Commit with a validated message:

   ```bash
   git commit -m "type: description"
   ```

3. Verify:

   ```bash
   git log --oneline -1
   ```

If a git hook rejects the commit, read the error, fix the message or staged content, and retry once. Do not bypass hooks.

## Amend Mode

Only amend when the user explicitly asks.

1. Stage the requested files.
2. If the user gives a new message, use it.
3. Otherwise preserve the existing subject with:

   ```bash
   git log -1 --format=%s
   ```

4. Run:

   ```bash
   git commit --amend -m "existing or user-provided message"
   ```

If an upstream branch exists, inspect whether rewriting the latest commit may affect already-pushed history. Warn before amending a commit that appears to be shared.

## Final Report

Run:

```bash
git log --oneline -5
git status --short
```

Report:

- Commits created or amended
- Files included in each commit
- Remaining uncommitted work
- Any commit that was blocked and why
