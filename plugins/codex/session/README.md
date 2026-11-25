# Session Handoff for Codex

Session handoff reports and recall for Codex, in the same format and directory as the Claude Code `session` plugin, so a report written by one tool can be read and resumed by the other.

## Storage

Reports live in one directory per project:

```text
<project-root>/.harness/sessions/
```

It is shared with the Claude Code plugin and any other tool that follows the same report contract. All reports of a project sit there, with no subdirectory per tool, model or user.

- `session_report.py prepare` creates the directory when a report is about to be written. `session_recall.py` never creates anything; a missing directory means no reports there.
- The former location, `.sessions/` (and `.claude/sessions/` for the Claude plugin before 3.0.0), is not read and not migrated. To keep old reports, move the files into `.harness/sessions/` unchanged; their content is still read.
- Nothing changes `.gitignore`, commit policy or project settings.

## Skills

- `report` writes and validates a handoff. An explicit `$report` requests an isolated commit. Add `--no-commit` to keep only the file. A request in words writes only the file unless it also asks for the commit.
- `recall` combines the three newest reports by default. Use `--me` or `--user <name>` to select the report author, or use one of the five explicit subcommands.

```text
$report
$report --no-commit
$report --lang pt-BR codex git plugin port
$recall
$recall --me
$recall list --limit 10
$recall filter status:partial since:2026-10-01
$recall grep "marketplace"
$recall resume --item "convert deploy/settings.ini"
$recall last 3
```

## Scripts

```bash
python3 -B -I plugins/codex/session/scripts/session_report.py prepare [--lang xx-YY] [title hint]
python3 -B -I plugins/codex/session/scripts/session_report.py check <report-path>
python3 plugins/codex/session/scripts/session_recall.py --after-report [--me | --user <name>]
python3 plugins/codex/session/scripts/session_recall.py list [--limit N]
python3 plugins/codex/session/scripts/session_recall.py filter <key:value>... [--limit N]
python3 plugins/codex/session/scripts/session_recall.py grep <pattern> [--limit N]
python3 plugins/codex/session/scripts/session_recall.py resume [<session-id>] [--item <text>]
python3 plugins/codex/session/scripts/session_recall.py last [<n>]
```

`prepare` prints JSON: the output path (one clock read for the header and the filename; a taken name gets `-2`, `-3`, ..., including names written by the other tool), the git user, HEAD as observed (not the session's base), the working tree as context only, and the authorship lines. It no longer reports a branch or the commits of the last day: neither is evidence of what the session did.

The two readers agree on the common lookup fields tested by the Claude
session suite's A05 case. `resume` and `last` print an explicit
`pending_state` of `items`, `none`, or `incomplete` with reasons.
`--after-report` asks the local Codex App Server for later user activity in
the repository and its worktrees. It returns dates and counts. When the
history is unavailable or incomplete, recall still returns the reports and
describes the gap. The ordinary CLI lookups use only the report files.
If the sandbox prevents the App Server from opening the local profile
database, the skill can retry that lookup through Codex's per-command approval.

## Report contract

The format is the Claude Code plugin's: fixed anchors (`Session contract`, `## 1.` to `## 6.`, `### 6.1` to `### 6.3`), `none` for empty sections, `\|` as a literal pipe in table cells, no Branch field. The full template and writing rules are in `skills/report/SKILL.md`; `plugins/claude/session/README.md` describes the fields.

§6.3 is *Known defects*. Record project failures or suspected failures with Status `confirmed` or `suspected`. A check the session's own work still needs goes in §6.1. Proposals, questions and accepted choices go in §4. Older reports may carry the heading *Known issues and hypotheses*. Recall reads and sorts those items, and the checker applies the current contract to new reports.

### Authorship fields

They describe who wrote this report, not everyone who took part in the session.

| Field | In this plugin |
|---|---|
| `Harness` | `codex`: the script belongs to the Codex integration and runs from its report skill |
| `Report generator` | `session/codex <version>`, from this plugin's manifest |

There is no `Model` line. Codex documents no way for a script to learn the model of the current turn: the `CODEX_*` variables it sets in its shells (`CODEX_THREAD_ID`, `CODEX_VERSION`) are not in the official documentation; the session rollout files are undocumented, and their `turn_context` records the requested model, which a server-side reroute can differ from; configured defaults are not the model of this execution. The field could only ever say `unknown`, so it is left out, as are `Harness version` and `Agent`.

Readers still accept those fields when a report from another tool carries them: a `Model` value is kept as a confirmed identifier, `alias: <value>` or `unknown`, and a report without it reads as `absent`. Any harness or model identifier is accepted as data.

## Tests

```bash
python3 -I plugins/codex/session/tests/test_session.py
```

Temporary git repositories with isolated git configuration and fictitious reports.
