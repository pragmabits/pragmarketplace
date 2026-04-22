---
name: commit
description: "Strategic git commit skill with semantic analysis, whole-file staging, and hook-validated commits following Conventional Commits (type: description, no scope). Use this skill when the user wants to commit changes, create commits, split changes into atomic commits, organize staged/unstaged work into proper commits, or run /commit. Also use when the user mentions committing, staging for commit, conventional commits format, separating refactoring from feature commits, or wants help figuring out the right commit strategy for their changes."
---

# Strategic Git Commit

Self-contained commit workflow. Analyzes the working tree, determines semantic boundaries, stages whole files, and commits with hook-validated messages. No sub-agent, no hunk-level staging, no Python scripts.

## Commit Convention

Format: `type: description`

- Exactly one line — no body, no footer, no metadata
- No scope (parentheses forbidden)
- Valid types: feat | fix | docs | style | refactor | test | chore | perf
- Description starts with a lowercase letter or digit
- Allowed characters: Unicode letters, digits, spaces, and `, . / + -`
- Breaking change: `!` after type (e.g., `feat!: remove legacy API`)
- Merge, revert, squash, cherry-pick e mensagens `fixup!`/`squash!`/`amend!` geradas pelo git pulam a validação automaticamente (paridade com `commitlint defaultIgnores`).

## Rules

### No signatures or metadata

Never append co-authored-by lines, generation metadata, or anything beyond the single-line message. The commit history stays clean.

### No git -C flag

All git commands run in the current working directory. The `-C` flag causes path resolution issues.

### No hunk-level staging

Stage whole files only via `git add <files>`. Never use `git add -p` or any patch-mode staging. If a file has mixed concerns, commit it under the dominant change type.

### Hook-based validation

Do not run any validation script. Git hooks handle message validation transparently. If `git commit` fails, read stderr for the error, fix the message, and retry. Never reimplement format checks manually.

### Hook check

Before the first commit, verify hooks are installed:

```bash
test -x .git/hooks/commit-msg && echo "hooks: installed" || echo "hooks: NOT installed"
```

If hooks are not installed, warn the user: "Commit message hooks are not installed. Run `/commit-setup --apply` to install them. Proceeding without validation."

### Commit message language

Write messages in the dominant language of the repository's existing commit history. Check `git log --oneline -10` during analysis and match that language. Do not infer language from code, variable names, or comments — only from commit messages.

### Git configuration

Use the existing git config as-is. Never run `git config user.name` or `git config user.email`.

## Project Settings

Check for `.claude/git.local.md` during analysis. If present, read its YAML frontmatter and apply:

- **extra_types**: Additional commit types beyond the default set (e.g., `build`, `ci`, `revert`). The git hooks also read this setting.
- **language**: Override commit message language detection.
- **allow_body**: If `true`, allow multi-line commit messages. Default: `false`.
- **max_length**: Maximum description length in characters. Default: no limit.

If the file doesn't exist, use defaults. Do not ask the user about settings.

## Workflow

### 1. Analyze

Run these four commands as **separate, parallel Bash calls** (not chained with `&&`). This ensures each matches its permission rule individually:

- `git status`
- `git diff HEAD`
- `git diff --cached`
- `git log --oneline -10`

Identify: modified/staged/untracked files, semantic intent of each change, history patterns, commit language.

- `git diff --cached` is the basis for all commit decisions
- `git diff HEAD` provides the full overview
- `git status` gives file-level context
- `git log` provides convention and language

### 2. Strategize

**Core principle:** one commit = one semantic change.

Before staging or committing, answer these diagnostic questions:
1. Does the diff change observable behavior or only internal structure?
2. Does it introduce a new capability, correct existing behavior, or reorganize code?
3. Does it change public contracts, interfaces, validation, return values, or error handling?
4. Are tests documenting the same change, or are they independent?

These answers determine: commit type, grouping boundaries, and whether to ask the user.

**Grouping criteria:**
- One behavioral intent, one coherent reason to exist
- No unrelated changes staged together
- Refactoring separated from behavioral changes

**Whole-file staging:** If a file contains mixed concerns that can't be separated at the file level, commit it under the dominant change type. Do not attempt to split within a file.

**Anti-grouping:** Changes touching different concerns must be separate commits, even if each is one line. Size never justifies grouping unrelated changes.

**Do not use file count as a heuristic.** A valid commit may touch many files if they share one semantic purpose.

### 3. Stage and Commit

For each planned commit, run each step as a **separate Bash call** (not chained):

1. `git add file1 file2`
2. `git commit -m "type: description"`
3. `git log --oneline -1`

If the commit fails (hook rejection), read stderr, fix the message, and retry step 2.

For multiple commits, repeat the sequence with different file groups:

First commit:
1. `git add auth/service.go auth/service_test.go`
2. `git commit -m "feat: add token expiry validation"`

Second commit:
1. `git add payment/calculator.go`
2. `git commit -m "fix: fix interest rounding in payment calculator"`

Then verify all at the end: `git log --oneline -5`

### 4. Decisions

**Always use AskUserQuestion** for any interaction with the user — never ask via plain text output. This ensures the user gets structured prompts they can act on.

Ask only when the commit strategy can't be determined reliably from the diff.

**Ask when:**
- More than one valid strategy remains after semantic analysis
- Staged diff mixes unrelated changes and the split isn't obvious
- Commit type is ambiguous after inspecting the diff
- Same change could be behavioral or pure refactor

**Don't ask when:**
- Staged diff clearly maps to one semantic change
- File grouping is obvious
- Commit type is clear from behavioral effect
- The question would only seek trivial confirmation

### 5. Report

Run as separate, parallel Bash calls:

- `git log --oneline -5`
- `git status`

Report: commits created (type + description + files), final status, and any blocked commits with reasons.

## Amend Mode

When the user explicitly requests amending (e.g., "amend", "add this to the last commit", "forgot a file"):

1. Stage the additional changes
2. Determine the message:
   - If user provides a new message, use it
   - Otherwise, reuse existing: `git log -1 --format=%s`
3. Execute: `git commit --amend -m "<message>"`
4. Verify: `git log --oneline -1`

**Rules:**
- Only amend when user explicitly requests it — never amend automatically
- Only amend the most recent commit (never interactive rebase)
- If last commit has been pushed, warn that amending requires force-push

## Special Cases

- **Clean working directory:** Report and stop. Do not attempt any commits.
- **No staged content:** Determine intent from working tree, stage, then commit.

## Quick Example

**Working tree:**
```
auth/service.go      — adds token expiry validation
auth/service_test.go — tests the new expiry check
payment/calculator.go — fixes rounding in interest calc
README.md            — updates installation steps
```

**Strategy:**
```
Commit 1: feat: add token expiry validation
  → git add auth/service.go auth/service_test.go

Commit 2: fix: fix interest rounding in payment calculator
  → git add payment/calculator.go

Commit 3: docs: update installation instructions
  → git add README.md
```
