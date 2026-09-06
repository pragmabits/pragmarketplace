# pragma

Standing working directives for Claude Code sessions.

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

## Install

```bash
claude plugin add pragmabits/pragmarketplace --plugin pragma
```

Then enable it — `"pragma@pragmatic": true` in `settings.json`, or `/plugin`.

## Verify it is working

```bash
bash plugins/claude/pragma/hooks/session-start.sh | jq -r '.hookSpecificOutput.additionalContext'
```

Prints the instruction text. The script exits non-zero if `instructions.md` is
unreadable or `jq` is missing, rather than emitting nothing — a hook that quietly
produces no context is indistinguishable from a plugin that was never enabled.

## Requires

`jq`, as the other hooks in this marketplace do.
