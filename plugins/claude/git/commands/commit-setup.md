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

## Execution

### If `$ARGUMENTS` is `--show` or empty

Display the recommended rules and explain what each one allows. Do not modify any files. Tell the user they can run `/commit-setup --apply` to apply them automatically.

### If `$ARGUMENTS` is `--apply`

1. Check if `.claude/settings.json` exists
2. If it exists, read it and merge the `permissions.allow` rules (do not duplicate existing rules, do not remove existing rules)
3. If it does not exist, create `.claude/settings.json` with only the permissions block
4. Report what was added

Use Bash to read and write the JSON file. Use `jq` for safe JSON manipulation.

### Important

- Never overwrite existing allow or deny rules
- Only add rules that are not already present
- If all rules are already present, report that and do nothing
- Show a before/after diff of what changed
