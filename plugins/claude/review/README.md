# Review Plugin

Independent, Codex-backed code review of the current `git diff` for Claude Code.

## Overview

The `review` plugin adds a `/codex-review` skill that runs an external [Codex](https://github.com/openai/codex) pass over the working-tree `git diff` and returns a structured verdict. The review runs out-of-band in a read-only sandbox, so it provides a second opinion that is independent of the Claude session driving the work.

The skill's shell exec is pre-authorized via the SKILL.md `allowed-tools` frontmatter, so end users get no permission prompt on first invocation.

### What you get

- A **verdict**: `PASS`, `NEEDS_FIX`, or `BLOCKER`.
- A one-sentence **summary** of the review result.
- A list of **findings** — each with severity, file, line, the issue, why it matters, and a minimal fix.
- Optional persistence: save the review as JSON, Markdown, or plain text.

## Prerequisites

- `codex` CLI available on `PATH` and authenticated.
- `git` (the script reviews the working-tree diff).
- `jq` — only required when using `-o json` (used to validate the JSON schema).
- `bash` — the review runs as a bundled shell script.

## Available Commands

### `/codex-review`

Review the current `git diff` and present the verdict, summary, and findings.

**Usage:**
```
/codex-review [raw flags]
```

Flags are passed verbatim to the bundled `codex-review.sh` script — the script's own argparse validates them, and Claude does not rewrite them.

| Flag | Value | Description |
|------|-------|-------------|
| `-c`, `--context` | TEXT | Optional review focus (e.g. `-c "focus on concurrency"`). |
| `-o`, `--output` | `json` \| `markdown` \| `md` \| `default` | Output format. Case-insensitive. Default: `default`. |
| `-m`, `--model` | MODEL | Codex model. Default: `gpt-5.4`. |
| `-e`, `--effort` | `minimal` \| `low` \| `medium` \| `high` \| `xhigh` | Reasoning effort. Default: `high`. |
| `-s`, `--save` | PATH | Save the review to a file or directory. |
| `-f`, `--filename` | FILENAME | File name to use when `--save` points to a directory. |
| `-v`, `--verbose` | — | Stream Codex progress to stdout. |

**Examples:**
```bash
# Basic review of the working-tree diff
/codex-review

# Focus the review on a specific concern
/codex-review -c "Check authentication regressions"

# Ask for JSON output with higher reasoning effort
/codex-review -o json -e xhigh

# Save the review alongside the repo (directory + auto-generated filename)
/codex-review -o md -s ./reviews

# Save with an explicit filename
/codex-review -o json -s ./reviews -f latest-review.json
```

### Auto-generated filenames

When `--save` points to a directory, the script produces a filename of the form:

```
codex-review-[<repo>-<branch>]-<YYYYMMDD-HHMMSS>.<ext>
```

- `<ext>` is `json`, `md`, or `txt` depending on `--output`.
- `<repo>` and `<branch>` are sanitized to `[a-z0-9._-]`.
- Use `-f / --filename` to override.

## Output Formats

| Format | Shape |
|--------|-------|
| `default` | Free-form review text ending with a `VERDICT: …` line. |
| `markdown` / `md` | Structured Markdown with `# Code Review` / `## Verdict` / `## Summary` / `## Findings` / `## Review Context Applied` sections. |
| `json` | A single JSON object with `verdict`, `summary`, `findings[]`, and `review_context_applied`. |

The `/codex-review` skill invokes the script with `-o json` internally and parses the result to present findings to the user. Passing `-s` to save a review is the idiomatic way to persist a human-readable artifact.

## How It Works

1. The skill is invoked as `/codex-review [flags]`.
2. Before the skill content reaches Claude, the `!` shell-exec block runs `codex-review.sh -o json $ARGUMENTS`.
3. The script pipes `git diff` into `codex exec --sandbox read-only` with a review prompt.
4. The script validates the output shape against the chosen format and, if `--save` was passed, writes the review to disk.
5. The JSON result is injected into the skill content; Claude parses it and presents the verdict, summary, and findings.

## Permissions

The skill's `SKILL.md` frontmatter includes:

```yaml
allowed-tools: Bash(bash */codex-review.sh:*)
```

This pre-approves execution of the bundled script while the skill is active, so end users do not get a permission prompt on every invocation. No per-project or per-user settings patch is required.

## Architecture

```
review/
├── .claude-plugin/
│   └── plugin.json
└── skills/
    └── codex-review/
        ├── SKILL.md               # Skill with !-exec block
        └── scripts/
            └── codex-review.sh    # Bash runner that calls codex
```

## Version History

### v1.0.1 — April 2026
- Added `allowed-tools: Bash(bash */codex-review.sh:*)` to SKILL.md frontmatter so the bundled script runs without a permission prompt.

### v1.0.0 — April 2026
- Initial release. `/codex-review` skill with JSON/Markdown/default output formats, configurable model and effort, optional save path, and verbose mode.

## License

Property of Pragmabits.

## Contact

**Author:** Leonardo Leoncio
**Email:** leonardoleoncio96@gmail.com
