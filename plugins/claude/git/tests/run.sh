#!/usr/bin/env bash
# tests/run.sh — deterministic tests for the git plugin's PreToolUse guard.
#
# Usage: bash plugins/claude/git/tests/run.sh
#
# Each case feeds validate-git-command.sh a fake PreToolUse input on stdin:
# tool_input.command and cwd, the directory Claude Code will run the command
# in, with CLAUDE_PROJECT_DIR set as Claude Code sets it for hooks.
# Repositories are temporary, and git is isolated from the user's
# configuration (GIT_CONFIG_GLOBAL, GIT_CONFIG_NOSYSTEM, HOME).
set -uo pipefail

PLUGIN="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HOOK="$PLUGIN/hooks/validate-git-command.sh"

ROOT_TMP="$(mktemp -d "${TMPDIR:-/tmp}/git-guard-tests.XXXXXX")"
ROOT_TMP="$(cd "$ROOT_TMP" && pwd -P)"
trap 'rm -rf "$ROOT_TMP"' EXIT

export HOME="$ROOT_TMP/home"
mkdir -p "$HOME"
export GIT_CONFIG_NOSYSTEM=1
export GIT_CONFIG_GLOBAL="$ROOT_TMP/gitconfig"
export GIT_CEILING_DIRECTORIES="$ROOT_TMP"
unset GIT_DIR GIT_WORK_TREE
git config --file "$GIT_CONFIG_GLOBAL" init.defaultBranch main

pass=0
fail=0
ok()     { pass=$((pass + 1)); printf 'ok - %s\n' "$1"; }
not_ok() {
  fail=$((fail + 1))
  printf 'not ok - %s\n' "$1"
  if [[ -n "${2:-}" ]]; then printf '%s\n' "$2" | sed 's/^/    # /'; fi
}

# Runs the hook. Args: cwd, command. Sets RC and MSG (the systemMessage).
run_hook() {
  local err
  err="$(jq -n --arg cwd "$1" --arg cmd "$2" '{cwd: $cwd, tool_input: {command: $cmd}}' | bash "$HOOK" 2>&1 >/dev/null)"
  RC=$?
  MSG="$(jq -r '.systemMessage // empty' <<< "$err" 2>/dev/null || printf '%s' "$err")"
}

# Args: description, cwd, command.
expect_pass() {
  run_hook "$2" "$3"
  if [[ $RC -eq 0 ]]; then ok "$1"; else not_ok "$1" "rc=$RC: $MSG"; fi
}

# Args: description, cwd, command, text the message must contain.
expect_deny() {
  run_hook "$2" "$3"
  if [[ $RC -ne 2 ]]; then not_ok "$1" "rc=$RC, expected a denial"; return; fi
  if [[ "$MSG" != *"$4"* ]]; then not_ok "$1" "missing: $4"$'\n'"in: $MSG"; return; fi
  ok "$1"
}

REPO="$ROOT_TMP/repo"
mkdir -p "$REPO/web" "$REPO/cmd" "$ROOT_TMP/outside"
git init -q "$REPO"
ln -s "$REPO" "$ROOT_TMP/link"
export CLAUDE_PROJECT_DIR="$REPO"

# The cases of the report (git-raiz-do-projeto.md).
expect_deny "(a) git from a subdirectory is denied, naming the root" \
  "$REPO/web" "git add cmd/x.go" "Run \`cd $REPO\` as its own Bash call"
expect_deny "(b) cd before git in one command is denied" \
  "$REPO" "cd $REPO && git commit -m \"fix: x\"" "Run the cd as its own Bash call"
expect_pass "(c) git from the root passes" "$REPO" "git add cmd/x.go"
expect_pass "(d) a non-git command outside any repository passes" "$ROOT_TMP/outside" "ls -la"

# cd before git.
expect_deny "cd from a subdirectory before git is denied, naming the root" \
  "$REPO/web" "cd $REPO && git add cmd/x.go" "its repository root is $REPO"
expect_deny "cd before git in a subshell is denied" "$REPO" "(cd web && git status)" "Run the cd as its own Bash call"
expect_deny "cd before git separated by ; is denied" "$REPO" "cd web; git status" "Run the cd as its own Bash call"
expect_deny "cd and git on separate lines are denied" "$REPO" $'cd web\ngit status' "Run the cd as its own Bash call"
expect_deny "pushd before git is denied" "$REPO" "pushd web && git status" "Run the cd as its own Bash call"
expect_deny "cd before git outside any repository is denied" \
  "$ROOT_TMP/outside" "cd $REPO && git status" "Run the cd as its own Bash call"
expect_pass "cd alone passes" "$REPO/web" "cd $REPO"
expect_pass "cd before a non-git command passes" "$REPO" "cd web && npm test"
expect_pass "a commit message that mentions cd and git passes" \
  "$REPO" "git commit -m \"docs: explain why cd web && git status asks for approval\""

# git below the root.
expect_deny "git later in a compound command from a subdirectory is denied" \
  "$REPO/web" "npm test && git status" "Run \`cd $REPO\`"
expect_deny "git in a command substitution from a subdirectory is denied" \
  "$REPO/web" "echo \$(git rev-parse HEAD)" "Run \`cd $REPO\`"
expect_pass "locating the root from a subdirectory passes" "$REPO/web" "git rev-parse --show-toplevel --show-prefix"
expect_pass "a command that only mentions git passes in a subdirectory" "$REPO/web" "grep -rn git ."
expect_pass "a non-git command passes in a subdirectory" "$REPO/web" "npm run build"
expect_pass "git from the root reached through a symlink passes" "$ROOT_TMP/link" "git status"
expect_pass "git inside .git passes (no work tree to compare)" "$REPO/.git" "git status"
expect_pass "git outside any repository passes" "$ROOT_TMP/outside" "git init"
expect_pass "an input without cwd keeps the previous checks only" "" "git add cmd/x.go"

# A session opened in a subdirectory cannot cd to a root above it.
CLAUDE_PROJECT_DIR="$REPO/web" expect_pass "git below a root outside the project directory passes" \
  "$REPO/web" "git add index.html"
CLAUDE_PROJECT_DIR="$ROOT_TMP" expect_deny "git below a root inside the project directory is denied" \
  "$REPO/web" "git status" "Run \`cd $REPO\`"
CLAUDE_PROJECT_DIR="$ROOT_TMP/link" expect_deny "a project directory reached through a symlink still counts" \
  "$REPO/web" "git status" "Run \`cd $REPO\`"
CLAUDE_PROJECT_DIR="" expect_pass "without CLAUDE_PROJECT_DIR, git below the root passes" "$REPO/web" "git status"
CLAUDE_PROJECT_DIR="$REPO/web" expect_deny "cd before git is denied whatever the project directory" \
  "$REPO/web" "cd $REPO && git status" "Run the cd as its own Bash call"

# The earlier checks are unchanged.
expect_deny "git add -p is denied" "$REPO" "git add -p ." "git add -p is blocked"
expect_deny "git -C is denied" "$REPO" "git -C web status" "git -C flag is blocked"
expect_deny "git config user.name is denied" "$REPO" "git config user.name x" "Modifying git user.name"

printf '\n%d passed, %d failed\n' "$pass" "$fail"
[[ $fail -eq 0 ]]
