---
# Extra commit types beyond the default set.
# Each entry: type_name: description
extra_types:
  build: build system or external dependencies
  ci: continuous integration configuration
  revert: revert a previous commit

# Override commit message language. By default, the agent detects
# language from git log. Set this to force a specific language.
# language: en

# Allow multi-line commit messages (body after blank line).
# Default: false (single-line only)
# allow_body: false

# Maximum description length (characters). Default: no limit.
# max_length: 72
---

# Git Plugin Settings

Per-project configuration for the git commit plugin.
Place this file at `.claude/git.local.md` in your project root.

After editing, restart Claude Code for changes to take effect.

## Recommended Permission Rules

The commit-maker agent runs several Bash commands per commit. To avoid being prompted
for each one, add these rules to `.claude/settings.json` in your project root:

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
      "Bash(python *git-staging.pyz*)",
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

Or run `/commit-setup --apply` to configure this automatically.

The safety hook still blocks dangerous patterns regardless of these rules.

## Native Git Hooks

For validation that works outside of Claude Code (terminal, IDE, CI), install the
commit-msg git hook via `/commit-setup --apply` and choose "Git hook" or "Both".

Additional hooks available: `pre-commit` (secret/file guard), `prepare-commit-msg` (smart drafting), `post-commit` (tag advisor).

## Recommended .gitignore entries

```
.claude/*.local.md
.claude/tag-suggestion
```
