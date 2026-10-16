#!/usr/bin/env bash
# commit-report.sh — commit one new session report, and nothing else.
#
# Usage: commit-report.sh <report-path>
#
# The report is staged by path and committed with `git commit --only`, which
# builds the commit from HEAD plus that one path. Other index entries and
# working-tree files are not touched: no reset, restore or stash. Hooks,
# signing and identity are the repository's own; this script never passes
# --no-verify, --no-gpg-sign or -c overrides, and makes a single attempt.
#
# Output is "key: value" lines, starting with "result: <outcome>". Git's own
# output is shown only on failure, redacted (lib/sensitive.sh), with the
# project path replaced by <project>, and capped at 20 lines.
#
# Exit codes:
#   0  committed and verified, or already committed with identical content
#   2  usage error
#   3  check-report.sh found problems; nothing was staged
#   4  refused before staging (not a git work tree, operation in progress,
#      ignored path, no usable identity, path already committed with other
#      content, not a report filename)
#   5  git add failed; nothing was committed
#   6  git commit failed; the report's index entry was removed again and the
#      file is unchanged on disk
#   7  a commit was created but verification found a problem
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/sensitive.sh
source "${SCRIPT_DIR}/lib/sensitive.sh"

# Every pathspec below is a literal path, never a glob.
export GIT_LITERAL_PATHSPECS=1
# Untranslated git messages, so that classify() can read them under any
# locale. LANGUAGE only selects message catalogs; character handling (LC_CTYPE)
# is left alone, so hooks that depend on it behave as usual.
export LANGUAGE=en

top=""

say() { printf '%s\n' "$1"; }

# Print captured git output for the user: redacted, project path hidden, capped.
diagnostic() {
  local text="$1" line total shown=0
  [[ -z "$text" ]] && return 0
  total="$(printf '%s\n' "$text" | wc -l | tr -d ' ')"
  say "diagnostic (git and hook output, redacted):"
  while IFS= read -r line; do
    [[ $shown -ge 20 ]] && break
    if [[ -n "$top" ]]; then line="${line//"$top"/<project>}"; fi
    printf '  %s\n' "$line"
    shown=$((shown + 1))
  done < <(printf '%s\n' "$text" | sensitive_redact)
  if [[ "$total" -gt 20 ]]; then
    say "  ($((total - 20)) more lines not shown)"
  fi
}

classify() {
  local text="$1"
  if printf '%s' "$text" | grep -qiE 'tell me who you are|unable to auto-detect email|empty ident|author identity unknown|invalid ident'; then
    say "category: identity — git has no usable author identity; the repository's configuration needs the user's attention"
  elif printf '%s' "$text" | grep -qiE 'gpg failed|failed to sign|signing failed|cannot run gpg|gpg:|ssh-keygen|no secret key|signing key|error: load key'; then
    say "category: signing — the repository requires signed commits and signing failed"
  elif printf '%s' "$text" | grep -qiE 'index\.lock|unable to create .*\.lock|cannot lock ref|another git process'; then
    say "category: lock — another git process holds a lock"
  elif printf '%s' "$text" | grep -qiE 'ignored by one of your \.gitignore'; then
    say "category: ignored — the repository ignores this path"
  elif printf '%s' "$text" | grep -qiE 'partial commit during a merge|in the middle of a merge'; then
    say "category: operation-in-progress — a merge is in progress"
  elif printf '%s' "$text" | grep -qiE 'permission denied|read-only file system|no space left'; then
    say "category: filesystem — the repository could not be written"
  else
    say "category: rejected — git reported no error of its own, which usually means a hook refused the commit; its output is below"
  fi
}

refuse() { # $1 = exit code, $2 = result, $3 = reason, [$4 = category line]
  say "result: $2"
  if [[ -n "${4:-}" ]]; then say "category: $4"; fi
  say "reason: $3"
  say "staged: no"
  exit "$1"
}

if [[ $# -ne 1 ]]; then
  printf 'Usage: commit-report.sh <report-path>\n' >&2
  exit 2
fi
if [[ ! -f "$1" ]]; then
  printf 'error: report not found: %s\n' "$1" >&2
  exit 2
fi

dir="$(cd "$(dirname "$1")" && pwd -P)"
name="$(basename "$1")"
abs="${dir}/${name}"
# check-report.sh looks for both the logical and the physical project path,
# so it gets the logical one; abs stays physical for comparing with git.
logical="$(cd "$(dirname "$1")" && pwd)/${name}"

base="${name%.md}"
if [[ "$name" != *.md ]] || ! [[ "$base" =~ -([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{6}(-[0-9]+)?)$ ]]; then
  refuse 4 refused "not a session report filename (<user>-<YYYY-MM-DDTHHMMSS>[-N].md)"
fi
message="chore: add session report ${BASH_REMATCH[1]}"

cd "$dir" || refuse 4 refused "cannot enter the report's directory"
if ! top="$(git rev-parse --show-toplevel 2>/dev/null)" || [[ -z "$top" ]]; then
  refuse 4 refused "the report is not inside a git work tree"
fi
top="$(cd "$top" && pwd -P)"
case "$abs" in
  "$top"/*) rel="${abs#"$top"/}" ;;
  *) refuse 4 refused "the report is outside the repository's work tree" ;;
esac
cd "$top" || refuse 4 refused "cannot enter the repository root"

for marker in MERGE_HEAD CHERRY_PICK_HEAD REVERT_HEAD rebase-merge rebase-apply; do
  if [[ -e "$(git rev-parse --git-path "$marker")" ]]; then
    refuse 4 refused "a merge, rebase, cherry-pick or revert is in progress ($marker)"
  fi
done

head_before="$(git rev-parse -q --verify HEAD 2>/dev/null || true)"

# A report already in HEAD is either the result of an earlier attempt (same
# content: nothing to do, no duplicate commit) or a historical report that is
# not rewritten.
if [[ -n "$head_before" ]] && git cat-file -e "HEAD:${rel}" 2>/dev/null; then
  if [[ "$(git rev-parse "HEAD:${rel}")" == "$(git hash-object -- "$rel")" ]]; then
    say "result: already-committed"
    say "commit: $(git log -1 --format=%h -- "$rel")"
    say "note: HEAD already holds this report with identical content; no new commit was made"
    exit 0
  fi
  refuse 4 refused "this path is already committed with different content; committed reports are not rewritten"
fi

# Conditions git would only report after staging, checked before it.
# check-ignore rejects the literal pathspec magic, hence the override.
if GIT_LITERAL_PATHSPECS=0 git check-ignore -q -- "$rel" 2>/dev/null; then
  refuse 4 refused "the repository's ignore rules cover $rel; committing it would mean forcing it" \
    "ignored — the repository ignores this path"
fi
if ! git var GIT_AUTHOR_IDENT >/dev/null 2>&1 || ! git var GIT_COMMITTER_IDENT >/dev/null 2>&1; then
  refuse 4 refused "git has no usable author or committer identity in this repository" \
    "identity — the repository's configuration needs the user's attention"
fi

if ! findings="$(bash "${SCRIPT_DIR}/check-report.sh" "$logical" 2>&1)"; then
  say "result: check-failed"
  say "staged: no"
  say "findings (fix these in the report, then run this command again):"
  printf '%s\n' "$findings" | sed 's/^/  /'
  exit 3
fi

others_snapshot() {
  git ls-files -s | awk -F '\t' -v p="$rel" '$2 != p' | git hash-object --stdin
}
others_before="$(others_snapshot)"

if ! add_out="$(git add -- "$rel" 2>&1)"; then
  say "result: add-failed"
  say "staged: unknown — check git status for $rel"
  classify "$add_out"
  diagnostic "$add_out"
  exit 5
fi

commit_out="$(git commit --only -m "$message" -- "$rel" 2>&1)"
commit_rc=$?

head_after="$(git rev-parse -q --verify HEAD 2>/dev/null || true)"

# Confirm a new HEAD holds exactly this report, on top of the previous HEAD,
# and that no other index entry moved. Prints the first problem found.
verify_commit() {
  local parent files
  parent="$(git rev-parse -q --verify 'HEAD^' 2>/dev/null || true)"
  if [[ "$parent" != "$head_before" ]]; then
    say "verification: HEAD's parent is not the HEAD observed before the commit"
    return 1
  fi
  files="$(git diff-tree --root --no-commit-id --name-only -r HEAD)"
  if [[ "$files" != "$rel" ]]; then
    say "verification: the commit contains other paths than the report"
    return 1
  fi
  if [[ "$(git rev-parse "HEAD:${rel}")" != "$(git hash-object -- "$rel")" ]]; then
    say "verification: the committed content differs from the report on disk"
    return 1
  fi
  if [[ "$(others_snapshot)" != "$others_before" ]]; then
    say "verification: index entries of other paths changed during the commit (a hook may have modified them)"
    return 1
  fi
  return 0
}

if [[ -n "$head_after" && "$head_after" != "$head_before" ]]; then
  if verify_commit; then
    say "result: committed"
    say "commit: $(git rev-parse --short HEAD)"
    say "message: $message"
    if [[ $commit_rc -ne 0 ]]; then
      say "note: git exited with status $commit_rc, but the commit exists and was verified"
    fi
    exit 0
  fi
  say "result: committed-unverified"
  say "commit: $(git rev-parse --short HEAD)"
  say "note: a commit was created; nothing was undone. Inspect it before relying on it"
  diagnostic "$commit_out"
  exit 7
fi

# No commit. Remove the report's index entry again so that no version of it
# stays staged; the file on disk is untouched. Only this path is affected.
say "result: commit-failed"
classify "$commit_out"
# -f only lifts git's "staged content differs" guard; with --cached the file on
# disk is never removed.
if git rm --cached -f -q -- "$rel" >/dev/null 2>&1 && [[ -z "$(git ls-files -s -- "$rel")" ]]; then
  say "staged: no — the report's index entry was removed; the file is unchanged on disk"
else
  say "staged: unknown — the report's index entry could not be confirmed removed; check git status for $rel"
fi
if [[ "$(others_snapshot)" != "$others_before" ]]; then
  say "warning: index entries of other paths changed during the attempt (a hook may have modified them)"
fi
diagnostic "$commit_out"
exit 6
