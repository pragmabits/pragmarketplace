---
name: codex-review
description: Independent Codex-based code review of the current `git diff`. Invoke with `/codex-review` optionally followed by raw script flags (e.g. `-c "focus text"`, `-s ./reviews`, `-e xhigh`). Presents the verdict, summary, and findings.
argument-hint: "[raw flags, e.g. -c \"focus text\" | -s ./reviews | -e xhigh]"
disable-model-invocation: true
---

# Codex Review

The bundled review script has **already been executed** before this prompt reached you. Its JSON output is injected directly below. Your job is to parse that JSON and present the review to the user — nothing else. You do not run the script, you do not re-run it, you do not choose its flags. The user's `/codex-review` arguments were passed verbatim by the shell; the script's own argparse validated them.

## Script output

```!
bash "${CLAUDE_SKILL_DIR}/scripts/codex-review.sh" -o json $ARGUMENTS 2>&1
```

## How to interpret the block above

On success, the block is a single JSON object matching this schema:

```json
{
  "verdict": "PASS" | "NEEDS_FIX" | "BLOCKER",
  "summary": "string",
  "findings": [
    {
      "severity": "blocker" | "high" | "medium" | "low",
      "file": "string",
      "line": number | null,
      "issue": "string",
      "why_it_matters": "string",
      "minimal_fix": "string"
    }
  ],
  "review_context_applied": "string" | null
}
```

On failure (non-zero script exit, empty diff, argparse rejection, missing `codex`/`jq`, etc.), the block contains free-form error text instead of JSON. Detect this by trying to parse as JSON; if parsing fails, treat the block as an error message.

## Presenting a successful review

1. **Verdict** on its own line: `PASS`, `NEEDS_FIX`, or `BLOCKER`.
2. **Summary** — verbatim from `summary`, one sentence.
3. **Findings** — sorted by severity (`blocker` → `high` → `medium` → `low`). For each, format as:

   ```
   [SEVERITY] path/to/file:line — issue
     Why: why_it_matters
     Fix: minimal_fix
   ```

   Use `file_path:line` so the user can click through. When `line` is `null`, omit it or write `?`.

4. If `review_context_applied` is non-null, echo it so the user sees which focus was applied.

For `PASS`, state the verdict and summary and stop. Do not manufacture findings from the summary.

## Presenting a failure

Show the raw error block verbatim so the user can diagnose (missing CLI, auth failure, bad flag, empty diff, etc.). Do not retry with different flags. Do not fabricate a review. If the cause is obvious (e.g. `codex: command not found`), state the fix in one line after the raw error.

## Follow-up etiquette

- Do not modify files based on findings without explicit user approval. The reviewer suggests fixes; the user decides what to apply.
- If the user wants a different review (different focus, higher effort, save to disk), they should re-invoke `/codex-review` with the flags they want. Do not silently re-run the script with flags the user did not type.
- Do not review committed-only changes or other branches — the script always reviews the working-tree `git diff`.
