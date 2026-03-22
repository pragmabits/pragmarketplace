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
