#!/usr/bin/env bash
# lib/report-user.sh — the user part of a report's filename. Sourced.
#
# /report names a report <user>-<YYYY-MM-DDTHHMMSS>[-N].md from the git user
# name, and /recall --me and --user look for that same name. Both derive it
# here, so the two cannot drift apart.

# Print the filename form of a user name: lowercased, each run of whitespace
# turned into -, characters outside [a-z0-9._-] dropped. Prints nothing when
# nothing is left.
report_file_user() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]' | sed -E 's/[[:space:]]+/-/g; s/[^a-z0-9._-]//g'
}
