# Session Plugin

Session lifecycle helpers for Claude Code. Turns the current working session into a structured handoff report the next agent can resume from, and lets you list, search, and resume prior reports without manually browsing files.

## Overview

The `session` plugin ships two skills:

- **`/report`** — analyzes the current conversation, writes a structured markdown handoff report under `.claude/sessions/`, and commits the new file in a single isolated `chore:` commit. Optimized for the next session's agent: stable section anchors, fixed numbering, an explicit Session contract block (user goal + goal status), and typed pending items. Pass `--no-commit` to write without committing.
- **`/recall`** — read-only retrieval over the same `.claude/sessions/` directory. Five subcommands — `list`, `filter`, `grep`, `resume`, `last`.

Reports are saved to `<repo-root>/.claude/sessions/`. The directory is auto-created on first use; the location resolves via `$CLAUDE_PROJECT_DIR`, then `git rev-parse --show-toplevel`, falling back to the current directory.

## Prerequisites

- `git` (optional, but enables branch / commit / user metadata in the report header).
- `bash` — both skills' `!` blocks shell out to bash.

## Available Commands

### `/report`

Generate a handoff report for the current session.

**Usage:**
```
/report [--lang xx-YY] [--no-commit] [optional report title]
```

| Argument | Description |
|----------|-------------|
| `--lang xx` / `--lang xx-YY` | Force the report language (e.g. `--lang pt-BR`, `--lang en-US`). |
| `--no-commit` | Write the report file without committing it. |
| *(remaining text)* | Free-form hint for the report title. |

**Language default:** if `--lang` is not passed, the report is written in the language the user used during the session. If the session was mixed, the most frequent language wins. Technical terms stay in English regardless.

**Auto-commit.** After writing the file, the skill issues exactly one command — `git commit -m "chore: add session report <timestamp>" -- <absolute-report-path>` — committing only the report file. This is git's partial-commit mode, so any other staged or unstaged work in the worktree is left untouched. The subject is fixed-format, contains no body, no emojis, and no scope, so it composes cleanly with most Conventional-Commits hooks in consumer repos. If the commit fails (no git repo, hook rejection, merge in progress, identity not configured, etc.), the skill reports the failure verbatim and leaves the written report intact for you to handle manually. Pass `--no-commit` to skip the commit step entirely.

**Examples:**
```bash
# Default report — language auto-detected, then auto-committed
/report

# Force Portuguese (Brazil)
/report --lang pt-BR

# Force English with a title hint
/report --lang en-US auth middleware rewrite

# Write the report without committing it
/report --no-commit
```

### `/recall`

Retrieve and resume work from prior session reports. Read-only.

**Usage:**
```
/recall <list | filter <criteria> | grep <pattern> | resume [<session-id>] | last [<n>]>
```

`list`, `filter`, and `grep` accept `--limit N` (positive integer) to cap output. The pattern in `grep` is a literal string by default; prefix with `re:` for regex.

| Subcommand | Output |
|------------|--------|
| `list` | Markdown table of all sessions, newest first (Session ID / Title / Timestamp / Branch / Status). |
| `filter <criteria>` | Same format, filtered by AND'd `key:value` pairs: `user:`, `branch:`, `status:` (`achieved`, `partial`, `abandoned`, `redirected`), `since:YYYY-MM-DD`, `until:YYYY-MM-DD`. |
| `grep <pattern>` | List of files containing the pattern, with up to 3 matching lines per file plus the surrounding `## N.` heading. |
| `resume [<session-id>]` | Reads §6 Pending Items from the target session and asks via `AskUserQuestion` which item to pick up. Default target: most recent session. |
| `last [<n>]` | Prints the full body of the `<n>` most recent reports verbatim, newest first. Default `<n>` is 1. |

**Session ID conventions** for `resume`:
- **Full ID** — e.g. `alice-2026-05-08T143022`.
- **Timestamp only** — e.g. `2026-05-08T143022`.
- **Partial match** — any unambiguous prefix or substring; ambiguous matches print a candidate list and stop.

**Examples:**
```bash
# Latest 10 sessions
/recall list --limit 10

# Sessions on the current branch since the start of the month
/recall filter branch:main since:2026-05-01

# Find sessions that touched the auth middleware
/recall grep "auth middleware"

# Resume the most recent session
/recall resume

# Resume a specific session
/recall resume alice-2026-05-08T143022

# Read back the 3 most recent reports verbatim
/recall last 3
```

## Output Location

Reports are written to:

```
<repo-root>/.claude/sessions/<git-user>-<YYYY-MM-DDTHHMMSS>.md
```

- `<repo-root>` is resolved via `$CLAUDE_PROJECT_DIR`, then `git rev-parse --show-toplevel`, falling back to the current directory.
- `<git-user>` is taken from `git config user.name`, sanitized to lowercase `[a-z0-9._-]` (whitespace → `-`). If empty or `unknown`, `unknown-user` is used.
- `<YYYY-MM-DDTHHMMSS>` is the UTC timestamp at report render time. The trailing `Z` is **dropped from the filename** to keep `@`-completion working in the Claude Code CLI; the in-file header retains the `Z` for timezone clarity.

The directory is created automatically if it does not exist.

## Report Template

Every report starts with a header:

```markdown
# Session Report: <concise title>

**Timestamp (UTC):** <YYYY-MM-DDTHHMMSSZ>
**Git user:** <name>
**Branch:** `<branch>`
**Base commit:** `<short-sha> (<subject>)`
**Commits generated:** <count> (from `<first>` to `<last>`)
```

Followed by a **Session contract** block that records intent and outcome:

```markdown
**User goal (entering session):** <what the user wanted at the start>
**Goal status:** <achieved | partial | abandoned | redirected>
**If partial, abandoned, or redirected:** <what changed and why; otherwise: n/a>
```

Then six fixed-number sections. **Empty sections are not omitted** — they render as `none`. This guarantees stable anchors so a downstream agent can rely on `## 4. Decisions Made` always being at that position (the `/recall resume` flow depends on §6 always existing).

| § | Section | Content |
|---|---------|---------|
| 1 | Outcome summary | Counts table: goal status, decisions, files created/modified/deleted, in-progress / promised / known-issue counts. |
| 2 | Work Completed | Per-topic Problem / Solution / Files. |
| 3 | Issues and Bugs Found | Issue / Root Cause / Resolution / Files table. |
| 4 | Decisions Made | Decision / Choice / Rejected / Evidence / Rationale table. |
| 5 | Files Changed | Created / Modified / Deleted lists. |
| 6 | Pending Items | 6.1 In-progress (must resume), 6.2 Promised but not started, 6.3 Known issues / tech debt. |

Tone is factual and direct. Specific over vague. References use backticked paths (`src/foo/bar.py`), function names (`parse_config()`), and short commit hashes.

## How It Works

### `/report`
1. The skill is invoked as `/report [args]`.
2. Before the skill content reaches Claude, several `!` shell-exec blocks collect repo metadata: git user, current branch, latest commit, two UTC timestamps (with `Z` for the header, without `Z` for the filename), recent commits, `git diff --stat`, and `git status --short`.
3. Another `!` block invokes the shared `ensure-sessions-dir.sh` script via `${CLAUDE_PLUGIN_ROOT}` to resolve and create the output directory.
4. Claude analyzes the conversation, applies the fixed template, fills `none` for empty sections, and writes the report to the pre-resolved absolute path using the Write tool.
5. Unless `--no-commit` was passed, Claude invokes one Bash command — `git commit -m "chore: add session report <timestamp>" -- <absolute-report-path>` — committing only the report file. On non-zero exit, the failure is reported back verbatim and the file is left in place.

### `/recall`
1. The skill is invoked as `/recall <subcommand> [args]`.
2. A render-time `!`-block invokes the bundled dispatcher `${CLAUDE_SKILL_DIR}/scripts/recall.sh` with the user's `$ARGUMENTS` quoted as a single string. The script performs all directory walking, metadata extraction, sorting, filtering, and rendering, then prints to stdout.
3. The dispatcher's output is injected into the prompt:
   - For `list` / `filter` / `grep` / `last`: ready-to-print markdown that the model emits verbatim.
   - For `resume`: a JSON object describing the target session's §6 Pending Items.
4. For `resume`, the skill parses the JSON and issues an `AskUserQuestion` listing each pending item plus a final **None — just printing for reference** option, then stops. The user's selection becomes the input to the next turn. If the JSON has `"empty": true`, it prints `Session <id> has no pending items.` and stops without asking.
5. The dispatcher is split across two files: `scripts/recall.sh` (subcommand routing + per-command formatting) and `scripts/lib/sessions.sh` (sourced helpers: directory resolution, ISO 8601 sort, anchor extraction, ID resolution).

## Architecture

```
session/
├── .claude-plugin/
│   └── plugin.json
├── scripts/
│   └── ensure-sessions-dir.sh         # Shared between both skills via ${CLAUDE_PLUGIN_ROOT}
└── skills/
    ├── report/
    │   └── SKILL.md                   # Report generator with metadata !-exec blocks and the fixed template
    └── recall/
        ├── SKILL.md                   # Thin dispatcher that relays scripts/recall.sh output
        └── scripts/
            ├── recall.sh              # Subcommand router (list / filter / grep / resume / last)
            └── lib/
                └── sessions.sh        # Sourced helpers: directory, sort, extraction, ID resolution
```

The plugin-level `ensure-sessions-dir.sh` is referenced by both skills as `${CLAUDE_PLUGIN_ROOT}/scripts/ensure-sessions-dir.sh`, so there is exactly one copy of the directory-resolution logic. The recall-specific `scripts/` directory contains the dispatcher and library used only by `/recall`.

## Permissions

Both skills are pre-authorized via their `SKILL.md` `allowed-tools` frontmatter so end users get no permission prompt:

- `/report` — `Bash(bash:*) Bash(git:*) Bash(date:*) Bash(echo:*)` (metadata collection + script exec).
- `/recall` — `Bash(bash:*)` (single dispatcher invocation; the script handles all internal `ls`/`grep`/`awk`/`sort` calls).

## Version History

### v2.3.0 — May 2026
- `/report` now commits the generated report file by itself, in a single isolated commit, immediately after writing it. The command is `git commit -m "chore: add session report <timestamp>" -- <absolute-report-path>` — subject-only, no body, no emojis, no scope, and partial-commit mode so any other staged or unstaged work in the worktree is preserved untouched.
- Added a `--no-commit` flag to opt out of the auto-commit step. The report file is still written normally.
- Commit failures (no git repo, hook rejection, merge in progress, missing identity, etc.) are reported back to the user verbatim and the report file is left intact for manual handling.

### v2.1.1 — May 2026
- Fix `/recall` reporting `No sessions found in .claude/sessions/` inside the Claude Code harness when `CLAUDE_PLUGIN_ROOT` is not exported into the `!`-block subshell. `lib/sessions.sh` now derives the plugin root from `BASH_SOURCE` as a fallback, so the dispatcher can locate `ensure-sessions-dir.sh` regardless of how the harness propagates env vars. The previous failure mode silently masked an exit-127 from `bash /scripts/ensure-sessions-dir.sh` (literal slash) as an empty-result notice.
- Reorder `ensure-sessions-dir.sh` precedence to `git toplevel → CLAUDE_PROJECT_DIR → pwd`. Fixes the case where the harness sets `CLAUDE_PROJECT_DIR=$HOME` while the user is operating inside an unrelated git repo, which previously routed `/recall` and `/report` to `$HOME/.claude/sessions/` instead of the repo's `.claude/sessions/`. Worktrees and explicit non-git `CLAUDE_PROJECT_DIR` overrides still work as fallbacks.

### v2.1.0 — May 2026
- Added `last [<n>]` subcommand to `/recall` — prints the full body of the `<n>` most recent reports verbatim, newest first; `<n>` defaults to 1.
- Moved all directory walking, metadata extraction, sorting, filtering, and rendering for `/recall` into a bundled bash dispatcher (`scripts/recall.sh` + sourced `scripts/lib/sessions.sh`). The skill prompt now relays the script's output verbatim instead of having the model parse files inline — substantially fewer tokens per invocation.
- `/recall` `allowed-tools` tightened from ten Bash matchers to just `Bash(bash:*)`.
- Sort order for all `/recall` subcommands now keys on the ISO 8601 timestamp suffix in filenames, so the git-user prefix never dominates ordering.
- For `resume`, the script emits structured JSON; the skill parses it to build the `AskUserQuestion` options. JSON schema is documented inline in `recall/SKILL.md`.

### v2.0.0 — May 2026
- **Breaking:** renamed the `/report-session` slash command to `/report` and the underlying skill directory to `skills/report/`.
- **Breaking:** report template is now fixed-numbered. Sections 1–6 are always present; empty sections render `none` instead of being omitted and renumbered. Downstream consumers can rely on `## 4. Decisions Made` and `## 6. Pending Items` always being at those positions.
- **Breaking:** report filename drops the trailing `Z` (`<git-user>-YYYY-MM-DDTHHMMSS.md`) to keep `@`-completion working in the Claude Code CLI; the in-file header retains the `Z`.
- Added a **Session contract** block above §1 that records the user's goal entering the session and a `goal status` of `achieved | partial | abandoned | redirected`.
- Added a new `/recall` skill with `list`, `filter`, `grep`, and `resume` subcommands for retrieving and resuming prior session reports.
- Moved `ensure-sessions-dir.sh` to the plugin-level `scripts/` directory so both skills can share a single copy via `${CLAUDE_PLUGIN_ROOT}/scripts/`.

### v1.0.1 — April 2026
- Moved output-directory resolution into a bundled `ensure-sessions-dir.sh` script invoked via a single `bash` call in SKILL.md. Pre-authorized via `allowed-tools: Bash(bash:*)` so end users got no permission prompt.
- Replaced the inline `dir=...; mkdir; printf` compound statement, which was rejected by Claude Code's permission matcher (compound / expansion checks).

### v1.0.0 — April 2026
- Initial release. `/report-session` skill with language auto-detection, optional `--lang` override, structured template, conditional section rules, and git-aware output path.

## License

Property of Pragmabits.

## Contact

**Author:** Leonardo Leoncio
**Email:** leonardoleoncio96@gmail.com
