#!/usr/bin/env bash
# lib/sessions-dir.sh — sourced by every script that needs the sessions directory.
#
# resolve_sessions_dir prints <root>/.harness/sessions and never creates anything.
# Creating the directory is the job of ensure-sessions-dir.sh, which only the
# report save step runs. /recall resolves through here and stays read-only.
#
# Root precedence:
#   1. git rev-parse --show-toplevel of the current directory
#   2. $CLAUDE_PROJECT_DIR, when it names an existing directory
#   3. the current directory
# The git root comes first because the harness can set CLAUDE_PROJECT_DIR=$HOME
# while the user works inside an unrelated repository.

resolve_sessions_root() {
  local root
  if root="$(git rev-parse --show-toplevel 2>/dev/null)" && [[ -n "$root" ]]; then
    :
  elif [[ -n "${CLAUDE_PROJECT_DIR:-}" && -d "$CLAUDE_PROJECT_DIR" ]]; then
    root="$CLAUDE_PROJECT_DIR"
  else
    root="$(pwd)" || return 1
  fi
  printf '%s' "$root"
}

resolve_sessions_dir() {
  local root
  root="$(resolve_sessions_root)" || return 1
  printf '%s/.harness/sessions' "$root"
}
