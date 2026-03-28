# Git Hooks: commit-msg Validator + Hook Possibilities Proposal

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Create a native git `commit-msg` hook that enforces the same validation rules as `validate-commit.py`, integrate it into the `commit-setup` flow with user choice, and propose creative uses of git hooks for the plugin.

**Architecture:** The `commit-msg` hook is a pure bash script placed in `.git/hooks/commit-msg`. It reads the commit message file, applies the same regex and character validation as `validate-commit.py`, and rejects non-conforming messages. The `commit-setup` command gains a new mode that lets the user choose between the Python validator (agent-side), the git hook (git-side), or both. The hook reads `.claude/git.local.md` frontmatter for project-specific settings (extra_types, allow_body, max_length).

**Tech Stack:** Bash, git hooks, YAML frontmatter parsing (sed/grep), regex validation

---

## Part 1: commit-msg Hook Implementation

### Task 1: Create the commit-msg hook script

**Files:**
- Create: `plugins/claude/git/hooks/commit-msg`

This script replicates the full logic of `scripts/validate-commit.py` in pure bash. It reads the commit message from `$1` (the temp file git passes to commit-msg hooks), validates format, type, description start character, and allowed characters.

It also reads `.claude/git.local.md` if present to pick up `extra_types`, `allow_body`, and `max_length` settings.

- [ ] **Step 1: Write the commit-msg hook script**

```bash
#!/bin/bash
set -euo pipefail

# commit-msg hook — validates commit message format.
# Mirrors the rules in validate-commit.py:
#   Format: type: description
#   - Single line (unless allow_body is true)
#   - No scope (parentheses forbidden)
#   - Valid types: feat|fix|docs|style|refactor|test|chore|perf (+ extra_types)
#   - Description starts with lowercase letter or digit
#   - Allowed chars: Unicode letters, digits, spaces, and , . / + -
#   - Breaking change marker (!) allowed after type

COMMIT_MSG_FILE="$1"

if [[ ! -f "$COMMIT_MSG_FILE" ]]; then
  echo "error: commit message file not found: $COMMIT_MSG_FILE" >&2
  exit 1
fi

# Read the commit message, stripping comment lines (lines starting with #)
message=$(sed '/^#/d' "$COMMIT_MSG_FILE")

if [[ -z "$message" ]]; then
  echo "error: commit message is empty" >&2
  exit 1
fi

# --- Read project settings from .claude/git.local.md ---
EXTRA_TYPES=""
ALLOW_BODY="false"
MAX_LENGTH=""

# Find the repo root
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
SETTINGS_FILE="$REPO_ROOT/.claude/git.local.md"

if [[ -f "$SETTINGS_FILE" ]]; then
  # Extract YAML frontmatter (between --- delimiters)
  frontmatter=$(sed -n '/^---$/,/^---$/p' "$SETTINGS_FILE" | sed '1d;$d')

  # Parse extra_types (collect indented lines after extra_types:)
  if echo "$frontmatter" | grep -q '^extra_types:'; then
    EXTRA_TYPES=$(echo "$frontmatter" | sed -n '/^extra_types:/,/^[^ #]/{/^  /p}' | sed 's/^\s*//' | cut -d: -f1 | tr '\n' '|' | sed 's/|$//')
  fi

  # Parse allow_body
  allow_body_val=$(echo "$frontmatter" | grep -E '^\s*allow_body:\s*' | head -1 | sed 's/.*:\s*//' | tr -d ' ')
  if [[ "$allow_body_val" == "true" ]]; then
    ALLOW_BODY="true"
  fi

  # Parse max_length
  max_length_val=$(echo "$frontmatter" | grep -E '^\s*max_length:\s*' | head -1 | sed 's/.*:\s*//' | tr -d ' ')
  if [[ -n "$max_length_val" ]] && [[ "$max_length_val" =~ ^[0-9]+$ ]]; then
    MAX_LENGTH="$max_length_val"
  fi
fi

# --- Build the valid types pattern ---
DEFAULT_TYPES="feat|fix|docs|style|refactor|test|chore|perf"
if [[ -n "$EXTRA_TYPES" ]]; then
  ALL_TYPES="$DEFAULT_TYPES|$EXTRA_TYPES"
else
  ALL_TYPES="$DEFAULT_TYPES"
fi

# --- Extract subject line ---
subject=$(echo "$message" | head -1)

# Check for body when not allowed
line_count=$(echo "$message" | wc -l)
if [[ "$ALLOW_BODY" == "false" ]] && [[ "$line_count" -gt 1 ]]; then
  echo "error: commit message must be a single line (no body or footer)" >&2
  echo "  received: $subject" >&2
  exit 1
fi

# --- Validate format: type(!?): description ---
if ! echo "$subject" | grep -qE "^($ALL_TYPES)!?: .+$"; then
  echo "error: commit message does not match the required format" >&2
  echo "  received: $subject" >&2
  echo "  expected: type: description" >&2
  echo "  valid types: $(echo "$ALL_TYPES" | tr '|' ', ')" >&2
  echo "  description must start with a lowercase letter or digit" >&2
  exit 1
fi

# --- Extract description (everything after "type(!?): ") ---
description=$(echo "$subject" | sed -E "s/^($ALL_TYPES)!?: //")

# --- Check max_length ---
if [[ -n "$MAX_LENGTH" ]]; then
  desc_len=${#description}
  if [[ "$desc_len" -gt "$MAX_LENGTH" ]]; then
    echo "error: description exceeds maximum length ($desc_len > $MAX_LENGTH)" >&2
    echo "  received: $subject" >&2
    exit 1
  fi
fi

# --- Check description starts with lowercase letter or digit ---
first_char="${description:0:1}"
if ! echo "$first_char" | grep -qE '^[a-z0-9]$'; then
  echo "error: description must start with a lowercase letter or digit" >&2
  echo "  received: $subject" >&2
  exit 1
fi

# --- Check allowed characters in description ---
# Allowed: Unicode letters, digits, spaces, and , . / + -
# Use a negative match: find any character that is NOT allowed
# Note: bash regex handles ASCII; for full Unicode support we use grep -P
if echo "$description" | grep -qP '[^\p{L}\p{N} ,./+\-]'; then
  # Find the offending character for a helpful error message
  bad_char=$(echo "$description" | grep -oP '[^\p{L}\p{N} ,./+\-]' | head -1)
  echo "error: description contains disallowed character: '$bad_char'" >&2
  echo "  received: $subject" >&2
  echo "  allowed: Unicode letters, digits, spaces, and , . / + -" >&2
  exit 1
fi

# --- Validate body format if present ---
if [[ "$ALLOW_BODY" == "true" ]] && [[ "$line_count" -gt 1 ]]; then
  second_line=$(echo "$message" | sed -n '2p')
  if [[ -n "$second_line" ]]; then
    echo "error: body must be separated from subject by a blank line" >&2
    echo "  received first body line: $second_line" >&2
    exit 1
  fi
fi

# All checks passed
exit 0
```

- [ ] **Step 2: Make the script executable**

Run: `chmod +x plugins/claude/git/hooks/commit-msg`

- [ ] **Step 3: Test the hook manually against valid messages**

Run:
```bash
# Create a temp file with a valid message
echo "feat: add user authentication" > /tmp/test-commit-msg
bash plugins/claude/git/hooks/commit-msg /tmp/test-commit-msg
echo "Exit code: $?"
```
Expected: Exit code 0 (no output)

Run:
```bash
echo "fix: fix token refresh logic" > /tmp/test-commit-msg
bash plugins/claude/git/hooks/commit-msg /tmp/test-commit-msg
echo "Exit code: $?"
```
Expected: Exit code 0

Run:
```bash
echo "feat!: remove legacy API endpoint" > /tmp/test-commit-msg
bash plugins/claude/git/hooks/commit-msg /tmp/test-commit-msg
echo "Exit code: $?"
```
Expected: Exit code 0 (breaking change marker)

- [ ] **Step 4: Test the hook against invalid messages**

Run:
```bash
echo "Add user authentication" > /tmp/test-commit-msg
bash plugins/claude/git/hooks/commit-msg /tmp/test-commit-msg 2>&1
echo "Exit code: $?"
```
Expected: Exit code 1, error about format

Run:
```bash
echo "feat: Add user authentication" > /tmp/test-commit-msg
bash plugins/claude/git/hooks/commit-msg /tmp/test-commit-msg 2>&1
echo "Exit code: $?"
```
Expected: Exit code 1, error about lowercase start

Run:
```bash
echo "feat: add user (authentication)" > /tmp/test-commit-msg
bash plugins/claude/git/hooks/commit-msg /tmp/test-commit-msg 2>&1
echo "Exit code: $?"
```
Expected: Exit code 1, error about disallowed character `(`

Run:
```bash
printf "feat: add auth\nsome body without blank line" > /tmp/test-commit-msg
bash plugins/claude/git/hooks/commit-msg /tmp/test-commit-msg 2>&1
echo "Exit code: $?"
```
Expected: Exit code 1, error about single line

- [ ] **Step 5: Test with project settings (extra_types)**

Run:
```bash
# Create a temporary settings file
mkdir -p /tmp/test-repo/.claude
cat > /tmp/test-repo/.claude/git.local.md << 'SETTINGS'
---
extra_types:
  build: build system
  ci: continuous integration
allow_body: true
max_length: 50
---
SETTINGS

# Override REPO_ROOT for testing
echo "build: update webpack config" > /tmp/test-commit-msg
cd /tmp/test-repo && git init && bash /home/leonardo/Projetos/pragmarketplace/plugins/claude/git/hooks/commit-msg /tmp/test-commit-msg 2>&1
echo "Exit code: $?"
```
Expected: Exit code 0 (build is an extra type)

- [ ] **Step 6: Commit the hook**

```bash
git add plugins/claude/git/hooks/commit-msg
```

Commit message: `feat: add native commit-msg git hook for message validation`

---

### Task 2: Update commit-setup to offer validation strategy choice

**Files:**
- Modify: `plugins/claude/git/commands/commit-setup.md`

The commit-setup command currently only handles Claude Code permission rules. It needs a new step that asks the user which validation strategy they want: Python script (agent-side only), git hook (native git enforcement), or both.

- [ ] **Step 1: Read the current commit-setup.md**

File: `plugins/claude/git/commands/commit-setup.md`

- [ ] **Step 2: Add the validation strategy section**

After the existing `## Execution` section, before `### Important`, add a new workflow step. The updated `commit-setup.md` should have its execution flow modified to:

1. First, handle permission rules (existing behavior)
2. Then, ask the user about validation strategy using AskUserQuestion

Replace the `## Execution` section with:

```markdown
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

Use AskUserQuestion to ask which validation approach the user wants:

1. **Python script only** — No git hook installed. The agent validates via `validate-commit.py` before each commit. (This is the current behavior.)
2. **Git hook (recommended)** — Install `commit-msg` hook to `.git/hooks/commit-msg`. Every commit is validated by git itself, regardless of whether it comes from Claude Code, the terminal, or an IDE.
3. **Both** — Install the git hook AND keep the agent-side validation. Belt and suspenders.
4. **Skip** — Don't change the validation setup.

Based on the user's choice:

- **Python script only**: Do nothing extra. Report that the agent will validate via the script.
- **Git hook** or **Both**: Copy `${CLAUDE_PLUGIN_ROOT}/hooks/commit-msg` to `.git/hooks/commit-msg` and make it executable. If a `commit-msg` hook already exists, warn the user and ask whether to overwrite or skip.
- **Both**: Also ensure the agent-side validation remains in the workflow (no changes needed — it's the default).

Report what was installed.
```

- [ ] **Step 3: Verify the updated command reads correctly**

Read the full file and confirm the flow makes sense.

- [ ] **Step 4: Commit the changes**

```bash
git add plugins/claude/git/commands/commit-setup.md
```

Commit message: `feat: add validation strategy choice to commit-setup`

---

### Task 3: Update the commit-maker agent to respect hook-only mode

**Files:**
- Modify: `plugins/claude/git/agents/commit-maker.md`

When the git hook is installed, the agent doesn't strictly need to call `validate-commit.py` before each commit — the hook will reject bad messages. However, running the validator first gives the agent early feedback (so it can fix the message without a failed `git commit`). In "both" mode, the agent validates first; in "hook-only" mode, it can skip the explicit validation call.

- [ ] **Step 1: Add a note to the Mandatory validation section**

In the `### Mandatory validation` section, after the existing rules, add:

```markdown
**When a commit-msg git hook is installed:**

If `.git/hooks/commit-msg` exists and is executable, the hook enforces the same rules at the git level. In this case, running the validator script before `git commit` is still recommended (it gives you early feedback and avoids a failed commit attempt), but not strictly required — the hook is the safety net. If the validator is unavailable (e.g., plugin root not resolved), you can rely on the hook and proceed directly with `git commit`.
```

- [ ] **Step 2: Commit the changes**

```bash
git add plugins/claude/git/agents/commit-maker.md
```

Commit message: `docs: document commit-msg hook fallback in agent`

---

### Task 4: Update the examples and README

**Files:**
- Modify: `plugins/claude/git/README.md`
- Modify: `plugins/claude/git/examples/git.local.md`

- [ ] **Step 1: Add git hooks section to README.md**

After the `## Safety Hooks` section, add:

```markdown
## Git Hooks (Native Validation)

The plugin includes a `commit-msg` git hook that validates commit messages at the git level — not just when using Claude Code, but from any git client (terminal, IDE, CI).

**Installation:**

```bash
/commit-setup --apply
```

Choose "Git hook" or "Both" when prompted. This copies the hook to `.git/hooks/commit-msg`.

**Manual installation:**

```bash
cp plugins/claude/git/hooks/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

The hook reads `.claude/git.local.md` for project-specific settings (extra_types, allow_body, max_length).
```

- [ ] **Step 2: Update the examples/git.local.md recommended rules section**

Add a note about the git hook option after the existing permission rules section:

```markdown
## Native Git Hook

For validation that works outside of Claude Code (terminal, IDE, CI), install the
commit-msg git hook via `/commit-setup --apply` and choose "Git hook" or "Both".
```

- [ ] **Step 3: Commit the changes**

```bash
git add plugins/claude/git/README.md plugins/claude/git/examples/git.local.md
```

Commit message: `docs: add git hooks documentation to README and examples`

---

## Part 2: Git Hook Possibilities Proposal

### What native git hooks can do for this plugin

Git hooks are scripts that run at specific points in the git workflow. They execute locally, require no network, and have full access to the repository. Here's what the git plugin could leverage beyond commit-msg validation:

---

#### 1. `prepare-commit-msg` — Smart message drafting

**What it does:** Runs before the commit message editor opens. Receives the message file, the source of the commit (message, template, merge, squash, commit), and the commit SHA (for amend).

**Proposal:** Pre-populate the commit message with a conventional-commits-formatted draft based on staged changes. The hook would:
- Read `git diff --cached --stat` to identify changed files
- Detect the likely commit type from file paths and diff content (e.g., files in `tests/` suggest `test:`, `README.md` suggests `docs:`)
- Write a draft subject line to the message file
- The user or agent can then refine it

**Value:** When committing from the terminal or IDE (outside Claude Code), the user gets a starting point instead of a blank message. Reduces friction for maintaining commit conventions.

**Complexity:** Medium. Heuristic-based type detection is imperfect but useful as a starting point.

---

#### 2. `pre-commit` — Staged content guardian

**What it does:** Runs before `git commit` is executed (before the message is even written). Exit non-zero to abort the commit.

**Proposal:** Enforce repository-specific rules on what can be committed:
- **Secret detection**: Reject staged files containing patterns like `ANTHROPIC_API_KEY=`, `AWS_SECRET_ACCESS_KEY`, private keys, `.env` files with real values
- **Large file guard**: Reject files over a configurable size threshold (e.g., 1MB) to prevent accidental binary commits
- **No-commit markers**: Reject files containing `// DO NOT COMMIT`, `# FIXME: remove before merge`, or similar markers that developers use as reminders
- **File type blocklist**: Reject `.pyc`, `.DS_Store`, `.env`, or other files that shouldn't be in the repository

**Value:** Catches mistakes that no amount of message validation can prevent. Secrets in git history are notoriously hard to remove. This is a safety net that protects every commit path — Claude Code, terminal, IDE.

**Complexity:** Low to medium. Pattern matching on staged content is straightforward. The configurable part (thresholds, patterns, blocklist) can read from `.claude/git.local.md`.

---

#### 3. `post-commit` — Automatic tagging advisor

**What it does:** Runs after a successful commit. Cannot abort the commit (it already happened). Has access to the new commit.

**Proposal:** After each commit, check if the accumulated changes since the last tag warrant a version bump. The hook would:
- Count commits since last tag
- Classify commit types (feat, fix, etc.)
- If a threshold is reached (e.g., 5+ commits, or any `feat` commit), write a suggestion to a `.claude/tag-suggestion` file
- The commit-maker agent or `/tag-it` can then read this file and proactively suggest tagging

**Value:** Creates a passive "you should probably tag soon" signal without interrupting the workflow. The tag suggestion accumulates context across commits so the eventual tag decision is informed by the full changelog.

**Complexity:** Low. It's purely informational — writes a file, doesn't block anything.

---

#### 4. `pre-push` — Release gate

**What it does:** Runs before `git push` sends data to the remote. Receives the remote name and URL. Can abort the push.

**Proposal:**
- **Branch protection**: Warn or block direct pushes to `main`/`master` without a PR
- **Tag validation**: If pushing tags, verify the tag message exists and follows the expected format
- **Changelog check**: If pushing a tag, verify that a changelog entry exists for the version

**Value:** Prevents "oops" pushes that bypass team workflow. Especially useful when the git plugin is used in a team setting.

**Complexity:** Low. Simple branch name and tag checks.

---

#### 5. `pre-rebase` — History safety

**What it does:** Runs before `git rebase` starts. Can abort the rebase.

**Proposal:**
- Warn when rebasing branches that have been pushed to a remote
- Block rebase of `main`/`master`
- Show a count of commits that will be rebased for awareness

**Value:** Prevents accidental history rewrites that create force-push situations.

**Complexity:** Low.

---

#### 6. `post-merge` / `post-checkout` — Environment sync

**What it does:** Runs after merge completes or after switching branches.

**Proposal:**
- Detect if `package.json`, `go.mod`, `requirements.txt`, or `Cargo.toml` changed and remind the user to update dependencies
- Detect if migration files changed and remind the user to run migrations
- Detect if `.claude/git.local.md` changed and note that Claude Code settings may need a restart

**Value:** Reduces "it works on my machine" issues by catching dependency drift at the moment it happens.

**Complexity:** Low. Diff comparison between old and new HEAD.

---

### Top 3 Implementation Plans

Based on value/complexity ratio, the top 3 to implement are:

1. **pre-commit (Staged content guardian)** — highest safety value, prevents irreversible mistakes
2. **prepare-commit-msg (Smart message drafting)** — best developer experience improvement
3. **post-commit (Automatic tagging advisor)** — complements the existing tag-it workflow

---

### Task 5: Implement pre-commit hook (Staged content guardian)

**Files:**
- Create: `plugins/claude/git/hooks/pre-commit`

- [ ] **Step 1: Write the pre-commit hook**

```bash
#!/bin/bash
set -euo pipefail

# pre-commit hook — catches dangerous content before it enters history.
# Checks: secrets, large files, no-commit markers, blocklisted file types.

# --- Configuration ---
MAX_FILE_SIZE_KB=1024  # 1MB default

# Read project settings for overrides
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
SETTINGS_FILE="$REPO_ROOT/.claude/git.local.md"

if [[ -f "$SETTINGS_FILE" ]]; then
  frontmatter=$(sed -n '/^---$/,/^---$/p' "$SETTINGS_FILE" | sed '1d;$d')
  size_val=$(echo "$frontmatter" | grep -E '^\s*max_file_size_kb:\s*' | head -1 | sed 's/.*:\s*//' | tr -d ' ')
  if [[ -n "$size_val" ]] && [[ "$size_val" =~ ^[0-9]+$ ]]; then
    MAX_FILE_SIZE_KB="$size_val"
  fi
fi

errors=()

# --- Get staged files ---
staged_files=$(git diff --cached --name-only --diff-filter=ACM)

if [[ -z "$staged_files" ]]; then
  exit 0
fi

# --- Check 1: Blocklisted file types ---
blocklist_pattern='\.(pyc|pyo|DS_Store|swp|swo)$|^\.env$|^\.env\.'
while IFS= read -r file; do
  if echo "$file" | grep -qE "$blocklist_pattern"; then
    errors+=("blocklisted file type: $file")
  fi
done <<< "$staged_files"

# --- Check 2: Large files ---
while IFS= read -r file; do
  if [[ -f "$file" ]]; then
    file_size_kb=$(( $(wc -c < "$file") / 1024 ))
    if [[ "$file_size_kb" -gt "$MAX_FILE_SIZE_KB" ]]; then
      errors+=("file too large (${file_size_kb}KB > ${MAX_FILE_SIZE_KB}KB): $file")
    fi
  fi
done <<< "$staged_files"

# --- Check 3: Secret patterns ---
secret_patterns=(
  'ANTHROPIC_API_KEY\s*='
  'OPENAI_API_KEY\s*='
  'AWS_SECRET_ACCESS_KEY\s*='
  'AWS_ACCESS_KEY_ID\s*='
  'PRIVATE_KEY\s*='
  '-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----'
  'ghp_[a-zA-Z0-9]{36}'
  'sk-[a-zA-Z0-9]{48}'
  'password\s*=\s*["\x27][^"\x27]{8,}'
)

combined_pattern=$(printf '%s|' "${secret_patterns[@]}")
combined_pattern="${combined_pattern%|}"  # Remove trailing |

while IFS= read -r file; do
  # Only check text files
  if [[ -f "$file" ]] && file "$file" | grep -q text; then
    if git diff --cached -- "$file" | grep -qEi "$combined_pattern"; then
      errors+=("possible secret detected in staged changes: $file")
    fi
  fi
done <<< "$staged_files"

# --- Check 4: No-commit markers ---
marker_pattern='DO NOT COMMIT|FIXME: remove before merge|XXX: temporary|HACK: remove'
while IFS= read -r file; do
  if [[ -f "$file" ]] && file "$file" | grep -q text; then
    if git diff --cached -- "$file" | grep -qEi "$marker_pattern"; then
      errors+=("no-commit marker found in staged changes: $file")
    fi
  fi
done <<< "$staged_files"

# --- Report ---
if [[ ${#errors[@]} -gt 0 ]]; then
  echo "error: pre-commit checks failed:" >&2
  for err in "${errors[@]}"; do
    echo "  - $err" >&2
  done
  echo "" >&2
  echo "To bypass (if you know what you're doing): git commit --no-verify" >&2
  exit 1
fi

exit 0
```

- [ ] **Step 2: Make the script executable**

Run: `chmod +x plugins/claude/git/hooks/pre-commit`

- [ ] **Step 3: Test against a clean staged set**

Run:
```bash
cd /home/leonardo/Projetos/pragmarketplace
bash plugins/claude/git/hooks/pre-commit
echo "Exit code: $?"
```
Expected: Exit code 0 (nothing staged, early return)

- [ ] **Step 4: Commit**

```bash
git add plugins/claude/git/hooks/pre-commit
```

Commit message: `feat: add pre-commit hook for secret detection and file guards`

---

### Task 6: Implement prepare-commit-msg hook (Smart message drafting)

**Files:**
- Create: `plugins/claude/git/hooks/prepare-commit-msg`

- [ ] **Step 1: Write the prepare-commit-msg hook**

```bash
#!/bin/bash
set -euo pipefail

# prepare-commit-msg hook — drafts a conventional commit message from staged changes.
# Only activates for new commits (not amend, merge, squash).
# Writes a draft subject line based on file path heuristics.

COMMIT_MSG_FILE="$1"
COMMIT_SOURCE="${2:-}"

# Only draft for new commits (no source means user ran "git commit")
# Skip for amend, merge, squash, commit -m (message source)
if [[ -n "$COMMIT_SOURCE" ]]; then
  exit 0
fi

# --- Analyze staged changes ---
staged_stat=$(git diff --cached --stat --name-only)

if [[ -z "$staged_stat" ]]; then
  exit 0
fi

# Count files by category
docs_count=0
test_count=0
config_count=0
style_count=0
total_count=0

while IFS= read -r file; do
  total_count=$((total_count + 1))

  case "$file" in
    README*|docs/*|*.md|CHANGELOG*|LICENSE*)
      docs_count=$((docs_count + 1)) ;;
    *test*|*spec*|*_test.*|*.test.*)
      test_count=$((test_count + 1)) ;;
    .eslintrc*|.prettierrc*|tsconfig*|*.config.*|.editorconfig|.gitignore)
      config_count=$((config_count + 1)) ;;
    *.css|*.scss|*.less)
      style_count=$((style_count + 1)) ;;
  esac
done <<< "$staged_stat"

# --- Determine commit type ---
commit_type="feat"

if [[ "$docs_count" -eq "$total_count" ]]; then
  commit_type="docs"
elif [[ "$test_count" -eq "$total_count" ]]; then
  commit_type="test"
elif [[ "$config_count" -eq "$total_count" ]]; then
  commit_type="chore"
elif [[ "$style_count" -eq "$total_count" ]]; then
  commit_type="style"
fi

# Check if diff looks like a fix (contains common fix patterns)
if git diff --cached | grep -qEi '(\bfix\b|bug|patch|correct|repair|resolve)'; then
  if [[ "$commit_type" == "feat" ]]; then
    commit_type="fix"
  fi
fi

# --- Build draft message ---
# Get the primary directory being changed
primary_dir=$(echo "$staged_stat" | head -1 | cut -d'/' -f1)

draft="${commit_type}: "

# Write the draft as a comment-style suggestion
# The actual message line is the draft, followed by helpful comments
{
  echo "$draft"
  echo ""
  echo "# --- Draft generated by git plugin ---"
  echo "# Type detected: $commit_type (based on staged files)"
  echo "# Files staged ($total_count):"
  echo "$staged_stat" | while IFS= read -r f; do echo "#   $f"; done
  echo "#"
  echo "# Edit the first line above. Lines starting with # are ignored."
  echo "# Format: type: description (lowercase, no parentheses)"
  echo "# Valid types: feat | fix | docs | style | refactor | test | chore | perf"
} > "$COMMIT_MSG_FILE"

exit 0
```

- [ ] **Step 2: Make the script executable**

Run: `chmod +x plugins/claude/git/hooks/prepare-commit-msg`

- [ ] **Step 3: Commit**

```bash
git add plugins/claude/git/hooks/prepare-commit-msg
```

Commit message: `feat: add prepare-commit-msg hook for smart message drafting`

---

### Task 7: Implement post-commit hook (Tagging advisor)

**Files:**
- Create: `plugins/claude/git/hooks/post-commit`

- [ ] **Step 1: Write the post-commit hook**

```bash
#!/bin/bash
set -euo pipefail

# post-commit hook — tracks commits since last tag and suggests when to tag.
# Writes a suggestion file to .claude/tag-suggestion when thresholds are met.
# This file can be read by the commit-maker agent or /tag-it command.

REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null || pwd)
SUGGESTION_FILE="$REPO_ROOT/.claude/tag-suggestion"

# --- Get last tag ---
last_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo "")

if [[ -z "$last_tag" ]]; then
  commits_since="all"
  commit_list=$(git log --oneline -20)
  commit_count=$(git rev-list --count HEAD 2>/dev/null || echo "0")
else
  commit_list=$(git log "${last_tag}..HEAD" --oneline)
  commit_count=$(echo "$commit_list" | grep -c '.' || echo "0")
fi

# --- Classify commits ---
feat_count=0
fix_count=0
breaking_count=0

while IFS= read -r line; do
  if echo "$line" | grep -qE '^[a-f0-9]+ feat!?:'; then
    feat_count=$((feat_count + 1))
  fi
  if echo "$line" | grep -qE '^[a-f0-9]+ fix:'; then
    fix_count=$((fix_count + 1))
  fi
  if echo "$line" | grep -qE '^[a-f0-9]+ [a-z]+!:'; then
    breaking_count=$((breaking_count + 1))
  fi
done <<< "$commit_list"

# --- Determine if we should suggest tagging ---
should_suggest=false
reason=""

if [[ "$breaking_count" -gt 0 ]]; then
  should_suggest=true
  reason="breaking change detected — major version bump recommended"
elif [[ "$feat_count" -ge 3 ]]; then
  should_suggest=true
  reason="$feat_count new features since last tag — minor version bump recommended"
elif [[ "$commit_count" -ge 10 ]]; then
  should_suggest=true
  reason="$commit_count commits since last tag — consider a release"
elif [[ "$commits_since" == "all" ]] && [[ "$commit_count" -ge 5 ]]; then
  should_suggest=true
  reason="no tags exist yet and $commit_count commits in history — consider creating v0.1.0"
fi

# --- Write or clean up suggestion file ---
if [[ "$should_suggest" == true ]]; then
  mkdir -p "$REPO_ROOT/.claude"
  cat > "$SUGGESTION_FILE" << SUGGESTION
---
generated: $(date -Iseconds)
last_tag: ${last_tag:-none}
commits_since: $commit_count
feats: $feat_count
fixes: $fix_count
breaking: $breaking_count
---
$reason

Run /tag-it to create a version tag.
SUGGESTION
else
  # Remove stale suggestion if thresholds no longer met (unlikely post-commit, but clean)
  rm -f "$SUGGESTION_FILE" 2>/dev/null || true
fi

exit 0
```

- [ ] **Step 2: Make the script executable**

Run: `chmod +x plugins/claude/git/hooks/post-commit`

- [ ] **Step 3: Commit**

```bash
git add plugins/claude/git/hooks/post-commit
```

Commit message: `feat: add post-commit hook for automatic tagging suggestions`

---

### Task 8: Update commit-setup to install all hooks

**Files:**
- Modify: `plugins/claude/git/commands/commit-setup.md`

The commit-setup command should now offer installation of all available hooks, not just commit-msg.

- [ ] **Step 1: Update the validation strategy AskUserQuestion**

Expand the options in the commit-setup command to include the additional hooks. After the validation strategy question, add a second question:

```markdown
**Step 3 — Additional git hooks (optional):**

Use AskUserQuestion to ask which additional hooks the user wants to install:

1. **pre-commit (secret & file guard)** — Blocks secrets, large files, no-commit markers, and blocklisted file types from being committed. Works everywhere, not just in Claude Code.
2. **prepare-commit-msg (smart drafting)** — Pre-populates commit messages with a conventional-commits draft based on staged files. Useful when committing from terminal or IDE.
3. **post-commit (tag advisor)** — Tracks commits since last tag and writes a suggestion file when it's time to create a release tag.
4. **All of the above**
5. **Skip** — Don't install additional hooks.

For each selected hook, copy from `${CLAUDE_PLUGIN_ROOT}/hooks/<hook-name>` to `.git/hooks/<hook-name>` and make executable. Warn if any hook already exists and ask whether to overwrite.
```

- [ ] **Step 2: Commit**

```bash
git add plugins/claude/git/commands/commit-setup.md
```

Commit message: `feat: add optional hook installation to commit-setup`

---

### Task 9: Add .claude/tag-suggestion to .gitignore awareness

**Files:**
- Modify: `plugins/claude/git/examples/git.local.md`

- [ ] **Step 1: Add .gitignore recommendation for tag-suggestion**

Add to the examples file:

```markdown
## Recommended .gitignore entries

```
.claude/*.local.md
.claude/tag-suggestion
```
```

- [ ] **Step 2: Commit**

```bash
git add plugins/claude/git/examples/git.local.md
```

Commit message: `docs: add tag-suggestion to recommended gitignore entries`

---

## Summary

| Task | What | Files |
|------|------|-------|
| 1 | commit-msg hook (validator in bash) | `hooks/commit-msg` |
| 2 | Update commit-setup with validation choice | `commands/commit-setup.md` |
| 3 | Agent fallback documentation | `agents/commit-maker.md` |
| 4 | README + examples docs | `README.md`, `examples/git.local.md` |
| 5 | pre-commit hook (secret/file guard) | `hooks/pre-commit` |
| 6 | prepare-commit-msg hook (smart draft) | `hooks/prepare-commit-msg` |
| 7 | post-commit hook (tag advisor) | `hooks/post-commit` |
| 8 | commit-setup installs all hooks | `commands/commit-setup.md` |
| 9 | gitignore for tag-suggestion | `examples/git.local.md` |
