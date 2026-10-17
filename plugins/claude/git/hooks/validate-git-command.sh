#!/bin/bash
set -euo pipefail

# Validate git commands to prevent interactive or problematic patterns.
# Blocks: git add -p (interactive), git -C (path resolution issues),
# git config user.name/email (intrusive identity changes), cd before git in
# one command (Claude Code asks for approval), git run below the repository
# root (the commit workflow's paths are relative to the root).

if ! command -v jq &>/dev/null; then
  echo '{"systemMessage": "jq is required but not installed. validate-git-command.sh cannot run."}' >&2
  exit 2
fi

input=$(cat)
command=$(echo "$input" | jq -r '.tool_input.command // ""')
# The directory the command runs in: Claude Code updates it after a cd.
cwd=$(echo "$input" | jq -r '.cwd // ""')

# No command — nothing to check
if [[ -z "$command" ]]; then
  exit 0
fi

# Only check git commands
if ! echo "$command" | grep -qE '(^|\s|&&|\|\||;|\()git\s'; then
  exit 0
fi

# Block git add -p / --patch (interactive, fails in headless environments)
# Match -p/--patch only as standalone flags, not inside paths like .claude-plugin/
if echo "$command" | grep -qE 'git\s+add\s+(.+\s+)?(-p|--patch)(\s|$)'; then
  cat >&2 <<'EOF'
{
  "hookSpecificOutput": {
    "permissionDecision": "deny"
  },
  "systemMessage": "git add -p is blocked because it requires interactive input. Use whole-file `git add <files>` — the commit workflow groups files by semantic intent rather than splitting hunks within a file."
}
EOF
  exit 2
fi

# Block git -C flag (causes path resolution issues)
if echo "$command" | grep -qE 'git\s+-C\s'; then
  cat >&2 <<'EOF'
{
  "hookSpecificOutput": {
    "permissionDecision": "deny"
  },
  "systemMessage": "git -C flag is blocked because it causes path resolution issues. Run git commands from the repository root instead."
}
EOF
  exit 2
fi

# Block git config user.name / user.email modifications
if echo "$command" | grep -qE 'git\s+config\s+(--global\s+)?user\.(name|email)'; then
  cat >&2 <<'EOF'
{
  "hookSpecificOutput": {
    "permissionDecision": "deny"
  },
  "systemMessage": "Modifying git user.name or user.email is blocked. The user's git identity is already configured — changing it would be intrusive."
}
EOF
  exit 2
fi

deny() {
  jq -n --arg msg "$1" '{hookSpecificOutput: {permissionDecision: "deny"}, systemMessage: $msg}' >&2
  exit 2
}

# Locate the repository root of the directory the command runs in.
here=""
root=""
if [[ -n "$cwd" && -d "$cwd" ]]; then
  here=$(cd "$cwd" && pwd -P) || here=""
  if [[ -n "$here" ]]; then
    root=$(cd "$here" && git rev-parse --show-toplevel 2>/dev/null) || root=""
  fi
fi
where=""
if [[ -n "$root" ]]; then
  where=" This shell is in $here; its repository root is $root."
fi
# Claude Code refuses a cd outside the project directory, so a root above it
# cannot be reached, and git below the root is blocked only when it can.
reachable=""
if [[ -n "$root" && -n "${CLAUDE_PROJECT_DIR:-}" ]]; then
  project=$(cd "$CLAUDE_PROJECT_DIR" 2>/dev/null && pwd -P) || project=""
  if [[ -n "$project" && ( "$root" == "$project" || "$root" == "$project"/* ) ]]; then
    reachable=1
  fi
fi

# Block cd before git in one command. Claude Code asks for approval for any
# command that changes directory before running git, even when the permission
# rules allow the git command.
cd_first='^[[:space:]]*[(]?[[:space:]]*(cd|pushd)([[:space:]]|$)'
if [[ "$command" =~ $cd_first ]] && grep -qE '(^|&&|\|\||;|\|)\s*git(\s|$)' <<< "$command"; then
  deny "cd before git in one command is blocked: Claude Code asks for approval for any command that changes directory before running git, even when the permission rules allow it. Run the cd as its own Bash call, then the git command without a prefix.$where"
fi

# Block git run below the repository root. Locating the root is allowed.
locate='^[[:space:]]*git[[:space:]]+rev-parse([[:space:]]+--show-(toplevel|prefix))+[[:space:]]*$'
if [[ -n "$reachable" && "$here" != "$root" ]] && ! [[ "$command" =~ $locate ]] \
  && grep -qE '(^|&&|\|\||;|\||\()\s*git(\s|$)' <<< "$command"; then
  deny "git commands run from the repository root, and this shell is in $here. Run \`cd $root\` as its own Bash call, then the git command without a prefix."
fi

# All checks passed
exit 0
