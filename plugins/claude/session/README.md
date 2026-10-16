# Session Plugin

Session lifecycle helpers for Claude Code. Writes the current working session as a structured handoff report, and lets a later session list, search and resume prior reports without browsing files by hand.

A report is a dated record of what the session observed. The next session reads it as evidence of what was true when it was written, and checks the current state before acting on anything in it.

## Overview

The `session` plugin ships two skills:

- **`/report`** writes a handoff report under `.harness/sessions/`: the session contract (goal, direction changes, status and the evidence for it), work done with its verification state, decisions with who made them, corrections, and pending items with their origin and evidence. `/report` then commits the new file in an isolated `chore:` commit; `--no-commit` writes the file only.
- **`/recall`** reads the same directory through five subcommands: `list`, `filter`, `grep`, `resume`, `last`. It never creates or changes a file.

## Storage

Reports live in one directory per project, `<project-root>/.harness/sessions/`, shared with the Codex `session` plugin and any other tool that follows the same report contract. All reports of a project sit in that one collection: no subdirectory per tool, model or user.

- Only the report save step creates the directory. `/recall` never creates it; a missing directory means no reports there.
- Nothing reads the older locations (`.claude/sessions/` before 3.0.0, `.sessions/` for the Codex plugin before 0.2.0) or warns about them. To keep old reports, move the files into `.harness/sessions/` as they are; their content keeps working (see *Reading reports from other tools and versions*). The plugin does not move, copy or rewrite them.
- The move changes nothing in `.gitignore`, commit policy or project settings.

## Prerequisites

- `bash` and the usual POSIX tools (`grep`, `sed`, `awk`, `sort`).
- `jq`, for `/recall`.
- `git`, to record the observed HEAD and to commit reports. Without a repository, `/report` still writes the file and does not commit it.

## `/report`

```
/report [--lang xx-YY] [--no-commit] [optional report title]
```

| Argument | Description |
|----------|-------------|
| `--lang xx` / `--lang xx-YY` | Report language (e.g. `--lang pt-BR`). Default: the language the user used most in the session. Headings, field labels, `none` and the goal-status values stay in English, because `/recall` reads them. |
| `--no-commit` | Write the report without committing it: no `git add`, nothing written to the index. |
| *(remaining text)* | Hint for the report title. |

### When it writes and when it commits

| Request | File | Commit |
|---|---|---|
| `/report` typed by the user, without `--no-commit` | yes | yes, unless the user already said not to commit in that conversation |
| `/report --no-commit`, or the user said not to commit | yes | no |
| A request in words for the report and its commit | yes | yes |
| A request in words for a report file only | yes | no, and no closing question about committing |
| "finish", "wrap up", "termine", "encerre", or a summary in the chat | no | no |

The skill's description lists only explicit report requests as triggers, so closing phrases no longer load it.

### What a report may claim

The skill keeps four states apart in the text: done and verified (with the command, file or hash that shows it), done with verification pending (and which check is missing), proposed or inferred, and not available. A started test is not a passed test; "docs updated" names the documents checked; a cause without evidence is a hypothesis; a partial view of the session is declared in **Context coverage** instead of filled in. Writing the report authorizes no new work.

Decisions name who decided (the user, the assistant within scope, or a proposal not accepted) and the evidence for that attribution. Corrections that the next session needs are recorded in one line each: earlier statement, corrected fact, consequence.

A report carries no credential value of any kind — no password, token, key, URL with credentials or authorization header — and that includes examples, fake and test values, placeholders shaped like a credential, and masked or truncated values. The report names the credential and where it lives instead. The model reviews the draft before saving; `check-report.sh` then flags credential shapes whether real or invented (a token whose body is `xxxx`, a stand-in password, a value given to a credential name or a `--password` flag); only prose and references to environment variables (`$NAME`, `${NAME}`) pass, and a flagged value is removed, never left in the file. Repository hooks are a third barrier. None of these finds every secret.

### Header and metadata

- **Timestamp (UTC)** and the filename come from one clock read, so they always agree.
- **HEAD observed at generation** is where HEAD was when the report was generated. It is not called the session's base, since nothing proves it was.
- **Commits made in this session** lists only commits whose creation appears in the session's own tool output. A time window, the author or the branch is not evidence. `none` means the whole session was visible and no commit was made; otherwise `not determined`.
- **Context coverage** is `full` or `partial` with what is not visible.
- Statements about the repository's current state (commits not pushed, a push or pull outstanding, staged or uncommitted changes, stashes, an operation in progress) come only from the *Repository state at generation* block that `prepare-report.sh` reads when the report is generated: commits ahead of and behind the upstream as this clone last saw the remote (nothing is fetched, and no branch name is printed), staged, unstaged and untracked counts, stash entries, and any merge, rebase, cherry-pick, revert or bisect in progress. An earlier reading in the session is recorded, if at all, as a past moment. What the block cannot see (the remote itself, pull requests, CI, other clones) is left out.
- There is no **Branch** field, and the worktree's name and location are kept out of the content. Paths are relative to the project.
- **Harness** and **Report generator** record who wrote the report (see *Authorship fields*).

### Authorship fields

These fields describe the generation of this report, not everyone who took part in the session: when work moved between tools, models or subagents, they name the writer of the report. They help investigate differences between tools and regressions; they prove nothing about the report's quality and give its content no authority.

| Field | Meaning | In this plugin |
|---|---|---|
| `Harness` | Tool that ran the execution writing the report | `claude-code` when `CLAUDECODE=1`, which Claude Code documents as set in the processes it spawns; otherwise `unknown` |
| `Report generator` | Plugin and version that supplied the procedure | `session/claude-code <version>`, from this plugin's own manifest |

`scripts/report-origin.sh` prints these lines during the turn that writes the report, and the skill copies them as printed.

There is no `Model` line. Claude Code documents no way for a skill, or the shell it spawns, to learn the model serving the current turn: `ANTHROPIC_MODEL` and the `model` setting are configured defaults, not the model of this execution; the session transcript does carry it, but its entry format is documented as internal and subject to change; the documented sources (status line input, `SessionStart` and model-switch hooks) would need a hook added just for this. The field could only ever say `unknown`, so it is left out, and the skill never fills it from the model's own beliefs or asks the user. `Harness version` and `Agent` are left out for the same reason: no documented source for the running process, no confirmed agent profile. `check-report.sh` flags a `Model` line in a new report.

Readers still accept those fields when a report from another tool carries them. A `Model` value is then kept as one of three states — a confirmed identifier, `alias: <value>` (never expanded into a version), or `unknown` — and a report without the field reads as `absent`.

### Saving and committing

The skill's render-time metadata comes from `scripts/prepare-report.sh`, which creates nothing. The save step runs `ensure-sessions-dir.sh`, writes the file, and runs `check-report.sh`, which reports credential shapes, the project's absolute path, a linked worktree's name, missing or out-of-order anchors, a Branch field, and a header timestamp that disagrees with the filename. Findings name the line and the kind, never the value.

When the commit is authorized, `scripts/commit-report.sh <report>`:

1. refuses before staging when the path is not in a git work tree, a merge/rebase/cherry-pick/revert is in progress, the path is ignored, git has no usable identity, or the path is already committed with other content (identical content reports `already-committed` instead of making a second commit);
2. runs `check-report.sh` and stages nothing if it has findings;
3. stages the report by path and runs `git commit --only -m "chore: add session report <timestamp>" -- <report>`, which builds the commit from HEAD plus that one path; other staged, partially staged, unstaged and untracked work stays as it was;
4. verifies that the new commit holds exactly the report, on top of the previous HEAD, with the content on disk, and that no other index entry moved;
5. on a failed commit, removes the report's own index entry again so no version of it stays staged, and prints a redacted, capped diagnostic with a category (`rejected`, `identity`, `signing`, `lock`, `ignored`, `operation-in-progress`, `filesystem`).

It never passes `--no-verify`, `--no-gpg-sign` or `-c` overrides, never changes configuration, and never runs `reset`, `restore` or `stash`. It makes one attempt per run. The skill allows one retry, and only after fixing report content a hook identifiably rejected; identity, signing, lock and similar failures are reported, not worked around. Blobs created by an earlier `git add` may remain in the object store until git collects them; the plugin does not promise their removal.

### Filename

```
<project-root>/.harness/sessions/<git-user>-<YYYY-MM-DDTHHMMSS>[-N].md
```

- `<git-user>` is `git config user.name`, lowercased, whitespace turned into `-`, characters outside `[a-z0-9._-]` dropped; `unknown-user` when empty.
- `<YYYY-MM-DDTHHMMSS>` is the UTC instant without the trailing `Z` (it breaks `@`-completion in the CLI); the header keeps the `Z`.
- `-N` (`-2`, `-3`, ...) is added only when a report with the plain name already exists, so an existing report is never replaced, including one written by the Codex plugin, which uses the same scheme. The name says nothing about which tool wrote the report.

## `/recall`

```
/recall <list | filter <key:value>... | grep <pattern> | resume [<session-id>] [--item <text>] | last [<n>]>
```

`list`, `filter` and `grep` accept `--limit N`. Multi-word arguments can be quoted with `'...'` or `"..."`.

| Subcommand | Output |
|------------|--------|
| `list` | Markdown table, newest first: Session ID / Title / Timestamp / Status. Files without the title or timestamp anchors, empty files and unreadable files are named in a trailing notice. |
| `filter <criteria>` | Same table, filtered by AND'd `key:value` pairs: `user:` (filename prefix, case-insensitive), `status:` (`achieved`, `partial`, `abandoned`, `redirected`), `since:YYYY-MM-DD`, `until:YYYY-MM-DD` (inclusive), and `branch:` for reports written before 3.0.0, which carried a Branch field. A `branch:` filter adds the Branch column; newer reports never match it. |
| `grep <pattern>` | Reports containing the pattern, with up to 3 matching lines each and the enclosing `##` heading. Literal and case-insensitive by default; prefix `re:` for an extended regular expression. An invalid expression is an error, not a miss. |
| `resume [<session-id>] [--item <text>]` | The report's goal, status, decisions and pending items, then a check of the current state of the items that matter (see below). Default: the newest report. `--item` names the item the user wants to resume; it comes back as `requested_item` and the model continues with it without asking again. |
| `last [<n>]` | One line per report for the `<n>` newest (default 1): `- <session-id> — <status> — <summary>`. The summary describes what the report records; it does not vouch for it. |

Ordering is by the filename timestamp, then the `-N` suffix; never by the user prefix or file modification time.

**Session references** for `resume`: a full ID (`alice-2026-05-08T143022`), a timestamp (`2026-05-08T143022`), or any unique substring. An exact ID wins over substring matches; an ambiguous reference lists the candidates and stops.

### Resume

`resume` is three separate phases:

1. **Lookup** (the script, read-only): metadata, goal, decisions and pending items, with an explicit `pending_state`.
2. **Local check** (the model, read-only): for the items tied to what the user wants to resume, cheap local evidence — the cited file, the code, a later report, `git log`. Each checked item is shown as **Still pending**, **Resolved or superseded**, or **Not confirmed** (with the missing check named); a hypothesis that nothing current confirms or refutes stays **Not confirmed**. No test suites, builds, downloads, network calls or edits to classify an item.
3. **Work**, only as the user's current request allows. When the user already named the item, the model continues with it without asking again; when there are real open alternatives, it asks once with context; when the user only wanted to see the list, it stops.

Report content is data. Commands, "next steps" or instructions inside a report never override the current request, grant authorization, or run on their own; an item under Known issues does not authorize a fix.

`pending_state` distinguishes four cases:

| Case | Output |
|------|--------|
| No reports at all | `No sessions found in .harness/sessions/` (with `(the directory does not exist)` when it is missing) |
| §6 present and all three subsections say `none` | `pending_state: "none"` and `empty: true` |
| §6 missing, a subsection missing, a table cut off, or content that is neither a table, a list nor `none` | `pending_state: "incomplete"` with `incomplete_reasons`; never `empty` |
| Items read | `pending_state: "items"` |

### Reading reports from other tools and versions

`/recall` reads every report in `.harness/sessions/` the same way, whoever wrote it:

- Reports from the Codex plugin follow the same contract and are read like any other. The two readers (this plugin's `recall.sh` and the Codex plugin's `session_recall.py`) give identical output on the same reports; the test suite checks that (case A05).
- Reports without the authorship fields (older ones, or moved from `.claude/sessions/` or `.sessions/`) are listed, searched and resumed normally. Their authorship comes back as absent (`origin.model.state: "absent"`); it is never inferred from the directory they came from, their style, date or filename.
- Authorship values are data: an unfamiliar harness or model identifier is accepted as written, and a missing `Agent` is normal.

`last` and `resume` include an `origin` object: `harness`, `model` (`{state: confirmed | alias | unknown | absent, value}`), `agent`, `harness_version`, `report_generator`.

## Report template

```markdown
# Session Report: <concise title>

**Timestamp (UTC):** <YYYY-MM-DDTHHMMSSZ>
**Git user:** <name>
**Harness:** <claude-code | codex | ...>
**Report generator:** <plugin and version>
**HEAD observed at generation:** `<short-sha>`
**Commits made in this session:** <hashes | none | not determined — reason>
**Context coverage:** <full | partial — what is not visible>

## Session contract

**User goal (entering session):** <goal as first stated>
**Direction changes:** <change and who authorized it | none>
**Goal status:** <achieved | partial | abandoned | redirected>
**Status evidence:** <observed result supporting the status>
```

Then six fixed-number sections. Empty ones say `none`; anchors never move.

| § | Section | Content |
|---|---------|---------|
| 1 | Outcome summary | Counts: status, verified and pending results, decisions, files, pending items. |
| 2 | Work Completed | Per topic: Problem / Done / Verification / Files. |
| 3 | Issues and Bugs Found | Issue / Cause (confirmed, hypothesis, unknown) / Resolution / Files, plus a Corrections table. |
| 4 | Decisions Made | Decision / Choice / Decided by / Evidence / Alternatives considered. |
| 5 | Files Changed | Created / Modified / Deleted, only by this session. |
| 6 | Pending Items | 6.1 In progress, 6.2 Agreed, not started (with origin), 6.3 Known issues and hypotheses. |

`examples/` holds two fictitious reports in this format: `ana-2026-10-14T171205.md`, an achieved session with a correction written by Claude Code, and `ana-2026-10-15T193040.md`, a partial one in Portuguese written by Codex.

## Testing

```bash
bash plugins/claude/session/tests/run.sh          # whole suite
bash plugins/claude/session/tests/run.sh D04 A05  # selected cases
python3 -I plugins/codex/session/tests/test_session.py   # the Codex plugin's own suite
```

The suite runs every case in temporary directories and disposable git repositories, with git configuration isolated from the user's, and uses only the fictitious fixtures in `tests/fixtures/`. Credential-shaped test values are assembled at run time. It covers the scripts and the static contracts of the skills, and, when `python3` and the Codex plugin are present, the Codex scripts and the agreement of both readers (cases A01–A12). Authorship values in these tests are injected at the scripts' real entry points; they show how the scripts handle the values, not that a platform supplies them. The model's behavior is described as cases in `skills/report/evals/evals.json` and `skills/recall/evals/evals.json`, which have no in-repo runner.

To try the development copy without installing it, start a session in a scratch repository with the plugin loaded from the checkout. `--setting-sources project,local` keeps the installed `session@pragmatic` (enabled in user settings) from loading next to it:

```bash
cd "$(mktemp -d)" && git init
claude --setting-sources project,local --plugin-dir /path/to/pragmarketplace/plugins/claude/session
```

In print mode (`claude -p`), a skill the model loads by itself needs `--allowedTools 'Skill(session:report)' 'Skill(session:recall)' 'Bash(bash:*)'`; an interactive session asks instead.

## Architecture

```
session/
├── .claude-plugin/plugin.json
├── scripts/
│   ├── lib/sessions-dir.sh      # Directory resolution; never creates anything
│   ├── lib/sensitive.sh         # Credential shapes: scan and redaction
│   ├── prepare-report.sh        # Render-time metadata for /report (read-only)
│   ├── ensure-sessions-dir.sh   # Creates the sessions directory (save step only)
│   ├── report-origin.sh         # Authorship header lines
│   ├── check-report.sh          # Pre-staging checks of a written report
│   └── commit-report.sh         # Isolated, verified commit of one report
├── skills/
│   ├── report/SKILL.md, evals/evals.json
│   └── recall/
│       ├── SKILL.md, evals/evals.json
│       └── scripts/
│           ├── recall.sh        # Subcommand routing and validation
│           └── lib/
│               ├── sessions.sh  # Listing, ordering, ID resolution
│               └── report.jq    # Report parsing and rendering
├── examples/                    # Two fictitious reports
└── tests/run.sh, fixtures/
```

The sessions directory resolves the same way for both skills: `git rev-parse --show-toplevel` of the current directory, then `$CLAUDE_PROJECT_DIR` when it names an existing directory, then the current directory. The git root comes first because the harness can set `CLAUDE_PROJECT_DIR` to `$HOME` while the user works inside an unrelated repository.

## Permissions

Pre-authorized through each skill's `allowed-tools`:

- `/report`: `Bash(bash:*)` for the helper scripts, `Bash(git log:*)` and `Bash(git show:*)` to confirm hashes seen in the session. Writing the report goes through the usual Write permission.
- `/recall`: `Bash(bash:*)` for the dispatcher, `Bash(git log:*)`, `Bash(git show:*)`, `Read`, `Grep` and `Glob` for the read-only check of pending items.

## Version History

### v3.0.0 — October 2026

Changes since 2.3.1 that affect existing users:

- **Breaking:** reports move from `.claude/sessions/` to `.harness/sessions/`, the one directory shared with the Codex `session` plugin. `/report` writes only there and `/recall` reads only there; the old directory is not read, searched or migrated. Move existing reports into the new directory to keep them in `/recall`. Writing under `.harness/` also avoids the extra approval Claude Code requires for files under `.claude/`.
- `/report` no longer triggers on "finish", "wrap up", "end session" or "summarize this session". A request in words commits only when it asks for the commit; `/report` itself still commits unless `--no-commit` is given.
- New reports drop **Branch** and **Base commit**. HEAD is recorded as **HEAD observed at generation**; **Commits generated** became **Commits made in this session**, which counts only commits whose creation the session shows (the `git log --since='1 day ago'` block is gone). New fields: **Context coverage**, **Direction changes**, **Status evidence**, a Corrections table in §3, **Decided by** in §4, and evidence and resume-condition columns in §6. The `## N.` and `### 6.N` anchors are unchanged, and reports written by earlier versions are still read.
- New authorship fields `Harness` and `Report generator`, printed by `scripts/report-origin.sh`. There is no `Model` line: no documented source gives a skill the current model, so the field could only say `unknown`; see *Authorship fields*. Readers accept `Model`, `Agent` and `Harness version` when another tool's report carries them.
- §6 subsections are now *In progress*, *Agreed, not started* and *Known issues and hypotheses*, without "must resume" or "should resume".
- One clock read yields both the header timestamp and the filename; a name collision adds `-2`, `-3`, ... instead of overwriting.
- No credential value of any kind goes into a report, including examples, fake values and placeholders shaped like a credential; `check-report.sh` flags credential shapes whether real or invented, and a flagged value is removed. Previously the skill allowed an "obviously fictitious" example and the checker let filler tokens and stand-in passwords through.
- Statements about the repository's current state come from a reading taken at generation (the *Repository state at generation* block), not from an earlier reading in the session.
- The commit runs through `commit-report.sh`: content checks before staging (`check-report.sh`: credential shapes, the project path, a worktree name, anchors, a Branch or Model line, a missing Harness), verification of the commit, the report unstaged again after a failed commit, a categorized and redacted diagnostic instead of git's full output, and at most one retry after fixing report content a hook rejected.
- `/recall` no longer creates a sessions directory. A missing directory reports no sessions; an unreadable directory or a failing helper is an error.
- `/recall resume`: `empty: true` now means only that all three subsections say `none`. A missing or unreadable §6 used to be reported as `empty: true`; it is now `pending_state: "incomplete"` with reasons. The JSON gains `pending_state`, `incomplete_reasons`, `subsection_states`, `decisions`, `goal`, `goal_status`, `status_note`, `direction_changes`, `timestamp`, `origin`, `requested_item` (with the new `--item` option), and per item `cells` and `line`. The skill checks the current state of pending items before offering them and no longer always asks which item to pick.
- `/recall last` outputs JSON excerpts per report, `origin` included, instead of file paths, so the one-line summaries need no full reads.
- `/recall list` and `filter` drop the Branch column; `filter branch:` still works for older reports and then shows it. A missing Branch no longer shifts Status into the wrong column.
- `/recall` validates its arguments (`--limit`, filter keys and values, unknown flags, extra arguments, invalid regular expressions) and honors quoted multi-word arguments. An exact session ID wins over substring matches.
- `/recall` receives its arguments through a quoted heredoc instead of `"$ARGUMENTS"` inside the `!` command. Claude Code pastes the arguments into the command text as typed, so a quote ended the string early (`grep "a b"` became three arguments) and a `$(` or backtick made the command fail the harness's permission check; both now reach the script as plain text.
- Reports written by the Codex plugin, and older reports without authorship fields, are read the same way; both readers give identical output on the same reports.

### v2.3.1 — May 2026
- Stage the brand-new report with `git add` before the partial commit, which otherwise fails with `pathspec did not match` for untracked files.

### v2.3.0 — May 2026
- `/report` commits the generated report in a single isolated `chore:` commit right after writing it. Added `--no-commit`.

### v2.1.1 — May 2026
- Fix `/recall` reporting `No sessions found` when `CLAUDE_PLUGIN_ROOT` is not exported into the `!`-block subshell: the plugin root is derived from `BASH_SOURCE`.
- Directory precedence: git toplevel, then `CLAUDE_PROJECT_DIR`, then the current directory.

### v2.1.0 — May 2026
- Added `/recall last [<n>]`. Moved directory walking, extraction, sorting, filtering and rendering into `scripts/recall.sh` and `scripts/lib/sessions.sh`. Ordering keys on the filename timestamp.

### v2.0.0 — May 2026
- **Breaking:** `/report-session` renamed to `/report`; fixed-numbered template with `none` for empty sections; filename without the trailing `Z`; Session contract block; new `/recall` skill.

### v1.0.1 — April 2026
- Output-directory resolution moved into `ensure-sessions-dir.sh`.

### v1.0.0 — April 2026
- Initial release.

## License

Property of Pragmabits.

## Contact

**Author:** Leonardo Leoncio
**Email:** leonardoleoncio96@gmail.com
