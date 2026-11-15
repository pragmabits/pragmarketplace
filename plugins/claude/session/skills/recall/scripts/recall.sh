#!/usr/bin/env bash
# recall.sh — dispatcher for the recall skill subcommands. Read-only.
#
# Usage: recall.sh [--me | --user <name>]
#        recall.sh <list|filter|grep|resume|last> [args]
#        recall.sh --args-stdin    (the same, read as one line from stdin)
#
# Output:
#   no subcommand    — JSON: the resume view (below) of each of the three
#                      newest reports, for resuming the work where recent
#                      sessions left it. --me (the git user) or -u/--user
#                      <name> keeps only that user's reports, by the user part
#                      of the filename.
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
# after_report (3.3.0; resume and the form without a subcommand): what no
# report records, because it came after the report resumed or the newest of
# the reports read (lib/after-report.sh):
#   { "report": str, "since": "YYYY-MM-DDTHH:MM:SSZ",
#     "memory": { "state": "read" | "missing" | "unreadable" | "unresolved",
#                 "dir", "source", "reason",
#                 "files": [{ "path", "name", "description", "modified" }] },
#     "sessions": { "after": <newest report in the directory>, "since",
#                   "state": <same values>, "dir", "current",
#                   "items": [{ "started", "last_active", "prompts_after",
#                               "ids": [str] }] } }
#   or { "error": str } when it could not be computed. sessions holds the
#   sessions in which the user wrote after the newest report in the directory;
#   $RECALL_CURRENT_SESSION, which the skill sets to the session's id, keeps
#   that session (and the file it was resumed from) out. The Codex reader has
#   no such block: the readers agree on everything else.
#
# Exit codes: 0 success (including "no sessions" notices), 1 error, 2 usage
# error or ambiguous reference. With --args-stdin, the form the skill uses, the
# exit code is always 0: Claude Code aborts a skill whose !-command exits
# non-zero and shows the raw command instead of its output, so the usage line
# or error would never reach the model that is told to emit it.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/sessions.sh
source "${SCRIPT_DIR}/lib/sessions.sh"
# shellcheck source=lib/after-report.sh
source "${SCRIPT_DIR}/lib/after-report.sh"
REPORT_JQ="${SCRIPT_DIR}/lib/report.jq"

NO_SESSIONS='No sessions found in .harness/sessions/'
# Reports read when no subcommand is given.
RECENT_COUNT=3

print_usage() {
  printf 'Usage: /recall [--me | --user <name>] | list [--limit N] | filter <key:value>... [--limit N] | grep <pattern> [--limit N] | resume [<session-id>] [--item <text>] | last [<n>]\n' >&2
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

# Add after_report to the JSON object on stdin. Args: the report that sets the
# moment for the memories, the newest report in the directory, which sets it
# for the sessions. A failure here never fails the lookup: after_report says so
# instead, with the cause.
with_after_report() {
  local report="$1" newest="$2" after="" rc=0
  after="$(after_report_json "$report" "$newest" "${SESSIONS_DIR%/.harness/sessions}" "${RECALL_CURRENT_SESSION:-}" 2>&1 </dev/null)" || rc=$?
  if [[ $rc -ne 0 ]] || ! printf '%s' "$after" | jq -e 'type == "object"' >/dev/null 2>&1; then
    after="$(jq -n -c --arg cause "$(printf '%s' "$after" | head -c 300)" \
      '{error: ("the memories and sessions after the report could not be listed" + (if $cause == "" then "" else ": " + $cause end))}')"
  fi
  jq --argjson after "$after" '. + {after_report: $after}'
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
    --arg f_user "" --arg f_branch "" --arg f_status "" --arg f_since "" --arg f_until "" --arg criteria "" \
    | with_after_report "$file" "${SESSION_FILES[0]}"
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
# no subcommand: the pending items of the newest reports
# ---------------------------------------------------------------------------

# Keep in SESSION_FILES only the reports whose filename user is $1, compared
# without regard to case.
keep_user() {
  local want="$1" f id kept=() had_nocasematch=0
  shopt -q nocasematch && had_nocasematch=1
  shopt -s nocasematch
  for f in ${SESSION_FILES[@]+"${SESSION_FILES[@]}"}; do
    id="$(session_id "$f")"
    if [[ "$id" =~ $SESSION_NAME_RE ]] && [[ "${BASH_REMATCH[2]}" == "$want" ]]; then
      kept+=("$f")
    fi
  done
  [[ $had_nocasematch -eq 1 ]] || shopt -u nocasematch
  SESSION_FILES=(${kept[@]+"${kept[@]}"})
}

cmd_recent() {
  local by="" name="" user=""
  while [[ $# -gt 0 ]]; do
    case "$1" in
      --me|-u|--user)
        if [[ -n "$by" ]]; then
          printf 'error: give --me or --user <name> once\n' >&2
          return 2
        fi
        by="$1"
        if [[ "$1" == "--me" ]]; then
          shift
        else
          if [[ -z "${2:-}" ]]; then
            printf 'error: %s requires a user name\n' "$1" >&2
            return 2
          fi
          name="$2"
          shift 2
        fi ;;
      *)
        printf 'error: without a subcommand /recall accepts only --me or --user <name> (got: %s)\n' "$1" >&2
        return 2 ;;
    esac
  done

  if [[ -n "$by" ]]; then
    local helper="${RECALL_PLUGIN_ROOT}/scripts/lib/report-user.sh"
    # shellcheck source=../../../scripts/lib/report-user.sh
    if [[ ! -r "$helper" ]] || ! source "$helper"; then
      printf 'error: the report user helper is missing from the plugin (scripts/lib/report-user.sh)\n' >&2
      return 1
    fi
    if [[ "$by" == "--me" ]]; then
      name="$(git config user.name 2>/dev/null || true)"
      user="$(report_file_user "$name")"
      # /report names these reports unknown-user, which says nothing about whose they are.
      if [[ -z "$user" || "$user" == "unknown" ]]; then
        printf 'error: --me needs a git user.name that /report can put in a filename; name the user with --user <name>\n' >&2
        return 1
      fi
    else
      user="$(report_file_user "$name")"
      if [[ -z "$user" ]]; then
        printf 'error: %s "%s" leaves no characters a report filename can hold\n' "$by" "$name" >&2
        return 2
      fi
    fi
  fi
  require_jq || return 1

  local rc=0
  load_or_notice || rc=$?
  [[ $rc -eq 10 ]] && return 0
  [[ $rc -ne 0 ]] && return 1
  local newest="${SESSION_FILES[0]}"

  if [[ -n "$user" ]]; then
    keep_user "$user"
    if [[ ${#SESSION_FILES[@]} -eq 0 ]]; then
      printf 'No sessions match: user:%s\n' "$user"
      return 0
    fi
  fi
  # All reports count as available, not just the ones passed to jq.
  AVAILABLE=${#SESSION_FILES[@]}
  if [[ $RECENT_COUNT -lt $AVAILABLE ]]; then
    SESSION_FILES=("${SESSION_FILES[@]:0:$RECENT_COUNT}")
  fi
  prepare_inputs
  run_report_jq recent --arg limit "$RECENT_COUNT" --arg item "" \
    --arg f_user "$user" --arg f_branch "" --arg f_status "" --arg f_since "" --arg f_until "" --arg criteria "" \
    | with_after_report "${SESSION_FILES[0]}" "$newest"
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
  local from_skill=0
  if [[ $# -eq 1 && "$1" == "--args-stdin" ]]; then
    from_skill=1
    local arg_text
    arg_text="$(cat)"
    split_words "$arg_text"
    set -- ${WORDS[@]+"${WORDS[@]}"}
  elif [[ $# -eq 1 ]]; then
    split_words "$1"
    set -- ${WORDS[@]+"${WORDS[@]}"}
  fi

  local rc=0
  if [[ $# -eq 0 || "$1" == -* ]]; then
    cmd_recent "$@" || rc=$?
  else
    local cmd="$1"
    shift
    case "$cmd" in
      list)   cmd_list "$@" || rc=$? ;;
      filter) cmd_filter "$@" || rc=$? ;;
      grep)   cmd_grep "$@" || rc=$? ;;
      resume) cmd_resume "$@" || rc=$? ;;
      last)   cmd_last "$@" || rc=$? ;;
      *)
        printf 'error: unknown subcommand: %s\n' "$cmd" >&2
        print_usage
        rc=2 ;;
    esac
  fi
  # The message is already on the output; see "Exit codes" above.
  [[ $from_skill -eq 1 ]] && exit 0
  exit "$rc"
}

main "$@"
