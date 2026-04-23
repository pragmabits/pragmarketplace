#!/usr/bin/env bash
set -euo pipefail

CONTEXT=""
OUTPUT_FORMAT="default"
MODEL="gpt-5.4"
EFFORT="high"
SAVE_PATH=""
SAVE_FILENAME=""
VERBOSE=false

usage() {
  cat <<'EOF'
Usage:
  codex-review.sh [-c|--context TEXT] [-o|--output FORMAT] [-m|--model MODEL] [-e|--effort EFFORT] [-s|--save PATH] [-f|--filename FILENAME] [-v|--verbose]

Options:
  -c, --context TEXT       Optional review context/focus. Can be a full text string.
  -o, --output FORMAT      Output format: json, markdown, md, or default.
                           Values are case-insensitive.
  -m, --model MODEL        Codex model to use. Default: gpt-5.4.
  -e, --effort EFFORT      Reasoning effort: minimal, low, medium, high, or xhigh.
                           Default: high. Values are case-insensitive.
  -s, --save PATH          Save the final review output.
                           If PATH points to an existing file, that file is used.
                           Otherwise, PATH is treated as a directory path.
  -f, --filename FILENAME  File name to use when --save points to a directory path.
                           Takes precedence over the generated default file name.
  -v, --verbose            Show all Codex output, including progress and tool activity.

Examples:
  codex-review.sh
  codex-review.sh -c "Focus on authentication regressions."
  codex-review.sh --context "Review concurrency and race conditions." --output json
  codex-review.sh -c "Check whether tests cover the changed behavior." -o md
  codex-review.sh -c "Check whether tests cover the changed behavior." -o MARKDOWN
  codex-review.sh --model gpt-5.4 --effort high
  codex-review.sh -m gpt-5.4 -e xhigh -o json
  codex-review.sh -o json --save review.json
  codex-review.sh -o md --save ./reviews
  codex-review.sh -o json --save ./reviews --filename latest-review.json
  codex-review.sh -o json -v
EOF
}

normalize_output_format() {
  local value
  value="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')"

  case "$value" in
    json)
      printf '%s\n' "json"
      ;;
    markdown|md)
      printf '%s\n' "markdown"
      ;;
    default)
      printf '%s\n' "default"
      ;;
    *)
      return 1
      ;;
  esac
}

normalize_effort() {
  local value
  value="$(printf '%s' "$1" | tr '[:upper:]' '[:lower:]')"

  case "$value" in
    minimal|low|medium|high|xhigh)
      printf '%s\n' "$value"
      ;;
    *)
      return 1
      ;;
  esac
}

output_extension() {
  case "$OUTPUT_FORMAT" in
    json)
      printf '%s\n' "json"
      ;;
    markdown)
      printf '%s\n' "md"
      ;;
    default)
      printf '%s\n' "txt"
      ;;
  esac
}

sanitize_filename_part() {
  printf '%s' "$1" \
    | tr '[:upper:]' '[:lower:]' \
    | sed -E 's#[^a-z0-9._-]+#-#g; s#^-+##; s#-+$##'
}

default_review_filename() {
  local repo_root
  local repo_name
  local branch_name
  local timestamp
  local extension

  repo_root="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
  repo_name="$(basename "$repo_root")"
  repo_name="$(sanitize_filename_part "$repo_name")"

  branch_name="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || printf '%s' "unknown-branch")"
  if [[ "$branch_name" == "HEAD" ]]; then
    branch_name="$(git rev-parse --short HEAD 2>/dev/null || printf '%s' "detached-head")"
  fi
  branch_name="$(sanitize_filename_part "$branch_name")"

  timestamp="$(date +%Y%m%d-%H%M%S)"
  extension="$(output_extension)"

  printf 'codex-review-[%s-%s]-%s.%s\n' "$repo_name" "$branch_name" "$timestamp" "$extension"
}

resolve_save_file() {
  local path="$1"
  local filename="$2"
  local target_dir
  local target_file

  if [[ -z "$path" && -n "$filename" ]]; then
    path="."
  fi

  if [[ -z "$path" ]]; then
    return 0
  fi

  if [[ -n "$filename" ]]; then
    case "$filename" in
      */*)
        echo "Error: --filename must be a file name only, not a path: $filename" >&2
        exit 2
        ;;
      "")
        echo "Error: --filename cannot be empty." >&2
        exit 2
        ;;
    esac
  fi

  if [[ -f "$path" ]]; then
    printf '%s\n' "$path"
    return 0
  fi

  if [[ -e "$path" && ! -d "$path" ]]; then
    echo "Error: save path exists but is neither a regular file nor a directory: $path" >&2
    exit 2
  fi

  target_dir="$path"
  mkdir -p "$target_dir"

  if [[ -n "$filename" ]]; then
    target_file="$filename"
  else
    target_file="$(default_review_filename)"
  fi

  if [[ -d "$target_dir/$target_file" ]]; then
    echo "Error: resolved save target points to a directory: $target_dir/$target_file" >&2
    exit 2
  fi

  printf '%s\n' "$target_dir/$target_file"
}

is_valid_json_output() {
  local file="$1"

  if ! command -v jq >/dev/null 2>&1; then
    return 1
  fi

  jq -e '
    type == "object" and
    (.verdict | type == "string") and
    (.verdict == "PASS" or .verdict == "NEEDS_FIX" or .verdict == "BLOCKER") and
    (.summary | type == "string") and
    (.findings | type == "array") and
    (.review_context_applied == null or (.review_context_applied | type == "string"))
  ' "$file" >/dev/null 2>&1
}

is_valid_markdown_output() {
  local file="$1"

  grep -q '^# Code Review$' "$file" &&
    grep -q '^## Verdict$' "$file" &&
    grep -q '^## Summary$' "$file" &&
    grep -q '^## Findings$' "$file" &&
    grep -q '^## Review Context Applied$' "$file" &&
    grep -Eq '^(PASS|NEEDS_FIX|BLOCKER)$' "$file"
}

is_valid_default_output() {
  local file="$1"

  grep -Eq '^VERDICT: (PASS|NEEDS_FIX|BLOCKER)$' "$file"
}

is_valid_review_output() {
  local file="$1"

  [[ -s "$file" ]] || return 1

  case "$OUTPUT_FORMAT" in
    json)
      is_valid_json_output "$file"
      ;;
    markdown)
      is_valid_markdown_output "$file"
      ;;
    default)
      is_valid_default_output "$file"
      ;;
    *)
      return 1
      ;;
  esac
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    -c|--context)
      if [[ $# -lt 2 ]]; then
        echo "Error: $1 requires a value." >&2
        usage >&2
        exit 2
      fi
      CONTEXT="$2"
      shift 2
      ;;
    -o|--output)
      if [[ $# -lt 2 ]]; then
        echo "Error: $1 requires a value." >&2
        usage >&2
        exit 2
      fi

      if ! OUTPUT_FORMAT="$(normalize_output_format "$2")"; then
        echo "Error: invalid output format: $2" >&2
        echo "Allowed values: json, markdown, md, default" >&2
        exit 2
      fi

      shift 2
      ;;
    -m|--model)
      if [[ $# -lt 2 ]]; then
        echo "Error: $1 requires a value." >&2
        usage >&2
        exit 2
      fi
      MODEL="$2"
      shift 2
      ;;
    -e|--effort)
      if [[ $# -lt 2 ]]; then
        echo "Error: $1 requires a value." >&2
        usage >&2
        exit 2
      fi

      if ! EFFORT="$(normalize_effort "$2")"; then
        echo "Error: invalid effort: $2" >&2
        echo "Allowed values: minimal, low, medium, high, xhigh" >&2
        exit 2
      fi

      shift 2
      ;;
    -s|--save)
      if [[ $# -lt 2 ]]; then
        echo "Error: $1 requires a value." >&2
        usage >&2
        exit 2
      fi
      SAVE_PATH="$2"
      shift 2
      ;;
    -f|--filename)
      if [[ $# -lt 2 ]]; then
        echo "Error: $1 requires a value." >&2
        usage >&2
        exit 2
      fi
      SAVE_FILENAME="$2"
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -v|--verbose)
      VERBOSE=true
      shift
      ;;
    *)
      echo "Error: unknown argument: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

SAVE_FILE="$(resolve_save_file "$SAVE_PATH" "$SAVE_FILENAME")"

if [[ -n "$CONTEXT" ]]; then
  EXTRA_INSTRUCTIONS=$(cat <<EOF
Additional review context requested by the caller:
$CONTEXT

Use this context to guide the review, but do not ignore serious issues outside this scope.
EOF
)
else
  EXTRA_INSTRUCTIONS="No additional review context was provided."
fi

case "$OUTPUT_FORMAT" in
  json)
    OUTPUT_INSTRUCTIONS=$(cat <<'EOF'
Return only valid JSON. Do not wrap it in Markdown. Do not include commentary outside the JSON.

Use this exact JSON structure:

{
  "verdict": "PASS",
  "summary": "No material issues found.",
  "findings": [],
  "review_context_applied": null
}

Or, when issues are found:

{
  "verdict": "NEEDS_FIX",
  "summary": "Brief objective summary of the review result.",
  "findings": [
    {
      "severity": "high",
      "file": "src/example.ts",
      "line": 42,
      "issue": "Objective description of the issue.",
      "why_it_matters": "Why this can break behavior, security, reliability, or contract expectations.",
      "minimal_fix": "Smallest reasonable fix."
    }
  ],
  "review_context_applied": "The caller-provided context, or null if none was provided."
}

Schema rules:
- "verdict" must be exactly one of: "PASS", "NEEDS_FIX", "BLOCKER".
- "severity" must be exactly one of: "blocker", "high", "medium", "low".
- "line" must be a JSON number or null, never a string.
- "findings" must be an array.
- If there are no material issues, use "verdict": "PASS" and "findings": [].
- Use "NEEDS_FIX" when there are material issues but no blocker.
- Use "BLOCKER" when the diff is unsafe to merge or likely to cause a serious regression.
EOF
)
    ;;
  markdown)
    OUTPUT_INSTRUCTIONS=$(cat <<'EOF'
Return the review as structured Markdown.

Use this exact structure:

# Code Review

## Verdict

PASS | NEEDS_FIX | BLOCKER

## Summary

A concise objective summary.

## Findings

For each finding, use:

### Finding N: Short title

- Severity: blocker | high | medium | low
- File: path/to/file
- Line: number or unknown
- Issue: objective description
- Why it matters: explanation
- Minimal fix: smallest reasonable fix

If there are no material issues, write:

No material issues found.

## Review Context Applied

State the caller-provided context, or write "None".
EOF
)
    ;;
  default)
    OUTPUT_INSTRUCTIONS=$(cat <<'EOF'
Return a clear code review.

For each finding, provide:
- severity: blocker | high | medium | low
- file and approximate line
- objective description
- why this breaks or may break
- minimal suggested fix

If there are no material issues, say so clearly.

End with exactly one of:
VERDICT: PASS
VERDICT: NEEDS_FIX
VERDICT: BLOCKER
EOF
)
    ;;
esac

PROMPT=$(cat <<EOF
You are an independent code reviewer. Review only the provided diff and any repository context that is strictly necessary.

You must use project agent instruction files such as CLAUDE.md, AGENTS.md, or similar files as the source of truth for project-specific conventions, guidelines, and architectural decisions.

Do not invent project-specific conventions that are not supported by those files, the provided diff, or the minimal repository context needed to review the change.

If you detect a divergence between the code and the documentation, point it out as a potential issue only when the divergence is not clearly explained by the current diff. Distinguish between:
- a likely violation introduced by the current change;
- a pre-existing inconsistency;
- documentation that may be outdated.

Prioritize:
1. behavioral bugs;
2. regressions;
3. security issues;
4. race conditions;
5. API or contract violations;
6. uncovered edge cases;
7. inconsistencies with tests or types.

Do not comment on purely subjective style, naming, formatting, or personal preferences.

However, do report violations of explicit project guidelines documented in CLAUDE.md, AGENTS.md, or similar instruction files, even when they involve style, naming, formatting, architecture, or workflow conventions.

When reporting such a violation, cite the relevant documented guideline and explain why the current diff violates it.

$EXTRA_INSTRUCTIONS

$OUTPUT_INSTRUCTIONS
EOF
)

LOG_FILE="$(mktemp -t codex-review.XXXXXX.log)"
OUTPUT_FILE="$(mktemp -t codex-review.XXXXXX.out)"
CODEX_EXIT_CODE=0

if [[ "$VERBOSE" == true ]]; then
  if ! git diff | codex exec \
    --sandbox read-only \
    --model "$MODEL" \
    --config model_reasoning_effort="\"$EFFORT\"" \
    "$PROMPT" | tee "$OUTPUT_FILE"; then
    CODEX_EXIT_CODE=$?
  fi
else
  if ! git diff | codex exec \
    --sandbox read-only \
    --model "$MODEL" \
    --config model_reasoning_effort="\"$EFFORT\"" \
    "$PROMPT" >"$OUTPUT_FILE" 2>"$LOG_FILE"; then
    CODEX_EXIT_CODE=$?
  fi
fi

if [[ "$CODEX_EXIT_CODE" -ne 0 ]] && ! is_valid_review_output "$OUTPUT_FILE"; then
  echo "Error: codex review failed." >&2
  if [[ "$VERBOSE" == false ]]; then
    echo "Codex stderr:" >&2
    cat "$LOG_FILE" >&2
  fi
  rm -f "$LOG_FILE" "$OUTPUT_FILE"
  exit 1
fi

OUTPUT="$(cat "$OUTPUT_FILE")"

rm -f "$LOG_FILE" "$OUTPUT_FILE"

if [[ -n "$SAVE_FILE" ]]; then
  printf '%s\n' "$OUTPUT" > "$SAVE_FILE"
fi

if [[ "$VERBOSE" == false ]]; then
  printf '%s\n' "$OUTPUT"
fi