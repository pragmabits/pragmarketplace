---
name: report
description: Use when the user asks to finish, wrap up, write a session report, generate a handoff, summarize the session for later, or preserve current work for a future agent.
---

# Session Report

Write a structured handoff report for the current session.

Reports are stored under the active repository's root-level `.sessions/` directory. This path is intentionally agent-agnostic. Do not write session reports to `.codex/`, `.agents/`, `.claude/`, or any plugin-owned path.

## Prepare Metadata

Resolve the script path relative to this skill:

```text
../../scripts/session_report.py
```

Run it from the user's repository root:

```bash
python3 <plugin-root>/scripts/session_report.py prepare [--lang xx-YY] [optional title hint]
```

Use any language flag or title hint the user provided. The script creates `.sessions/` if needed and prints JSON containing:

- `output_path`
- `timestamp_utc`
- `git_user`
- `branch`
- `base_commit`
- `commits_last_day`
- `diff_stat`
- `status_short`
- `language`
- `title_hint`

Use those values as facts. Do not recompute the output path.

## Language

If `language` is set, write the report in that language. Otherwise use the dominant language the user used during the session. Keep technical terms, commands, paths, and identifiers in their original form.

## Report Requirements

The report is for the next agent after context reset, regardless of which agent tool is used. It must be factual, specific, and resumable.

Use fixed section numbers. Empty sections must contain `none`, not be omitted.

Write to `output_path` using the normal Codex file-editing tool.

## Template

```markdown
# Session Report: <concise title>

**Timestamp (UTC):** <timestamp_utc>
**Git user:** <git_user>
**Branch:** `<branch>`
**Base commit:** `<base_commit>`
**Commits generated:** <count from commits_last_day that are relevant to this session, or 0>

---

## Session contract

**User goal (entering session):** <what the user wanted at the start>
**Goal status:** <achieved | partial | abandoned | redirected>
**If partial, abandoned, or redirected:** <what changed and why; otherwise: n/a>

---

## 1. Outcome summary

| Field | Value |
|-------|-------|
| Goal status | <achieved | partial | abandoned | redirected> |
| Decisions recorded | <count> |
| Files created | <count> |
| Files modified | <count> |
| Files deleted | <count> |
| In-progress items | <count> |
| Promised items | <count> |
| Known issues | <count> |

---

## 2. Work Completed

### 2.1 <Topic>

**Problem:** <what needed to be done or fixed>
**Solution:** <what was implemented>
**Files:** <key files created or modified, with paths>

If empty: `none`

---

## 3. Issues and Bugs Found

| Issue | Root Cause | Resolution | Files |
|-------|------------|------------|-------|
| <description> | <why it happened> | <how it was fixed> | <paths> |

If empty: `none`

---

## 4. Decisions Made

| Decision | Choice | Alternative Rejected | Evidence | Rationale |
|----------|--------|----------------------|----------|-----------|
| <what> | <chosen> | <rejected, or n/a> | <paths/output/user input> | <why> |

If empty: `none`

---

## 5. Files Changed

### Created
- `<path>` - <purpose>

### Modified
- `<path>` - <what changed>

### Deleted
- `<path>` - <why>

If a subsection is empty: `none`

---

## 6. Pending Items

### 6.1 In-progress (must resume)

| Task | State | Next step | Blocked on | Files |
|------|-------|-----------|------------|-------|
| <task> | <where it stopped> | <concrete next action> | <dependency or n/a> | <paths> |

If empty: `none`

### 6.2 Promised but not started (should resume)

| Task | Promised in | Why deferred |
|------|-------------|--------------|
| <task> | <context where promise was made> | <reason> |

If empty: `none`

### 6.3 Known issues / tech debt (noted but not owned)

| Issue | Location | Severity |
|-------|----------|----------|
| <issue> | <path or component> | <low | medium | high> |

If empty: `none`
```

## Quality Bar

- Include exact file paths for every created, modified, or deleted file.
- Record decisions with evidence, including tool output when relevant.
- Put anything that a future agent must do first under `6.1`.
- Put user-promised follow-ups that were not started under `6.2`.
- Put known fragility or future cleanup under `6.3`.
- Do not invent completed work, commits, tests, or decisions.
