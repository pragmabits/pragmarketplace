---
name: commit-setup
description: Configure recommended permission rules and install git hooks for commit and tag-it execution
argument-hint: "[--show | --apply]"
---

# Commit Setup

Configures permission allow rules and installs git hooks so the commit workflow can run without prompting for each command.

## Context

$ARGUMENTS

## What this does

The commit workflow runs several Bash commands per commit (git status, git diff, git add, git commit, git log). Without permission rules, each one prompts for approval.

This command adds targeted allow rules to your project's `.claude/settings.json` so these specific commands run without prompts. The safety hook (`validate-git-command.sh`) still blocks dangerous patterns (git add -p, git -C, git config user.name/email).

## Recommended rules

These are the permission rules this command configures:

```json
{
  "permissions": {
    "allow": [
      "Bash(git status*)",
      "Bash(git diff *)",
      "Bash(git diff)",
      "Bash(git log *)",
      "Bash(git add *)",
      "Bash(git reset HEAD*)",
      "Bash(git commit *)",
      "Bash(git tag *)",
      "Bash(git rev-parse *)",
      "Bash(test -x *)"
    ]
  }
}
```

## Execution

### If `$ARGUMENTS` is `--show` or empty

Display the recommended permission rules and explain what each one allows.

Then explain the hook-based validation approach:
- The commit workflow relies on native git hooks for all validation. A `commit-msg` hook installed in `.git/hooks/` validates every commit — inside Claude Code, from the terminal, from IDEs, everywhere. If the message is invalid, `git commit` fails and the error explains what's wrong.

Tell the user they can run `/commit-setup --apply` to apply permissions and install git hooks.

### If `$ARGUMENTS` is `--apply`

**Step 1 — Permission rules:**

1. Check if `.claude/settings.json` exists
2. If it exists, read it and merge the `permissions.allow` rules (do not duplicate existing rules, do not remove existing rules)
3. If it does not exist, create `.claude/settings.json` with only the permissions block
4. Report what was added

Use Bash to read and write the JSON file. Use `jq` for safe JSON manipulation.

**Step 2 — Install commit-msg hook:**

Check if `.git/hooks/commit-msg` exists and is executable. Report the current state.

If the hook is not installed, copy `${CLAUDE_PLUGIN_ROOT}/hooks/commit-msg` to `.git/hooks/commit-msg` and make it executable.

If a `commit-msg` hook already exists:
- Check if it was installed by this plugin (contains the marker comment `# commit-msg hook — validates commit message format.`)
- If it's from this plugin, report it as already up to date
- If it's from another source, warn the user and ask (via AskUserQuestion) whether to overwrite or skip

Report what was installed.

**Step 3 — Additional git hooks (optional):**

First, detect which additional hooks are already installed by checking `.git/hooks/` for `pre-commit`, `prepare-commit-msg`, and `post-commit`. Report which are currently active.

Use AskUserQuestion to ask which additional hooks the user wants to install:

1. **pre-commit (secret and file guard)** — Blocks secrets, large files, no-commit markers, and blocklisted file types from being committed. Works everywhere, not just in Claude Code.
2. **prepare-commit-msg (smart drafting)** — Pre-populates commit messages with a conventional-commits draft based on staged files. Useful when committing from terminal or IDE.
3. **post-commit (tag advisor)** — Tracks commits since last tag and writes a suggestion file when it's time to create a release tag.
4. **All of the above**
5. **Skip** — Don't install additional hooks.

For each selected hook, copy from `${CLAUDE_PLUGIN_ROOT}/hooks/<hook-name>` to `.git/hooks/<hook-name>` and make executable.

If any hook already exists and was NOT installed by this plugin, warn the user and ask whether to overwrite or skip. To determine if a hook was installed by this plugin, check for these marker comments near the top of each script:
- `commit-msg`: `# commit-msg hook — validates commit message format.`
- `pre-commit`: `# pre-commit hook — catches dangerous content before it enters history.`
- `prepare-commit-msg`: `# prepare-commit-msg hook — drafts a conventional commit message from staged changes.`
- `post-commit`: `# post-commit hook — tracks commits since last tag and suggests when to tag.`

If the marker is present, report the hook as already up to date.

If the user did not select a hook that is currently installed, use AskUserQuestion to ask whether to remove it. This keeps the setup clean — the user should be in control of which hooks are active.

### Important

- Never overwrite existing allow or deny rules
- Only add rules that are not already present
- If all rules are already present, report that and do nothing
- Show a before/after diff of what changed
- When installing hooks, always check for existing hooks before overwriting
