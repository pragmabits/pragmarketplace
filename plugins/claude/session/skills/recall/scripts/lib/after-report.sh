#!/usr/bin/env bash
# lib/after-report.sh — sourced by recall.sh. Read-only: it lists and reads
# files, and never creates or changes one.
#
# What no report records: the memories of this project that Claude Code
# changed after a given report, and the sessions in which the user wrote after
# the newest report. A session that ends without /report, or goes on after
# writing one, leaves what it decided, measured or found only in memory, so a
# lookup that reads the reports alone hands back a state one session or more
# behind, and nothing in it says so.
#
# Where Claude Code keeps them (read from Claude Code 2.1.325):
#   memory      — $CLAUDE_COWORK_MEMORY_PATH_OVERRIDE; else autoMemoryDirectory
#                 of the managed settings file, of <root>/.claude/settings.local.json
#                 or of the user settings (absolute, or ~/...); else
#                 <base>/projects/<key of the canonical root>/memory/, where
#                 the canonical root is the main working tree's root, which
#                 every worktree of the repository shares. Not read: a
#                 --settings file, managed-settings.d and server-managed policy.
#   transcripts — <config>/projects/<key of the repository root>/<session>.jsonl,
#                 for the sessions started at the repository root.
#   <config> is $CLAUDE_CONFIG_DIR or ~/.claude; <base> is
#   $CLAUDE_CODE_REMOTE_MEMORY_DIR or <config>. A key is
#   $CLAUDE_CODE_PROJECT_DIR_NAME, or the path with every UTF-16 unit outside
#   [a-zA-Z0-9] replaced by "-"; a key longer than 200 characters is cut there
#   and given a hash suffix, which is found here by its prefix.
#
# A resumed session continues in a new transcript that starts with a copy of
# the old one, every record given the new session's id; the first timestamp is
# what the two files share, so sessions are grouped by it.

AFTER_REPORT_KEY_MAX=200

claude_config_dir() {
  printf '%s' "${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
}

managed_settings_file() {
  case "$(uname -s 2>/dev/null)" in
    Darwin) printf '%s' "/Library/Application Support/ClaudeCode/managed-settings.json" ;;
    *) printf '%s' "/etc/claude-code/managed-settings.json" ;;
  esac
}

# Modification time of a file, in seconds since the epoch.
file_mtime() {
  stat -c %Y -- "$1" 2>/dev/null || stat -f %m -- "$1" 2>/dev/null
}

# The folder name Claude Code gives a path under <config>/projects. Args: path,
# projects folder. Fails when a long key matches no folder or several.
project_key() {
  local path="$1" projects="$2" key f matches=()
  if [[ -n "${CLAUDE_CODE_PROJECT_DIR_NAME:-}" ]]; then
    printf '%s' "$CLAUDE_CODE_PROJECT_DIR_NAME"
    return 0
  fi
  key="$(jq -r -n --arg p "$path" '$p | explode
    | map(if (. >= 48 and . <= 57) or (. >= 65 and . <= 90) or (. >= 97 and . <= 122) then [.]
          elif . > 65535 then [45, 45] else [45] end)
    | add // [] | implode')" || return 1
  if [[ ${#key} -le $AFTER_REPORT_KEY_MAX ]]; then
    printf '%s' "$key"
    return 0
  fi
  for f in "$projects/${key:0:$AFTER_REPORT_KEY_MAX}-"*; do
    [[ -d "$f" ]] && matches+=("${f##*/}")
  done
  [[ ${#matches[@]} -eq 1 ]] || return 1
  printf '%s' "${matches[0]}"
}

# The main working tree's root for a repository root; the root itself outside
# git or for a repository without a working tree of its own.
canonical_root() {
  local root="$1" common
  common="$(cd "$root" 2>/dev/null && git rev-parse --git-common-dir 2>/dev/null)" || common=""
  if [[ -z "$common" ]]; then
    printf '%s' "$root"
    return 0
  fi
  [[ "$common" == /* ]] || common="$root/$common"
  common="$(cd "$common" 2>/dev/null && pwd -P)" || common=""
  if [[ "${common##*/}" == ".git" ]]; then
    printf '%s' "${common%/*}"
  else
    printf '%s' "$root"
  fi
}

# Sets MEMORY_DIR and MEMORY_SOURCE, or MEMORY_REASON and returns 1.
memory_location() {
  local root="$1" file value base
  MEMORY_DIR=""
  MEMORY_SOURCE=""
  MEMORY_REASON=""
  if [[ -n "${CLAUDE_COWORK_MEMORY_PATH_OVERRIDE:-}" ]]; then
    MEMORY_DIR="${CLAUDE_COWORK_MEMORY_PATH_OVERRIDE%/}"
    MEMORY_SOURCE="CLAUDE_COWORK_MEMORY_PATH_OVERRIDE"
    return 0
  fi
  for file in "$(managed_settings_file)" "$root/.claude/settings.local.json" "$(claude_config_dir)/settings.json"; do
    [[ -r "$file" ]] || continue
    value="$(jq -r '.autoMemoryDirectory? // empty | strings' "$file" 2>/dev/null)" || value=""
    # A literal "~/" in the setting, expanded the way Claude Code does.
    # shellcheck disable=SC2088
    [[ "$value" == "~/"* ]] && value="$HOME/${value#\~/}"
    if [[ "$value" == /* ]]; then
      MEMORY_DIR="${value%/}"
      MEMORY_SOURCE="autoMemoryDirectory in $file"
      return 0
    fi
  done
  base="${CLAUDE_CODE_REMOTE_MEMORY_DIR:-$(claude_config_dir)}"
  if ! value="$(project_key "$(canonical_root "$root")" "$base/projects")"; then
    MEMORY_REASON="no single folder under $base/projects matches this repository's long path"
    return 1
  fi
  MEMORY_DIR="$base/projects/$value/memory"
  MEMORY_SOURCE="default"
}

# Memories changed after a moment, one line each: mtime, path, name and
# description from the front matter (empty when it does not close), separated
# by \037. A folded or literal block value is joined into one line. Args:
# folder, epoch.
list_memories() {
  local dir="$1" since="$2" f m
  while IFS= read -r f; do
    m="$(file_mtime "$f")" || continue
    if [[ ! "$m" =~ ^[0-9]+$ ]] || (( m <= since )); then continue; fi
    awk -v mtime="$m" -v path="$f" '
      NR == 1 { if ($0 !~ /^---[[:space:]]*$/) exit; next }
      /^---[[:space:]]*$/ { closed = 1; exit }
      block != "" {
        if ($0 ~ /^[[:space:]]+[^[:space:]]/) {
          line = $0; sub(/^[[:space:]]+/, "", line); sub(/[[:space:]]+$/, "", line)
          value[block] = value[block] (value[block] == "" ? "" : " ") line
          next
        }
        block = ""
      }
      /^(name|description):/ {
        key = ($0 ~ /^name:/) ? "name" : "description"
        if (key in value) next
        v = substr($0, index($0, ":") + 1); sub(/^[[:space:]]+/, "", v); sub(/[[:space:]]+$/, "", v)
        if (v ~ /^[>|][-+]?$/) { block = key; value[key] = "" } else value[key] = v
      }
      END {
        if (!closed) { value["name"] = ""; value["description"] = "" }
        printf "%s\037%s\037%s\037%s\n", mtime, path, value["name"], value["description"]
      }
    ' "$f" 2>/dev/null || true
  done < <(find -H "$dir" -type f -name '*.md' ! -name 'MEMORY.md' 2>/dev/null)
}

# Sessions in which the user wrote after a moment, one line each: id, first
# timestamp, mtime, prompts after the moment, separated by \037. A prompt is a
# user record with text of its own: not a tool result, a skill's or a hook's
# injected text, a compaction summary or a subagent's record. Sessions run
# through the SDK or `claude -p` (entrypoint sdk-*) are automation and left out.
# Args: transcripts folder, epoch, the same moment as YYYY-MM-DDTHH:MM:SSZ.
list_sessions() {
  local dir="$1" since="$2" since_iso="$3" f id m row
  for f in "$dir"/*.jsonl; do
    [[ -f "$f" ]] || continue
    id="${f##*/}"
    id="${id%.jsonl}"
    m="$(file_mtime "$f")" || continue
    if [[ ! "$m" =~ ^[0-9]+$ ]] || (( m <= since )); then continue; fi
    row="$(jq -R -n -r --arg since "${since_iso:0:19}" '
      def prompt: .type == "user" and (.isMeta | not) and (.isSidechain | not)
        and (.isCompactSummary | not) and (.isVisibleInTranscriptOnly | not)
        and ((.message.content | type) == "string"
             or ((.message.content | type) == "array" and any(.message.content[]; .type? == "text")));
      reduce (inputs | fromjson? | select(type == "object")) as $r ({started: null, entrypoint: null, prompts: 0};
        (if .started == null and ($r.timestamp | type) == "string" then
           .started = $r.timestamp | .entrypoint = ($r.entrypoint // "")
         else . end)
        | if ($r | prompt) and (($r.timestamp // "")[0:19] > $since) then .prompts += 1 else . end)
      | select(.started != null and .prompts > 0 and ((.entrypoint // "") | startswith("sdk") | not))
      | "\(.started)\u001f\(.prompts)"' "$f" 2>/dev/null)" || row=""
    [[ -n "$row" ]] || continue
    printf '%s\037%s\037%s\037%s\n' "$id" "${row%%$'\037'*}" "$m" "${row#*$'\037'}"
  done
}

# The after_report object. Args: the report that sets the moment for the
# memories, the newest report in the directory (the moment for the sessions),
# the repository root, the current session's id or "".
after_report_json() {
  local report="$1" newest="$2" root="$3" current="$4"
  local id newest_id ts since_iso since sessions_iso sessions_since
  local memories="" memory_state sessions="" sessions_state sessions_dir="" key
  id="${report##*/}"
  id="${id%.md}"
  newest_id="${newest##*/}"
  newest_id="${newest_id%.md}"
  [[ "$id" =~ $SESSION_NAME_RE ]] || { printf 'report name %s has no timestamp\n' "$id" >&2; return 1; }
  ts="${BASH_REMATCH[3]}"
  since_iso="${ts:0:13}:${ts:13:2}:${ts:15:2}Z"
  [[ "$newest_id" =~ $SESSION_NAME_RE ]] || { printf 'report name %s has no timestamp\n' "$newest_id" >&2; return 1; }
  ts="${BASH_REMATCH[3]}"
  sessions_iso="${ts:0:13}:${ts:13:2}:${ts:15:2}Z"
  since="$(jq -r -n --arg t "$since_iso" '$t | fromdateiso8601')" || return 1
  sessions_since="$(jq -r -n --arg t "$sessions_iso" '$t | fromdateiso8601')" || return 1

  if memory_location "$root"; then
    if [[ ! -e "$MEMORY_DIR" ]]; then
      memory_state="missing"
    elif [[ ! -d "$MEMORY_DIR" || ! -r "$MEMORY_DIR" || ! -x "$MEMORY_DIR" ]]; then
      memory_state="unreadable"
    else
      memory_state="read"
      memories="$(list_memories "$MEMORY_DIR" "$since")"
    fi
  else
    memory_state="unresolved"
  fi

  if key="$(project_key "$root" "$(claude_config_dir)/projects")"; then
    sessions_dir="$(claude_config_dir)/projects/$key"
    if [[ ! -e "$sessions_dir" ]]; then
      sessions_state="missing"
    elif [[ ! -d "$sessions_dir" || ! -r "$sessions_dir" || ! -x "$sessions_dir" ]]; then
      sessions_state="unreadable"
    else
      sessions_state="read"
      sessions="$(list_sessions "$sessions_dir" "$sessions_since" "$sessions_iso")"
    fi
  else
    sessions_state="unresolved"
  fi

  jq -n -c \
    --arg report "$id" --arg since "$since_iso" \
    --arg memory_state "$memory_state" --arg memory_dir "$MEMORY_DIR" \
    --arg memory_source "$MEMORY_SOURCE" --arg memory_reason "$MEMORY_REASON" --arg memories "$memories" \
    --arg newest "$newest_id" --arg sessions_since "$sessions_iso" \
    --arg sessions_state "$sessions_state" --arg sessions_dir "$sessions_dir" \
    --arg current "$current" --arg sessions "$sessions" '
    def clean: sub("^\\s+"; "") | sub("\\s+$"; "")
      | if test("^\".*\"$") then (fromjson? // .[1:-1])
        elif test("^'"'"'.*'"'"'$") then .[1:-1] | gsub("'"''"'"; "'"'"'")
        else . end
      | if . == "" then null else . end;
    def rows: split("\n") | map(select(length > 0) | split("\u001f"));
    {
      report: $report,
      since: $since,
      memory: ({state: $memory_state, dir: (if $memory_dir == "" then null else $memory_dir end)}
        + (if $memory_source != "" then {source: $memory_source} else {} end)
        + (if $memory_reason != "" then {reason: $memory_reason} else {} end)
        + {files: ($memories | rows
            | map({path: .[1], name: (.[2] // "" | clean), description: (.[3] // "" | clean),
                   modified: (.[0] | tonumber | todate)})
            | sort_by(.modified) | reverse)}),
      sessions: {
        after: $newest,
        since: $sessions_since,
        state: $sessions_state,
        dir: (if $sessions_dir == "" then null else $sessions_dir end),
        current: (if $current == "" then null else $current end),
        items: ($sessions | rows
          | map({id: .[0], started: .[1], last_active: (.[2] | tonumber | todate), prompts: (.[3] | tonumber)})
          | group_by(.started)
          | map(select(all(.[]; .id != $current)))
          | map({started: .[0].started, last_active: (map(.last_active) | max),
                 prompts_after: (map(.prompts) | max),
                 ids: (sort_by(.last_active) | reverse | map(.id))})
          | sort_by(.last_active) | reverse)
      }
    }'
}
