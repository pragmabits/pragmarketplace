#!/usr/bin/env bash
# recall.sh — dispatcher for the recall skill subcommands. Read-only.
#
# Usage: recall.sh <list|filter|grep|resume|last> [args]
#        recall.sh --args-stdin    (the same, read as one line from stdin)
#
# Output:
#   list/filter/grep — markdown the skill emits verbatim.
#   last             — JSON: one excerpt per report (title, goal, status,
#                      status note, work topics, pending state and counts),
#                      enough for a one-line summary without reading the files.
#   resume           — JSON: metadata, goal, decisions and pending items of one
#                      report, with an explicit pending_state.
#
# resume JSON (fields added in 3.0.0 are marked +):
#   { "session_id": str, "title": str, "file_path": str,
#     + "timestamp", "goal", "goal_status", "status_note", "direction_changes",
#     + "requested_item": str              (only with --item: what the user asked to resume),
#     + "pending_state": "items" | "none" | "incomplete",
#     "empty": true                          (only when pending_state is "none"),
#     + "incomplete_reasons": [str]          (only when pending_state is "incomplete"),
#     "subsections": { "in_progress" | "promised" | "known_issues":
#                      [{ "label", "raw", +"cells", +"line" }] },
#     + "subsection_states": { <same keys>: { "state", "columns", "reason",
#                                            "notes", "unparsed", "line" } },
#     + "decisions": { "state", "columns", "items", ... } }
#   "empty": true means the report says `none` in all three subsections. A
#   missing, truncated or unreadable §6 is "incomplete", never "empty".
#
# Exit codes: 0 success (including "no sessions" notices), 1 error, 2 usage
# error or ambiguous reference.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/sessions.sh
source "${SCRIPT_DIR}/lib/sessions.sh"
REPORT_JQ="${SCRIPT_DIR}/lib/report.jq"

NO_SESSIONS='No sessions found in .harness/sessions/'

print_usage() {
  printf 'Usage: /recall <list [--limit N] | filter <key:value>... [--limit N] | grep <pattern> [--limit N] | resume [<session-id>] [--item <text>] | last [<n>]>\n' >&2
}

require_jq() {
  if ! command -v jq >/dev/null 2>&1; then
    printf 'error: jq is required by /recall but was not found in PATH\n' >&2
    return 1
  fi
}

validate_positive_int() {
  local val="$1" label="$2"
  if ! [[ "$val" =~ ^[1-9][0-9]*$ ]]; then
    printf 'error: %s must be a positive integer (got: %s)\n' "$label" "$val" >&2
    return 1
  fi
}

# Load SESSION_FILES. Returns 0 to continue, 10 when a "no sessions" notice was
# printed and the caller should stop successfully, 1 on error.
load_or_notice() {
  local rc=0
  load_session_files || rc=$?
  case "$rc" in
    0)
      if [[ ${#SESSION_FILES[@]} -eq 0 ]]; then
        printf '%s\n' "$NO_SESSIONS"
        return 10
      fi
      return 0 ;;
    3)
      printf '%s (the directory does not exist)\n' "$NO_SESSIONS"
      return 10 ;;
    *)
      return 1 ;;
  esac
}

# Split SESSION_FILES into INPUT_FILES (readable, non-empty) and the IDs of
# empty or unreadable files, which are reported instead of silently dropped.
INPUT_FILES=()
EMPTY_IDS=""
UNREADABLE_IDS=""
prepare_inputs() {
  INPUT_FILES=()
  EMPTY_IDS=""
  UNREADABLE_IDS=""
  local f id
  for f in ${SESSION_FILES[@]+"${SESSION_FILES[@]}"}; do
    id="$(session_id "$f")"
    if [[ ! -r "$f" ]]; then
      UNREADABLE_IDS+="${UNREADABLE_IDS:+, }$id"
    elif [[ ! -s "$f" ]]; then
      EMPTY_IDS+="${EMPTY_IDS:+, }$id"
    else
      INPUT_FILES+=("$f")
    fi
  done
}

# Run lib/report.jq over INPUT_FILES. Args: mode, then extra jq options.
run_report_jq() {
  local mode="$1"
  shift
  jq -R -n -r -f "$REPORT_JQ" \
    --arg mode "$mode" \
    --arg empty_ids "$EMPTY_IDS" \
    --arg unreadable_ids "$UNREADABLE_IDS" \
    --arg available "${AVAILABLE:-}" \
    "$@" \
    ${INPUT_FILES[@]+"${INPUT_FILES[@]}"} </dev/null
}

# Split one argument string into words without evaluating anything: no
# globbing, no expansion, no command substitution. A quote opens a quoted span
# only at the start of a word and closes it only at the end of one, so an
# apostrophe inside a word ("don't") stays literal. Backslashes are literal
# except \" and \\ inside double quotes, which keeps regex patterns intact.
# With an unbalanced quote, falls back to a plain whitespace split.
WORDS=()
split_words() {
  local s="$1" n=${#1} i=0 c next word="" have=0 q=""
  WORDS=()
  while [[ $i -lt $n ]]; do
    c="${s:i:1}"
    next="${s:i+1:1}"
    if [[ -n "$q" ]]; then
      if [[ "$c" == "$q" ]] && [[ -z "$next" || "$next" == " " || "$next" == $'\t' ]]; then
        q=""
      elif [[ "$q" == '"' && "$c" == '\' ]] && [[ "$next" == '"' || "$next" == '\' ]]; then
        word+="$next"
        i=$((i + 1))
      else
        word+="$c"
      fi
    else
      case "$c" in
        ' '|$'\t'|$'\n')
          if [[ $have -eq 1 ]]; then WORDS+=("$word"); word=""; have=0; fi ;;
        "'"|'"')
          if [[ $have -eq 0 ]]; then q="$c"; have=1; else word+="$c"; fi ;;
        *)
          word+="$c"; have=1 ;;
      esac
    fi
    i=$((i + 1))
  done
  if [[ -n "$q" ]]; then
    WORDS=()
    read -r -a WORDS <<< "$s" || true
    return 0
  fi
  if [[ $have -eq 1 ]]; then WORDS+=("$word"); fi
  return 0
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
      *)
        printf 'error: list accepts only --limit N (got: %s)\n' "$1" >&2
        return 2 ;;
    esac
  done
  require_jq || return 1

  local rc=0
  load_or_notice || rc=$?
  [[ $rc -eq 10 ]] && return 0
  [[ $rc -ne 0 ]] && return 1
  prepare_inputs
  run_report_jq list --arg limit "$limit" --arg item "" \
    --arg f_user "" --arg f_branch "" --arg f_status "" --arg f_since "" --arg f_until "" --arg criteria ""
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
    return 2
  fi

  local f_user="" f_branch="" f_status="" f_since="" f_until="" c key val
  for c in "${criteria[@]}"; do
    if [[ "$c" != *":"* ]]; then
      printf 'error: criterion "%s" must be key:value\n' "$c" >&2
      return 2
    fi
    key="${c%%:*}"
    val="${c#*:}"
    if [[ -z "$val" ]]; then
      printf 'error: criterion "%s" has an empty value\n' "$c" >&2
      return 2
    fi
    case "$key" in
      user)   f_user="$val" ;;
      branch) f_branch="$val" ;;
      status)
        case "$val" in
          achieved|partial|abandoned|redirected) f_status="$val" ;;
          *)
            printf 'error: status must be achieved, partial, abandoned or redirected (got: %s)\n' "$val" >&2
            return 2 ;;
        esac ;;
      since|until)
        if ! [[ "$val" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]]; then
          printf 'error: %s must be a date in YYYY-MM-DD form (got: %s)\n' "$key" "$val" >&2
          return 2
        fi
        if [[ "$key" == since ]]; then f_since="$val"; else f_until="$val"; fi ;;
      *)
        printf 'error: unknown filter key "%s" (allowed: user, branch, status, since, until)\n' "$key" >&2
        return 2 ;;
    esac
  done
  require_jq || return 1

  local rc=0
  load_or_notice || rc=$?
  [[ $rc -eq 10 ]] && return 0
  [[ $rc -ne 0 ]] && return 1
  prepare_inputs
  run_report_jq filter --arg limit "$limit" --arg item "" \
    --arg f_user "$f_user" --arg f_branch "$f_branch" --arg f_status "$f_status" \
    --arg f_since "$f_since" --arg f_until "$f_until" --arg criteria "${criteria[*]}"
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
    return 2
  fi

  local pattern="${pattern_args[*]}"
  local grep_flag="-F"
  if [[ "$pattern" == re:* ]]; then
    grep_flag="-E"
    pattern="${pattern#re:}"
  fi
  if [[ -z "$pattern" ]]; then
    printf 'error: grep requires a non-empty pattern\n' >&2
    return 2
  fi
  if [[ "$grep_flag" == "-E" ]]; then
    local probe_rc=0
    printf '' | grep -E -e "$pattern" >/dev/null 2>&1 || probe_rc=$?
    if [[ $probe_rc -eq 2 ]]; then
      printf 'error: invalid regular expression: %s\n' "$pattern" >&2
      return 2
    fi
  fi

  local rc=0
  load_or_notice || rc=$?
  [[ $rc -eq 10 ]] && return 0
  [[ $rc -ne 0 ]] && return 1
  prepare_inputs

  local matched=() f grc
  for f in ${INPUT_FILES[@]+"${INPUT_FILES[@]}"}; do
    grc=0
    grep -a "$grep_flag" -q -i -e "$pattern" -- "$f" 2>/dev/null || grc=$?
    if [[ $grc -eq 0 ]]; then
      matched+=("$f")
      if [[ -n "$limit" ]] && [[ ${#matched[@]} -ge $limit ]]; then break; fi
    elif [[ $grc -ne 1 ]]; then
      UNREADABLE_IDS+="${UNREADABLE_IDS:+, }$(session_id "$f")"
    fi
  done

  if [[ ${#matched[@]} -eq 0 ]]; then
    printf 'No matches for: %s\n' "$pattern"
  else
    local first=1 id title lineno match heading count
    for f in "${matched[@]}"; do
      [[ $first -eq 0 ]] && printf '\n'
      first=0
      id="$(session_id "$f")"
      title="$(grep -a -m1 '^# Session Report: ' "$f" | sed 's/^# Session Report: //' || true)"
      printf '### %s — %s\n\n' "$id" "$title"

      count=0
      while IFS=':' read -r lineno match; do
        [[ $count -ge 3 ]] && break
        heading="$(section_for_line "$f" "$lineno")"
        [[ -z "$heading" ]] && heading="(before any ## section)"
        printf '%s — line %s\n  > %s\n\n' "$heading" "$lineno" "$match"
        count=$((count + 1))
      done < <(grep -a "$grep_flag" -n -i -e "$pattern" -- "$f" 2>/dev/null || true)
    done
  fi

  if [[ -n "$EMPTY_IDS" ]]; then printf '\nSkipped empty file(s): %s\n' "$EMPTY_IDS"; fi
  if [[ -n "$UNREADABLE_IDS" ]]; then printf '\nCould not read: %s\n' "$UNREADABLE_IDS"; fi
  return 0
}

# ---------------------------------------------------------------------------
# resume
# ---------------------------------------------------------------------------

cmd_resume() {
  local ref="" item="" has_item=0
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --item)
        shift
        has_item=1
        item="$*"
        break ;;
      --*)
        printf 'error: unknown resume option: %s (allowed: --item <text>)\n' "$1" >&2
        return 2 ;;
      *)
        if [[ -n "$ref" ]]; then
          printf 'error: resume takes at most one session reference (got "%s" and "%s"); name the item to resume with: resume [<session-id>] --item <text>\n' "$ref" "$1" >&2
          return 2
        fi
        ref="$1"
        shift ;;
    esac
  done
  if [[ $has_item -eq 1 && -z "$item" ]]; then
    printf 'error: --item requires the text of the item to resume\n' >&2
    return 2
  fi
  require_jq || return 1

  local rc=0
  load_or_notice || rc=$?
  [[ $rc -eq 10 ]] && return 0
  [[ $rc -ne 0 ]] && return 1

  local file=""
  if [[ -z "$ref" ]]; then
    file="${SESSION_FILES[0]}"
  else
    local stderr_file
    stderr_file="$(mktemp)"
    rc=0
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

  if [[ ! -r "$file" ]]; then
    printf 'error: cannot read session report %s\n' "$(session_id "$file")" >&2
    return 1
  fi
  if [[ ! -s "$file" ]]; then
    printf 'error: session report %s is empty\n' "$(session_id "$file")" >&2
    return 1
  fi

  INPUT_FILES=("$file")
  EMPTY_IDS=""
  UNREADABLE_IDS=""
  run_report_jq resume --arg limit "" --arg item "$item" \
    --arg f_user "" --arg f_branch "" --arg f_status "" --arg f_since "" --arg f_until "" --arg criteria ""
}

# ---------------------------------------------------------------------------
# last
# ---------------------------------------------------------------------------

cmd_last() {
  if [[ $# -gt 1 ]]; then
    printf 'error: last takes one optional count (got %d arguments)\n' "$#" >&2
    return 2
  fi
  local n="${1:-1}"
  validate_positive_int "$n" "<n>" || return 1
  require_jq || return 1

  local rc=0
  load_or_notice || rc=$?
  [[ $rc -eq 10 ]] && return 0
  [[ $rc -ne 0 ]] && return 1

  local available=${#SESSION_FILES[@]}
  # All reports count as available, not just the n passed to jq.
  AVAILABLE="$available"
  if [[ $n -lt $available ]]; then
    SESSION_FILES=("${SESSION_FILES[@]:0:$n}")
  fi
  prepare_inputs
  run_report_jq last --arg limit "$n" --arg item "" \
    --arg f_user "" --arg f_branch "" --arg f_status "" --arg f_since "" --arg f_until "" --arg criteria "" \
    || return 1
  if [[ $n -gt $available ]]; then
    printf '\nOnly %d session(s) available; all are shown.\n' "$available"
  fi
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

main() {
  # Three invocation forms are accepted:
  #   (1) Positional:  recall.sh list --limit 5
  #   (2) One string:  recall.sh "list --limit 5"
  #   (3) Stdin:       recall.sh --args-stdin <<'EOF' ... EOF
  # Form (3) is what the skill's !-block uses. The harness pastes $ARGUMENTS
  # into the command text as is, so inside quotes a user's quote would end the
  # string and a $(...) would run. A heredoc with a quoted delimiter keeps the
  # text inert; split_words then splits it without evaluating anything.
  if [[ $# -eq 1 && "$1" == "--args-stdin" ]]; then
    local arg_text
    arg_text="$(cat)"
    split_words "$arg_text"
    set -- ${WORDS[@]+"${WORDS[@]}"}
  elif [[ $# -eq 1 ]]; then
    split_words "$1"
    set -- ${WORDS[@]+"${WORDS[@]}"}
  fi

  if [[ $# -eq 0 ]] || [[ -z "${1:-}" ]]; then
    print_usage
    exit 2
  fi
  local cmd="$1"
  shift
  local rc=0
  case "$cmd" in
    list)   cmd_list "$@" || rc=$? ;;
    filter) cmd_filter "$@" || rc=$? ;;
    grep)   cmd_grep "$@" || rc=$? ;;
    resume) cmd_resume "$@" || rc=$? ;;
    last)   cmd_last "$@" || rc=$? ;;
    *)      print_usage; exit 2 ;;
  esac
  exit "$rc"
}

main "$@"
