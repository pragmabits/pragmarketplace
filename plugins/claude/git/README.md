# Git Plugin

Strategic commit tool powered by an intelligent agent for analysis and advanced validation.

# CRITICAL WARNING - READ FIRST

This plugin follows **ABSOLUTE and INVIOLABLE** rules for commit messages:

```
✅ CORRECT FORMAT:    type: description
❌ FORBIDDEN FORMAT:  type(scope): description
❌ FORBIDDEN FORMAT:  type: description\n\nadditional body
❌ FORBIDDEN FORMAT:  messages with signatures/metadata
```

**WHAT IS FORBIDDEN:**
- ❌ Claude Code signatures (`🤖 Generated with...`)
- ❌ Automatic Co-authored-by
- ❌ Scope in parentheses: `type(scope):`
- ❌ Body/multiple lines
- ❌ Messages in a language inconsistent with the repository history

**WHAT IS MANDATORY:**
- ✅ Format: `type: description`
- ✅ Single line only
- ✅ Dominant language from repository commit history
- ✅ Use configured git user
- ✅ Validation via script before every commit

**These rules exist to keep the history clean and professional.**

---

## Overview

The Git plugin provides a **specialized agent** (commit-maker) that automatically analyzes the repository, detects patterns, validates quality, and creates small, focused, strategic commits following Conventional Commits. The commit message language follows the dominant language established by the repository's existing commit history.

### Architecture

```
/commit (gateway) → commit-maker (all logic)
```

**How it works:**
1. User runs `/commit`
2. Command delegates to the commit-maker agent
3. Agent analyzes, plans, validates, and executes commits
4. User receives result

### Features

- **🤖 Intelligent Agent**: Deep analysis with commit-maker
- **⚡ Strategic Commits**: Groups changes logically into small, focused commits
- **🔪 Patch Mode**: Uses `git add -p` for surgical commits when needed
- **📝 Standardized Messages**: Follows Conventional Commits without scope (`type: description`)
- **✅ Mandatory Validation**: Runs `validate-commit.py` before every commit
- **🧠 Pattern Learning**: Adapts to the project's history
- **💬 Interactive**: Asks the user only when there are strategic decisions
- **🔒 Respects Configuration**: Uses the existing git user config, never modifies it

## Available Commands

### `/commit`

Creates strategic, focused commits with standardized messages.

**Usage:**
```
/commit [context or instruction]
```

**Examples:**
```bash
# Simple commit - let the agent analyze and decide
/commit

# Complete feature
/commit complete login feature

# Split by context/module
/commit split by module

# Use patch mode for granular changes
/commit use patch mode for independent changes
```

**What happens when you use `/commit`:**

1. **Command delegates** to the commit-maker agent automatically
2. **Agent analyzes** the repository (git status, diff, diff --cached, log)
3. **Agent performs semantic diff analysis** to determine type and commit boundaries
4. **Agent plans** partitioning strategy with explicit justification
5. **Agent validates** each message via `validate-commit.py` before committing
6. **Agent executes** commits only after successful validation
7. **Agent reports** final result (commits created, status, blocks)

**You don't need to know about the agent** - just use `/commit` normally!

## Project Conventions

### Message Format

**Required format:**
```
type: concise description
```

**Characteristics:**
- ✅ Single line only (no body, no footer)
- ✅ No scope in parentheses
- ✅ Dominant language from repository commit history
- ✅ Description starts with a lowercase letter or digit
- ✅ Allowed characters: Unicode letters, digits, spaces, and `, . / + -`
- ✅ Validated by `validate-commit.py` before every commit

**Valid types:**

| Type       | Description             | Example                                    |
| ---------- | ----------------------- | ------------------------------------------ |
| `feat`     | New feature             | `feat: add JWT authentication`             |
| `fix`      | Bug fix                 | `fix: fix CPF validation`                  |
| `docs`     | Documentation           | `docs: update installation instructions`   |
| `style`    | Formatting (no logic)   | `style: format code following standard`    |
| `refactor` | Refactoring             | `refactor: extract validation function`    |
| `test`     | Tests                   | `test: add payment tests`                  |
| `chore`    | Maintenance/deps        | `chore: update dependencies`               |
| `perf`     | Performance             | `perf: optimize database query`            |

**Valid examples:**
```
feat: add OAuth2 authentication system
fix: fix compound interest calculation
docs: update REST API documentation
refactor: extract validation to separate function
test: add unit tests for calculator
chore: update project dependencies
style: format code following Go standard
perf: add index on users table
```

**Invalid examples:**
```
❌ feat(auth): add OAuth2                    (no scope allowed)
❌ fix: fix bug                              (too vague)

    Bug details here                         (no body allowed)
❌ Add OAuth2 authentication                 (missing type, invalid format)
❌ feat: Add authentication                  (description must start lowercase)
```

### Commit Strategies

**Fundamental principle: One commit = one semantic change**

Commit boundaries are determined by **semantic cohesion**, not by file count. A valid commit may touch one file or many, as long as all staged changes belong to the same logical change.

✅ **Primary grouping criteria:**
- One behavioral intent
- One coherent reason to exist
- No unrelated changes staged together
- Pure refactoring separated from behavioral changes

❌ **Avoid:**
- Multiple unrelated features in one commit
- Mixing refactor and behavioral change in the same commit
- Using file count as a primary heuristic
- Vague messages like "updates" or "fixes"

**Supporting heuristics** (subordinate to semantic analysis):
- **Module/directory**: `auth/`, `payment/`, `user/` — may indicate separate changes
- **Change type**: feat, fix, docs, refactor — different types often indicate separate commits
- **Tests**: `*_test.go` — typically grouped with the implementation being tested

**Patch Mode (`git add -p`):**

The agent uses `git add -p` when:
- A file contains multiple independent changes
- A file mixes refactoring and behavioral change
- More than 3 distinct hunks may justify inspection

**Practical example:**

```bash
# File service.go has:
# - New cache function (feat)
# - Bug fix in error handling (fix)

# The agent executes:
git add -p service.go
# Selects only the fix hunks
MESSAGE="fix: fix error handling in service"
python "${CLAUDE_PLUGIN_ROOT}/scripts/validate-commit.py" "$MESSAGE"
git commit -m "$MESSAGE"

git add service.go  # Add the rest
MESSAGE="feat: add result caching in service"
python "${CLAUDE_PLUGIN_ROOT}/scripts/validate-commit.py" "$MESSAGE"
git commit -m "$MESSAGE"
```

## Git-Orchestrator Agent

The Git plugin includes a **specialized agent** that provides advanced intelligence for commits.

### What is an Agent?

An agent is an **autonomous subprocess** of Claude that:
- Has specialized tools (Bash, Grep, Read, AskUserQuestion, TodoWrite)
- Maintains context throughout execution
- Can make multiple chained decisions
- Is specialized in a specific domain (git workflows)

### Git-Orchestrator Capabilities

**Repository Analysis:**
- Runs git status, diff, diff --cached, log
- Identifies patterns from commit history
- Detects relationships between files
- Recognizes module structure (auth/, payment/, etc.)

**Semantic Diff Analysis:**
- Evaluates whether the diff changes observable behavior or only internal structure
- Identifies whether it introduces a new capability, corrects existing behavior, or reorganizes code
- Checks changes in public contracts, interfaces, validation, return values, and error handling
- Determines whether tests document the same change or are an independent changeset

**Intelligent Strategy:**
- Groups changes by semantic cohesion (not by file count)
- Automatically detects when to use `git add -p`
- Requires explicit partitioning justification for each commit
- Separates pure refactoring from behavioral changes

**Mandatory Validation:**
- Runs `validate-commit.py` before every `git commit`
- Aborts immediately if validation fails
- Does not retry with the same invalid message

**Hard Failures (aborts execution):**
- Nothing staged (`git diff --cached` empty, without prior preparation)
- Commit decision requires user input that has not been provided
- Independent semantic changes staged together without being split
- Commit message validation failure

**Tests for Sensitive Changes:**
- Inspects whether relevant tests exist for changes in validation, control flow, public contracts, persistence, authorization, money-related logic, error handling
- Includes related test updates in the same commit as the behavioral change
- Explicitly reports when tests are absent for sensitive changes

**Progress Tracking with TodoWrite:**
- For multiple commits, tracks progress using TodoWrite
- Tracks status of each planned commit (pending, in_progress, complete)

### When Does the Agent Ask?

The agent only asks when the commit decision cannot be reliably made from the staged diff:

✅ **Asks when:**
- More than one valid strategy remains after semantic diff analysis
- The staged diff mixes unrelated semantic changes and the split is not obvious
- Commit type is materially ambiguous after inspecting `git diff --cached`
- The same change could reasonably be classified as either behavioral change or pure refactor
- More than 10 files involved across multiple contexts with unclear semantic grouping

❌ **Does NOT ask when:**
- The staged diff clearly maps to one semantic change
- File grouping is obvious from the diff
- Commit type is clear from behavioral effect
- The question would only seek trivial confirmation

## Installation

This plugin is automatically loaded by Claude Code when present in the plugins directory.

**Expected location:**
- `~/.claude/plugins/git/` (global installation)
- `<project>/.claude/plugins/git/` (local installation)

## Important Rules

### 1. Git Configuration Preserved

The agent **always uses** the existing user configuration:

```bash
git config user.name    # Used as-is
git config user.email   # Used as-is
```

**Never modifies** git configuration.

### 2. Mandatory Validation via Script

Every commit message is validated by the `scripts/validate-commit.py` script before `git commit` execution. If validation fails, the commit is aborted immediately.

```bash
# The agent runs before every commit:
python "${CLAUDE_PLUGIN_ROOT}/scripts/validate-commit.py" "$MESSAGE"
# Only runs git commit if validation passes
git commit -m "$MESSAGE"
```

### 3. Simple and Direct Messages

Messages are **simple and direct**, without automatic signatures or additional metadata.

# ABSOLUTE RULES - ZERO TOLERANCE

**The plugin enforces extremely strict validations:**

#### ❌ FORBIDDEN (with consequences)

1. **Claude Code signatures**
   ```bash
   # NEVER DO THIS
   git commit -m "feat: new feature

   🤖 Generated with Claude Code
   Co-Authored-By: Claude"
   ```
   **Consequence:** Invalid commit, polluted history

2. **Scope usage**
   ```bash
   # NEVER DO THIS
   git commit -m "feat(auth): add login"
   ```
   **Consequence:** Format not accepted in this project

3. **Body/multiple lines**
   ```bash
   # NEVER DO THIS
   git commit -m "feat: new feature

   Detailed description here"
   ```
   **Consequence:** Violates single-line directive

4. **Messages in language inconsistent with history**
   ```bash
   # If history is in Portuguese, NEVER DO THIS
   git commit -m "feat: add new feature"
   ```
   **Consequence:** Language inconsistent with history

#### ✅ CORRECT FORMAT

```bash
# ALWAYS DO THIS
git commit -m "feat: add new feature"
git commit -m "fix: fix calculation bug"
git commit -m "docs: update API documentation"
```

**Characteristics:**
- Single line
- Format: `type: description`
- Dominant language from repository history
- No signatures or metadata
- No scope in parentheses
- Validated by `validate-commit.py`

### 4. Intelligent Interactivity

The agent asks the user only when necessary:

✅ **Asks when:**
- Multiple valid grouping strategies
- Ambiguous changes that can be interpreted in various ways
- Large files with many independent changes
- Uncertainty about commit type

❌ **Does not ask when:**
- There is a clearly superior strategy
- Changes are obvious and direct
- Trivial formatting decisions

## Usage Examples

### Scenario 1: Complete feature

**Situation:** Implemented JWT authentication with tests

**Command:**
```
/commit authentication feature
```

**Result:**
```
feat: add JWT authentication system with validation
```

**Files included:** `auth/jwt.go`, `auth/jwt_test.go`, `auth/middleware.go`

---

### Scenario 2: Multiple contexts

**Situation:** Changes in `auth/`, `payment/`, and `README.md`

**Command:**
```
/commit split by context
```

**Result:**
```
feat: add token validation in middleware
fix: fix fee calculation in payment
docs: update deployment instructions
```

---

### Scenario 3: Complex changes in one file

**Situation:** `service.go` has a new feature + a bug fix

**Command:**
```
/commit use patch mode
```

**Process:**
1. Agent detects multiple independent changes
2. Uses `git add -p service.go` to select hunks
3. First commit with the fix
4. Second commit with the feature

**Result:**
```
fix: fix error handling in service
feat: add result caching in service
```

---

### Scenario 4: Automatic analysis

**Situation:** Multiple files modified, let the agent decide

**Command:**
```
/commit
```

**Process:**
1. Agent analyzes git status, diff, diff --cached, and log
2. Performs semantic diff analysis to determine boundaries
3. Stages and commits separately by semantic cohesion (validating each message)
4. Reports final result

**Result:**
```
feat: add user listing endpoint
fix: fix email validation in registration
test: add tests for user controller
docs: update API documentation
```

## Troubleshooting

### Problem: Many unrelated changes

**Symptom:** Working directory with files across multiple modules

**Solution:** The agent will ask which grouping strategy to use (by semantic cohesion, by type, etc.)

---

### Problem: Unsure which commit type to use

**Symptom:** Doubt whether the change is `feat:` or `refactor:`

**Solution:** The agent will analyze the nature of the change via semantic diff analysis, and will ask using AskUserQuestion if ambiguous

---

### Problem: File with changes that should be in separate commits

**Symptom:** A file has a new feature and a bug fix

**Solution:** Use `/commit use patch mode` to select specific hunks

---

### Problem: Previous commits use a different format

**Symptom:** History has messages like `feat(auth): description`

**Solution:** The agent will follow the specified format (`type: description` without scope), validated by the `validate-commit.py` script

## Versioning

- **Current version:** 1.0.0
- **Versioning:** Semantic Versioning (MAJOR.MINOR.PATCH)

### Version History

#### v1.0.0 - December 2025
- **Initial release** with agent-based architecture
- commit-maker agent for commit analysis and execution
- `/commit` command as gateway delegating to the agent
- Advanced quality validations
- Project pattern learning
- Automatic patch mode detection
- Conventional Commits without scope, language follows repository history
- Strict format rules with zero tolerance for violations

## Contributing

To add new commands or improvements:

1. Follow command structure in `commands/*.md`
2. Update `plugin.json` if necessary
3. Document in README.md
4. Test locally
5. Commit: `feat: add command X` (following conventions)

## License

Property of Pragmabits.

## Contact

**Author:** Leonardo Leôncio
**Email:** leonardoleoncio96@gmail.com
**Company:** Pragmabits

---

**Version:** 1.0.0
**Updated:** December 2025
**Status:** Active
