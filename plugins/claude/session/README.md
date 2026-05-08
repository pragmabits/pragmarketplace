# Session Plugin

Session lifecycle helpers for Claude Code. Turns the current working session into a structured handoff report the next agent can resume from, and lets you list, search, and resume prior reports without manually browsing files.

## Overview

The `session` plugin ships two skills:

- **`/report`** — analyzes the current conversation and writes a structured markdown handoff report under `.claude/sessions/`. Optimized for the next session's agent: stable section anchors, fixed numbering, an explicit Session contract block (user goal + goal status), and typed pending items.
- **`/recall`** — read-only retrieval over the same `.claude/sessions/` directory. Four subcommands — `list`, `filter`, `grep`, `resume`.

Reports are saved to `<repo-root>/.claude/sessions/`. The directory is auto-created on first use; the location resolves via `$CLAUDE_PROJECT_DIR`, then `git rev-parse --show-toplevel`, falling back to the current directory.

## Prerequisites

- `git` (optional, but enables branch / commit / user metadata in the report header).
- `bash` — both skills' `!` blocks shell out to bash.

## Available Commands

### `/report`

Generate a handoff report for the current session.

**Usage:**
```
/report [--lang xx-YY] [optional report title]
```

| Argument | Description |
|----------|-------------|
| `--lang xx` / `--lang xx-YY` | Force the report language (e.g. `--lang pt-BR`, `--lang en-US`). |
| *(remaining text)* | Free-form hint for the report title. |

**Language default:** if `--lang` is not passed, the report is written in the language the user used during the session. If the session was mixed, the most frequent language wins. Technical terms stay in English regardless.

**Examples:**
```bash
# Default report — language auto-detected from the session
/report

# Force Portuguese (Brazil)
/report --lang pt-BR

# Force English with a title hint
/report --lang en-US auth middleware rewrite
```

### `/recall`

Retrieve and resume work from prior session reports. Read-only.

**Usage:**
```
/recall <list | filter <criteria> | grep <pattern> | resume [<session-id>]>
```

All subcommands except `resume` accept `--limit N` (positive integer) to cap output. The pattern in `grep` is a literal string by default; prefix with `re:` for regex.

| Subcommand | Output |
|------------|--------|
| `list` | Markdown table of all sessions, newest first (Session ID / Title / Timestamp / Branch / Status). |
| `filter <criteria>` | Same format, filtered by AND'd `key:value` pairs: `user:`, `branch:`, `status:` (`achieved`, `partial`, `abandoned`, `redirected`), `since:YYYY-MM-DD`, `until:YYYY-MM-DD`. |
| `grep <pattern>` | List of files containing the pattern, with up to 3 matching lines per file plus the surrounding `## N.` heading. |
| `resume [<session-id>]` | Prints §6 Pending Items verbatim from the target session, then asks via `AskUserQuestion` which item to pick up. Default target: most recent session. |

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

### `/recall`
1. The skill is invoked as `/recall <subcommand> [args]`.
2. The shared `ensure-sessions-dir.sh` resolves the directory; the skill then dispatches on the first argument (`list` / `filter` / `grep` / `resume`).
3. All file reads use the read-only Bash tools listed in `allowed-tools` (`ls`, `cat`, `grep`, `head`, `tail`, `awk`, `sed`, `sort`, `find`, `wc`). No writes.
4. For `resume`, after extracting §6 Pending Items, the skill issues an `AskUserQuestion` listing each pending item plus a final **None — just printing for reference** option, and stops. The user's selection becomes the input to the next turn.

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
        └── SKILL.md                   # Read-only retrieval (list / filter / grep / resume)
```

The `ensure-sessions-dir.sh` script is referenced by both skills as `${CLAUDE_PLUGIN_ROOT}/scripts/ensure-sessions-dir.sh`, so there is exactly one copy of the directory-resolution logic.

## Permissions

Both skills are pre-authorized via their `SKILL.md` `allowed-tools` frontmatter so end users get no permission prompt:

- `/report` — `Bash(bash:*) Bash(git:*) Bash(date:*) Bash(echo:*)` (metadata collection + script exec).
- `/recall` — `Bash(ls:*) Bash(cat:*) Bash(grep:*) Bash(head:*) Bash(tail:*) Bash(awk:*) Bash(sed:*) Bash(sort:*) Bash(find:*) Bash(wc:*)` (read-only retrieval only).

## Version History

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
