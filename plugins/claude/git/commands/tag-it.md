---
name: tag-it
description: Suggest and create a version tag based on repository history and commit analysis
argument-hint: "[version or context] - e.g. 'v2.0.0' or 'tag the latest work'"
---

# Tag It

Create a version tag for the current HEAD.

## User Context

$ARGUMENTS

## Workflow

### 1. Gather context

Run as **separate, parallel Bash calls**:

- `git tag --sort=-creatordate | head -5`
- `git log --oneline -15`

The first tag in the list is the latest. No tags means start at `v0.1.0`.

### 2. Determine next version

From the tags, detect the scheme (semver `v1.2.3` or calver `2026.04`). Preserve the existing prefix convention (`v` or no `v`).

If `$ARGUMENTS` contains an explicit version (e.g. "v2.0.0"), skip to step 4.

For semver, classify commits since the latest tag:
- `feat!:` or `!` marker → major bump
- `feat:` → minor bump
- Everything else → patch bump

The highest-impact type wins.

### 3. Ask the user

**Always use AskUserQuestion** — never ask via plain text output.

Present the recommended version first, all three semver increments, and a "Skip" option. Reference the actual commits that drive the recommendation.

Example:
```
header: "Version Tag"
question: "Which version? Latest: v1.2.3 (4 commits since)"
options:
  - "v1.3.0 (Recommended) — Minor: includes feat: add OAuth2 support"
  - "v1.2.4 — Patch: fixes and maintenance only"
  - "v2.0.0 — Major: breaking API changes"
  - "Skip — Don't create a tag"
```

If user chooses "Skip", stop.

### 4. Create the tag

Build the annotation from the commit list since the last tag:

```bash
git tag -a "<version>" -m "<annotation>"
```

The annotation format:

```
Release <version>

- feat: add OAuth2 support
- fix: correct token refresh logic
```

Then verify: `git tag -l "<version>"`

Report: tag name, what it points to, remind user about `git push --tags`.
