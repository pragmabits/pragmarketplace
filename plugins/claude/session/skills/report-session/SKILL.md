---
name: report-session
description: This skill should be used when the user asks to "finish", "generate session report", "write session report", "end session", "wrap up", or "summarize this session". Produces a structured markdown retrospective capturing work completed, issues, learnings, decisions, and pending items from the current conversation.
allowed-tools: Bash(bash:*) Bash(git:*) Bash(date:*) Bash(echo:*)
argument-hint: "[--lang xx-YY] [optional report title]"
---

# Session Report Generator

Generate a structured retrospective report for the current working session. The report captures what was done, what went wrong, what was learned, and what remains pending — serving as a handoff document for future sessions.

## Session metadata (injected)

The following values are resolved at skill-render time and come from the user's actual repo state. Use them as-is; do not re-run the underlying commands.

- Git user: !`git config user.name 2>/dev/null || echo "unknown"`
- Branch: !`git branch --show-current 2>/dev/null || echo "unknown"`
- Base commit: !`git log -1 --format='%h (%s)' 2>/dev/null || echo "no-commits"`
- Timestamp (UTC): !`date -u +"%Y-%m-%dT%H%M%SZ"`

### Commits during session

```!
git log --oneline --since='1 day ago' 2>/dev/null || echo "(none or not a git repo)"
```

### Uncommitted changes (stat)

```!
git diff --stat 2>/dev/null
```

### Working tree status

```!
git status --short 2>/dev/null
```

## User-provided arguments

```
$ARGUMENTS
```

Parse the arguments as follows:

- If `$ARGUMENTS` contains `--lang xx` or `--lang xx-YY` (e.g. `--lang pt-BR`), use that as the report language.
- Otherwise, write in the language the user used during the session. If the session was mixed, default to the most frequent. Technical terms stay in English regardless.
- Any remaining non-flag text in `$ARGUMENTS` may be used as a hint for the report title.

## Output location

**Output directory (already created):** !`bash "${CLAUDE_SKILL_DIR}/scripts/ensure-sessions-dir.sh"`

The directory above was resolved and created at skill-render time. Use that exact absolute path for the Write tool — do not call `mkdir` yourself, and do not recompute the path.

**Filename template:** `<git-user>-<timestamp>.md`

- Substitute `<git-user>` from the injected metadata. Sanitize by lowercasing, replacing whitespace with `-`, and stripping characters outside `[a-z0-9._-]`.
- Substitute `<timestamp>` from the injected UTC timestamp (`YYYY-MM-DDTHHMMSSZ`).
- If the sanitized git-user is empty or was `unknown`, use `unknown-user`.

Final file path: `<output directory above>/<sanitized-git-user>-<timestamp>.md`.

## Workflow

### 1. Analyze the conversation

Review the full conversation to identify:

- **Work completed** — features implemented, bugs fixed, refactors, investigations.
- **Issues encountered** — bugs found, errors hit, unexpected behavior.
- **Mistakes made** — wrong approaches, wasted iterations, missed patterns, skipped verification.
- **Decisions taken** — user choices between alternatives, design decisions, deferred items.
- **Pending items** — unfinished work, known issues, deferred tasks.

### 2. Apply the template

Use the template below. Apply the section rules *before* numbering — omit empty conditional sections and renumber the surviving sections sequentially so the report never has numeric gaps.

```markdown
# Session Report: <concise title summarizing the session's main topics>

**Date:** <YYYY-MM-DD extracted from the injected timestamp>
**Branch:** `<branch from metadata>`
**Base commit:** `<base commit from metadata>`
**Commits generated:** <count from the "Commits during session" block> (from `<first>` to `<last>`) OR 0 (uncommitted work only)

---

## 1. Executive Summary

<2-4 sentences. What the session focused on, what was achieved, significant problems. Scannable.>

---

## 2. Work Completed

### 2.1 <Topic>

**Problem:** <what needed to be done or fixed>
**Solution:** <what was implemented>
**Files:** <key files created or modified>

### 2.2 <Topic>
...

---

## 3. Issues and Bugs Found

| Issue | Root Cause | Resolution |
|-------|-----------|------------|
| <description> | <why it happened> | <how it was fixed> |

---

## 4. Mistakes and Learnings

### 4.1 <Mistake title>

**What happened:** <factual description>
**Root cause:** <missing knowledge, wrong assumption, skipped verification>
**Impact:** <wasted iterations, broken functionality, user frustration>
**Learning:** <what to do differently>

---

## 5. Decisions Made

| Decision | Choice | Alternative Rejected | Rationale |
|----------|--------|---------------------|-----------|
| <what> | <chosen> | <rejected> | <why> |

---

## 6. Files Changed

### Created
- `<path>` — <purpose>

### Modified
- `<path>` — <what changed>

---

## 7. Pending Items

1. **<item>** — <description with enough context for a fresh session to continue>
```

### Section rules

**Required sections:** Executive Summary, Work Completed, Files Changed — always present.

**Conditional sections:** Issues and Bugs Found, Mistakes and Learnings, Decisions Made, Pending Items — omit when empty. A 30-line report for a simple session beats 200 lines of filler.

After deciding which sections survive, renumber sequentially so there are no gaps (e.g., if Issues is omitted, former `## 4. Mistakes` becomes `## 3.`). Update any cross-references to match.

**Tone:** Factual and direct. Self-critical in Mistakes — root cause analysis, not excuses. Specific over vague — include file paths, function names, error messages.

### 3. Save the file

Write the rendered report to the absolute path resolved in "Output location" above, using the Write tool. Do not run `mkdir`, `git rev-parse`, or `pwd` — those were handled by the `!` injection.

## What makes a good report

A good report answers five questions for a future reader:

1. **What happened?** — Executive Summary + Work Completed.
2. **What went wrong?** — Issues + Mistakes (root causes, not surface descriptions).
3. **What was decided?** — Decisions (with rejected alternatives and rationale).
4. **What's left?** — Pending Items (enough context to resume).
5. **What changed?** — Files Changed (quick git reference).
