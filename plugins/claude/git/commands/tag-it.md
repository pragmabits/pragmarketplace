---
name: tag-it
description: Suggest and create a version tag based on repository history and commit analysis
argument-hint: "[version or context] - e.g. 'v2.0.0' or 'tag the latest work'"
---

# Tag It

Create a version tag for the current HEAD based on repository history analysis.

## User Context

$ARGUMENTS

## Workflow

### 1. Gather context

Run a single combined command:

```bash
echo "=== LATEST TAG ===" && { git describe --tags --abbrev=0 2>/dev/null || echo "NO_TAGS_FOUND"; } && echo "=== ALL TAGS (last 10) ===" && git tag --sort=-version:refname | head -10; echo "=== COMMITS SINCE LAST TAG ===" && { git log "$(git describe --tags --abbrev=0 2>/dev/null || echo 'HEAD~10')..HEAD" --oneline 2>/dev/null || git log --oneline -10; } && echo "=== HEAD ===" && git log --oneline -1
```

### 2. Detect versioning scheme

Examine existing tags to determine the project's versioning convention:

- **Semver** (e.g. `v1.2.3`, `1.2.3`): the most common scheme. Look for `major.minor.patch` patterns, with or without a `v` prefix.
- **CalVer** (e.g. `2026.03.26`, `2026.03`): date-based versions. Look for year-prefixed patterns.
- **Custom**: any other pattern — describe what you see and propose a next version that follows the convention.
- **No tags exist**: default to semver starting at `v0.1.0`.

Preserve the prefix convention (with or without `v`) from existing tags.

### 3. Analyze commits

For semver, classify the commits since the last tag:

- **Breaking change** (`!` after type, e.g. `feat!:`) → recommend **major** bump
- **New feature** (`feat:`) → recommend **minor** bump
- **Everything else** (`fix:`, `docs:`, `chore:`, `refactor:`, `style:`, `test:`, `perf:`) → recommend **patch** bump

When multiple commit types are present, the highest-impact type determines the recommendation.

For calver, compute the next date-based version.

### 4. Handle explicit version

If `$ARGUMENTS` contains an explicit version (e.g. "v2.0.0", "1.5.0"), skip the suggestion step. Validate the format matches the existing convention and proceed to tag creation (step 6).

### 5. Ask the user

Use AskUserQuestion to present version options. The recommended version goes first with justification based on the commit analysis.

For semver, always present all three increments plus a skip option. The justification should reference the actual commits that drive the recommendation.

Example:
```
Question: "Which version tag do you want to create? Latest: v1.2.3 (4 commits since)"
Options:
  1. "v1.3.0 (Recommended)" — "Minor: includes feat: add OAuth2 support"
  2. "v1.2.4" — "Patch: if these are just fixes and maintenance"
  3. "v2.0.0" — "Major: if this includes breaking API changes"
  4. "Skip" — "Don't create a tag"
```

### 6. Create the tag

If the user chose a version (or provided one explicitly):

1. Build an annotated tag message listing the commits since the last tag:

```
Release <version>

- feat: add OAuth2 support
- fix: correct token refresh logic
- docs: update API reference
```

2. Create the tag using `printf` to build the multi-line message:

```bash
git tag -a "<version>" -m "$(printf 'Release <version>\n\n- feat: add OAuth2 support\n- fix: correct token refresh logic\n- docs: update API reference')"
```

3. Verify:

```bash
git tag -l "<version>" && git log --oneline -1 "<version>"
```

4. Report the result: tag name, what it points to, and whether the user needs to `git push --tags` to publish it.

### 7. Skip

If the user chose "Skip", acknowledge and stop. No further action.

## Edge cases

- **Dirty working directory**: warn the user that there are uncommitted changes. Suggest committing first (mention `/commit`), but don't block tagging if they want to proceed.
- **HEAD already tagged**: report the existing tag and ask if they want to create an additional tag or skip.
- **Detached HEAD**: warn and ask for confirmation before tagging.
