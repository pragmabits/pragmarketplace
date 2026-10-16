#!/usr/bin/env bash
# lib/sessions.sh — sourced helpers for recall.sh.
#
# Read-only: nothing here creates a directory or writes a file. Resolution goes
# through the plugin's scripts/lib/sessions-dir.sh, the same resolver the report
# skill uses, but without its mkdir step.
#
# Report filename: <user>-<YYYY-MM-DDTHHMMSS>[-N].md (UTC, no Z). The optional
# -N suffix is added by prepare-report.sh when the plain name is taken. Order is
# by the timestamp, then by N, never by the user prefix.

RECALL_LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# <plugin>/skills/recall/scripts/lib → <plugin>. Derived from this file's own
# location rather than CLAUDE_PLUGIN_ROOT, which the !-block subshell does not
# always export.
RECALL_PLUGIN_ROOT="${RECALL_LIB_DIR%/skills/recall/scripts/lib}"

SESSION_NAME_RE='^((.*)-)?([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{6})(-([0-9]+))?$'

SESSIONS_DIR=""
SESSION_FILES=()

# Print the sessions directory path without creating it.
sessions_dir() {
  local resolver="${RECALL_PLUGIN_ROOT}/scripts/lib/sessions-dir.sh"
  if [[ ! -r "$resolver" ]]; then
    printf 'error: the sessions directory resolver is missing from the plugin (scripts/lib/sessions-dir.sh)\n' >&2
    return 1
  fi
  # shellcheck source=../../../../scripts/lib/sessions-dir.sh
  if ! source "$resolver"; then
    printf 'error: the sessions directory resolver failed to load\n' >&2
    return 1
  fi
  if ! resolve_sessions_dir; then
    printf 'error: the sessions directory could not be resolved\n' >&2
    return 1
  fi
}

# Fill SESSION_FILES with report paths, newest first, and SESSIONS_DIR.
# Returns 0 when the directory was read (SESSION_FILES may be empty), 3 when
# the directory does not exist, 1 on any other problem (message on stderr).
# A directory that exists but cannot be read is an error, not "no reports".
load_session_files() {
  SESSION_FILES=()
  local dir
  dir="$(sessions_dir)" || return 1
  SESSIONS_DIR="$dir"
  if [[ ! -e "$dir" && ! -L "$dir" ]]; then
    return 3
  fi
  if [[ ! -d "$dir" ]]; then
    printf 'error: .harness/sessions exists but is not a directory\n' >&2
    return 1
  fi
  if [[ ! -r "$dir" || ! -x "$dir" ]]; then
    printf 'error: cannot read .harness/sessions/: permission denied\n' >&2
    return 1
  fi

  local had_nullglob=0 f base rows="" line
  shopt -q nullglob && had_nullglob=1
  shopt -s nullglob
  for f in "$dir"/*.md; do
    base="${f##*/}"
    base="${base%.md}"
    if [[ "$base" =~ $SESSION_NAME_RE ]]; then
      rows+="${BASH_REMATCH[3]}"$'\t'"${BASH_REMATCH[5]:-1}"$'\t'"$f"$'\n'
    fi
  done
  [[ $had_nullglob -eq 1 ]] || shopt -u nullglob

  [[ -z "$rows" ]] && return 0
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    SESSION_FILES+=("${line#*$'\t'*$'\t'}")
  done < <(printf '%s' "$rows" | sort -t $'\t' -k1,1r -k2,2nr)
  return 0
}

# Session ID (filename without .md) of a report path.
session_id() {
  local base="${1##*/}"
  printf '%s' "${base%.md}"
}

# Resolve a reference (full ID, timestamp, or any unique substring) against
# SESSION_FILES. An exact ID wins over substring matches.
# 0: unique match, path on stdout. 1: no match. 2: ambiguous, candidates on stderr.
resolve_id() {
  local ref="${1%.md}" f id matches=()
  for f in ${SESSION_FILES[@]+"${SESSION_FILES[@]}"}; do
    if [[ "$(session_id "$f")" == "$ref" ]]; then
      printf '%s\n' "$f"
      return 0
    fi
  done
  for f in ${SESSION_FILES[@]+"${SESSION_FILES[@]}"}; do
    id="$(session_id "$f")"
    if [[ "$id" == *"$ref"* ]]; then
      matches+=("$f")
    fi
  done
  case "${#matches[@]}" in
    0) return 1 ;;
    1) printf '%s\n' "${matches[0]}"; return 0 ;;
    *)
      printf 'Ambiguous reference "%s" matches:\n' "$ref" >&2
      for f in "${matches[@]}"; do
        printf '  %s\n' "$(session_id "$f")" >&2
      done
      return 2
      ;;
  esac
}

# Print the "## ..." heading that contains a given line number, ignoring
# headings inside fenced code blocks.
section_for_line() {
  local file="$1" target="$2"
  awk -v target="$target" '
    /^[[:space:]]*(```|~~~)/ { fence = !fence }
    !fence && /^## / { last = $0 }
    NR == target { print last; exit }
  ' "$file"
}
