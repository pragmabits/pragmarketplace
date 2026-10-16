# lib/report.jq — parse session reports and render /recall output.
#
# Run as: jq -R -n -r -f report.jq --arg mode <mode> [--arg ...] <files...>
# recall.sh passes the files already sorted newest first; this program keeps
# that order. Anchors mirror plugins/claude/session/skills/report/SKILL.md and
# stay compatible with reports written by earlier versions (Branch, Base
# commit, "If partial, abandoned, or redirected").
#
# Modes: list, filter, last, resume.

def ws_trim: sub("^\\s+"; "") | sub("\\s+$"; "");

# Group raw input lines by file, keeping the argument order.
def group_inputs:
  reduce inputs as $l ([];
    input_filename as $f
    | ($l | rtrimstr("\r")) as $t
    | if length > 0 and .[-1].file == $f then .[-1].lines += [$t]
      else . + [{file: $f, lines: [$t]}] end);

# true for lines outside fenced code blocks; fence lines themselves are false.
def structural_flags:
  reduce .[] as $l ({fence: false, out: []};
    if ($l | test("^\\s*(```|~~~)")) then .fence = (.fence | not) | .out += [false]
    else .out += [(.fence | not)] end)
  | .out;

def first_index($L; $S; $from; $to; $re):
  first(range($from; $to) | select($S[.] and ($L[.] | test($re)))) // null;

def field_in($L; $from; $to; $label):
  ("**" + $label + ":**") as $p
  | first(range($from; $to) | select($L[.] | startswith($p)) | $L[.] | ltrimstr($p) | ws_trim) // null;

def is_blank: test("^\\s*$");
def is_rule: test("^\\s*(-{3,}|\\*{3,}|_{3,})\\s*$");
def is_none_line: test("^\\s*[*_`]*\\s*(none|nenhum|nenhuma|n/a)\\s*[*_`]*\\s*\\.?\\s*$"; "i");
def is_table_line: test("^\\s*\\|");
def is_sep_line: test("^\\s*\\|?\\s*:?-{3,}:?\\s*(\\|\\s*:?-{3,}:?\\s*)*\\|?\\s*$");
def is_bullet: test("^([-*+]|[0-9]+[.)]) ");
def is_indented: test("^\\s+\\S");
def row_closed: test("(?<!\\\\)\\|\\s*$");

# Table cells, honoring \| as a literal pipe inside a cell.
def cells:
  gsub("\\\\\\|"; "\u0001") | ws_trim | ltrimstr("|")
  | (if endswith("|") then .[:-1] else . end)
  | split("|") | map(gsub("\u0001"; "|") | ws_trim);

# Classify the body of a pending subsection (or any table section).
# Input rows: [{n: line number, t: text}]. States:
#   items        rows were read
#   none         the subsection says `none` and nothing else
#   incomplete   rows were read but at least one looks cut off
#   unrecognized content that is neither a table with rows, a list, nor `none`
def classify($rows):
  ($rows | map(select((.t | is_blank | not) and (.t | is_rule | not)))) as $c
  | if ($c | length) == 0 then
      {state: "unrecognized", reason: "empty (expected a table or `none`)"}
    elif ($c | length) == 1 and ($c[0].t | is_none_line) then
      {state: "none"}
    else
      ($c | map(select(.t | is_table_line))) as $tbl
      | ($c | map(select(.t | is_table_line | not))) as $other
      | if ($tbl | length) > 0 then
          if ($tbl | length) < 2 or ($tbl[1].t | is_sep_line | not) then
            {state: "unrecognized", reason: "table without a header separator", unparsed: ($c | map(.t))}
          else
            ($tbl[0].t | cells) as $cols
            | ($tbl[2:]) as $data
            | if ($data | length) == 0 then
                {state: "unrecognized", reason: "table has no rows (an empty subsection is written as `none`)", columns: $cols}
                + (if ($other | length) > 0 then {notes: ($other | map(.t))} else {} end)
              else
                ($data | map(select(.t | row_closed | not)) | map(.n)) as $open
                | {state: (if ($open | length) > 0 then "incomplete" else "items" end),
                   columns: $cols,
                   items: ($data | map({label: (.t | cells | .[0]), raw: .t, cells: (.t | cells), line: .n}))}
                + (if ($open | length) > 0
                   then {reason: "row at line \($open | map(tostring) | join(", ")) does not end with | (possibly truncated)"}
                   else {} end)
                + (if ($other | length) > 0 then {notes: ($other | map(.t))} else {} end)
              end
          end
        else
          (reduce $c[] as $r ({items: [], notes: []};
             if ($r.t | is_bullet) then
               ($r.t | sub("^([-*+]|[0-9]+[.)]) +"; "")) as $label
               | .items += [{label: $label, raw: $r.t, cells: [$label], line: $r.n}]
             elif ($r.t | is_indented) and (.items | length) > 0 then
               .items[-1].raw += "\n" + $r.t
             else .notes += [$r.t] end)) as $b
          | if ($b.items | length) > 0 then
              {state: "items", columns: null, items: $b.items}
              + (if ($b.notes | length) > 0 then {notes: $b.notes} else {} end)
            else
              {state: "unrecognized", reason: "neither a table, a list, nor `none`", unparsed: ($c | map(.t))}
            end
        end
    end;

def rows_between($L; $from; $to):
  [range($from; $to) | {n: (. + 1), t: $L[.]}];

# A header field, backticks dropped; null when absent.
def header_field($L; $to; $label):
  field_in($L; 0; $to; $label) | if . == null then null else gsub("`"; "") | ws_trim end;

# The Model field keeps four cases apart: a confirmed identifier, an alias
# reported as such, an explicit unknown, and no field at all (older reports).
# Values are data: any identifier is accepted, none is looked up.
def model_info:
  if . == null then {state: "absent", value: null}
  elif ascii_downcase == "unknown" then {state: "unknown", value: null}
  elif test("^alias:"; "i") then {state: "alias", value: (sub("^alias:\\s*"; ""; "i"))}
  else {state: "confirmed", value: .} end;

def parse_report($file; $L):
  ($L | structural_flags) as $S
  | ($L | length) as $len
  | ($file | split("/") | last | sub("\\.md$"; "")) as $id
  | ($id | capture("^(?:(?<user>.*)-)?(?<ts>[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{6})(?:-(?<n>[0-9]+))?$") // {user: null, ts: null, n: null}) as $name
  | (first_index($L; $S; 0; $len; "^## ") // $len) as $first_h2
  | (first(range(0; $len) | select($S[.] and ($L[.] | startswith("# Session Report: "))) | $L[.] | ltrimstr("# Session Report: ") | ws_trim) // null) as $title
  | field_in($L; 0; $len; "Timestamp (UTC)") as $timestamp
  | (field_in($L; 0; $len; "Branch") | if . == null then null else gsub("`"; "") | ws_trim end) as $branch
  | first_index($L; $S; 0; $len; "^## Session contract") as $ci
  | (if $ci == null then null else (first_index($L; $S; $ci + 1; $len; "^## ") // $len) end) as $ce
  | (if $ci == null then {} else {
        goal: field_in($L; $ci; $ce; "User goal (entering session)"),
        goal_status: field_in($L; $ci; $ce; "Goal status"),
        direction_changes: field_in($L; $ci; $ce; "Direction changes"),
        status_note: (field_in($L; $ci; $ce; "Status evidence")
                      // field_in($L; $ci; $ce; "If partial, abandoned, or redirected"))
      } end) as $contract
  | (($contract.goal_status // "") | ascii_downcase
     | first(match("achieved|partial|abandoned|redirected").string) // null) as $status_word
  | first_index($L; $S; 0; $len; "^## 2\\.") as $s2
  | (if $s2 == null then null else
       (first_index($L; $S; $s2 + 1; $len; "^## ") // $len) as $e2
       | [range($s2 + 1; $e2) | select($S[.] and ($L[.] | test("^### "))) | $L[.] | ltrimstr("### ") | ws_trim]
     end) as $topics
  | first_index($L; $S; 0; $len; "^## 4\\.") as $s4
  | (if $s4 == null then {state: "missing", reason: "section 4 (Decisions) not found"} else
       (first_index($L; $S; $s4 + 1; $len; "^## ") // $len) as $e4
       | classify(rows_between($L; $s4 + 1; $e4))
     end) as $decisions
  | first_index($L; $S; 0; $len; "^## 6\\.") as $s6
  | (if $s6 == null then
       {state: "incomplete",
        reasons: ["section 6 (Pending Items) not found — the report may be truncated or in an unrecognized format"],
        subsections: {}}
     else
       (first_index($L; $S; $s6 + 1; $len; "^## ") // $len) as $e6
       | (reduce (["in_progress", "6\\.1", "6.1"], ["promised", "6\\.2", "6.2"], ["known_issues", "6\\.3", "6.3"]) as $k ({};
           first_index($L; $S; $s6 + 1; $e6; "^### " + $k[1]) as $h
           | .[$k[0]] =
               (if $h == null then {state: "missing", reason: "heading ### \($k[2]) not found"}
                else
                  (first_index($L; $S; $h + 1; $e6; "^#{1,3} ") // $e6) as $he
                  | classify(rows_between($L; $h + 1; $he)) + {line: ($h + 1)}
                end))) as $subs
       | ([$subs | to_entries[] | select(.value.state != "items" and .value.state != "none")
           | "\(.key): \(.value.state)\(if .value.reason then " — " + .value.reason else "" end)"]) as $reasons
       | {state: (if ([$subs[] | .state] | all(. == "none")) then "none"
                  elif ($reasons | length) > 0 then "incomplete"
                  else "items" end),
          subsections: $subs}
         + (if ($reasons | length) > 0 then {reasons: $reasons} else {} end)
     end) as $pending
  | {
      session_id: $id,
      file_path: $file,
      user: $name.user,
      name_timestamp: $name.ts,
      title: $title,
      timestamp: $timestamp,
      branch: $branch,
      goal: $contract.goal,
      goal_status: $contract.goal_status,
      status_word: $status_word,
      status_note: $contract.status_note,
      direction_changes: $contract.direction_changes,
      work_topics: $topics,
      decisions: $decisions,
      pending: $pending,
      origin: {
        harness: header_field($L; $first_h2; "Harness"),
        model: (header_field($L; $first_h2; "Model") | model_info),
        agent: header_field($L; $first_h2; "Agent"),
        harness_version: header_field($L; $first_h2; "Harness version"),
        report_generator: header_field($L; $first_h2; "Report generator")
      },
      malformed: ($title == null or $timestamp == null)
    };

def md: gsub("\\|"; "\\|");

def pending_counts:
  .pending as $p
  | if $p.state == "none" then {in_progress: 0, promised: 0, known_issues: 0}
    else ($p.subsections // {}) as $s
      | reduce ("in_progress", "promised", "known_issues") as $k ({};
          .[$k] = (if $s[$k].state == "items" then ($s[$k].items | length)
                   elif $s[$k].state == "none" then 0
                   else null end))
    end;

def table($rows; $with_branch; $limit; $total):
  (if $with_branch then
     "| Session ID | Title | Timestamp | Branch | Status |\n|------------|-------|-----------|--------|--------|"
   else
     "| Session ID | Title | Timestamp | Status |\n|------------|-------|-----------|--------|"
   end),
  ($rows | (if $limit > 0 then .[:$limit] else . end) | .[]
   | if $with_branch then
       "| \(.session_id | md) | \(.title // "" | md) | \(.timestamp // "" | md) | \(.branch // "" | md) | \(.goal_status // "" | md) |"
     else
       "| \(.session_id | md) | \(.title // "" | md) | \(.timestamp // "" | md) | \(.goal_status // "" | md) |"
     end),
  (if $limit > 0 and $total > $limit then
     "\n\($total) total, showing \($limit). Use --limit <higher> or filter further to see more."
   else empty end);

# Files that are not shown, so that a short listing is never mistaken for a
# complete one.
def notices($bad):
  (if ($bad | length) > 0 then
     "\nSkipped \($bad | length) file(s) without the '# Session Report:' title or the '**Timestamp (UTC):**' field: \($bad | map(.session_id) | join(", "))"
   else empty end),
  (if $empty_ids != "" then "\nSkipped empty file(s): \($empty_ids)" else empty end),
  (if $unreadable_ids != "" then "\nCould not read: \($unreadable_ids)" else empty end);

group_inputs
| map(parse_report(.file; .lines)) as $all
| ($limit | tonumber? // 0) as $lim
| if $mode == "list" then
    ($all | map(select(.malformed | not))) as $ok
    | ($all | map(select(.malformed))) as $bad
    | if ($ok | length) == 0 then
        "No sessions found in .harness/sessions/", notices($bad)
      else
        table($ok; false; $lim; $ok | length), notices($bad)
      end
  elif $mode == "filter" then
    ($all | map(select(.malformed | not))
     | map(select(
         ($f_user == "" or ((.user // "") | ascii_downcase) == ($f_user | ascii_downcase))
         and ($f_branch == "" or .branch == $f_branch)
         and ($f_status == "" or .status_word == $f_status)
         and ($f_since == "" or ((.name_timestamp // "")[0:10]) >= $f_since)
         and ($f_until == "" or ((.name_timestamp // "")[0:10]) <= $f_until)))) as $hits
    | if ($hits | length) == 0 then "No sessions match: \($criteria)", notices([])
      else table($hits; $f_branch != ""; $lim; $hits | length), notices([]) end
  elif $mode == "last" then
    {
      requested: $lim,
      available: ($available | tonumber? // ($all | length)),
      sessions: [$all[] | {
        session_id, file_path, title, timestamp, goal_status, goal, status_note, origin,
        work_topics, pending_state: .pending.state, pending_counts: pending_counts,
        malformed
      }],
      skipped_empty: $empty_ids,
      unreadable: $unreadable_ids
    }
  elif $mode == "resume" then
    $all[0] as $r
    | {
        session_id: $r.session_id,
        title: $r.title,
        file_path: $r.file_path,
        timestamp: $r.timestamp,
        goal: $r.goal,
        goal_status: $r.goal_status,
        status_note: $r.status_note,
        direction_changes: $r.direction_changes,
        origin: $r.origin,
        pending_state: $r.pending.state
      }
    + (if $item != "" then {requested_item: $item} else {} end)
    + (if $r.pending.state == "none" then {empty: true} else {} end)
    + (if $r.pending.reasons then {incomplete_reasons: $r.pending.reasons} else {} end)
    + (if ($r.pending.subsections | length) > 0 then {
        subsections: ($r.pending.subsections | with_entries(.value = (.value.items // []))),
        subsection_states: ($r.pending.subsections | with_entries(.value |= del(.items)))
      } else {} end)
    + {decisions: $r.decisions}
  else
    error("unknown mode: \($mode)")
  end
