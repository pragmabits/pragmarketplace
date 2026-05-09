---
name: recall
description: Retrieve, search, and resume work from past session reports stored in .claude/sessions. Invoked explicitly via subcommands (list, filter, grep, resume, last) when the user wants to find a prior session or pick up pending work without manually browsing files.
allowed-tools: Bash(bash:*)
argument-hint: "list [--limit N] | filter <criteria> [--limit N] | grep <pattern> [--limit N] | resume [<session-id>] | last [<n>]"
---

# Session Recall

Retrieve and resume work from session reports produced by the `report` skill. Reports are stored in `<repo>/.claude/sessions/` and follow a fixed structure with stable section anchors. This skill exposes five read-only subcommands: `list`, `filter`, `grep`, `resume`, `last`.

All directory walking, metadata extraction, sorting, filtering, and rendering are handled by `${CLAUDE_SKILL_DIR}/scripts/recall.sh`. The dispatcher has already run with `$ARGUMENTS`; this prompt's job is mostly to relay its output. The exception is `resume`, which returns JSON and requires `AskUserQuestion` afterward.

## Script output

```!
bash "${CLAUDE_SKILL_DIR}/scripts/recall.sh" "$ARGUMENTS" 2>&1
```

## How to handle the output

### list, filter, grep, last

The script's output is the final user-facing render — markdown tables, grep matches with section headings, or full report bodies. **Emit it verbatim.** Do not reformat, summarize, add a preamble, or append a closing comment.

If the output is a usage line (`Usage: /recall ...`), an error (`error: ...`), or an empty-result notice (`No sessions match: ...`, `No matches for: ...`, `No sessions found ...`), still emit it verbatim and stop.

### resume

`resume`'s success output is **JSON**, not markdown. Two shapes:

**Pending items present:**

```json
{
  "session_id": "alice-2026-05-08T143022",
  "title": "Implement JWT auth middleware",
  "subsections": {
    "in_progress":  [{ "label": "task description", "raw": "| task description | ... |" }, ...],
    "promised":     [{ "label": "...", "raw": "..." }, ...],
    "known_issues": [{ "label": "...", "raw": "..." }, ...]
  }
}
```

**Empty (§6 missing or all three subsections are `none`):**

```json
{ "session_id": "...", "title": "...", "empty": true }
```

Other `resume` outputs — `Ambiguous reference ...`, `No session matches: ...`, `No sessions found ...` — are not JSON. Emit them verbatim and stop.

When the JSON has `"empty": true`: print `Session <session_id> has no pending items.` and stop. **Do not call `AskUserQuestion`.**

When the JSON has `subsections`:

1. Print a one-line header: `Resuming session: <session_id> — <title>`.
2. For each non-empty subsection, in order — `in_progress`, `promised`, `known_issues` — print a sub-header (`### In-progress`, `### Promised`, `### Known issues`) followed by each item's `raw` value on its own line.
3. Call `AskUserQuestion`:
   - **question**: `Which item would you like to pick up?`
   - **header**: `Resume`
   - **options**: each item's `label`, truncated to 60 characters if longer; ordering is `in_progress` first, then `promised`, then `known_issues`. Add a final option exactly: `None — just printing for reference`.
4. Do not begin work on any item until the user answers. The user's selection becomes the next turn's input.

## Session ID conventions

`resume` accepts three reference forms (resolved by `recall.sh` internally):

- **Full ID** — e.g., `alice-2026-05-08T143022`
- **Timestamp only** — e.g., `2026-05-08T143022`
- **Partial substring** — any unambiguous prefix or substring of a session ID

Ambiguous matches yield exit 2 from the script with the candidate list captured in the output above. Emit verbatim and stop.

## Failure modes

The script handles directory non-existence, empty directories, malformed reports (skipped from `list`/`filter`, included in `grep`/`last`), ambiguous references, unknown filter keys, invalid `--limit`/`<n>` values, and missing or unknown subcommands internally. Emit its output verbatim regardless of exit code; the model's only branching responsibility is recognizing JSON vs non-JSON for `resume`.
