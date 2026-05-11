---
name: recall
description: Use when the user wants to list, filter, search, inspect, or resume previous agent-agnostic session reports from .sessions. Supports list, filter, grep, resume, and last workflows.
---

# Session Recall

Retrieve session reports created by the `report` skill. This skill is read-only.

Reports live in the repository root:

```text
<repo-root>/.sessions/
```

Do not write to `.codex/`, `.agents/`, `.claude/`, or any plugin-owned path while recalling sessions.

## Command Script

Resolve the script path relative to this skill:

```text
../../scripts/session_recall.py
```

Run from the user's repository root:

```bash
python3 <plugin-root>/scripts/session_recall.py <subcommand> [args]
```

Subcommands:

```text
list [--limit N]
filter <criteria> [--limit N]
grep <pattern> [--limit N]
resume [<session-id>]
last [<n>]
```

Filter criteria are ANDed `key:value` pairs:

```text
user:<name>
branch:<branch>
status:<achieved|partial|abandoned|redirected>
since:YYYY-MM-DD
until:YYYY-MM-DD
```

`grep` is literal and case-insensitive by default. Prefix with `re:` for a regular expression.

## Handling Output

### list, filter, grep

Emit the script output verbatim. Do not summarize or reformat markdown tables, grep matches, usage lines, or empty-result messages.

### last

The script prints report file paths, newest first, and may append a trailing notice.

Read each printed report path. Then emit one line per report in the same order:

```text
- <session-id> - <one-line summary>
```

The summary should be no more than 120 characters and should describe what the session did and how it ended. If the script printed a trailing notice, append it after the summary list.

Do not dump full report bodies into chat unless the user explicitly asks.

### resume

Successful `resume` output is JSON.

If the JSON has `"empty": true`, print:

```text
Session <session_id> has no pending items.
```

If the JSON has `subsections`:

1. Read `file_path` before deciding what to do.
2. Print:

   ```text
   Resuming session: <session_id> - <title>
   ```

3. Show non-empty pending sections in this order:
   - `in_progress`
   - `promised`
   - `known_issues`
4. Ask the user which item to pick up. Do not start work until the user chooses.

If the output is not JSON, emit it verbatim and stop.

## Session ID Matching

`resume` accepts:

- Full ID, for example `alice-2026-05-08T143022`
- Timestamp suffix, for example `2026-05-08T143022`
- Any unambiguous substring

Ambiguous references print candidates and stop.
