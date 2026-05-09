#!/usr/bin/env bash
# recall.sh — dispatcher for the recall skill subcommands.
#
# Usage: recall.sh <list|filter|grep|resume|last> [args]
#
# Output:
#   list/filter/grep — markdown (model emits verbatim).
#   last             — file paths, one per line (model Reads each, then summarizes).
#   resume           — JSON (model Reads file_path, then drives AskUserQuestion).
#
# resume JSON schema:
#   { "session_id": str,
#     "title": str,
#     "file_path": str,
#     "subsections": {
#       "in_progress": [{ "label": str, "raw": str }, ...],
#       "promised":    [{ "label": str, "raw": str }, ...],
#       "known_issues":[{ "label": str, "raw": str }, ...]
#     }
#   }
# When §6 is absent or all three subsections are "none":
#   { "session_id": str, "title": str, "file_path": str, "empty": true }

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/sessions.sh
source "${SCRIPT_DIR}/lib/sessions.sh"

# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------

print_usage() {
  printf 'Usage: /recall <list | filter <criteria> | grep <pattern> | resume [<session-id>] | last [<n>]>\n' >&2
}

# Escape a value for embedding in a markdown table cell.
md_escape() {
  printf '%s' "$1" | sed 's/|/\\|/g'
}

# Emit a markdown table from TSV rows on stdin. Handles --limit truncation.
# Args: $1 = limit (may be empty), $2 = total count seen
emit_table() {
  local limit="$1"
  local total="$2"
  printf '| Session ID | Title | Timestamp | Branch | Status |\n'
  printf '|------------|-------|-----------|--------|--------|\n'
  local shown=0
  while IFS=$'\t' read -r id title ts branch status; do
    [[ -z "$id" ]] && continue
    if [[ -n "$limit" ]] && [[ $shown -ge $limit ]]; then break; fi
    printf '| %s | %s | %s | %s | %s |\n' \
      "$(md_escape "$id")" \
      "$(md_escape "$title")" \
      "$(md_escape "$ts")" \
      "$(md_escape "$branch")" \
      "$(md_escape "$status")"
    shown=$((shown + 1))
  done
  if [[ -n "$limit" ]] && [[ $total -gt $limit ]]; then
    printf '\n%d total, showing %d. Use --limit <higher> or filter further to see more.\n' "$total" "$limit"
  fi
}

validate_positive_int() {
  local val="$1"
  local label="$2"
  if ! [[ "$val" =~ ^[1-9][0-9]*$ ]]; then
    printf 'error: %s must be a positive integer (got: %s)\n' "$label" "$val" >&2
    return 1
  fi
}

# ---------------------------------------------------------------------------
# list
# ---------------------------------------------------------------------------

cmd_list() {
  local limit=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --limit)
        validate_positive_int "${2:-}" "--limit value" || return 1
        limit="$2"; shift 2 ;;
      *) shift ;;
    esac
  done

  local files
  if ! files="$(list_session_files 2>/dev/null)"; then
    printf 'No sessions directory found at .claude/sessions/. Run the report skill at session end to create it.\n'
    return 0
  fi
  if [[ -z "$files" ]]; then
    printf 'No sessions found in .claude/sessions/\n'
    return 0
  fi

  local rows="" total=0
  while IFS= read -r f; do
    if is_malformed "$f"; then continue; fi
    rows+="$(extract_meta "$f")"$'\n'
    total=$((total + 1))
  done <<< "$files"

  if [[ $total -eq 0 ]]; then
    printf 'No sessions found in .claude/sessions/\n'
    return 0
  fi

  printf '%s' "$rows" | emit_table "$limit" "$total"
}

# ---------------------------------------------------------------------------
# filter
# ---------------------------------------------------------------------------

cmd_filter() {
  local limit=""
  local criteria=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --limit)
        validate_positive_int "${2:-}" "--limit value" || return 1
        limit="$2"; shift 2 ;;
      *) criteria+=("$1"); shift ;;
    esac
  done

  if [[ ${#criteria[@]} -eq 0 ]]; then
    printf 'error: filter requires at least one key:value criterion\n' >&2
    return 1
  fi

  local f_user="" f_branch="" f_status="" f_since="" f_until=""
  for c in "${criteria[@]}"; do
    if [[ "$c" != *":"* ]]; then
      printf 'error: criterion "%s" must be key:value\n' "$c" >&2
      return 1
    fi
    local key="${c%%:*}" val="${c#*:}"
    case "$key" in
      user)   f_user="$val" ;;
      branch) f_branch="$val" ;;
      status) f_status="$val" ;;
      since)  f_since="$val" ;;
      until)  f_until="$val" ;;
      *)
        printf 'error: unknown filter key "%s" (allowed: user, branch, status, since, until)\n' "$key" >&2
        return 1 ;;
    esac
  done

  local files
  if ! files="$(list_session_files 2>/dev/null)"; then
    printf 'No sessions directory found at .claude/sessions/. Run the report skill at session end to create it.\n'
    return 0
  fi
  if [[ -z "$files" ]]; then
    printf 'No sessions match: %s\n' "${criteria[*]}"
    return 0
  fi

  local rows="" total=0
  while IFS= read -r f; do
    if is_malformed "$f"; then continue; fi
    local meta m_id m_title m_ts m_branch m_status m_user m_date
    meta="$(extract_meta "$f")"
    IFS=$'\t' read -r m_id m_title m_ts m_branch m_status <<< "$meta"

    if [[ -n "$f_user" ]]; then
      m_user="$(session_user "$m_id")"
      [[ "$m_user" == "$f_user" ]] || continue
    fi
    if [[ -n "$f_branch" ]]; then
      [[ "$m_branch" == "$f_branch" ]] || continue
    fi
    if [[ -n "$f_status" ]]; then
      [[ "$m_status" == "$f_status" ]] || continue
    fi
    if [[ -n "$f_since" ]] || [[ -n "$f_until" ]]; then
      m_date="${m_ts:0:10}"
      if [[ -n "$f_since" ]] && [[ "$m_date" < "$f_since" ]]; then continue; fi
      if [[ -n "$f_until" ]] && [[ "$m_date" > "$f_until" ]]; then continue; fi
    fi

    rows+="$meta"$'\n'
    total=$((total + 1))
  done <<< "$files"

  if [[ $total -eq 0 ]]; then
    printf 'No sessions match: %s\n' "${criteria[*]}"
    return 0
  fi

  printf '%s' "$rows" | emit_table "$limit" "$total"
}

# ---------------------------------------------------------------------------
# grep
# ---------------------------------------------------------------------------

cmd_grep() {
  local limit=""
  local pattern_args=()
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --limit)
        validate_positive_int "${2:-}" "--limit value" || return 1
        limit="$2"; shift 2 ;;
      *) pattern_args+=("$1"); shift ;;
    esac
  done

  if [[ ${#pattern_args[@]} -eq 0 ]]; then
    printf 'error: grep requires a pattern\n' >&2
    return 1
  fi

  local pattern="${pattern_args[*]}"
  local grep_flag="-F"
  if [[ "$pattern" == re:* ]]; then
    grep_flag="-E"
    pattern="${pattern#re:}"
  fi

  local files
  if ! files="$(list_session_files 2>/dev/null)"; then
    printf 'No sessions directory found at .claude/sessions/. Run the report skill at session end to create it.\n'
    return 0
  fi
  if [[ -z "$files" ]]; then
    printf 'No matches for: %s\n' "$pattern"
    return 0
  fi

  local matched=()
  while IFS= read -r f; do
    if grep "$grep_flag" -l -i -- "$pattern" "$f" >/dev/null 2>&1; then
      matched+=("$f")
      if [[ -n "$limit" ]] && [[ ${#matched[@]} -ge $limit ]]; then break; fi
    fi
  done <<< "$files"

  if [[ ${#matched[@]} -eq 0 ]]; then
    printf 'No matches for: %s\n' "$pattern"
    return 0
  fi

  local first=1
  for f in "${matched[@]}"; do
    [[ $first -eq 0 ]] && printf '\n'
    first=0
    local id title
    id="$(basename "$f" .md)"
    title="$(grep -m1 '^# Session Report: ' "$f" | sed 's/^# Session Report: //')"
    printf '### %s — %s\n\n' "$id" "$title"

    local count=0
    while IFS=':' read -r lineno match; do
      [[ $count -ge 3 ]] && break
      local heading
      heading="$(section_for_line "$f" "$lineno")"
      [[ -z "$heading" ]] && heading="(before any ## section)"
      printf '%s — line %s\n  > %s\n\n' "$heading" "$lineno" "$match"
      count=$((count + 1))
    done < <(grep "$grep_flag" -n -i -- "$pattern" "$f" 2>/dev/null)
  done
}

# ---------------------------------------------------------------------------
# resume
# ---------------------------------------------------------------------------

# Build a JSON array of {label, raw} from a §6 subsection body string.
# Returns "[]" if the subsection is "none" or has no table rows.
extract_subsection_items() {
  local body="$1"
  # Trim leading blank lines
  body="$(printf '%s' "$body" | sed '/./,$!d')"
  # Check for "none" as first non-blank content
  if printf '%s' "$body" | awk 'NF { print; exit }' | grep -q '^none$'; then
    printf '[]'
    return 0
  fi

  local rows
  rows="$(printf '%s' "$body" | awk '
    /^\|[ -]*-/ { after_sep = 1; next }
    !after_sep { next }
    /^\| / { print }
  ')"

  if [[ -z "$rows" ]]; then
    printf '[]'
    return 0
  fi

  # Each row → {label: <first column>, raw: <full row>}
  printf '%s\n' "$rows" | jq -R '
    . as $row |
    ($row | sub("^\\| *"; "") | sub(" *\\|.*$"; "")) as $label |
    { label: $label, raw: $row }
  ' | jq -s '.'
}

cmd_resume() {
  local ref="${1:-}"
  local file=""

  if [[ -z "$ref" ]]; then
    file="$(list_session_files 2>/dev/null | head -n1)"
    if [[ -z "$file" ]]; then
      printf 'No sessions found in .claude/sessions/\n'
      return 0
    fi
  else
    local rc=0
    local stderr_file
    stderr_file="$(mktemp)"
    file="$(resolve_id "$ref" 2>"$stderr_file")" || rc=$?
    if [[ $rc -ne 0 ]]; then
      if [[ $rc -eq 2 ]]; then
        cat "$stderr_file" >&2
        rm -f "$stderr_file"
        return 2
      fi
      rm -f "$stderr_file"
      printf 'No session matches: %s\n' "$ref" >&2
      return 1
    fi
    rm -f "$stderr_file"
  fi

  local id title section6 in_progress promised known
  id="$(basename "$file" .md)"
  title="$(grep -m1 '^# Session Report: ' "$file" | sed 's/^# Session Report: //')"
  section6="$(extract_section "$file" 6)"

  if [[ -z "$section6" ]]; then
    jq -n --arg id "$id" --arg title "$title" --arg file "$file" \
      '{session_id: $id, title: $title, file_path: $file, empty: true}'
    return 0
  fi

  local body_61 body_62 body_63
  body_61="$(printf '%s' "$section6" | awk '
    /^### 6\.1/ { capture = 1; next }
    capture && /^### / { exit }
    capture { print }
  ')"
  body_62="$(printf '%s' "$section6" | awk '
    /^### 6\.2/ { capture = 1; next }
    capture && /^### / { exit }
    capture { print }
  ')"
  body_63="$(printf '%s' "$section6" | awk '
    /^### 6\.3/ { capture = 1; next }
    capture && /^### / { exit }
    capture { print }
  ')"

  in_progress="$(extract_subsection_items "$body_61")"
  promised="$(extract_subsection_items "$body_62")"
  known="$(extract_subsection_items "$body_63")"

  if [[ "$in_progress" == "[]" ]] && [[ "$promised" == "[]" ]] && [[ "$known" == "[]" ]]; then
    jq -n --arg id "$id" --arg title "$title" --arg file "$file" \
      '{session_id: $id, title: $title, file_path: $file, empty: true}'
    return 0
  fi

  jq -n \
    --arg id "$id" \
    --arg title "$title" \
    --arg file "$file" \
    --argjson in_progress "$in_progress" \
    --argjson promised "$promised" \
    --argjson known "$known" \
    '{
      session_id: $id,
      title: $title,
      file_path: $file,
      subsections: {
        in_progress: $in_progress,
        promised: $promised,
        known_issues: $known
      }
    }'
}

# ---------------------------------------------------------------------------
# last
# ---------------------------------------------------------------------------

cmd_last() {
  local n="${1:-1}"
  validate_positive_int "$n" "<n>" || return 1

  local files
  if ! files="$(list_session_files 2>/dev/null)"; then
    printf 'No sessions found in .claude/sessions/\n'
    return 0
  fi
  if [[ -z "$files" ]]; then
    printf 'No sessions found in .claude/sessions/\n'
    return 0
  fi

  local total=0
  local selected=()
  while IFS= read -r f; do
    total=$((total + 1))
    if [[ ${#selected[@]} -lt $n ]]; then
      selected+=("$f")
    fi
  done <<< "$files"

  for f in "${selected[@]}"; do
    printf '%s\n' "$f"
  done

  if [[ $n -gt $total ]]; then
    printf '\nOnly %d session(s) available; all paths shown.\n' "$total"
  fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

main() {
  # Two invocation forms are accepted:
  #   (1) Positional: recall.sh list --limit 5
  #   (2) Single quoted string: recall.sh "list --limit 5"
  # Form (2) is what the SKILL's !-block uses so that user-typed input is never
  # shell-evaluated; we re-split on whitespace via read -ra (no metachar eval).
  if [[ $# -eq 1 ]] && [[ "$1" == *" "* ]]; then
    local -a args=()
    read -ra args <<< "$1"
    set -- "${args[@]}"
  fi

  if [[ $# -eq 0 ]] || [[ -z "${1:-}" ]]; then
    print_usage
    exit 2
  fi
  local cmd="$1"; shift
  case "$cmd" in
    list)   cmd_list "$@" ;;
    filter) cmd_filter "$@" ;;
    grep)   cmd_grep "$@" ;;
    resume) cmd_resume "$@" ;;
    last)   cmd_last "$@" ;;
    *)      print_usage; exit 2 ;;
  esac
}

main "$@"
