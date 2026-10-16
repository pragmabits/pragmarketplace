---
name: report
description: Write a session handoff report file under .harness/sessions/ — the session contract, verified work, decisions with who made them, and pending items with their evidence — for a later session to check against the current state. Use only when the user explicitly asks for a session report file, e.g. "/report", "write the session report", "generate a session report", "gere o relatório da sessão", "salve o relatório desta sessão". Not for "finish", "wrap up", "termine", "encerre" or a summary in the chat, which ask for neither a file nor a commit. /report commits the new file in an isolated chore commit unless --no-commit is given; a request in words commits only when it asks for the commit.
argument-hint: "[--lang xx-YY] [--no-commit] [optional report title]"
allowed-tools: Bash(bash:*) Bash(git log:*) Bash(git show:*)
---

# Session Report

Write a handoff report of this session for a later session. The report is a dated record of what was observed. The next session reads it as evidence of what was true when it was written, and checks the current state before acting on it.

## Report metadata (injected)

Resolved once, when this skill was loaded. Nothing has been created yet.

!`bash "${CLAUDE_PLUGIN_ROOT}/scripts/prepare-report.sh"`

## Arguments

```
$ARGUMENTS
```

- `--lang xx` or `--lang xx-YY` (e.g. `--lang pt-BR`): the report language. Without it, use the language the user used most in the session. Technical terms stay in English. Template headings, field labels, `none` and the goal-status values stay in English in every language, because /recall reads them.
- `--no-commit`: write the file without committing it.
- Any remaining text is a hint for the title.

## When to write and when to commit

| Request | Write the file | Commit |
|---|---|---|
| The user typed `/report` (or `/session:report`) without `--no-commit` | yes | yes, unless the user already said in this conversation not to commit |
| `--no-commit`, or the user said not to commit | yes | no: no `git add`, no commit, nothing written to the index |
| The user asked in their own words for the report and for its commit | yes | yes |
| The user asked in their own words for a report file and said nothing about committing | yes | no, and do not end by asking whether to commit |
| "finish", "wrap up", "termine", "encerre", or a summary in the chat | no | no: this skill should not have been loaded; answer in the chat and write nothing |

When you load this skill yourself for a request in words that does not ask for a commit, pass `--no-commit`. An authorization or restriction the user already gave in this conversation stands: do not ask for it again, and do not widen permissions to make the flow easier.

## What the report may claim

The report records what this session's visible conversation and tool results show. It does not record intentions, what you meant to say, or what a command would have printed.

Keep these four apart wherever the information appears, through the wording itself rather than a label on every line:

- **Done and verified**: the action ran and its result was observed. Give enough to check it: the command and its outcome, the file, the commit hash.
- **Done, verification pending**: what changed, and which relevant check has not run.
- **Proposed or inferred**: a hypothesis, suggestion or conclusion that was not confirmed.
- **Not available**: what the session does not let you determine.

Rules:

1. An intention, a prepared command, a started task, or subagent output nobody checked is not a completed action.
2. A test that was started is not a test that passed. Record the command, the result and its scope when they matter. No full logs.
3. "Docs updated" covers only the documents that were actually checked. Name them and the change; never generalize to "all documentation".
4. A cause is confirmed only with evidence. Otherwise describe the symptom and mark the cause as a hypothesis.
5. When part of the session is not visible (for example, turns replaced by a context summary), do not reconstruct its start, approvals, counts or conclusions. Say what is missing in **Context coverage**.
6. Writing the report authorizes no new work. Do not run a pending test suite, fix the project, or finish a task so the report looks better. Record the state as it is.
7. Any statement about the repository's current state — commits not pushed, a push or pull outstanding, staged or uncommitted changes, stashes, an operation in progress — comes only from the **Repository state at generation** block, read when this report is generated. A reading taken earlier in the session describes that earlier moment, and the repository can change outside the session; when such a reading matters, record it with its moment ("before the fix, `git status` showed ..."), never as the present. What the block does not see — the remote itself (nothing is fetched), pull requests, CI, other clones — is not determined: leave it out. Pending items follow the same rule, and the block precedes this report's own commit.

### Goal, direction, status

- **User goal** is the goal as the user first stated it. Later changes go in **Direction changes**, each with who authorized it.
- **Goal status** matches the goal and the observed result: `achieved`, `partial`, `abandoned` or `redirected`. Corrections along the way do not make an achieved goal partial, and ending the turn does not make a goal achieved. **Status evidence** names the result that supports the status and, for anything but `achieved`, what is missing or what replaced the goal.

### Decisions

For each material decision, say who decided and what supports that attribution: the user (and where they said it), the assistant within the requested scope, or a proposal that was not accepted. A general approval such as "go ahead" is not a decision about a detail the user was never shown. List alternatives only when they were actually raised or rejected; otherwise write `—`.

### Corrections

When something said earlier in the session turned out to be wrong and the next session needs to know, record it in §3 under Corrections: the earlier statement, the corrected fact, the consequence. Keep to what the transcript supports: "The answer had not been given yet; it was given later", not "The answer was hidden in the output". No discussion, no quoted insults, no self-justification.

### Pending items (§6)

The three subsections are historical. They say what was open when the report was written and grant no authorization to act later.

- **6.1 In progress**: work started in this session and not finished.
- **6.2 Agreed, not started**: work someone committed to, with an identifiable origin (who committed and where). An assistant suggestion the user did not accept is not a 6.2 item.
- **6.3 Known issues and hypotheses**: noted, and outside the authorized work. A hypothesis stays a hypothesis; do not promote it to a confirmed defect.

Each item says what is missing, the evidence available, and the condition for resuming it, plus a file or decision reference when there is one. Write `—` in a cell rather than inventing content. Do not list as pending anything finished or dropped during this session. An item carried over from an earlier report says so, and whether it was rechecked in this session.

### Metadata

- No Branch field, and never the worktree's name or location: not as a field, not in a paraphrase, not by mentioning the rule that leaves them out.
- Paths in the content are relative to the project. The absolute report path is only for saving the file.
- **HEAD observed at generation** is the hash from the metadata block: where HEAD was when the report was generated, not where the session started. Call a commit the session's base only with evidence of that.
- **Commits made in this session** lists only commits whose creation appears in this session's tool output (a `git commit` result showing the hash). A time window, the author or the branch is not evidence. Write `none` only when the whole session is visible and no commit was made; otherwise write `not determined` and the reason. Do not count the commit of this report.
- The working tree in the metadata block can hold work that predates the session or belongs to someone else. Attribute to this session only the changes its own tool calls show.
- **Harness** and **Report generator** describe who wrote this report, not everyone who took part in the session. Copy them exactly as **Report origin** prints them; `unknown` needs no explanation. Add no other authorship line: no **Model**, **Harness version** or **Agent**, since this integration has no documented source for them. Never state the model from your own knowledge, the system prompt, settings or a default, and do not ask the user which model is running. Other models or subagents appear in the body only when they matter to a decision, a result or a limit, and only with evidence.

### Credentials and sensitive content

A report contains no credential value of any kind: no password, token, API key, private key, connection string or URL with credentials, or authorization header, whether real or invented. Examples, fake values, test values, placeholders shaped like a credential, truncated or partly masked values and dummy assignments are values too, and none of them goes in. An example is never needed: name the credential and where it lives (the variable, the file, the service) and say what happened to it. Never show an assignment, a command line, a URL, a header or an error message that carries a value; describe it in words instead. Personal data the next session does not need stays out as well.

Review the draft for this before saving it. `check-report.sh` then flags credential shapes whether real or invented; remove what it flags rather than rewording it into another value. It and the repository's hooks are later barriers, not a replacement, and none of them finds every secret.

### Form

Keep every heading of the template. A section, subsection or table with nothing to record is replaced by `none`, and nothing more. State each fact once, in the section it belongs to, instead of repeating the same history in the summary, the issues, the decisions and the pending items.

## Template

Section numbers are fixed. Do not renumber, rename the `## N.` and `### 6.N` anchors, or drop a section.

```markdown
# Session Report: <concise title naming the session's main topics>

**Timestamp (UTC):** <Timestamp from the metadata block>
**Git user:** <Git user from the metadata block>
**Harness:** <from Report origin>
**Report generator:** <from Report origin>
**HEAD observed at generation:** `<HEAD hash from the metadata block>`
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
| Results verified | <count of §2 topics whose Verification shows an observed result> |
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

`\|` inside a table cell is a literal pipe. In the angle-bracket placeholders, `|` separates alternatives; pick one.

## Steps

1. Draft the report from the conversation, following *What the report may claim* and the template. Copy the Timestamp, Git user and HEAD hash from the metadata block exactly.
2. Review the draft for sensitive content and for claims the conversation does not support.
3. Run **Create the directory**, then **Report origin**, from the helper commands in the metadata block. Copy the `**...**` lines Report origin prints into the header; the `#` lines only explain where the values came from.
4. Write the report with the Write tool to the **Report path**. If a file already exists at that path, stop and reload this skill to get a new name. Never overwrite a report.
5. Run **Check the report**. Fix each finding in the report only, then check again. A `sensitive` finding never stays in the file: remove the value, and if the line is still flagged, delete the line. After two rounds with other findings left, keep the file, skip the commit, and tell the user what remains.
6. If the commit is authorized (see *When to write and when to commit*), run **Commit the report** in one Bash call and handle its result as below. Otherwise stop after this step.
7. Tell the user in one or two lines: the report path relative to the project and, if a commit was attempted, its result, stated separately from the fact that the file was saved.

## Commit results

`commit-report.sh` stages only the report, commits it with `git commit --only`, checks that the new commit holds exactly that file on top of the previous HEAD, and leaves every other index entry and file alone. It respects the repository's hooks, signing and identity, and makes one attempt per run. Its output starts with `result:`.

| result | Meaning | What to do |
|---|---|---|
| `committed` | The report alone was committed and verified | Report the hash. |
| `already-committed` | An earlier run already committed this exact file | Report the hash. Never commit it a second time. |
| `check-failed` | The report has findings; nothing was staged | Fix only the flagged lines, check again, then run the commit command once more. |
| `commit-failed`, category `rejected` | A hook refused the commit; the report was unstaged | If the diagnostic points at content of the report (a secret pattern, a marker, a format rule), fix only that content, check again, and retry once. If the cause is not identifiable, or the retry is rejected too, stop. |
| `commit-failed`, any other category | Identity, signing, a lock, an ignored path, an operation in progress or the filesystem blocks the commit | Do not retry and do not touch configuration, identity, signing or hooks. Tell the user the file is saved and what blocks the commit. |
| `add-failed` | `git add` failed; nothing was committed | Skip the commit. Report the cause. |
| `refused` | Not a git work tree, an operation in progress, or the path is already committed | Report the reason. |
| `committed-unverified` | A commit exists, but verification found a problem | Report it as such. Nothing was undone; never commit it a second time. |

Never use `--no-verify`, `-c` overrides, `--no-gpg-sign`, another identity, `git reset`, `git restore` or `git stash`. A rejected report does not justify changing the project's code, weakening a hook, or rewriting older reports. If the output says `staged: unknown`, tell the user the staged version could not be confirmed removed. Do not promise that git objects created by an earlier `git add` are gone.

When a step fails, give the user the useful part of the diagnostic in a line or two: the category and what the hook or git objected to, with any sensitive value left out. Keep what git printed apart from your reading of it, and do not paste the whole output.
