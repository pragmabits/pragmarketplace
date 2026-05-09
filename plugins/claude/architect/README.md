# architect

A Claude Code plugin for **deciding whether sub-agents and loops are worth their cost** — and scaffolding them properly when they are. Surveys existing projects and existing capabilities before writing anything.

Built on a simple premise: most multi-agent designs are architectural theater. This plugin pushes back when they are, helps you build the minimum viable architecture when they aren't, and — before any of that — checks whether something already in your session or installed plugins already does the job.

This plugin is distributed through the **pragmatic** marketplace.

## What's in it

### Slash commands

**Guided entry point**

- **`/architect <task>`** — Walks you through the full flow: triage → confirm → scaffold → next step. Pauses at each branch and lets you steer.

**Direct commands**

- **`/triage <task>`** — Recommends the minimum viable architecture for a task. Walks the gradient: *capability check → single execution → tools → bounded loop → one specialist → multi-agent*. Defaults to the lowest tier that works.
- **`/loop-contract <description>`** — Generates a bounded loop, but only after confirming you have a stopping criterion, an iteration cap, and a progress evaluator. Refuses to scaffold a roulette wheel.
- **`/subagent-contract <description>`** — Generates a sub-agent with a one-sentence role, closed input/output contract, and explicit guardrails. Refuses if the role is vague or if an existing capability covers it.
- **`/coordination-audit`** — Audits an existing setup. Runs structural validation first (via script), then judgment-level checks. Surfaces conflicts between plugin principles and project conventions.

### Auto-invoked skills

- **`capability-radar`** — Runs as Step 0 for every scaffold or recommendation command. Checks in-session tools, skills, sub-agents, slash commands, and installed pragmatic plugins for substantial fit before generating new infrastructure. **Existing capabilities outrank every tier of generation.**
- **`project-survey`** — Detects stack, paths, off-limits scopes, and existing project infrastructure. Persists findings to `.architect.json`.
- **`theater-check`** — Triggers when you describe multi-agent designs. Runs four filter questions starting with the capability check.
- **`loop-forensics`** — Triggers when a loop misbehaves. Diagnoses the failure mode (via script-detected patterns) and prescribes a fix.

### Sub-agent

- **`verifier-judge`** — Returns PASS/FAIL with evidence given an objective criterion. Use it as the verification step inside loops.

### Templates

- **`templates/test-fixing-loop.md`** — Worked reference for the canonical case where sub-agents + loops pay off.

### Scripts

The mechanical layer. Stdlib Python 3.8+, JSON in/out, all read-only. See `scripts/README.md` for the full catalog.

- **`survey.py`** — repo discovery
- **`validate.py`** — structural validation of generated scaffolds
- **`loop_log_analyze.py`** — pattern detection in loop logs
- **`check_staleness.py`** — verifies `.architect.json` consistency
- **`marketplace_inventory.py`** — lists installed plugins from the pragmatic marketplace and their components

## The capability radar

The plugin's central addition over generic scaffolding tooling. Before any command produces a recommendation or generates a file, it checks:

1. **In-session capabilities** — tools available in this conversation, active skills, sub-agents from `.claude/agents/`, slash commands, MCP server tools
2. **Installed pragmatic plugins** — every plugin installed from the pragmatic marketplace and the components it contributes

If something substantially fits the user's task — meaning, *if you invoked it directly you'd get most of what you asked for* — the plugin recommends using it instead of generating new infrastructure. The "tier 0" answer is *don't generate anything because it already exists*.

The radar is conservative on purpose. False negatives (proceeding with a normal scaffold when a capability would have fit) are recoverable. False positives (pushing the user toward the wrong tool) are worse, so the radar errs on "no match" when the fit is unclear.

Uninstalled plugins from the marketplace are **not** surfaced. Install-mid-task is too disruptive, and the value of "you might want to install this" is much lower than "this is already on your machine."

## Working with existing projects

When you run a scaffold command for the first time in a project, the `project-survey` skill discovers stack, test commands, existing sub-agents, off-limits paths, and conventions, then persists the findings to `.architect.json` at the repo root. Subsequent commands read this file and skip re-prompting.

Generated loops automatically include your project's off-limits paths in guardrails and use your project's actual test commands. Generated sub-agents check whether an existing project sub-agent already does the job. Audits evaluate against both plugin principles and project conventions, with the project winning by default.

You can edit `.architect.json` directly. To re-run discovery, say "re-survey" or delete the file.

## Naming convention

The commands follow `<noun>-<role>` where the role names *what kind of action the command performs*:

- **`-contract`** (loop-contract, subagent-contract) — generates an artifact defining what the runtime must honor; refuses when the contract can't be specified
- **`-audit`** (coordination-audit) — examines an existing setup
- **`-check`** (theater-check) — runs filter questions before commitment
- **`-forensics`** (loop-forensics) — diagnoses a failure pattern after the fact
- **`-radar`** (capability-radar) — surfaces existing capabilities before generation
- **`-survey`** (project-survey) — inspects the local project once

## Install

This plugin lives in the **pragmatic** marketplace. Add the marketplace if you haven't already, then install:

```bash
/plugin marketplace add <pragmatic-marketplace-source>
/plugin install architect@pragmatic
```

The plugin does not ship its own marketplace file — it expects to be discovered through pragmatic's listing.

## Quick start

```
You: /architect I want to build something that reads my repo, writes summaries
of each module, has another agent review them, and a third agent merge them
into one doc.

Plugin: [capability-radar runs first]
[no match found — proceeds]

RECOMMENDATION: Tier 2 — single execution with tools

WHY: All three "agents" you described see the same context (the full repo)
and use the same tools (read files, write text). There is no objective
verifier between stages. A single agent reading the repo and producing a
structured summary will do this faster, cheaper, and is easier to debug.

WATCH FOR: If you find yourself wanting a "review agent", what you actually
want is a stricter template.

[asks you] How would you like to proceed?
  • Do it now
  • Save the approach and stop
  • Pick a higher tier anyway
  • Refine the task
```

If a capability fits, you'll see this instead:

```
You: /loop-contract fix failing tests in src/payments

Plugin: [capability-radar runs first]

CAPABILITY MATCH: test-runner (in-session sub-agent)
WHY IT FITS: It already runs project tests with structured failure output —
the verifier role this loop would need is already filled.
RECOMMENDATION: Use the existing test-runner sub-agent for verification.
The loop would only add iteration on top.

[asks you] Proceed?
  • Use the existing capability and skip scaffolding
  • Scaffold a loop that uses test-runner as its verifier
  • Generate a fully new loop anyway
  • Cancel
```

## Design principles

1. **Default to the lowest tier that works.** Multi-agent design must earn its place with measured wins.
2. **Tier 0 outranks every tier.** Use what exists before generating anything new.
3. **Loops without verifiers are roulette wheels.** No verifier → not a loop.
4. **Sub-agent roles fit in one objective sentence.** "Given X, produce Y, fail when Z."
5. **Coordination cost is real.** Every sub-agent adds prompt overhead, context handoff, semantic loss.
6. **Fail closed.** Sub-agents return failure verdicts; the orchestrator decides recovery.
7. **Observability is non-negotiable.** Loops log hypothesis / command / result / decision.
8. **The orchestrator does not soften refusals.** `/architect` makes the path visible but applies the same validation.
9. **The project wins.** Plugin defaults are starting points; project conventions take precedence.
10. **Mechanical work belongs in scripts.** Skills handle judgment; scripts handle deterministic inspection.

## When this plugin is the wrong tool

- You're learning Claude Code and just want to see what's possible — start with the docs
- Your task is small enough that a single direct prompt works — the plugin will tell you so
- You don't have the pragmatic marketplace configured — capability-radar's plugin matching will be a no-op, but the plugin still works for in-session capabilities and project surveys

## License

MIT
