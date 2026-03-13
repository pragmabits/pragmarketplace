#!/usr/bin/env bash
# Claude Code status line - Aura theme (ANSI colors)

# Force C locale for numeric formatting (decimal dot)
export LC_NUMERIC=C

input=$(cat)

cwd=$(echo "$input" | jq -r '.workspace.current_dir // .cwd')
model=$(echo "$input" | jq -r '.model.display_name')
used_pct=$(echo "$input" | jq -r '.context_window.used_percentage // empty')
duration_ms=$(echo "$input" | jq -r '.cost.total_duration_ms // empty')
lines_added=$(echo "$input" | jq -r '.cost.total_lines_added // empty')
lines_removed=$(echo "$input" | jq -r '.cost.total_lines_removed // empty')

# Project name (workspace folder name)
project_name="${cwd##*/}"

# Get git branch and status (skip optional locks, non-fatal)
git_branch=""
if git -C "$cwd" rev-parse --is-inside-work-tree --no-optional-locks >/dev/null 2>&1; then
  branch=$(git -C "$cwd" symbolic-ref --short HEAD 2>/dev/null || git -C "$cwd" rev-parse --short HEAD 2>/dev/null)
  if [ -n "$branch" ]; then
    git_icons=""

    # Staged changes (✓) - dim
    staged=$(git -C "$cwd" diff --cached --name-only 2>/dev/null | head -1)
    if [ -n "$staged" ]; then
      git_icons="${git_icons} \033[90m✓\033[0m"
    fi

    # Unstaged modified + untracked files (?) - dim
    modified=$(git -C "$cwd" diff --name-only 2>/dev/null | head -1)
    untracked=$(git -C "$cwd" ls-files --others --exclude-standard "$cwd" 2>/dev/null | head -1)
    if [ -n "$modified" ] || [ -n "$untracked" ]; then
      git_icons="${git_icons} \033[90m?\033[0m"
    fi

    # Deleted files (✗) - dim
    deleted=$(git -C "$cwd" diff --diff-filter=D --name-only 2>/dev/null | head -1)
    deleted_staged=$(git -C "$cwd" diff --cached --diff-filter=D --name-only 2>/dev/null | head -1)
    if [ -n "$deleted" ] || [ -n "$deleted_staged" ]; then
      git_icons="${git_icons} \033[90m✗\033[0m"
    fi

    # Ahead/behind remote (↑↓) - dim
    upstream=$(git -C "$cwd" rev-parse --abbrev-ref '@{upstream}' 2>/dev/null)
    if [ -n "$upstream" ]; then
      ahead=$(git -C "$cwd" rev-list --count '@{upstream}..HEAD' 2>/dev/null)
      behind=$(git -C "$cwd" rev-list --count 'HEAD..@{upstream}' 2>/dev/null)
      if [ "${ahead:-0}" -gt 0 ] 2>/dev/null; then
        git_icons="${git_icons} \033[90m↑\033[0m"
      fi
      if [ "${behind:-0}" -gt 0 ] 2>/dev/null; then
        git_icons="${git_icons} \033[90m↓\033[0m"
      fi
    fi

    if [ -n "$git_icons" ]; then
      git_branch=" \033[0;35m\ue0a0 ${branch}\033[0m |${git_icons}"
    else
      git_branch=" \033[0;35m\ue0a0 ${branch}\033[0m"
    fi
  fi
fi

# Format duration (ms -> Xh Ym Zs)
format_duration() {
  local ms=$1
  if [ -z "$ms" ] || [ "$ms" = "null" ]; then echo "0s"; return; fi
  local total_s=$((ms / 1000))
  local h=$((total_s / 3600))
  local m=$(( (total_s % 3600) / 60 ))
  local s=$((total_s % 60))
  if [ "$h" -gt 0 ]; then
    printf "%dh %dm %ds" "$h" "$m" "$s"
  elif [ "$m" -gt 0 ]; then
    printf "%dm %ds" "$m" "$s"
  else
    printf "%ds" "$s"
  fi
}

# Context usage indicator (color-coded) - green/yellow/red
ctx_info=""
if [ -n "$used_pct" ] && [ "$used_pct" != "null" ]; then
  pct_int=${used_pct%.*}
  if [ "$pct_int" -ge 80 ] 2>/dev/null; then
    ctx_info=" \033[0;31m🗗 ${pct_int}%\033[0m"
  elif [ "$pct_int" -ge 50 ] 2>/dev/null; then
    ctx_info=" \033[0;33m🗗 ${pct_int}%\033[0m"
  else
    ctx_info=" \033[1;34m🗗 ${pct_int}%\033[0m"
  fi
fi

# Lines changed - green/red
lines_info=""
if [ -n "$lines_added" ] && [ "$lines_added" != "null" ]; then
  lines_info=" \033[0;32m✚ ${lines_added}\033[0m \033[0;31m✘ ${lines_removed:-0}\033[0m"
fi

# Duration - yellow
dur_info=""
if [ -n "$duration_ms" ] && [ "$duration_ms" != "null" ]; then
  dur_fmt=$(format_duration "$duration_ms")
  dur_info=" \033[0;33m🕐 ${dur_fmt}\033[0m"
fi

printf "\033[1;34m%s\033[0m%b%s%b%s\033[0;36m🧠 %s\033[0m %s%b%s%b" \
  "$project_name" \
  "$git_branch" \
  " |" \
  "$lines_info" \
  " | " \
  "$model" \
  "|" \
  "$ctx_info" \
  " |" \
  "$dur_info"
