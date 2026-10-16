#!/usr/bin/env bash
# prepare-report.sh — metadata for the report skill, injected at render time.
#
# Read-only: creates no directory and no file. The save step creates the
# sessions directory (ensure-sessions-dir.sh) right before the report is written.
#
# One `date` call yields one instant; the header timestamp and the filename are
# both derived from it, so they cannot straddle a second boundary. When a report
# with that name already exists, the name gets a -2, -3, ... suffix instead of
# replacing it; /recall sorts the suffix after the plain name.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/sessions-dir.sh
source "${SCRIPT_DIR}/lib/sessions-dir.sh"

root="$(resolve_sessions_root)"
sessions_dir="$root/.harness/sessions"

git_user="$(git config user.name 2>/dev/null || true)"
file_user="$(printf '%s' "$git_user" | tr '[:upper:]' '[:lower:]' | sed -E 's/[[:space:]]+/-/g; s/[^a-z0-9._-]//g')"
if [[ -z "$file_user" || "$file_user" == "unknown" ]]; then
  file_user="unknown-user"
fi
[[ -z "$git_user" ]] && git_user="unknown"

stamp="$(date -u +%Y-%m-%dT%H%M%SZ)"
name_ts="${stamp%Z}"

id="${file_user}-${name_ts}"
n=2
while [[ -e "${sessions_dir}/${id}.md" ]]; do
  if [[ $n -gt 99 ]]; then
    printf 'error: more than 98 reports named %s-%s already exist\n' "$file_user" "$name_ts" >&2
    exit 1
  fi
  id="${file_user}-${name_ts}-${n}"
  n=$((n + 1))
done
path="${sessions_dir}/${id}.md"

head_line="not a git repository"
head_subject=""
in_git="no"
status_lines=""
if (cd "$root" && git rev-parse --is-inside-work-tree >/dev/null 2>&1); then
  in_git="yes"
  if hash="$(cd "$root" && git rev-parse --short HEAD 2>/dev/null)"; then
    head_line="$hash"
    head_subject="$(cd "$root" && git log -1 --format=%s 2>/dev/null || true)"
  else
    head_line="no commits yet"
  fi
  status_lines="$(cd "$root" && git status --short 2>/dev/null || true)"

  # Repository state, read now. Remote-tracking refs are this clone's last view
  # of the remote: nothing is fetched, so the remote itself is not seen. No
  # branch name is printed.
  if ! (cd "$root" && git symbolic-ref -q HEAD >/dev/null 2>&1); then
    upstream_line="HEAD is detached; there is no upstream branch to compare with"
  elif counts="$(cd "$root" && git rev-list --left-right --count '@{upstream}...HEAD' 2>/dev/null)"; then
    behind="${counts%%[[:space:]]*}"
    ahead="${counts##*[[:space:]]}"
    upstream_line="${ahead} local commit(s) not in the upstream branch, ${behind} upstream commit(s) not here — as this clone last saw the remote; nothing was fetched"
  else
    upstream_line="no upstream branch configured"
  fi
  staged=0; unstaged=0; untracked=0
  while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    if [[ "${line:0:2}" == "??" ]]; then untracked=$((untracked + 1)); continue; fi
    [[ "${line:0:1}" != " " ]] && staged=$((staged + 1))
    [[ "${line:1:1}" != " " ]] && unstaged=$((unstaged + 1))
  done <<< "$status_lines"
  stashes="$(cd "$root" && git stash list 2>/dev/null | wc -l | tr -d ' ')"
  operation="none"
  for marker in MERGE_HEAD:merge rebase-merge:rebase rebase-apply:rebase CHERRY_PICK_HEAD:cherry-pick REVERT_HEAD:revert BISECT_LOG:bisect; do
    if [[ -e "$(cd "$root" && git rev-parse --git-path "${marker%%:*}")" ]]; then
      operation="${marker#*:}"
      break
    fi
  done
fi

if [[ -d "$sessions_dir" ]]; then
  dir_state="exists"
else
  dir_state="does not exist yet; the save step creates it"
fi

printf -- '- Git user: %s\n' "$git_user"
printf -- '- Timestamp (UTC): %s\n' "$stamp"
printf -- '- Session ID: %s\n' "$id"
printf -- '- Report path: %s\n' "$path"
printf -- '- Sessions directory: %s\n' "$dir_state"
printf -- '- HEAD observed at generation: %s\n' "$head_line"
if [[ -n "$head_subject" ]]; then
  printf -- '- HEAD subject (context only; not copied into the report): %s\n' "$head_subject"
fi
if [[ "$in_git" == "yes" ]]; then
  printf -- '- Git repository: yes\n'
else
  printf -- '- Git repository: no — the report can be written but not committed\n'
fi

printf '\nHelper commands (run each exactly as written, one Bash call each):\n'
printf -- '- Create the directory: bash %q %q\n' "${SCRIPT_DIR}/ensure-sessions-dir.sh" "$sessions_dir"
printf -- '- Report origin: bash %q\n' "${SCRIPT_DIR}/report-origin.sh"
printf -- '- Check the report: bash %q %q\n' "${SCRIPT_DIR}/check-report.sh" "$path"
printf -- '- Commit the report: bash %q %q\n' "${SCRIPT_DIR}/commit-report.sh" "$path"

if [[ "$in_git" == "yes" ]]; then
  printf '\nRepository state at generation (read just now; the only basis for any statement about the current state of the repository):\n'
  printf -- '- Upstream: %s\n' "$upstream_line"
  printf -- '- Changes: %d staged, %d unstaged, %d untracked file(s)\n' "$staged" "$unstaged" "$untracked"
  printf -- '- Stash entries: %s\n' "$stashes"
  printf -- '- Operation in progress: %s\n' "$operation"

  printf '\nWorking tree at generation (context only: it can hold work that predates this session or belongs to someone else, so it is not evidence of what this session changed):\n'
  if [[ -z "$status_lines" ]]; then
    printf '    clean\n'
  else
    total="$(printf '%s\n' "$status_lines" | wc -l | tr -d ' ')"
    printf '%s\n' "$status_lines" | head -n 50 | sed 's/^/    /'
    if [[ "$total" -gt 50 ]]; then
      printf '    (%d more entries not shown; run git status to see them)\n' "$((total - 50))"
    fi
  fi
fi
