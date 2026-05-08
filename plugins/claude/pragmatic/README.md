# Pragmatic Plugin

A Claude Code output style for evidence-driven engineering: the user owns every material decision, Claude owns procedural investigation.

## Overview

The `pragmatic` plugin ships one output style — **`pragmatic-autonomy`** — that reshapes how Claude collaborates inside a session. It does **not** provide a slash command. Activate the style and Claude immediately starts behaving differently:

- Investigates freely (reads, searches, sandboxed execution).
- Stops at every **material** fork (writes, behavior changes, strategy choices, destructive ops, anything not settled by repo evidence) and uses `AskUserQuestion`.
- Batches related material decisions into a single question per turn instead of asking one at a time.
- Cites evidence for every material claim and refuses to bluff verification.
- Announces material decisions in-line as they happen — short for obvious picks, a compact block for trade-offs.
- Defaults to terse, filler-free responses; concept explanations only get extra room when a term is genuinely new in the session.

The style sets `keep-coding-instructions: true`, so it layers on top of Claude Code's built-in coding guidance rather than replacing it.

## Prerequisites

None. The style is a single Markdown file consumed by Claude Code's output-style system — no scripts, hooks, agents, or external tools.

## Installation

From the marketplace:

```bash
claude plugin add pragmabits/pragmarketplace --plugin pragmatic
```

## Activation

Activate the style with `/config` and pick **`pragmatic:pragmatic-autonomy`**, or set it directly in `~/.claude/settings.json`:

```json
{
  "outputStyle": "pragmatic:pragmatic-autonomy"
}
```

The style stays active until you change it; switching back to the default style restores Claude's standard behavior.

## What the style enforces

| Section | Rule |
|---------|------|
| Core principle | Procedural autonomy is allowed; material decisions require `AskUserQuestion`. |
| Definitions | Explicit lists of what counts as **material** vs **procedural**. Any write to a tracked file or non-sandboxed execution is material. |
| Gating rules | No material decisions without a question unless evidence or explicit instruction settles it. Missing evidence is not permission to choose. |
| Batching | Investigate procedurally → identify all material forks → group into one `AskUserQuestion` call → proceed only after the batch is answered. Re-batch if new forks emerge. |
| Question format | One material decision per question, materially distinct options, final option always exactly **"Elaborate more on the options and ask me again"**. |
| In-line decision announcements | Obvious decisions get a one-line `Decision: … — basis`; non-obvious ones get a `Decision / Basis / Effect` block. No running ledger across turns. |
| Evidence policy | Every material claim states either the supporting evidence, that it's blocked, or that it depends on user preference. Speculation is never framed as fact. |
| Conflict handling | State the conflict, state what is blocked, ask the user — never resolve unilaterally. |
| Verbosity | Short complete sentences. No restatement, no preamble, no hedging adverbs, no closing summaries. |
| Tone | Flat, technical, direct. Push back on unclear or contradictory requests instead of accommodating them. |

## When to use it

Best for sessions where:

- The user wants tight control over what gets written, refactored, or restructured.
- Multiple plausible implementation strategies exist and the user wants the trade-offs surfaced as questions, not absorbed silently.
- Verbose, exploratory responses are actively unwanted — short, decision-oriented updates are preferred.
- Evidence-traceable answers matter (paths, output, citations) and bluffed verification would be costly.

Less useful for one-off "just do it" tasks where every choice is obvious from context — the style still works but adds question overhead with no decision content to gate.

## Architecture

```
pragmatic/
├── .claude-plugin/
│   └── plugin.json
└── styles/
    └── pragmatic-autonomy.md   # Output style with frontmatter and rule sections
```

The plugin manifest registers the `styles/` directory via `"outputStyles": "./styles/"`. Claude Code auto-discovers every `*.md` file in that directory as an available output style.

## Version History

### v1.0.1 — May 2026
- Shortened the style description.
- Trimmed the opening prose of the style.
- Removed the closing paragraph of the *In-line decision announcements* section.
- Pruned an unused keyword from the manifest.

### v1.0.0 — May 2026
- Initial release. `pragmatic-autonomy` output style covering material/procedural gating, `AskUserQuestion` batching, evidence policy, in-line decision announcements, conflict handling, terse verbosity rules, and language-following.

## License

Property of Pragmabits.

## Contact

**Author:** Leonardo Leoncio
**Email:** leonardoleoncio96@gmail.com
