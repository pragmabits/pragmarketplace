---
name: report
description: This skill should be used when the user asks to "finish", "generate session report", "write session report", "end session", "wrap up", or "summarize this session". Produces a structured markdown handoff report capturing session contract, work completed, decisions, and pending items — optimized for the next session's agent to resume without re-investigation. After writing the file, the skill commits it in a single subject-only `chore:` commit isolated to the report path; pass `--no-commit` to skip.
allowed-tools: Bash(bash:*) Bash(git:*) Bash(date:*) Bash(echo:*)
argument-hint: "[--lang xx-YY] [--no-commit] [optional report title]"
---

# Session Report Generator

Generate a structured handoff report for the current working session. The primary consumer is the next session's agent, which will read the report after a context reset to resume work. Optimize for unambiguous references, stable structure, and resumable state.

## Session metadata (injected)

The following values are resolved at skill-render time and come from the user's actual repo state. Use them as-is; do not re-run the underlying commands.

- Git user: !`git config user.name 2>/dev/null || echo "unknown"`
- Branch: !`git branch --show-current 2>/dev/null || echo "unknown"`
- Base commit: !`git log -1 --format='%h (%s)' 2>/dev/null || echo "no-commits"`
- Timestamp (UTC, with Z): !`date -u +"%Y-%m-%dT%H%M%SZ"`
- Timestamp (UTC, no Z, for filename): !`date -u +"%Y-%m-%dT%H%M%S"`

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
- If `$ARGUMENTS` contains `--no-commit`, skip the commit step in §4 (the report file is still written normally).
- Any remaining non-flag text in `$ARGUMENTS` may be used as a hint for the report title.

## Output location

**Output directory (already created):** !`bash "${CLAUDE_PLUGIN_ROOT}/scripts/ensure-sessions-dir.sh"`

The directory above was resolved and created at skill-render time. Use that exact absolute path for the Write tool — do not call `mkdir` yourself, and do not recompute the path.

**Filename template:** `<git-user>-<timestamp>.md`

- Substitute `<git-user>` from the injected metadata. Sanitize by lowercasing, replacing whitespace with `-`, and stripping characters outside `[a-z0-9._-]`.
- Substitute `<timestamp>` from the injected no-Z UTC timestamp (`YYYY-MM-DDTHHMMSS`). The `Z` is dropped from the filename to avoid breaking `@`-completion in the Claude Code CLI; the in-file header retains the `Z` for timezone clarity.
- If the sanitized git-user is empty or was `unknown`, use `unknown-user`.

Final file path: `<output directory above>/<sanitized-git-user>-<timestamp>.md`.

## Workflow

### 1. Analyze the conversation

Review the full conversation to identify:

- **Session contract** — the user's goal entering the session and whether it was achieved, partial, abandoned, or redirected.
- **Work completed** — features implemented, bugs fixed, refactors, investigations, with file references.
- **Decisions taken** — material decisions with the rejected alternatives and the evidence or user input that settled them.
- **Pending items** — typed by category: in-progress (must resume), promised but not started (should resume), known issues (noted but not owned).
- **Files changed** — created, modified, deleted, with purpose.

### 2. Apply the template

Use the template below verbatim. Section numbers are **fixed** — do not renumber. If a section has no content, write the heading followed by `none` on the next line. This preserves stable anchors for downstream consumers.

```markdown
# Session Report: <concise title summarizing the session's main topics>

**Timestamp (UTC):** <full timestamp from metadata, e.g. 2026-05-08T143022Z>
**Git user:** <git user from metadata>
**Branch:** `<branch from metadata>`
**Base commit:** `<base commit from metadata>`
**Commits generated:** <count from the "Commits during session" block> (from `<first>` to `<last>`) OR 0 (uncommitted work only)

---

## Session contract

**User goal (entering session):** <what the user wanted at the start>
**Goal status:** <achieved | partial | abandoned | redirected>
**If partial, abandoned, or redirected:** <what changed and why; otherwise: n/a>

---

## 1. Outcome summary

| Field | Value |
|-------|-------|
| Goal status | <achieved \| partial \| abandoned \| redirected> |
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

### 2.2 <Topic>
...

If empty: `none`

---

## 3. Issues and Bugs Found

| Issue | Root Cause | Resolution | Files |
|-------|-----------|------------|-------|
| <description> | <why it happened> | <how it was fixed> | <paths> |

If empty: `none`

---

## 4. Decisions Made

| Decision | Choice | Alternative Rejected | Evidence | Rationale |
|----------|--------|---------------------|----------|-----------|
| <what> | <chosen> | <rejected, or n/a if evidence-determined> | <paths/output, or n/a if user-answered> | <why> |

If empty: `none`

---

## 5. Files Changed

### Created
- `<path>` — <purpose>

### Modified
- `<path>` — <what changed>

### Deleted
- `<path>` — <why>

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
| <issue> | <path or component> | <low \| medium \| high> |

If empty: `none`
```

### Section rules

**All sections are required and numbered fixed.** Empty sections are marked `none` rather than omitted. This guarantees stable anchors so a downstream agent can rely on `## 4. Decisions Made` always being at that position.

**Tone:** Factual and direct. Specific over vague — include file paths, function names, error messages, line numbers when relevant. No prose filler.

**Reference discipline:** When referring to code, use backticked paths (`src/foo/bar.py`) and function names (`parse_config()`). When referring to commits, use short hashes. When referring to decisions, use the row description from §4 — do not invent decision IDs.

### 3. Save the file

Write the rendered report to the absolute path resolved in "Output location" above, using the Write tool. Do not run `mkdir`, `git rev-parse`, or `pwd` — those were handled by the `!` injection.

### 4. Commit the report

Unless `$ARGUMENTS` contained `--no-commit`, commit the report file in a single isolated commit immediately after step 3. The commit must:

- contain **only** the report file just written — never co-commit other staged or unstaged work;
- carry a subject-only message — no body, no emojis, no scope, no trailers.

Use the Bash tool to run the following **two** commands in order, substituting the values resolved at render time:

```bash
git add -- "<absolute-report-path>"
git commit -m "chore: add session report <timestamp>" -- "<absolute-report-path>"
```

- `<timestamp>` — the injected no-Z UTC timestamp (e.g. `2026-05-11T143022`). Same value used in the filename.
- `<absolute-report-path>` — the exact path passed to the Write tool in step 3.

The `git add` is required because the report file is brand-new and therefore untracked; `git commit -- <path>` is partial-commit mode that only operates on tracked paths and would otherwise fail with `pathspec ... did not match any files`. After the add, partial-commit mode commits only `<path>` and leaves any other staged or unstaged changes for unrelated paths untouched. This is intentional — the report is workflow metadata and must not entangle with the user's in-progress work.

**Failure handling.** If either command exits non-zero (no git repo, hook rejection, merge in progress, identity not configured, etc.):

1. Do **not** delete or rewrite the report. It remains exactly as Write left it. Do **not** run `git reset` or `git restore --staged` to unstage it either — leave the staged state as-is so the user can inspect what `git add` produced.
2. Tell the user in a single line which command failed (`git add` or `git commit`) and include the git error output verbatim so they can act on it.
3. Do **not** retry, do **not** propose alternate commit messages, and do **not** stage anything else. If `git add` failed, do not proceed to `git commit`.

**Opt-out.** If `$ARGUMENTS` contained `--no-commit`, skip this step entirely and tell the user the report was written without a commit. Do not stage the file in any other way.

## What makes a good handoff report

The report is consumed by an agent after a context reset. It must answer:

1. **What was the user trying to do?** — Session contract.
2. **What got done?** — §2 Work Completed + §5 Files Changed.
3. **What was decided and why?** — §4 Decisions Made (with evidence and rejected alternatives, so the next agent does not re-propose them).
4. **What must I pick up first?** — §6.1 In-progress.
5. **What was promised but not done?** — §6.2 Promised.
6. **What's broken or fragile that I should know about?** — §3 Issues + §6.3 Known issues.

A report that does not let the next agent answer these without re-reading the source code has failed.