#!/usr/bin/env bash
# ensure-sessions-dir.sh — create the sessions directory and print its path.
#
# Usage: ensure-sessions-dir.sh [<sessions-dir>]
#
# Run only by the report save step, right before the report is written. With an
# argument, creates exactly that directory (prepare-report.sh prints it, so the
# save step does not depend on the shell's current directory); it must end in
# /.harness/sessions. Without one, resolves the directory the same way /recall does.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=lib/sessions-dir.sh
source "${SCRIPT_DIR}/lib/sessions-dir.sh"

if [[ $# -gt 1 ]]; then
  printf 'Usage: ensure-sessions-dir.sh [<sessions-dir>]\n' >&2
  exit 2
fi

if [[ $# -eq 1 ]]; then
  dir="$1"
  if [[ "$dir" != /* || "$dir" != */.harness/sessions ]]; then
    printf 'error: expected an absolute path ending in /.harness/sessions (got: %s)\n' "$dir" >&2
    exit 2
  fi
else
  dir="$(resolve_sessions_dir)"
fi

mkdir -p -- "$dir"
printf '%s' "$dir"
