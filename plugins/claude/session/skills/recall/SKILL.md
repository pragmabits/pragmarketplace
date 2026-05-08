---
name: recall
description: Retrieve, search, and resume work from past session reports stored in .claude/sessions. Invoked explicitly via subcommands (list, filter, grep, resume) when the user wants to find a prior session or pick up pending work without manually browsing files.
allowed-tools: Bash(ls:*) Bash(cat:*) Bash(grep:*) Bash(head:*) Bash(tail:*) Bash(awk:*) Bash(sed:*) Bash(sort:*) Bash(find:*) Bash(wc:*)
argument-hint: "list [--limit N] | filter <criteria> [--limit N] | grep <pattern> [--limit N] | resume [<session-id>]"
---

# Session Recall

Retrieve and resume work from session reports produced by the `report` skill. Reports are stored in `.claude/sessions/` and follow a fixed structure with stable section anchors. This skill exposes four read-only subcommands.

## Sessions directory

**Sessions directory:** !`bash "${CLAUDE_PLUGIN_ROOT}/scripts/ensure-sessions-dir.sh"`

Use that path for all read operations. All files have the form `<git-user>-<timestamp>.md` where timestamp is `YYYY-MM-DDTHHMMSS` (UTC, no `Z`).

## User-provided arguments

```
$ARGUMENTS
```

## Dispatch

Parse the first token of `$ARGUMENTS` as the subcommand:

- `list` → §1
- `filter` → §2
- `grep` → §3
- `resume` → §4

If the subcommand is missing or unrecognized, print:

```
Usage: /recall <list | filter <criteria> | grep <pattern> | resume [<session-id>]>
```

and stop. Do not guess.

## Session ID conventions

A session is identified by its filename without extension: `<git-user>-<timestamp>`. Accept three reference forms in arguments:

- **Full ID** — e.g., `alice-2026-05-08T143022`
- **Timestamp only** — e.g., `2026-05-08T143022`, matched against the timestamp portion of any filename
- **Partial match** — any unambiguous prefix or substring; if it matches more than one file, list the matches and ask the user to disambiguate

Resolve the reference to an absolute path before reading.

## Shared flags

- **`--limit N`** — cap output to the first `N` rows (for `list` and `filter`) or the first `N` matching files (for `grep`). `N` must be a positive integer. If omitted, no limit applies. Invalid values produce an error and stop. Not applicable to `resume`.

When a limit truncates output, append a final line: `<total> total, showing <N>. Use --limit <higher> or filter further to see more.`

## §1 — `list`

Print a compact table of all sessions in the directory, newest first.

For each report, extract:

- **Session ID** (filename without `.md`)
- **Title** (first `# Session Report:` line, content after the colon)
- **Timestamp** (from the `**Timestamp (UTC):**` field in the body)
- **Branch** (from the `**Branch:**` field)
- **Goal status** (from the Session contract block)

Render as a markdown table:

```markdown
| Session ID | Title | Timestamp | Branch | Status |
|------------|-------|-----------|--------|--------|
```

Sort rows by timestamp descending. If the directory is empty, print `No sessions found in .claude/sessions/`.

## §2 — `filter <criteria>`

Same output format as `list`, but limited to sessions matching one or more criteria. Criteria are space-separated `key:value` pairs:

- `user:<git-user>` — match git user from filename
- `branch:<branch>` — match the `**Branch:**` field
- `status:<achieved|partial|abandoned|redirected>` — match goal status
- `since:<YYYY-MM-DD>` — sessions on or after this date
- `until:<YYYY-MM-DD>` — sessions on or before this date

Multiple criteria are AND'd. Unknown keys produce an error and stop execution.

If no sessions match, print `No sessions match: <criteria>`.

## §3 — `grep <pattern>`

Run `grep -l -i <pattern>` against all `.md` files in the sessions directory. For each matching file:

- Print the Session ID and Title.
- Print up to 3 matching lines with surrounding context (1 line before, 1 line after), prefixed with the section heading they fall under.

Use `grep -n` to get line numbers and resolve each line to its containing `## N.` heading by reading backward through the file.

If no matches, print `No matches for: <pattern>`.

The pattern is treated as a literal string by default. If the user wants regex behavior, they can prefix the pattern with `re:` (e.g., `re:^Decision`).

## §4 — `resume [<session-id>]`

If `<session-id>` is omitted, target the most recent session (newest timestamp in the filename). Print which session was selected:

```
Resuming most recent session: <Session ID> — <Title>
```

If `<session-id>` is provided, resolve it per §"Session ID conventions". On ambiguity, list candidates and stop.

Then extract and print **§6 Pending Items** verbatim from the target file, preserving the three subsections (6.1 In-progress, 6.2 Promised, 6.3 Known issues). If a subsection is `none`, omit it from the output (this is a presentation choice for resume; the source file is unchanged).

After printing, ask the user which item(s) to pick up using `AskUserQuestion`. Build the option list from 6.1 In-progress entries first, then 6.2 Promised, then 6.3 Known issues. Each option is the task description, truncated to ~60 characters if longer. Include a final option exactly: **None — just printing for reference**.

Do not begin work on any item until the user answers. The user's selection becomes the input to the next turn; this skill's job ends with the question.

## Output discipline

- Tables use markdown table syntax. Do not pad columns with spaces beyond standard markdown.
- Do not add prose summaries before or after subcommand output. The user invoked a specific subcommand and wants its output.
- Errors are one line, no preamble.
- All paths in output are repo-relative when possible (`.claude/sessions/<file>.md`), absolute only when ambiguity would otherwise result.

## Failure modes

- **Sessions directory does not exist** — print `No sessions directory found at .claude/sessions/. Run the report skill at session end to create it.` and stop.
- **A report is malformed** (missing required fields like Title or Timestamp) — skip it in `list` and `filter` output but include it in `grep` results. Do not error the whole subcommand.
- **`resume` target has no Pending Items section or all three subsections are `none`** — print `Session <ID> has no pending items.` and stop without asking a question.