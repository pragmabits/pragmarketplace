# pragma

Standing working directives for Claude Code sessions, and a review gate that
holds the agent to them at two moments: before it asks the user a question, and
when it ends a turn.

A `#pragma` is a directive that changes behaviour without being called. This
plugin is the same idea for a session: `hooks/session-start.sh` emits
`instructions.md` as session context on startup, `/clear` and compaction, so the
rules are in force before the first decision rather than waiting to be invoked.

## Why a hook and not a skill or an output style

A skill has to be invoked, and a rule about how to answer must already be in
force when the answer is composed. An output style carries the content but needs
`outputStyle` selected per machine, which is a second setting to replicate.
Enabling the plugin is the only step a hook needs.

## What it ships

Four rules. See `instructions.md`.

**Verify before conceding.** When the user says something is wrong, check, then
report what the check found — fix it if they are right, say they are wrong if
they are not. Conceding an error you did not make is ego-polishing by self-blame:
once anything will be conceded, a real error is indistinguishable from a conceded
one, and every agreement stops carrying information.

**A complaint is not a work order.** A description of something irritating is a
question, not a request to build a tool for it.

**A dominated option is not an option.** Offering an alternative that loses with
no compensating trade asserts a decision exists where none does. A two-column
comparison makes that claim by its shape.

**Verify before claiming.** No result reported that was not run, and no work
reported as done while a known inconsistency in it is open.

Further standing directives belong in the same file rather than in a second one.

## Review gate

Instructions alone leave the user to notice what was skipped. The gate checks
two moments against the user's request and the evidence in the transcript, and
returns a proven pending obligation to the agent, so the user does not have to
ask for it again.

| Moment | Hook | What it catches |
|---|---|---|
| Before `AskUserQuestion` | `PreToolUse` | a question the user already answered; an offer to do a step already asked for; a choice the user's constraints already settle; a question that presumes an explanation never shown |
| Turn end | `Stop` | requested work left as an offer or a command for the user; a verification the task called for, skipped; a started or inconclusive test reported as passed; a user question left unanswered or falsely claimed as answered; completion declared over a known failure in scope; a stale pending item; temporary resources left without a decision; an answer only internal codes explain |

A refused question or a blocked turn end reaches the agent as a message that
starts with `pragma question review` or `pragma stop review`, with the finding,
an excerpt of the evidence and the corrective action. The agent resolves it, or
disputes it with evidence. In normal operation the user sees nothing from the
gate.

How it works:

- `gate/hook.py` is the Claude Code adapter. `UserPromptSubmit` opens a request
  (keyed by the hook's `prompt_id`); `PreToolUse` on `AskUserQuestion` and
  `Stop` build an evidence package and ask for a verdict.
- `gate/transcript.py` keeps an incremental index of the transcript —
  references and byte offsets only, never text — and reads back what a package
  needs. The agent's reasoning, a thinking block with no text, is never
  included. A thinking block with text is narration, which the screen shows as
  a summary: it enters the package as an `assistant` item marked
  `summarized`. At a turn end, Claude Code writes
  the final response, and any of the turn's last steps still unwritten, a
  fraction of a second after `Stop` starts; the review waits up to
  `stop_wait_s` for the transcript to hold the final response. If it does not
  arrive, the package says the last steps may be missing, and their absence is
  not treated as proven.
- `gate/display.py` covers what the transcript lacks when a question is
  reviewed. Claude Code writes the transcript asynchronously, and the message
  that holds the question — with the text the agent wrote right before it — is
  usually not in the file when its `PreToolUse` runs. A `MessageDisplay` hook
  keeps the lines shown on screen, and the question review adds the ones the
  transcript does not hold yet to the package, after waiting up to
  `display_wait_s` for the end of the message. Without that capture, the
  package says the text may be missing, and a missing explanation is not
  treated as proven. Narration never reaches `MessageDisplay`: in a session
  that shows narration, when the transcript does not hold the question's
  message yet and nothing was captured, the package says narration shown with
  the question may be missing.
- `gate/evidence.py` builds the package (64 KiB by default): the request and
  the files attached to it, the user's earlier messages and answers, this
  turn's tool calls and results, the question or the final response, and the
  git status, environment and date Claude Code showed the agent. Cuts keep the
  head and the tail of a text and say how much was cut; whatever is left out
  is listed in `omitted`.
- `gate/evaluator.py` runs one `claude -p` per evaluation in a fresh empty
  directory, with `--safe-mode` (no plugins, hooks, MCP servers or CLAUDE.md),
  `--tools ""`, `--strict-mcp-config`, `--disallowedTools "mcp__*"`,
  `--no-session-persistence` and `--json-schema`, on the CLI's own
  authentication. The reviewer only judges: it cannot edit, run or delete
  anything. Its reply is validated — verdict, categories, and every cited
  reference must exist in the package.
- `gate/core.py` applies the budgets and the cache. The criteria are in
  `gate/rubric/`.

Limits, per user request and adjustable:

- two independent budgets, questions and turn ends, each with 3 evaluations
  and 2 returns; answers to questions, tool calls and continuations after a
  return do not reset them, only a new prompt does;
- 30 s per evaluation, after which the reviewer's process group is killed;
- one evaluation at a time per session; an identical package reuses the
  previous verdict without a call;
- a failed call (timeout, error, invalid reply) still counts as an evaluation.

Any failure of the gate lets the moment through and is never recorded as
approval: timeouts, reviewer errors, invalid replies, an `unknown` verdict, a
missing transcript, a request the transcript does not hold yet (judging then
would mean judging against an earlier request) and exhausted budgets each
produce, at most once per request, a one-line `systemMessage` to the user with
the reason and the log path.

What it does not cover:

- Subagents are not reviewed directly; the main turn end judges what they
  returned.
- `Stop` runs after the response is shown. A blocked turn end makes the agent
  continue; it does not hide what was already displayed.
- The gate controls questions and turn ends, not every action before them.
  Permissions stay necessary.
- The verdict is a model's judgment and can be wrong in either direction.
- The capture needs a Claude Code that delivers `MessageDisplay`. Without it,
  a question that presumes an explanation is let through with an inconclusive
  verdict instead of being returned. The same holds, in a session that shows
  narration, for a question asked before the transcript holds its message:
  narration cannot be captured.
- `AskUserQuestion` does not exist in `claude -p`, so in print mode only turn
  ends are reviewed. A session without a saved transcript (for example
  `--no-session-persistence`) is not reviewed.

### Configuration

Optional. `~/.config/pragma/gate.json` (or `$XDG_CONFIG_HOME/pragma/gate.json`,
or the path in `PRAGMA_GATE_CONFIG`) overrides any of:

```json
{
  "enabled": true,
  "model": null,
  "effort": "low",
  "timeout_s": 30,
  "budgets": {"question": {"evaluations": 3, "returns": 2},
              "stop": {"evaluations": 3, "returns": 2}},
  "package_limit_bytes": 65536,
  "display_wait_s": 1.5,
  "stop_wait_s": 2,
  "retention_days": 14
}
```

`model: null` uses the model the session itself is running, read from the
transcript; the log records the model actually used.

### State

`~/.local/state/pragma/gate/` (or `$XDG_STATE_HOME/pragma/gate/`), outside any
project: per session, the requests with their counters and cached verdicts,
the transcript index, and `log.jsonl` with one line per decision — outcome,
categories and references, durations and token usage, never message text.
Sessions untouched for 14 days are removed at session start.

The one file with message text is `shown.json`, the text shown on screen that
the transcript did not hold yet. It never outlives the request it belongs to:
a new prompt and every session start empty it, every review drops what the
transcript already holds, and it keeps at most the 6 newest messages, each cut
to 6,000 characters (head and tail).

### Turning the gate off

Only the gate; the four directives stay:

```bash
mkdir -p ~/.config/pragma && echo '{"enabled": false}' > ~/.config/pragma/gate.json
```

It takes effect at the next hook call, without a restart; the next session
start also stops loading the gate's contract text. `PRAGMA_GATE=off` in the
environment does the same for one process tree. Delete the file, or set
`"enabled": true`, to turn it back on.

## Install

```bash
claude plugin marketplace add pragmabits/pragmarketplace
claude plugin install pragma@pragmatic
```

An existing install picks up a new version with
`claude plugin marketplace update pragmatic` followed by
`claude plugin update pragma@pragmatic --scope user` — and `--scope project`,
run from the project, for each project that also enabled it there. Restart the
session afterwards.

## Verify it is working

```bash
bash plugins/claude/pragma/hooks/session-start.sh | jq -r '.hookSpecificOutput.additionalContext'
```

Prints the instruction text and, while the gate is on, its contract. The script
exits non-zero if `instructions.md` is unreadable or `jq` is missing, rather
than emitting nothing — a hook that quietly produces no context is
indistinguishable from a plugin that was never enabled.

The gate's decisions for the current session are in
`~/.local/state/pragma/gate/sessions/<session id>/log.jsonl`.

## Tests

```bash
# Deterministic: budgets, cache, concurrency, isolation, failures, package
python3 -B -I plugins/claude/pragma/tests/test_gate.py

# Behavior: every scenario judged by the real reviewer (calls the model)
python3 -B -I plugins/claude/pragma/tests/behavior.py --repeat 3

# End to end with a real agent, in throwaway projects (calls the model).
# With --plugin-dir: this checkout, for the session only. Without: the installed plugin.
python3 -B -I plugins/claude/pragma/tests/demo.py --base /tmp/pragma-demo \
  --plugin-dir plugins/claude/pragma --state-dir /tmp/pragma-demo/state
```

## Requires

`jq` and `python3` (standard library only), and the `claude` CLI on `PATH`,
authenticated, for the gate's reviewer.
