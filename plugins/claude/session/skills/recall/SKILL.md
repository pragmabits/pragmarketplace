---
name: recall
description: Retrieve, search, and resume work from past session reports stored in .claude/sessions. Invoked explicitly via subcommands (list, filter, grep, resume, last) when the user wants to find a prior session or pick up pending work without manually browsing files.
allowed-tools: Bash(bash:*), Read
argument-hint: "list [--limit N] | filter <criteria> [--limit N] | grep <pattern> [--limit N] | resume [<session-id>] | last [<n>]"
---

# Session Recall

Retrieve and resume work from session reports produced by the `report` skill. Reports are stored in `<repo>/.claude/sessions/` and follow a fixed structure with stable section anchors. This skill exposes five read-only subcommands: `list`, `filter`, `grep`, `resume`, `last`.

All directory walking, metadata extraction, sorting, filtering, and rendering are handled by `${CLAUDE_SKILL_DIR}/scripts/recall.sh`. The dispatcher has already run with `$ARGUMENTS`. For `list`, `filter`, and `grep`, this prompt's job is to relay its output verbatim. For `last` and `resume`, the script returns *pointers* (file paths or JSON containing a path) — the agent must call the `Read` tool to ingest the actual report content, then take the follow-up action described below.

## Script output

```!
bash "${CLAUDE_SKILL_DIR}/scripts/recall.sh" "$ARGUMENTS" 2>&1
```

## How to handle the output

### list, filter, grep

The script's output is the final user-facing render — markdown tables or grep matches with section headings. **Emit it verbatim.** Do not reformat, summarize, add a preamble, or append a closing comment.

If the output is a usage line (`Usage: /recall ...`), an error (`error: ...`), or an empty-result notice (`No sessions match: ...`, `No matches for: ...`, `No sessions found ...`), still emit it verbatim and stop.

### last

The script returns a list of session-report **file paths** (most recent first), one per line, optionally followed by a trailing notice (e.g. `Only X session(s) available; all paths shown.`).

If the output is an empty-result notice (`No sessions found ...`) or an error (`error: ...`), emit it verbatim and stop.

Otherwise:

1. Call the `Read` tool on **every** returned path. Issue all `Read` calls in **parallel** in a single message — they are independent.
2. After every read completes, emit one line per report **in the same order the script returned them**:
   `- <session-id> — <one-line summary>`
   The session ID is the filename without `.md`. The summary is your own ≤120-char distillation of what the session actually did and how it ended (the §1 contract and §7 outcome are usually the right material). No boilerplate, no leading verbs like "this session …", no closing remarks.
3. If the script printed a trailing notice, append it as the last line.

**Do not** dump full report bodies into the chat — the Read calls put the content in your context, which is the point.

### resume

`resume`'s success output is **JSON**, not markdown. Two shapes:

**Pending items present:**

```json
{
  "session_id": "alice-2026-05-08T143022",
  "title": "Implement JWT auth middleware",
  "file_path": "/path/to/repo/.claude/sessions/alice-2026-05-08T143022.md",
  "subsections": {
    "in_progress":  [{ "label": "task description", "raw": "| task description | ... |" }, ...],
    "promised":     [{ "label": "...", "raw": "..." }, ...],
    "known_issues": [{ "label": "...", "raw": "..." }, ...]
  }
}
```

**Empty (§6 missing or all three subsections are `none`):**

```json
{ "session_id": "...", "title": "...", "file_path": "...", "empty": true }
```

Other `resume` outputs — `Ambiguous reference ...`, `No session matches: ...`, `No sessions found ...` — are not JSON. Emit them verbatim and stop.

When the JSON has `"empty": true`: print `Session <session_id> has no pending items.` and stop. **Do not call `Read` or `AskUserQuestion`.**

When the JSON has `subsections`:

1. **First**, call the `Read` tool on `file_path` to load the full session report into context. Do this *before* anything else — the §6 extract alone is not enough to resume work intelligently.
2. Print a one-line header: `Resuming session: <session_id> — <title>`.
3. For each non-empty subsection, in order — `in_progress`, `promised`, `known_issues` — print a sub-header (`### In-progress`, `### Promised`, `### Known issues`) followed by each item's `raw` value on its own line.
4. Call `AskUserQuestion`:
   - **question**: `Which item would you like to pick up?`
   - **header**: `Resume`
   - **options**: each item's `label`, truncated to 60 characters if longer; ordering is `in_progress` first, then `promised`, then `known_issues`. Add a final option exactly: `None — just printing for reference`.
5. Do not begin work on any item until the user answers. The user's selection becomes the next turn's input.

## Session ID conventions

`resume` accepts three reference forms (resolved by `recall.sh` internally):

- **Full ID** — e.g., `alice-2026-05-08T143022`
- **Timestamp only** — e.g., `2026-05-08T143022`
- **Partial substring** — any unambiguous prefix or substring of a session ID

Ambiguous matches yield exit 2 from the script with the candidate list captured in the output above. Emit verbatim and stop.

## Failure modes

The script handles directory non-existence, empty directories, malformed reports (skipped from `list`/`filter`, included in `grep`/`last`), ambiguous references, unknown filter keys, invalid `--limit`/`<n>` values, and missing or unknown subcommands internally. Emit its output verbatim regardless of exit code; the model's only branching responsibility is recognizing JSON vs non-JSON for `resume`.
