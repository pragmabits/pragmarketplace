---
name: report
description: Write a session handoff report file under .harness/sessions/ — the session contract, verified work, decisions with who made them, and pending items with their evidence — for a later session, in Codex or another tool, to check against the current state. Use only when the user explicitly asks for a session report file, e.g. "$report", "write the session report", "generate a session report", "gere o relatório da sessão". Not for "finish", "wrap up", "termine", "encerre" or a summary in the chat, which do not ask for a file.
---

# Session Report

Write a handoff report of this session. The report is a dated record of what was observed; the next session, in Codex or in another tool that reads the same contract, treats it as evidence of what was true when it was written and checks the current state before acting on it.

Reports live in `<project-root>/.harness/sessions/`, shared by every tool that writes this format. Never write them anywhere else.

This skill writes the file and does not commit it. Commit it only if the user asks, with the repository's own hooks and identity, staging only the report.

## Prepare

Run from the project, with the path resolved relative to this skill:

```bash
python3 <plugin-root>/scripts/session_report.py prepare [--lang xx-YY] [title hint]
```

It creates `.harness/sessions/` if needed and prints JSON. Use its values as facts:

- `output_path`: write the report there, with the normal file-editing tool. If a file appears there before you write, run prepare again; never overwrite a report.
- `timestamp_utc`, `git_user`, `head_observed`: copy them into the header.
- `origin.lines`: copy these lines into the header exactly. `origin.sources` says where each value came from; it does not go in the report.
- `repository_state`: the repository as it is now. Any statement about its current state — commits not pushed, a push or pull outstanding, staged or uncommitted changes, stashes, an operation in progress — comes only from here. A reading taken earlier in the session describes that earlier moment, and the repository can change outside the session; record such a reading with its moment, never as the present. What this does not see (the remote itself, pull requests, CI, other clones) is not determined: leave it out.
- `status_short`: context only. It can hold work that predates this session or belongs to someone else.
- `language`: when set, the report language. Otherwise the language the user used most. Headings, field labels, `none` and the goal-status values stay in English in every language.

## What the report may claim

The report records what this session's visible conversation and tool results show, not intentions or what a command would have printed. Keep these apart through the wording:

- **Done and verified**: the action ran and its result was observed, with enough to check it.
- **Done, verification pending**: what changed, and which check has not run.
- **Proposed or inferred**: a hypothesis or suggestion not confirmed.
- **Not available**: what the session does not let you determine.

1. An intention, a prepared command, a started task or unchecked subagent output is not a completed action.
2. A started test is not a passed test. Record command, result and scope when they matter; no full logs.
3. "Docs updated" names the documents actually checked; never "all documentation".
4. A cause is confirmed only with evidence; otherwise describe the symptom and mark the cause as a hypothesis.
5. When part of the session is not visible, do not reconstruct it; say what is missing in **Context coverage**.
6. Writing the report authorizes no new work.

**Goal and status.** User goal is the goal as first stated; later changes go in Direction changes with who authorized them. Goal status matches the goal and the observed result; corrections along the way do not make an achieved goal partial, and ending the turn does not make it achieved.

**Decisions.** Say who decided and what supports that: the user (where), the assistant within scope, or a proposal not accepted. List alternatives only when they were actually raised.

**Corrections.** Something said earlier that turned out wrong, and that the next session needs to know, goes in §3 Corrections: earlier statement, corrected fact, consequence. No discussion, no quoted insults.

**Pending items.** Historical, and no authorization to act later. 6.1 work started and not finished; 6.2 work someone committed to, with its origin (an assistant suggestion the user did not accept is not 6.2); 6.3 known issues and hypotheses, outside the authorized work. Each item says what is missing, the evidence, and the condition to resume; `—` rather than invented content.

**Metadata.** No Branch field, and never the worktree's name or location. Paths relative to the project. Head observed is not the session's base. Commits made in this session lists only commits whose creation appears in this session's tool output; `none` only when the whole session is visible; otherwise `not determined` and why. The authorship lines describe who wrote this report, not everyone who took part. Copy `origin.lines` and add no other authorship line — no Model, Harness version or Agent, for lack of a documented source. Never state the model from your own knowledge, settings or a default, and do not ask the user which model is running.

**Credentials and sensitive content.** No credential value of any kind: no password, token, API key, private key, connection string or URL with credentials, or authorization header, whether real or invented. Examples, fake values, test values, placeholders shaped like a credential, truncated or partly masked values and dummy assignments are values too, and none goes in. An example is never needed: name the credential and where it lives, and say what happened to it; describe assignments, command lines, URLs, headers and error messages in words instead of showing them. No personal data the next session does not need.

**Form.** Keep every heading. Empty sections, subsections and tables say `none` and nothing more. State each fact once.

## Template

Section numbers are fixed; do not renumber or drop a section.

```markdown
# Session Report: <concise title naming the session's main topics>

**Timestamp (UTC):** <timestamp_utc>
**Git user:** <git_user>
<origin.lines, one per line>
**HEAD observed at generation:** `<head_observed>`
**Commits made in this session:** <short hashes | none | not determined — reason>
**Context coverage:** <full | partial — what is not visible>

---

## Session contract

**User goal (entering session):** <the goal as the user first stated it>
**Direction changes:** <each change and who authorized it | none>
**Goal status:** <achieved | partial | abandoned | redirected>
**Status evidence:** <the observed result that supports the status; if not achieved, what is missing or what replaced the goal>

---

## 1. Outcome summary

| Field | Value |
|-------|-------|
| Goal status | <same value as above> |
| Results verified | <count> |
| Results pending verification | <count> |
| Decisions recorded | <count> |
| Files created | <count> |
| Files modified | <count> |
| Files deleted | <count> |
| In-progress items | <count> |
| Agreed items | <count> |
| Known issues and hypotheses | <count> |

---

## 2. Work Completed

### 2.1 <Topic>

**Problem:** <what needed doing>
**Done:** <what was changed>
**Verification:** <the check and its observed result, with its scope | pending: the relevant check not yet run>
**Files:** `<relative/path>`, ...

---

## 3. Issues and Bugs Found

| Issue | Cause | Resolution | Files |
|-------|-------|------------|-------|
| <symptom> | <confirmed: ... (evidence) \| hypothesis: ... \| unknown> | <fixed, verified by ... \| fixed, not verified \| open, see §6.N> | <paths> |

### Corrections

| Earlier statement | Corrected fact | Consequence |
|-------------------|----------------|-------------|
| <what was said> | <what is true, per the transcript> | <what the next session needs to know> |

---

## 4. Decisions Made

| Decision | Choice | Decided by | Evidence | Alternatives considered |
|----------|--------|------------|----------|-------------------------|
| <what> | <chosen> | <user, where \| assistant, within scope \| proposed, not accepted> | <what supports it> | <only those actually raised \| —> |

---

## 5. Files Changed

### Created
- `<relative/path>` — <purpose>

### Modified
- `<relative/path>` — <what changed>

### Deleted
- `<relative/path>` — <why>

---

## 6. Pending Items

### 6.1 In progress

| Item | What is missing | Evidence | Resume when | Refs |
|------|-----------------|----------|-------------|------|
| <task> | <what remains> | <what shows its state> | <condition> | <path or decision> |

### 6.2 Agreed, not started

| Item | Origin | Resume when | Refs |
|------|--------|-------------|------|
| <task> | <who committed to it, and where> | <condition> | <path or decision> |

### 6.3 Known issues and hypotheses

| Issue | Status | Evidence | Location |
|-------|--------|----------|----------|
| <issue> | <confirmed \| hypothesis> | <what supports it, or what is missing> | <path or component> |
```

`\|` inside a table cell is a literal pipe. In the placeholders, `|` separates alternatives; pick one.

## Finish

Tell the user in one or two lines where the report was written, relative to the project. Do not end by asking whether to commit.
