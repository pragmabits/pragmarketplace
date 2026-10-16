#!/usr/bin/env bash
# lib/sensitive.sh — credential shapes shared by check-report.sh (scan) and
# commit-report.sh (redaction of git diagnostics before they reach the chat).
#
# A report carries no credential value of any kind: not a real one, and not an
# example, a fake, a test value or a placeholder shaped like one. So a token
# shape is a finding even when its body is filler (xxxx, ****), and a value
# given to a credential name is a finding unless it is a reference to an
# environment variable. Only prose (a plain word after "token:") and
# references ($NAME, ${NAME}, %NAME%) pass.
#
# This is a second barrier behind the model's own review of the report, not a
# guarantee: it recognizes common credential shapes, not every secret, and it
# does not look for personal data.
#
# Patterns are POSIX ERE and case-sensitive on purpose, so that grep -E and
# sed -E behave the same on GNU and BSD. Case-insensitive words are spelled
# with bracket pairs by _sensitive_ci.

_sensitive_ci() {
  local word="$1" out="" c upper lower i
  for ((i = 0; i < ${#word}; i++)); do
    c="${word:i:1}"
    case "$c" in
      [A-Za-z])
        upper="$(printf '%s' "$c" | tr '[:lower:]' '[:upper:]')"
        lower="$(printf '%s' "$c" | tr '[:upper:]' '[:lower:]')"
        out+="[${upper}${lower}]" ;;
      *) out+="$c" ;;
    esac
  done
  printf '%s' "$out"
}

SENSITIVE_KINDS=()
SENSITIVE_RES=()

_sensitive_add() {
  SENSITIVE_KINDS+=("$1")
  SENSITIVE_RES+=("$2")
}

_sensitive_init() {
  local q="'" bt='`' key flag
  key="[A-Za-z0-9_.-]*($(_sensitive_ci password)|$(_sensitive_ci passwd)|$(_sensitive_ci passphrase)"
  key+="|$(_sensitive_ci secret)|$(_sensitive_ci token)|$(_sensitive_ci api)[_-]?$(_sensitive_ci key)"
  key+="|$(_sensitive_ci access)[_-]?$(_sensitive_ci key)|$(_sensitive_ci private)[_-]?$(_sensitive_ci key)"
  key+="|$(_sensitive_ci credentials?))"
  flag="--($(_sensitive_ci password)|$(_sensitive_ci passwd)|$(_sensitive_ci pass)|$(_sensitive_ci token)"
  flag+="|$(_sensitive_ci api)-?$(_sensitive_ci key)|$(_sensitive_ci secret))"

  _sensitive_add "private key block"             '-----BEGIN [A-Z0-9 ]*PRIVATE KEY( BLOCK)?-----'
  _sensitive_add "GitHub token"                  'gh[pousr]_[A-Za-z0-9]{16,}'
  _sensitive_add "GitHub token"                  'github_pat_[A-Za-z0-9_]{16,}'
  _sensitive_add "GitLab token"                  'glpat-[A-Za-z0-9_-]{16,}'
  _sensitive_add "npm token"                     'npm_[A-Za-z0-9]{16,}'
  _sensitive_add "API secret key"                'sk-[A-Za-z0-9_-]{16,}'
  _sensitive_add "API key"                       '(sk|pk|rk)_(live|test)_[A-Za-z0-9]{8,}'
  _sensitive_add "AWS access key id"             '(AKIA|ASIA)[0-9A-Z]{16}'
  _sensitive_add "Slack token"                   'xox[abposr]-[A-Za-z0-9-]{8,}'
  _sensitive_add "Google API key"                'AIza[0-9A-Za-z_-]{30,}'
  _sensitive_add "JSON web token"                'eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}'
  _sensitive_add "URL with embedded credentials" '[A-Za-z][A-Za-z0-9+.-]*://[^/[:space:]:@]+:[^/[:space:]@]+@'
  _sensitive_add "bearer token"                  '[Bb]earer [A-Za-z0-9._~+/=-]{20,}'
  _sensitive_add "basic authorization"           '[Aa]uthorization:[[:space:]]*[Bb]asic [A-Za-z0-9+/=]{8,}'
  _sensitive_add "credential on a command line"  "${flag}[= ][\"${q}${bt}]?[^[:space:]\"${q}${bt}]{3,}"
  _sensitive_add "credential assignment"         "${key}[\"${q}]?[[:space:]]*[:=][*_]*[[:space:]]*[\"${q}${bt}]?[^[:space:]\"${q}${bt},;)]{4,}"
}
_sensitive_init

_sensitive_lower() {
  printf '%s' "$1" | tr '[:upper:]' '[:lower:]'
}

# Return 0 for a reference to an environment variable: $NAME, ${NAME}, %NAME%.
# A reference names where the value lives without containing it.
_sensitive_env_ref() {
  [[ "$1" =~ ^\$\{?[A-Za-z_][A-Za-z0-9_]*\}?$ || "$1" =~ ^%[A-Za-z_][A-Za-z0-9_]*%$ ]]
}

# Values people type as stand-ins for a password; a report shows none of them.
_sensitive_stand_in() {
  case "$(_sensitive_lower "$1")" in
    changeme|change_me|password|passwd|passw0rd|p@ssw0rd|secret|admin|root|letmein|hunter2|qwerty|example|sample|dummy|fake|test|testing|placeholder|redacted|default|foobar) return 0 ;;
  esac
  return 1
}

# Decide whether one grep match is a finding. Args: kind, matched text.
_sensitive_is_finding() {
  local kind="$1" m="$2" v sep quoted=0
  case "$kind" in
    "credential assignment")
      sep="$(printf '%s' "$m" | sed -E 's/^[^:=]*([:=]).*/\1/')"
      v="$(printf '%s' "$m" | sed -E 's/^[^:=]*[:=][*_]*[[:space:]]*//')"
      case "$v" in \"*|\'*|\`*) quoted=1; v="${v:1}" ;; esac
      _sensitive_env_ref "$v" && return 1
      case "$v" in /*|./*|~/*) return 1 ;; esac         # file paths
      # "KEY=value" and quoted values are assignments, whatever the value.
      if [[ "$sep" == "=" || $quoted -eq 1 ]]; then return 0; fi
      # "key: value" is often prose; a lone word ("token: refreshed") passes,
      # a stand-in, a value with digits or symbols, or a long one does not.
      [[ "$v" =~ ^[0-9]+$ ]] && return 1                 # counts, ids
      _sensitive_stand_in "$v" && return 0
      if [[ "$v" =~ [^A-Za-z-] || ${#v} -ge 16 ]]; then return 0; fi
      return 1 ;;
    "credential on a command line")
      v="$(printf '%s' "$m" | sed -E 's/^--[A-Za-z-]+[= ]["'"'"'`]?//')"
      _sensitive_env_ref "$v" && return 1
      return 0 ;;
    "URL with embedded credentials")
      v="${m#*://}"; v="${v#*:}"; v="${v%@}"
      _sensitive_env_ref "$v" && return 1
      return 0 ;;
    *)
      # Token shapes, keys and headers: a finding whether real or invented.
      return 0 ;;
  esac
}

# Print "<line><TAB><kind>" for every finding in a file, sorted by line.
# Never prints the matched value.
sensitive_scan() {
  local file="$1" i re kind out ln match
  for i in "${!SENSITIVE_RES[@]}"; do
    re="${SENSITIVE_RES[$i]}"
    kind="${SENSITIVE_KINDS[$i]}"
    while IFS= read -r out; do
      [[ -z "$out" ]] && continue
      ln="${out%%:*}"
      match="${out#*:}"
      _sensitive_is_finding "$kind" "$match" || continue
      printf '%s\t%s\n' "$ln" "$kind"
    done < <(grep -a -noE -e "$re" -- "$file" 2>/dev/null || true)
  done | sort -t "$(printf '\t')" -k1,1n -k2 -u
}

# Copy stdin to stdout with every credential-shaped match replaced by [REDACTED].
# Over-redacts references and prose; that is acceptable for diagnostics.
sensitive_redact() {
  local args=() i
  for i in "${!SENSITIVE_RES[@]}"; do
    args+=(-e "s#${SENSITIVE_RES[$i]}#[REDACTED]#g")
  done
  sed -E "${args[@]}"
}
