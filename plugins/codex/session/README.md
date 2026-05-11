# Session Handoff for Codex

Agent-agnostic session lifecycle helpers exposed as a Codex plugin.

This plugin ports the Claude session plugin's core idea without making the session store belong to any vendor, product, or agent runtime. New reports are written to the user project's root-level session directory:

```text
<repo-root>/.sessions/
```

## Skills

- `report` - writes a fixed-structure handoff report for the current session.
- `recall` - lists, filters, searches, summarizes, and resumes reports from `.sessions/`.

## Usage

```text
$report
$report --lang pt-BR codex git plugin port
$recall list --limit 10
$recall filter branch:main status:partial
$recall grep "marketplace"
$recall resume
$recall last 3
```

## Native Codex Design

The Claude plugin used render-time shell blocks. This version uses explicit local scripts:

- `scripts/session_report.py prepare` gathers git metadata, creates `.sessions/`, and returns the exact report path as JSON.
- `scripts/session_recall.py` performs deterministic listing, filtering, searching, ID resolution, and pending-item extraction.

The agent writes the actual report body because only the agent has the full conversation context.

## Report Contract

Every report has stable sections:

- Session contract
- `1. Outcome summary`
- `2. Work Completed`
- `3. Issues and Bugs Found`
- `4. Decisions Made`
- `5. Files Changed`
- `6. Pending Items`

Empty sections are rendered as `none` so future agents can rely on stable anchors.

## Recall Commands

```bash
python3 plugins/codex/session/scripts/session_recall.py list --limit 10
python3 plugins/codex/session/scripts/session_recall.py filter branch:main since:2026-05-01
python3 plugins/codex/session/scripts/session_recall.py grep "auth middleware"
python3 plugins/codex/session/scripts/session_recall.py resume
python3 plugins/codex/session/scripts/session_recall.py last 3
```

`grep` is literal by default. Prefix with `re:` for regex mode.
