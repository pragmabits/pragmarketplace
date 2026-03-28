---
name: commit-setup
description: Configure recommended permission rules to reduce prompts during commit-maker and tag-it execution
argument-hint: "[--show | --apply]"
---

# Commit Setup

Configures permission allow rules so the commit-maker agent can run git and validation commands without prompting for each one.

## Context

$ARGUMENTS

## What this does

The commit-maker agent runs ~11 Bash commands per commit (git status, git diff, git add, python validate-commit.py, git commit, git log). Without permission rules, each one prompts for approval.

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
      "Bash(git commit *)",
      "Bash(python *validate-commit.py*)",
      "Bash(python3 *validate-commit.py*)",
      "Bash(python *git-staging.pyz*)",
      "Bash(python3 *git-staging.pyz*)",
      "Bash(echo *=== STATUS ===*)",
      "Bash(echo *=== DIFF*)",
      "Bash(echo *=== LOG ===*)",
      "Bash(echo *=== COMMITS ===*)",
      "Bash(echo *=== LATEST TAG ===*)",
      "Bash(echo *=== ALL TAGS*)",
      "Bash(echo *=== COMMITS SINCE LAST TAG ===*)",
      "Bash(echo *=== HEAD ===*)",
      "Bash(echo *NO_TAGS_FOUND*)",
      "Bash(git describe *)",
      "Bash(git tag --sort*)",
      "Bash(git tag -a *)",
      "Bash(git tag -l *)",
      "Bash(git rev-parse *)"
    ]
  }
}
```

## Execution

### If `$ARGUMENTS` is `--show` or empty

Display the recommended permission rules and explain what each one allows.

Then explain the validation strategy options:
- **Python script only** (current default): The commit-maker agent calls `validate-commit.py` before each commit. Validation only happens inside Claude Code sessions.
- **Git hook only**: A native `commit-msg` hook installed in `.git/hooks/` that validates every commit — inside Claude Code, from the terminal, from IDEs, everywhere. The agent no longer needs to call the validator script separately.
- **Both** (recommended): The git hook catches everything at the git level, and the agent still validates before attempting the commit to get early feedback and avoid a hook rejection.

Tell the user they can run `/commit-setup --apply` to apply permissions and choose their validation strategy.

### If `$ARGUMENTS` is `--apply`

**Step 1 — Permission rules:**

1. Check if `.claude/settings.json` exists
2. If it exists, read it and merge the `permissions.allow` rules (do not duplicate existing rules, do not remove existing rules)
3. If it does not exist, create `.claude/settings.json` with only the permissions block
4. Report what was added

Use Bash to read and write the JSON file. Use `jq` for safe JSON manipulation.

**Step 2 — Validation strategy:**

First, detect the current validation setup:
- Check if `.git/hooks/commit-msg` exists and is executable → git hook is currently active
- The Python script is always available (it's part of the plugin) — the agent calls it by default

Report what is currently configured before asking the user to choose.

Use AskUserQuestion to ask which validation approach the user wants:

1. **Python script only** — No git hook installed. The agent validates via `validate-commit.py` before each commit. (This is the current behavior.)
2. **Git hook (recommended)** — Install `commit-msg` hook to `.git/hooks/commit-msg`. Every commit is validated by git itself, regardless of whether it comes from Claude Code, the terminal, or an IDE.
3. **Both** — Install the git hook AND keep the agent-side validation. Belt and suspenders.
4. **Skip** — Don't change the validation setup.

Based on the user's choice:

- **Python script only**: If a `commit-msg` git hook is currently installed, use AskUserQuestion to ask whether to remove it. If the user confirms, delete `.git/hooks/commit-msg`. If they decline, leave it in place and warn that both will remain active.
- **Git hook** or **Both**: Copy `${CLAUDE_PLUGIN_ROOT}/hooks/commit-msg` to `.git/hooks/commit-msg` and make it executable. If a `commit-msg` hook already exists that was NOT installed by this plugin (check if it contains the marker comment `# commit-msg hook — validates commit message format.`), warn the user and ask whether to overwrite or skip.
- **Both**: Also ensure the agent-side validation remains in the workflow (no changes needed — it's the default).

Report what was installed or removed.

**Step 3 — Additional git hooks (optional):**

First, detect which additional hooks are already installed by checking `.git/hooks/` for `pre-commit`, `prepare-commit-msg`, and `post-commit`. Report which are currently active.

Use AskUserQuestion to ask which additional hooks the user wants to install:

1. **pre-commit (secret and file guard)** — Blocks secrets, large files, no-commit markers, and blocklisted file types from being committed. Works everywhere, not just in Claude Code.
2. **prepare-commit-msg (smart drafting)** — Pre-populates commit messages with a conventional-commits draft based on staged files. Useful when committing from terminal or IDE.
3. **post-commit (tag advisor)** — Tracks commits since last tag and writes a suggestion file when it's time to create a release tag.
4. **All of the above**
5. **Skip** — Don't install additional hooks.

For each selected hook, copy from `${CLAUDE_PLUGIN_ROOT}/hooks/<hook-name>` to `.git/hooks/<hook-name>` and make executable.

If any hook already exists and was NOT installed by this plugin, warn the user and ask whether to overwrite or skip. If a hook is already installed by this plugin (check for the plugin's marker comments at the top of each script), report it as already up to date.

If the user did not select a hook that is currently installed, use AskUserQuestion to ask whether to remove it. This keeps the setup clean — the user should be in control of which hooks are active.

### Important

- Never overwrite existing allow or deny rules
- Only add rules that are not already present
- If all rules are already present, report that and do nothing
- Show a before/after diff of what changed
- When installing hooks, always check for existing hooks before overwriting
