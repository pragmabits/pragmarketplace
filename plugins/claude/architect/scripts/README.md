# Scripts

Mechanical work for the architect plugin lives here. These scripts handle deterministic tasks (file inspection, structural validation, pattern detection) so the skills don't spend tokens on work a script can do faster and more reliably.

All scripts:
- Are written in Python 3.8+ using only the standard library (no `pip install` needed)
- Take input via flags or positional arguments
- Output JSON to stdout, errors to stderr
- Have a `--help` flag and a docstring at the top of the file
- Are read-only by default (none of these scripts modify the user's repo)

## When to use a script vs. when to use Claude

**Use a script when** the question has a deterministic answer: does this file exist, does this section appear, does this metric stagnate. The script returns the same answer every time.

**Use Claude when** the question requires judgment: is this role one objective sentence, does this description risk over-invocation, is the verifier rubric tight enough. Claude reads the prose; the script counts the structure.

The skills decide when to call each script — you generally don't run them directly unless you're debugging.

---

## `survey.py`

**What it does:** Inspects a repository and emits a JSON survey describing detected stack(s), test commands, existing sub-agents/commands under `.claude/`, and off-limits paths from `.gitignore` and `CODEOWNERS`.

**Used by:** `project-survey` skill (called at the start of every scaffold).

**Why it's a script:** Listing manifest files, parsing `package.json` for test scripts, globbing `.claude/agents/*.md` — all mechanical. Spending tokens on this work was the highest-cost, lowest-value part of the original plugin.

**What it does NOT do:** Extract conventions from `CLAUDE.md`. That requires prose understanding and stays with Claude.

**Run it:**
```bash
python3 scripts/survey.py --root /path/to/repo
```

**Exit codes:** 0 if survey ran (regardless of findings), 2 if root path is invalid.

---

## `validate.py`

**What it does:** Structural validation of generated loop and sub-agent files. Checks that required frontmatter fields exist, required sections (`## Role`, `## Output contract`, etc.) are present, iteration caps aren't above 10, and placeholder text (`<...>`) hasn't been left unfilled.

**Used by:** `/coordination-audit` (Step 1 — runs the validator, then only spends tokens on judgment-level checks for files that pass mechanical validation).

**Why it's a script:** "Does this file have a `## Guardrails` section" is a regex check, not a reading-comprehension check. There's no value in having Claude do this.

**What it does NOT do:** Judge whether the role is *actually* one objective sentence, or whether the description will cause over-invocation. Those are judgment calls.

**Run it:**
```bash
python3 scripts/validate.py --root /path/to/repo --target both
python3 scripts/validate.py --root /path/to/repo --paths-from-config  # uses .architect.json
```

**Exit codes:** 0 if no errors (warnings allowed), 1 if any error found, 2 if invalid arguments.

**Issue codes:** Documented in the script's docstring. Errors include `missing-objective`, `missing-stop`, `missing-frontmatter`, `missing-role`, etc. Warnings include `cap-too-high`, `placeholder-unfilled`, `generic-description`.

---

## `loop_log_analyze.py`

**What it does:** Reads a JSON-lines loop log and detects failure patterns: oscillation, stagnation, no-progress, cap-reached, scope-creep, verifier-flapping. Each pattern is detected by a deterministic algorithm (counting consecutive identical values, checking for alternation, comparing first/last counts).

**Used by:** `loop-forensics` skill (Step 1 — runs the analyzer, then maps detected patterns to prescriptions).

**Why it's a script:** Pattern detection over a list of integers is exactly what algorithms are good at. The skill's value-add is the *prescription* (what to do about each pattern), not the detection.

**What it does NOT do:** Decide what to do about a detected pattern. The mapping from pattern to fix lives in `loop-forensics/SKILL.md`.

**Run it:**
```bash
python3 scripts/loop_log_analyze.py /path/to/loop.log
```

**Expected log format:** JSON Lines, one record per iteration. Required fields: `iter` and either `failing_count_after` or `verdict`. Optional: `hypothesis`, `diff_summary`, `decision`, `files_modified`. The schema matches the format prescribed by `/loop-contract`.

**Exit codes:** 0 if analysis ran, 1 if log is malformed, 2 if invalid arguments.

**Pattern codes:** Documented in the script's docstring. See `loop-forensics/SKILL.md` for the prescription tied to each.

---

## `check_staleness.py`

**What it does:** Reads `.architect.json` and verifies that listed sub-agents/commands still exist on disk and that the recorded primary stack still matches the repo. Returns `stale: true` with reasons if anything's off.

**Used by:** `project-survey` skill (called before every scaffold to decide whether to use the cached survey or run a fresh one).

**Why it's a script:** File existence checks and string comparisons. Trivial. Running this before each scaffold avoids both stale-config bugs and unnecessary re-surveys.

**What it does NOT do:** Re-run the survey. It only reports staleness; the skill handles the response.

**Run it:**
```bash
python3 scripts/check_staleness.py --root /path/to/repo
```

**Exit codes:** 0 if check ran (regardless of staleness), 2 if invalid arguments.

**Reason codes:** `no-config`, `malformed-config`, `missing-agent`, `missing-command`, `stack-changed`.

---

## `marketplace_inventory.py`

**What it does:** Reads the user's Claude Code plugin install state (`~/.claude/plugins/installed_plugins.json`) and returns metadata for every plugin installed from the pragmatic marketplace, including the components (skills, commands, agents) each plugin contributes.

**Used by:** `capability-radar` skill (called as Step 0 of every scaffold or recommendation command).

**Why it's a script:** Reading JSON files, globbing directories for components, parsing frontmatter — all mechanical. Doing this in prose would mean the model walking the filesystem turn by turn for every scaffold.

**What it does NOT do:** Judge whether any plugin "fits" the user's task. That's prose-comprehension judgment that stays with Claude.

**What it does NOT do (deliberately):** Surface uninstalled plugins from the marketplace catalog. Install-mid-task is too disruptive to recommend.

**Run it:**
```bash
python3 scripts/marketplace_inventory.py
```

**Exit codes:** 0 if inventory ran (regardless of findings), 2 if plugin state files are corrupted.

**Output structure:** Top-level `marketplace_known` (boolean) tells you whether the user has the pragmatic marketplace configured at all. If false, the `plugins` list is empty and the calling skill should skip plugin matching entirely.

---

## Adding a new script

If you find yourself writing a skill that does mechanical work — counting things, checking file existence, comparing values, parsing structured data — consider extracting it to a script. Use the existing scripts as templates. Each one:

1. Has a top-of-file docstring covering purpose, usage, output schema, exit codes, and (where applicable) issue/pattern codes.
2. Uses `argparse` for argument parsing and `--help`.
3. Outputs JSON to stdout, never prose.
4. Sends errors and warnings to stderr.
5. Avoids dependencies outside the standard library.
6. Is invoked by exactly one skill or command, which is named in the script's docstring.

The test for "should this be a script" is whether the output is deterministic given the input. If two runs of the same input could produce different outputs, it belongs in a skill, not a script.
