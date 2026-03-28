---
name: commit
description: "Strategic git commit skill that delegates to the commit-maker agent for semantic analysis, intelligent change partitioning, hunk-level staging, and validated commits following Conventional Commits (type: description, no scope). Use this skill when the user wants to commit changes, create commits, split changes into atomic commits, organize staged/unstaged work into proper commits, or run /commit. Also use when the user mentions committing, staging for commit, conventional commits format, patch mode for commits, separating refactoring from feature commits, or wants help figuring out the right commit strategy for their changes."
---

# Strategic Git Commit

This skill delegates to the `commit-maker` agent, which provides semantic diff analysis, intelligent change partitioning, hunk-level staging, and mandatory message validation. The agent produces focused, single-purpose commits following the project's Conventional Commits convention (`type: description`, no scope).

## Why this skill exists

Creating good commits requires analyzing the staged diff to determine semantic boundaries, choosing the right commit type, separating refactoring from behavioral changes, and validating message format. The commit-maker agent handles all of this autonomously — it reads the repository state, plans a partitioning strategy, stages changes (including hunk-level staging when a file contains independent changes), validates each message against the project's format rules, and executes the commits.

Without this skill, commit messages tend to be vague, changes get lumped together, and format rules get violated.

## When to use this skill

Use this skill when the user wants to:

- Commit their current changes (staged or unstaged)
- Create one or more commits from their work
- Split changes into multiple focused, atomic commits
- Use patch/hunk-level staging for granular commits
- Separate refactoring from behavioral changes in commits
- Figure out the right commit strategy for mixed changes
- Ensure commit messages follow conventional commits format
- Run `/commit` with or without context

This skill applies even when the user doesn't say "commit" directly — phrases like "can you organize these changes properly", "split these into clean atomic commits", "I need to commit but the refactor and feature are mixed", or "make sure the messages follow our format" all indicate this skill should be used.

## How to use

Invoke the `/commit` command, passing any user context as the argument:

```
/commit <user's context or instruction>
```

The agent will:
1. Analyze the working tree (status, diff, diff --cached, log)
2. Perform semantic diff analysis to determine commit boundaries
3. Stage changes (whole files or specific hunks via the staging tool)
4. Validate each message per the configured `validation_strategy` in `.claude/git.local.md`
5. Execute commits only after validation passes
6. Report the result

Do not attempt to commit changes yourself — the agent has specialized tooling (staging tool, validator) and a detailed workflow for producing clean, focused commits. Let the agent handle it.
