# Git Plugin

Strategic commit tool with semantic analysis, whole-file staging, and hook-validated commits.

## Commit Format

```
type: description

optional body
```

- Subject on the first line — `type: description`
- Optional body separated from the subject by a single blank line
- No scope (parentheses forbidden)
- No signatures, no co-authored-by lines, no generation metadata
- Language follows the dominant language from repository commit history
- Validated by git hooks on every commit

Valid types: `feat` | `fix` | `docs` | `style` | `refactor` | `test` | `chore` | `perf`

## Architecture

```
/commit (skill) → git add + git commit
                   ↑
                 git hooks (commit-msg, pre-commit)
                   ↑
                 safety hook (PreToolUse)
```

1. User runs `/commit [context]` — the `commit` skill is invoked directly
2. Safety hook validates git commands (blocks `git add -p`, `git -C`, config changes)
3. Skill runs inline — analyzes, stages, commits
4. Git hooks validate messages and block dangerous content

## Features

- **Semantic analysis**: Groups changes by behavioral intent, not file count
- **Whole-file staging**: Simple `git add` — no hunk-level complexity
- **Hook-based validation**: Git hooks enforce commit format, block secrets, and guard against dangerous content
- **Inline workflow**: Runs directly in the main context — no sub-agent, no extra token cost
- **Intelligent partitioning**: Separates refactoring from behavioral changes at the file level
- **Pattern learning**: Adapts to the project's commit history and language
- **Minimal interactivity**: Asks only when the commit strategy is genuinely ambiguous
- **Amend mode**: Amend the last commit when explicitly requested
- **Safety hooks**: PreToolUse hook blocks dangerous git patterns

## Usage

```bash
# Let the workflow analyze and decide
/commit

# Provide context
/commit complete login feature

# Request splitting
/commit split by module

# Amend the last commit
/commit amend, I forgot to add the config file
```

## How It Works

The commit workflow runs inline (no sub-agent):

1. **Analyzes** the repository — `git status`, `git diff HEAD`, `git diff --cached`, `git log`
2. **Performs semantic diff analysis** — determines commit type and boundaries
3. **Plans partitioning** — groups files by semantic purpose
4. **Stages** — whole files via `git add`
5. **Commits** — git hooks validate the message; on failure, fixes and retries
6. **Reports** — commits created, final status, any blocks

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
- Allowed characters in the description: Unicode letters, digits, spaces, and `, . / + - : ' # >`
- No scope, no co-authored-by, no signatures, no generation metadata
- Body is optional; when present, separated from the subject by a single blank line
- Body rejects control and bidirectional Unicode characters (C0/C1 controls except tab/LF/CR, bidi formatting `U+202A`–`U+202E` / `U+2066`–`U+2069`, zero-width chars `U+200B`–`U+200F` / `U+2060`–`U+2064`, and the BOM `U+FEFF`) — Trojan Source / CVE-2021-42574 mitigation
- Breaking changes: use `!` after type (e.g., `feat!: remove legacy API`)

## Safety Hooks

The plugin includes a PreToolUse hook that blocks:
- `git add -p` / `--patch` — interactive, fails in headless environments
- `git -C` — causes path resolution issues
- `git config user.name/email` — intrusive identity modifications

## Git Hooks (Native Validation)

The plugin includes native git hooks that enforce commit conventions at the git level — not just when using Claude Code, but from any git client (terminal, IDE, CI).

**Available hooks:**
- `commit-msg` — validates commit message format
- `pre-commit` — blocks secrets, large files, no-commit markers, and blocklisted file types
- `prepare-commit-msg` — drafts a conventional commit message from staged files

**Installation:**

```bash
/commit-setup --apply
```

Choose your hooks when prompted.

**Manual installation:**

```bash
cp plugins/claude/git/hooks/commit-msg .git/hooks/commit-msg
chmod +x .git/hooks/commit-msg
```

## Important Rules

1. **Git config preserved** — never modifies `user.name` or `user.email`
2. **Hook-based validation** — git hooks validate every message on commit
3. **No git -C flag** — all commands run in current working directory
4. **Refactor/behavior separation** — pure refactoring and behavioral changes go in separate commits when separable at the file level
5. **Message accuracy** — the message must accurately describe the staged changes
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

### Amend last commit

```
/commit amend, forgot to include the migration file
```

Stages the migration file and amends the last commit.

### Automatic analysis

```
/commit
```

Determines the strategy autonomously, only asking when genuinely ambiguous.

## Installation

```bash
claude plugin add pragmabits/pragmarketplace --plugin git
```

Then run `/commit-setup --apply` to configure permission rules and install the git hooks.

## Version History

### v3.0.1 — April 2026
- `commit-msg` hook agora pula validação para commits gerados pelo git (merge, revert, squash, cherry-pick, `fixup!`/`squash!`/`amend!`) — paridade com `@commitlint/is-ignored defaultIgnores`
- Detecção primária via marker files (`MERGE_HEAD`, `SQUASH_MSG`, `CHERRY_PICK_HEAD`, `REVERT_HEAD`) e fallback textual por prefixo
- Resolve caso em que `git merge` / `git revert` falhavam por tentar validar a mensagem padrão do git contra o formato Conventional Commits

### v3.0.0 — April 2026
- Replaced sub-agent architecture with inline commit workflow
- Removed hunk-level staging — whole-file staging only via `git add`
- Removed Python script validation — git hooks are the sole validation mechanism
- Commit skill is now self-contained — no agent dispatch, no extra token cost
- Simplified permission rules (removed Python script/staging tool entries)
- Added `git reset HEAD` permission rule for unstaging
- Added hook installation check at workflow start
- Retired `validate-commit.py` and `git-staging.pyz` (to be removed separately)

### v2.3.1 — March 2026
- Added `validation_strategy` setting (`script` | `hook` | `both`) to `.claude/git.local.md`
- Commit-maker agent respects validation strategy — skips python validator when set to `hook`
- `/commit-setup --apply` persists the chosen validation strategy
- Fixed `post-commit` hook: empty commit list no longer miscounts as 1
- Added `jq` availability check to `validate-git-command.sh` safety hook
- Documented hook marker strings in `commit-setup` for reliable detection
- Added `python3` permission rule variants to `examples/git.local.md`

### v2.3.0 — March 2026
- Added native git hooks: `commit-msg` (message validation), `pre-commit` (secret/file guard), `prepare-commit-msg` (smart drafting), `post-commit` (tag advisor)
- Updated `commit-setup` with validation strategy choice and optional hook installation
- Added `python3` permission rule variants for validator and staging tool
- Agent now requires `AskUserQuestion` for all user-facing communication
- Agent documents `commit-msg` hook as fallback when validator unavailable

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
