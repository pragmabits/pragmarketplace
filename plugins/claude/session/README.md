# Session Plugin

Session lifecycle helpers for Claude Code. Turns the current working session into a structured retrospective that future sessions can pick up from.

## Overview

The `session` plugin adds a `/report-session` skill that analyzes the current conversation and produces a structured markdown retrospective — a handoff document capturing what was done, what went wrong, what was decided, and what's left.

The report is saved under `.claude/sessions/` in the repo root (or the current directory if outside a git repo), with a filename derived from the git user and a UTC timestamp. It is safe to run at any point during the session.

### What the report contains

A good session report answers five questions for a future reader:

1. **What happened?** — Executive summary + work completed.
2. **What went wrong?** — Issues + mistakes, with root causes rather than surface descriptions.
3. **What was decided?** — Decisions with rejected alternatives and rationale.
4. **What's left?** — Pending items with enough context to resume.
5. **What changed?** — File-level changes.

Empty sections are omitted and the surviving sections are renumbered so there are no numeric gaps — a 30-line report for a simple session is preferred over 200 lines of filler.

## Prerequisites

- `git` (optional, but enables branch/commit/user metadata in the report header).
- Nothing else — the skill runs entirely inside Claude Code.

## Available Commands

### `/report-session`

Generate a retrospective report for the current session.

**Usage:**
```
/report-session [--lang xx-YY] [optional report title]
```

| Argument | Description |
|----------|-------------|
| `--lang xx` / `--lang xx-YY` | Force the report language (e.g. `--lang pt-BR`, `--lang en-US`). |
| *(remaining text)* | Free-form hint for the report title. |

**Language default:** if `--lang` is not passed, the report is written in the language the user used during the session. If the session was mixed, the most frequent language wins. Technical terms stay in English regardless.

**Examples:**
```bash
# Default report — language auto-detected from the session
/report-session

# Force Portuguese (Brazil)
/report-session --lang pt-BR

# Force English with a title hint
/report-session --lang en-US auth middleware rewrite
```

## Output Location

Reports are written to:

```
<repo-root>/.claude/sessions/<git-user>-<YYYY-MM-DDTHHMMSSZ>.md
```

- `<repo-root>` is resolved via `git rev-parse --show-toplevel`, falling back to the current directory if there is no git repo.
- `<git-user>` is taken from `git config user.name`, sanitized to lowercase `[a-z0-9._-]` (whitespace → `-`). If empty or `unknown`, `unknown-user` is used.
- `<YYYY-MM-DDTHHMMSSZ>` is the UTC timestamp at report render time.

The directory is created automatically if it does not exist.

## Report Template

Every report starts with a header:

```markdown
# Session Report: <concise title>

**Date:** <YYYY-MM-DD>
**Branch:** `<branch>`
**Base commit:** `<short-sha> (<subject>)`
**Commits generated:** <count>
```

Then a subset of the following sections, numbered sequentially with no gaps:

| Section | Required | Purpose |
|---------|----------|---------|
| Executive Summary | Always | 2–4 sentences scannable overview. |
| Work Completed | Always | Per-topic problem / solution / files. |
| Issues and Bugs Found | If any | Issue / root cause / resolution table. |
| Mistakes and Learnings | If any | Self-critical root-cause entries. |
| Decisions Made | If any | Decision / chosen / rejected / rationale table. |
| Files Changed | Always | Created vs modified lists. |
| Pending Items | If any | Enough context for a fresh session to resume. |

Tone is factual and direct — specific over vague. Mistakes section is self-critical with root-cause analysis, not excuses.

## How It Works

1. The skill is invoked as `/report-session [args]`.
2. Before the skill content reaches Claude, several `!` shell-exec blocks collect repo metadata: git user, current branch, latest commit, UTC timestamp, recent commits, `git diff --stat`, and `git status --short`.
3. Another `!` block resolves the output directory (`<repo-root>/.claude/sessions/`) and creates it.
4. Claude analyzes the full conversation, applies the template, omits empty sections, renumbers the survivors, and writes the report to the pre-resolved path using the Write tool.

## Architecture

```
session/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── report-session/
        └── SKILL.md   # Skill with metadata !-exec blocks and the report template
```

## Version History

### v1.0.0 — April 2026
- Initial release. `/report-session` skill with language auto-detection, optional `--lang` override, structured template, conditional section rules, and git-aware output path.

## License

Property of Pragmabits.

## Contact

**Author:** Leonardo Leoncio
**Email:** leonardoleoncio96@gmail.com
