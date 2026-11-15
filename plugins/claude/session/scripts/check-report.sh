#!/usr/bin/env bash
# check-report.sh — check a written session report before it is staged.
#
# Usage: check-report.sh <report-path>
#
# Prints one finding per line, "<category>: [line N: ]<message>", and never the
# offending value itself:
#   sensitive  — a credential-shaped value (lib/sensitive.sh)
#   privacy    — the project's absolute path, or a linked worktree's name
#   structure  — a missing, duplicated or out-of-order anchor, a field that
#                new reports no longer carry, or a §6.3 that is not the
#                template's table of defects
#   coherence  — the header timestamp disagrees with the filename
#
# Exit: 0 no findings, 1 findings, 2 usage error or unreadable file.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/sensitive.sh
source "${SCRIPT_DIR}/lib/sensitive.sh"

if [[ $# -ne 1 ]]; then
  printf 'Usage: check-report.sh <report-path>\n' >&2
  exit 2
fi
file="$1"
if [[ ! -f "$file" || ! -r "$file" ]]; then
  printf 'error: cannot read report: %s\n' "$file" >&2
  exit 2
fi

findings=()
add() { findings+=("$1"); }

# --- sensitive ---------------------------------------------------------------
while IFS="$(printf '\t')" read -r ln kind; do
  [[ -z "$ln" ]] && continue
  add "sensitive: line $ln: $kind — remove the value, keep what the reader needs to understand the problem"
done < <(sensitive_scan "$file")

# --- privacy -----------------------------------------------------------------
dir="$(cd "$(dirname "$file")" && pwd)"
dir_phys="$(cd "$dir" && pwd -P)"
roots=()
for d in "$dir" "$dir_phys"; do
  case "$d" in
    */.harness/sessions) roots+=("${d%/.harness/sessions}") ;;
  esac
done
reported_roots=""
for r in ${roots[@]+"${roots[@]}"}; do
  [[ -z "$r" || "$r" == "/" ]] && continue
  case "$reported_roots" in *"|$r|"*) continue ;; esac
  reported_roots+="|$r|"
  while IFS= read -r ln; do
    [[ -z "$ln" ]] && continue
    add "privacy: line $ln: absolute project path — use a path relative to the project"
  done < <(grep -a -nF -- "$r" "$file" 2>/dev/null | cut -d: -f1 | sort -n -u || true)
done

# A linked worktree's name and location stay out of reports. Its location is
# the project path above; its name is the directory and the worktree id.
if [[ ${#roots[@]} -gt 0 ]] && git_dir="$(cd "${roots[0]}" && git rev-parse --absolute-git-dir 2>/dev/null)" \
   && common_dir="$(cd "${roots[0]}" && cd "$(git rev-parse --git-common-dir 2>/dev/null)" && pwd -P)" \
   && [[ "$(cd "$git_dir" && pwd -P)" != "$common_dir" ]]; then
  main_name="$(basename "$(dirname "$common_dir")")"
  for name in "$(basename "${roots[0]}")" "$(basename "$git_dir")"; do
    [[ ${#name} -lt 3 || "$name" == "$main_name" ]] && continue
    while IFS= read -r ln; do
      [[ -z "$ln" ]] && continue
      add "privacy: line $ln: worktree name — leave the worktree's name and location out of the report"
    done < <(grep -a -nwF -- "$name" "$file" 2>/dev/null | cut -d: -f1 | sort -n -u || true)
  done
fi

# --- structure ---------------------------------------------------------------
# Headings and fields count only outside fenced code blocks.
outside_fences() {
  awk '
    /^[[:space:]]*(```|~~~)/ { fence = !fence; next }
    !fence { printf "%d\t%s\n", NR, $0 }
  ' "$file"
}
body="$(outside_fences)"

first_line="$(awk 'NF { print; exit }' "$file")"
case "$first_line" in
  '# Session Report: '?*) ;;
  *) add "structure: the first line must be '# Session Report: <title>'" ;;
esac

anchor_line() { # $1 = ERE matched against the line text; prints matching line numbers
  # ENVIRON instead of -v: -v would process the backslashes in the pattern.
  printf '%s\n' "$body" | ANCHOR_RE="$1" awk -F '\t' '
    { line = $0; sub(/^[0-9]+\t/, "", line) }
    line ~ ENVIRON["ANCHOR_RE"] { print $1 }
  '
}

prev=0
prev_label=""
for spec in \
  '^## Session contract|## Session contract' \
  '^## 1\.|## 1.' '^## 2\.|## 2.' '^## 3\.|## 3.' '^## 4\.|## 4.' '^## 5\.|## 5.' '^## 6\.|## 6.' \
  '^### 6\.1|### 6.1' '^### 6\.2|### 6.2' '^### 6\.3|### 6.3'; do
  re="${spec%%|*}"
  label="${spec#*|}"
  lines="$(anchor_line "$re")"
  count="$(printf '%s' "$lines" | grep -c . || true)"
  if [[ "$count" -eq 0 ]]; then
    add "structure: missing heading '$label'"
    continue
  fi
  if [[ "$count" -gt 1 ]]; then
    add "structure: heading '$label' appears $count times"
  fi
  first="$(printf '%s\n' "$lines" | head -n1)"
  if [[ "$first" -lt "$prev" ]]; then
    add "structure: line $first: heading '$label' comes before '$prev_label'"
  fi
  prev="$first"
  prev_label="$label"
done

ts_lines="$(anchor_line '^\*\*Timestamp \(UTC\):\*\* ')"
header_ts=""
if [[ -z "$ts_lines" ]]; then
  add "structure: missing '**Timestamp (UTC):**' field"
else
  header_ts="$(sed -n "$(printf '%s\n' "$ts_lines" | head -n1)p" "$file" | sed 's/^\*\*Timestamp (UTC):\*\* *//; s/[[:space:]]*$//')"
  if ! [[ "$header_ts" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{6}Z$ ]]; then
    add "structure: line $(printf '%s\n' "$ts_lines" | head -n1): timestamp is not in YYYY-MM-DDTHHMMSSZ form"
    header_ts=""
  fi
fi

status_line="$(printf '%s\n' "$body" | awk -F '\t' '
  { line = $0; sub(/^[0-9]+\t/, "", line) }
  line ~ /^## Session contract/ { inside = 1; next }
  inside && line ~ /^## / { exit }
  inside && line ~ /^\*\*Goal status:\*\*/ { print $1 "\t" line; exit }
')"
if [[ -z "$status_line" ]]; then
  add "structure: missing '**Goal status:**' in the Session contract"
else
  value="${status_line#*$'\t'}"
  value="${value#\*\*Goal status:\*\*}"
  value="$(printf '%s' "$value" | sed 's/^[[:space:]]*//; s/[[:space:]]*$//')"
  case "$value" in
    achieved|partial|abandoned|redirected) ;;
    *) add "structure: line ${status_line%%$'\t'*}: goal status must be one of achieved, partial, abandoned, redirected" ;;
  esac
fi

while IFS= read -r ln; do
  [[ -z "$ln" ]] && continue
  add "structure: line $ln: new reports carry no Branch field"
done < <(anchor_line '^\*\*Branch:\*\*')

if [[ -z "$(anchor_line '^\*\*Harness:\*\* +[^ ]')" ]]; then
  add "structure: missing '**Harness:**' field — copy it from Report origin; unknown is a valid value"
fi
while IFS= read -r ln; do
  [[ -z "$ln" ]] && continue
  add "structure: line $ln: new reports carry no Model field — no documented source identifies the model"
done < <(anchor_line '^\*\*Model:\*\*')

# §6.3 holds only defects: the template's table and nothing else, or `none`,
# and a Status cell that says confirmed or suspected (code marks, emphasis and
# case aside). A qualifier such as "(by choice)" or "(code reading)" marks
# something that is not a defect, or belongs in Evidence.
while IFS="$(printf '\t')" read -r ln kind; do
  [[ -z "$ln" ]] && continue
  case "$kind" in
    status) add "structure: line $ln: a §6.3 Status is confirmed or suspected and nothing else — a qualifier goes in Evidence; what is not a defect leaves §6.3" ;;
    no-status) add "structure: line $ln: the §6.3 table has no Status column" ;;
    no-separator) add "structure: line $ln: the §6.3 table has no separator row under its header, so /recall cannot read it" ;;
    no-table) add "structure: line $ln: §6.3 is the template's table, or none" ;;
    extra) add "structure: line $ln: §6.3 holds only the template's table — text next to it goes in its section or out of the report" ;;
  esac
done < <(printf '%s\n' "$body" | awk -F '\t' '
  function trim(s) { sub(/^[[:space:]]+/, "", s); sub(/[[:space:]]+$/, "", s); return s }
  # A cell value without code marks or emphasis, in lower case.
  function plain(s) { gsub(/[`*_]/, "", s); return tolower(trim(s)) }
  # Table cells, honoring \| as a literal pipe inside a cell.
  function cells(s, out,    n, i) {
    gsub(/\\\|/, "\001", s)
    s = trim(s); sub(/^\|/, "", s); sub(/\|$/, "", s)
    n = split(s, out, "|")
    for (i = 1; i <= n; i++) { gsub(/\001/, "|", out[i]); out[i] = trim(out[i]) }
    return n
  }
  { n = $1; line = $0; sub(/^[0-9]+\t/, "", line) }
  line ~ /^### 6\.3/ { inside = 1; start = n; next }
  inside && line ~ /^(#|##|###) / { inside = 0 }
  !inside { next }
  line ~ /^[[:space:]]*$/ || line ~ /^[[:space:]]*(---+|\*\*\*+|___+)[[:space:]]*$/ { next }
  line ~ /^[[:space:]]*\|/ {
    rows++
    if (rows == 1) {
      k = cells(line, head)
      for (i = 1; i <= k; i++) if (plain(head[i]) == "status") col = i
      if (!col) print n "\tno-status"
      next
    }
    # The separator row, as /recall reads it: three dashes or more per cell.
    if (rows == 2 && line ~ /^[[:space:]]*\|?[[:space:]]*:?---+:?[[:space:]]*(\|[[:space:]]*:?---+:?[[:space:]]*)*\|?[[:space:]]*$/) next
    if (rows == 2) print n "\tno-separator"
    if (col) {
      cells(line, c)
      v = plain(c[col])
      if (v != "confirmed" && v != "suspected") print n "\tstatus"
    }
    next
  }
  { other++; if (!first_other) first_other = n; if (tolower(line) ~ /^[[:space:]]*[*_`]*[[:space:]]*(none|nenhum|nenhuma|n\/a)[[:space:]]*[*_`]*[[:space:]]*\.?[[:space:]]*$/) none = 1 }
  END {
    if (!start) exit
    if (rows == 0 && !(none && other == 1)) print start "\tno-table"
    else if (rows > 0 && other > 0) print first_other "\textra"
  }
')

# --- coherence ---------------------------------------------------------------
base="$(basename "$file" .md)"
if [[ "$base" =~ -([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{6})(-[0-9]+)?$ ]]; then
  name_ts="${BASH_REMATCH[1]}"
  if [[ -n "$header_ts" && "${header_ts%Z}" != "$name_ts" ]]; then
    add "coherence: header timestamp ${header_ts} does not match the filename timestamp ${name_ts}"
  fi
else
  add "coherence: filename is not <user>-<YYYY-MM-DDTHHMMSS>[-N].md, so /recall will not list it"
fi

if [[ ${#findings[@]} -eq 0 ]]; then
  exit 0
fi
printf '%s\n' "${findings[@]}"
exit 1
