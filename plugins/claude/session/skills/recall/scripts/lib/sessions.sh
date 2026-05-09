#!/usr/bin/env bash
# lib/sessions.sh — sourced helpers for the recall skill.
# Reads session report files written by the report skill and exposes
# extraction primitives. Anchors mirror plugins/claude/session/skills/report/SKILL.md.
#
# Filename pattern: <git-user>-YYYY-MM-DDTHHMMSS.md (UTC, no Z).
# Lex-descending sort on filenames == timestamp-descending sort.

# Resolve the sessions directory. Delegates to the plugin-scoped resolver so
# both report and recall agree on the location (CLAUDE_PROJECT_DIR > git toplevel > pwd).
sessions_dir() {
  bash "${CLAUDE_PLUGIN_ROOT}/scripts/ensure-sessions-dir.sh"
}

# Print absolute paths of *.md files in the sessions dir, newest first.
# Sort key is the YYYY-MM-DDTHHMMSS suffix in the filename so that the user
# prefix never dominates the order. Files without that suffix are skipped here
# (they are not valid session reports — distinct from "malformed but valid name").
list_session_files() {
  local dir
  dir="$(sessions_dir)" || return 1
  [[ -d "$dir" ]] || return 1
  shopt -s nullglob
  local f base ts
  for f in "$dir"/*.md; do
    base="$(basename "$f" .md)"
    ts="$(printf '%s' "$base" | grep -oE '[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{6}$' || true)"
    [[ -z "$ts" ]] && continue
    printf '%s\t%s\n' "$ts" "$f"
  done | sort -r | cut -f2-
  shopt -u nullglob
}

# Extract one TSV metadata row: session_id<TAB>title<TAB>timestamp<TAB>branch<TAB>status
extract_meta() {
  local file="$1"
  local id title timestamp branch status
  id="$(basename "$file" .md)"
  title="$(grep -m1 '^# Session Report: ' "$file" | sed 's/^# Session Report: //')"
  timestamp="$(grep -m1 '^\*\*Timestamp (UTC):\*\* ' "$file" | sed 's/^\*\*Timestamp (UTC):\*\* //')"
  branch="$(grep -m1 '^\*\*Branch:\*\* ' "$file" | sed 's/^\*\*Branch:\*\* //; s/`//g')"
  status="$(awk '
    /^## Session contract/ { in_block = 1; next }
    in_block && /^\*\*Goal status:\*\*/ {
      sub(/^\*\*Goal status:\*\* */, "")
      print
      exit
    }
    in_block && /^## / { exit }
  ' "$file")"
  printf '%s\t%s\t%s\t%s\t%s\n' "$id" "$title" "$timestamp" "$branch" "$status"
}

# Return 0 if the file is missing required anchors (title or timestamp), else 1.
is_malformed() {
  local file="$1"
  if ! grep -q '^# Session Report: ' "$file"; then return 0; fi
  if ! grep -q '^\*\*Timestamp (UTC):\*\* ' "$file"; then return 0; fi
  return 1
}

# Resolve an ID reference (full ID, timestamp-only, or substring) to an absolute path.
# 0: unique match (path on stdout). 1: no match. 2: ambiguous (candidates on stderr).
resolve_id() {
  local ref="$1"
  ref="${ref%.md}"
  local dir
  dir="$(sessions_dir)" || return 1
  [[ -d "$dir" ]] || return 1
  local matches=()
  while IFS= read -r f; do
    local base
    base="$(basename "$f" .md)"
    if [[ "$base" == "$ref" ]] || [[ "$base" == *"$ref"* ]]; then
      matches+=("$f")
    fi
  done < <(ls -1 "$dir"/*.md 2>/dev/null)
  case "${#matches[@]}" in
    0) return 1 ;;
    1) printf '%s\n' "${matches[0]}"; return 0 ;;
    *)
      printf 'Ambiguous reference "%s" matches:\n' "$ref" >&2
      for m in "${matches[@]}"; do
        printf '  %s\n' "$(basename "$m" .md)" >&2
      done
      return 2
      ;;
  esac
}

# Print the body of section ## N. (numeric N) up to the next "## " heading.
extract_section() {
  local file="$1"
  local n="$2"
  awk -v n="$n" '
    $0 ~ "^## " n "\\." { capture = 1; next }
    capture && /^## / { exit }
    capture { print }
  ' "$file"
}

# Print the "## N. <title>" heading that contains a given line number.
section_for_line() {
  local file="$1"
  local target="$2"
  awk -v target="$target" '
    /^## [0-9]/ { last = $0 }
    NR == target { print last; exit }
  ' "$file"
}

# Extract git user (filename prefix before the timestamp).
session_user() {
  local id="$1"
  echo "$id" | sed -E 's/-[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{6}$//'
}
