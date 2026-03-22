# Git Plugin

Strategic commit tool powered by the commit-maker agent for semantic analysis, intelligent partitioning, and validated commits.

## Commit Format

```
type: description
```

- Single line only — no body, no footer, no signatures (configurable via settings)
- No scope (parentheses forbidden)
- Language follows the dominant language from repository commit history (overridable via settings)
- Validated by `scripts/validate-commit.py` before every commit

Valid types: `feat` | `fix` | `docs` | `style` | `refactor` | `test` | `chore` | `perf`

Additional types can be configured via project settings (see below).

## Architecture

```
/commit (command) → commit-maker (agent) → staging tool + validator
                                         ↑
                               safety hook (PreToolUse)
```

1. User runs `/commit [context]`
2. Safety hook validates git commands (blocks `git add -p`, `git -C`, config changes)
3. Command delegates to the commit-maker agent
4. Agent analyzes, plans, validates, and executes commits

## Features

- **Semantic analysis**: Groups changes by behavioral intent, not file count
- **Hunk-level staging**: Non-interactive `.pyz` tool (Dulwich-based) for surgical commits
- **Unstage support**: Reset staged files back to HEAD state
- **Mandatory validation**: `validate-commit.py` runs before every `git commit`
- **Intelligent partitioning**: Separates refactoring from behavioral changes
- **Pattern learning**: Adapts to the project's commit history and language
- **Minimal interactivity**: Asks only when the commit strategy is genuinely ambiguous
- **Amend mode**: Amend the last commit when explicitly requested
- **Safety hooks**: PreToolUse hook blocks dangerous git patterns
- **Project settings**: Per-project configuration via `.claude/git.local.md`
- **.gitignore awareness**: Parser respects .gitignore when scanning for untracked files

## Usage

```bash
# Let the agent analyze and decide
/commit

# Provide context
/commit complete login feature

# Request splitting
/commit split by module

# Request hunk-level staging
/commit use patch mode for independent changes

# Amend the last commit
/commit amend, I forgot to add the config file
```

## How It Works

The commit-maker agent:

1. **Analyzes** the repository — `git status`, `git diff HEAD`, `git diff --cached`, `git log`
2. **Reads settings** — checks `.claude/git.local.md` for project-specific configuration
3. **Performs semantic diff analysis** — determines commit type and boundaries
4. **Plans partitioning** — explicit justification for how changes are grouped
5. **Stages** — whole files via `git add`, specific hunks via the staging tool, or unstages via unstage mode
6. **Validates** — runs `validate-commit.py`; aborts on failure
7. **Commits** — only after validation passes (supports amend mode)
8. **Reports** — commits created, final status, any blocks

## Commit Convention

| Type       | Description           | Example                                  |
| ---------- | --------------------- | ---------------------------------------- |
| `feat`     | New feature           | `feat: add JWT authentication`           |
| `fix`      | Bug fix               | `fix: fix CPF validation`                |
| `docs`     | Documentation         | `docs: update installation instructions` |
| `style`    | Formatting (no logic) | `style: format code following standard`  |
| `refactor` | Refactoring           | `refactor: extract validation function`  |
| `test`     | Tests                 | `test: add payment tests`                |
| `chore`    | Maintenance/deps      | `chore: update dependencies`             |
| `perf`     | Performance           | `perf: optimize database query`          |

**Message rules:**
- Description starts with a lowercase letter or digit
- Allowed characters: Unicode letters, digits, spaces, and `, . / + -`
- No scope, no body, no co-authored-by, no signatures
- Breaking changes: use `!` after type (e.g., `feat!: remove legacy API`)

## Staging Tool

The staging tool (`tools/git-staging.pyz`) replaces `git add -p` for non-interactive environments.

**Parse** — read-only analysis:
```bash
python "tools/git-staging.pyz" parse --repo .
```

**Stage** — selective hunk staging:
```bash
python "tools/git-staging.pyz" stage --repo . --spec '{"file.py": [0, 2], "other.py": "all"}'
```

**Unstage** — reset files to HEAD state:
```bash
python "tools/git-staging.pyz" unstage --repo . --spec '{"file.py": "all"}'
```

**Commit** — stage + commit in one step:
```bash
python "tools/git-staging.pyz" commit --repo . --spec '{"file.py": [0]}' --message "fix: description"
```

Spec values: `"all"` (whole file), `[0, 2]` (hunk indices), `"delete"` (file deletion).

The commit mode does not validate messages — always run `validate-commit.py` first.

## Validator

```bash
# Basic validation
python scripts/validate-commit.py "feat: add login endpoint"

# With extra types
python scripts/validate-commit.py --extra-types build,ci,revert "build: update webpack config"

# With body support
python scripts/validate-commit.py --allow-body "feat: add auth

Implements JWT-based authentication with refresh tokens."

# With max length
python scripts/validate-commit.py --max-length 72 "feat: add login"
```

## Project Settings

Create `.claude/git.local.md` in your project root to customize behavior:

```markdown
---
extra_types:
  build: build system or external dependencies
  ci: continuous integration configuration
  revert: revert a previous commit
language: en
allow_body: false
max_length: 72
---
```

Available settings:
- **extra_types**: Additional commit types beyond the default 8
- **language**: Override commit message language (default: detected from git log)
- **allow_body**: Allow multi-line commit messages (default: `false`)
- **max_length**: Maximum description length in characters (default: no limit)

After editing, restart Claude Code for changes to take effect.

Add to `.gitignore`:
```
.claude/*.local.md
```

See `examples/git.local.md` for a complete template.

## Safety Hooks

The plugin includes a PreToolUse hook that blocks:
- `git add -p` / `--patch` — interactive, fails in headless environments
- `git -C` — causes path resolution issues with staging tool
- `git config user.name/email` — intrusive identity modifications

## Important Rules

1. **Git config preserved** — never modifies `user.name` or `user.email`
2. **Mandatory validation** — every message validated by script before commit
3. **No git -C flag** — all commands run in current working directory
4. **Refactor/behavior separation** — pure refactoring and behavioral changes go in separate commits when separable
5. **Message accuracy** — the message must accurately describe every hunk in `git diff --cached`
6. **Amend only on request** — never amends automatically

## Examples

### Multiple contexts

Changes in `auth/`, `payment/`, and `README.md`:

```
/commit split by context
```

Result:
```
feat: add token validation in middleware
fix: fix fee calculation in payment
docs: update deployment instructions
```

### Mixed changes in one file

`service.go` has a new feature + a bug fix:

```
/commit use patch mode
```

The agent parses hunks, stages them separately, and creates two commits.

### Amend last commit

```
/commit amend, forgot to include the migration file
```

The agent stages the migration file and amends the last commit.

### Automatic analysis

```
/commit
```

The agent determines the strategy autonomously, only asking when genuinely ambiguous.

## Installation

Place in plugins directory:
- `~/.claude/plugins/git/` (global)
- `<project>/.claude/plugins/git/` (local)

## Version History

### v2.0.0 — March 2026
- Extracted shared utilities (`repo_utils.py`) — eliminates code duplication
- Fixed timezone bug in committer (correct DST handling via `tm_gmtoff`)
- Fixed git index flags field (encodes path name length per spec)
- Added `.gitignore` awareness to parser (respects ignore patterns)
- Added `unstage` subcommand to staging tool
- Added project settings support (`.claude/git.local.md`)
- Added safety hook (blocks `git add -p`, `git -C`, config changes)
- Optimized parser for large repos (SHA-based fast path, separate tracked/untracked)
- Added amend mode support
- Extended validator: `--extra-types`, `--allow-body`, `--max-length`, breaking change `!`
- Expanded eval suite with negative and edge-case test scenarios
- Moved development workspace out of distribution (`dev/`)

### v1.2.0 — March 2026
- Added `commit` skill with evaluation test cases
- Improved agent prompt: leaner, less repetitive, explains reasoning
- Overhauled README for clarity and conciseness

### v1.1.0 — March 2026
- Non-interactive staging tool (`tools/git-staging.pyz`) via Dulwich
- Three staging modes: parse, stage, commit
- Racy-git protection for partial hunk staging

### v1.0.1 — March 2026
- Portable plugin root resolution via `CLAUDE_PLUGIN_ROOT`

### v1.0.0 — December 2025
- Initial release with agent-based architecture

## License

Property of Pragmabits.

## Contact

**Author:** Leonardo Leoncio
**Email:** leonardoleoncio96@gmail.com
**Company:** Pragmabits
