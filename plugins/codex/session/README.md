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

- `report`: writes a report for the current session when the user explicitly asks for a report file. It does not commit.
- `recall`: `list`, `filter`, `grep`, `last` and `resume` over `.harness/sessions/`. Read-only.

```text
$report
$report --lang pt-BR codex git plugin port
$recall list --limit 10
$recall filter status:partial since:2026-10-01
$recall grep "marketplace"
$recall resume --item "convert deploy/settings.ini"
$recall last 3
```

## Scripts

```bash
python3 plugins/codex/session/scripts/session_report.py prepare [--lang xx-YY] [title hint]
python3 plugins/codex/session/scripts/session_recall.py list [--limit N]
python3 plugins/codex/session/scripts/session_recall.py filter <key:value>... [--limit N]
python3 plugins/codex/session/scripts/session_recall.py grep <pattern> [--limit N]
python3 plugins/codex/session/scripts/session_recall.py resume [<session-id>] [--item <text>]
python3 plugins/codex/session/scripts/session_recall.py last [<n>]
```

`prepare` prints JSON: the output path (one clock read for the header and the filename; a taken name gets `-2`, `-3`, ..., including names written by the other tool), the git user, HEAD as observed (not the session's base), the working tree as context only, and the authorship lines. It no longer reports a branch or the commits of the last day: neither is evidence of what the session did.

`session_recall.py` follows the shared contract the same way the Claude plugin's reader does; on the same reports both give identical output (checked by `plugins/claude/session/tests/run.sh`, case A05). `resume` and `last` print JSON with an explicit `pending_state` (`items`, `none` — all three subsections say `none` —, or `incomplete`, with reasons); `empty: true` appears only for `none`.

## Report contract

The format is the Claude Code plugin's: fixed anchors (`Session contract`, `## 1.` to `## 6.`, `### 6.1` to `### 6.3`), `none` for empty sections, `\|` as a literal pipe in table cells, no Branch field. The full template and writing rules are in `skills/report/SKILL.md`; `plugins/claude/session/README.md` describes the fields.

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
