#!/usr/bin/env python3
"""
loop_log_analyze.py — Detect failure patterns in bounded loop logs.

Reads a JSON-lines log file (the format prescribed by /loop-contract)
and identifies recognizable failure patterns: oscillation, stagnation,
no-progress runs, scope creep, cap-reached. Outputs structured findings
that the `loop-forensics` skill turns into a prescription.

Pattern detection here is fully deterministic — counting things,
comparing consecutive values, checking thresholds. Claude's role is
the prescription (what to do about it), not the diagnosis.

USAGE
    python3 loop_log_analyze.py <log_file>

ARGUMENTS
    <log_file>   Path to a .log file containing JSON-lines records,
                 one record per loop iteration. Each record should
                 have at minimum:
                   - iter (int)
                   - failing_count_after (int) OR a "verdict" field
                 Other fields (hypothesis, diff_summary, decision)
                 are forwarded to output but not analyzed.

OUTPUT
    A JSON object on stdout:
    {
      "log_file": "<path>",
      "iterations": <count>,
      "patterns": [
        {
          "code": "oscillation" | "stagnation" | "no-progress" |
                  "cap-reached" | "scope-creep" | "verifier-flapping",
          "severity": "error" | "warning" | "info",
          "evidence": "<one-line concrete observation>",
          "iterations_involved": [<int>, ...]
        }
      ],
      "summary": {
        "first_failing_count": <int> | null,
        "last_failing_count": <int> | null,
        "total_progress": <int> | null,
        "final_verdict": "PASS" | "FAIL" | "STALLED" | "CAP" | null
      }
    }

EXIT CODES
    0   Analysis completed (regardless of findings)
    1   Log file is malformed (parse errors)
    2   Invalid arguments

PATTERN DEFINITIONS
    oscillation       failing_count_after alternates A→B→A→B across
                      a 4-iteration window (true alternation, not just
                      a value reappearing)
    stagnation        failing_count_after unchanged across 3+ consecutive
                      iterations
    no-progress       cap reached with failing_count_after >= initial
    cap-reached       loop hit its iteration cap without PASS
    scope-creep       diff touches expanding set of files across iters
                      (requires diff_summary or files_modified field)
    verifier-flapping verdict alternates PASS/FAIL across iterations
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def parse_log(log_path: Path) -> list[dict]:
    """Parse a JSON-lines log file. Raises on malformed input."""
    records = []
    with open(log_path) as f:
        for line_no, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError as e:
                raise ValueError(f"Line {line_no}: {e}")
    return records


# --- Pattern detectors ------------------------------------------------------

def detect_oscillation(records: list[dict]) -> dict | None:
    """A→B→A→B alternation in failing_count_after across a 4-iter window."""
    counts_with_iters = [(r.get("iter", i+1), r.get("failing_count_after"))
                         for i, r in enumerate(records)]
    counts_with_iters = [(it, c) for it, c in counts_with_iters if isinstance(c, int)]

    if len(counts_with_iters) < 4:
        return None

    for i in range(len(counts_with_iters) - 3):
        a = counts_with_iters[i][1]
        b = counts_with_iters[i+1][1]
        if (a != b
                and counts_with_iters[i+2][1] == a
                and counts_with_iters[i+3][1] == b):
            iters = [counts_with_iters[j][0] for j in range(i, i+4)]
            return {
                "code": "oscillation",
                "severity": "error",
                "evidence": f"failing_count_after alternated {a}→{b}→{a}→{b} across iterations {iters}",
                "iterations_involved": iters,
            }
    return None


def detect_stagnation(records: list[dict]) -> dict | None:
    """failing_count_after unchanged across 2+ consecutive iterations."""
    counts_with_iters = [(r.get("iter", i+1), r.get("failing_count_after"))
                         for i, r in enumerate(records)]
    counts_with_iters = [(it, c) for it, c in counts_with_iters if isinstance(c, int)]

    if len(counts_with_iters) < 3:
        return None

    # Find the longest run of identical consecutive values
    longest_run = []
    current_run = [counts_with_iters[0]]
    for i in range(1, len(counts_with_iters)):
        if counts_with_iters[i][1] == current_run[-1][1]:
            current_run.append(counts_with_iters[i])
        else:
            if len(current_run) > len(longest_run):
                longest_run = current_run
            current_run = [counts_with_iters[i]]
    if len(current_run) > len(longest_run):
        longest_run = current_run

    if len(longest_run) >= 3:
        iters = [it for it, _ in longest_run]
        return {
            "code": "stagnation",
            "severity": "error",
            "evidence": f"failing_count_after stayed at {longest_run[0][1]} for {len(longest_run)} consecutive iterations",
            "iterations_involved": iters,
        }
    return None


def detect_no_progress(records: list[dict]) -> dict | None:
    """Cap reached without net improvement."""
    counts = [r.get("failing_count_after") for r in records]
    counts = [c for c in counts if isinstance(c, int)]

    if len(counts) < 2:
        return None

    final_decision = records[-1].get("decision", "")
    final_verdict = records[-1].get("verdict", "")
    if "cap" in str(final_decision).lower() or final_verdict == "CAP":
        if counts[-1] >= counts[0]:
            return {
                "code": "no-progress",
                "severity": "error",
                "evidence": f"loop reached cap with failing_count_after={counts[-1]} (started at {counts[0]})",
                "iterations_involved": [records[0].get("iter", 1), records[-1].get("iter", len(records))],
            }
    return None


def detect_cap_reached(records: list[dict]) -> dict | None:
    """Loop hit cap without PASS."""
    if not records:
        return None
    last = records[-1]
    decision = str(last.get("decision", "")).lower()
    verdict = last.get("verdict", "")
    if ("cap" in decision and "stop" in decision) or verdict == "CAP":
        return {
            "code": "cap-reached",
            "severity": "warning",
            "evidence": f"loop reached its iteration cap at iter={last.get('iter', len(records))} without PASS verdict",
            "iterations_involved": [last.get("iter", len(records))],
        }
    return None


def detect_scope_creep(records: list[dict]) -> dict | None:
    """Each iteration's diff touches an expanding set of files."""
    files_per_iter = []
    for r in records:
        files = r.get("files_modified")
        if files is None:
            # Try to extract from diff_summary string heuristically
            diff_summary = r.get("diff_summary", "")
            if isinstance(diff_summary, str):
                # Look for "filename:" patterns
                import re
                file_mentions = re.findall(r"([\w./_-]+\.[a-zA-Z]+)", diff_summary)
                files = list(set(file_mentions)) if file_mentions else None
        if files is None:
            return None  # Can't analyze without this data
        files_per_iter.append((r.get("iter", len(files_per_iter)+1), set(files)))

    if len(files_per_iter) < 3:
        return None

    # Check if file count strictly increases over 3+ iterations
    sizes = [len(f) for _, f in files_per_iter]
    if all(sizes[i] < sizes[i+1] for i in range(len(sizes)-1)) and sizes[-1] - sizes[0] >= 2:
        return {
            "code": "scope-creep",
            "severity": "warning",
            "evidence": f"files modified expanded from {sizes[0]} to {sizes[-1]} across iterations",
            "iterations_involved": [it for it, _ in files_per_iter],
        }
    return None


def detect_verifier_flapping(records: list[dict]) -> dict | None:
    """verdict alternates PASS/FAIL."""
    verdicts = [r.get("verdict") for r in records]
    verdicts = [v for v in verdicts if v in ("PASS", "FAIL")]

    if len(verdicts) < 4:
        return None

    flips = sum(1 for i in range(len(verdicts)-1) if verdicts[i] != verdicts[i+1])
    if flips >= 3:
        return {
            "code": "verifier-flapping",
            "severity": "error",
            "evidence": f"verdict alternated {flips} times across {len(verdicts)} iterations — verifier may be unreliable",
            "iterations_involved": list(range(1, len(records)+1)),
        }
    return None


# --- Summary ----------------------------------------------------------------

def compute_summary(records: list[dict]) -> dict:
    counts = [r.get("failing_count_after") for r in records]
    counts = [c for c in counts if isinstance(c, int)]

    final_verdict = None
    if records:
        last = records[-1]
        decision = str(last.get("decision", "")).lower()
        verdict = last.get("verdict")
        if "cap" in decision:
            final_verdict = "CAP"
        elif "stall" in decision:
            final_verdict = "STALLED"
        elif "criterion met" in decision or "pass" in decision:
            final_verdict = "PASS"
        elif verdict in ("PASS", "FAIL", "STALLED", "CAP"):
            final_verdict = verdict
        elif "stop" in decision:
            final_verdict = "FAIL"

    return {
        "first_failing_count": counts[0] if counts else None,
        "last_failing_count": counts[-1] if counts else None,
        "total_progress": (counts[0] - counts[-1]) if len(counts) >= 2 else None,
        "final_verdict": final_verdict,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Analyze a loop log for failure patterns.")
    parser.add_argument("log_file", help="Path to JSON-lines log file")
    args = parser.parse_args()

    log_path = Path(args.log_file)
    if not log_path.is_file():
        print(f"Error: {log_path} is not a file", file=sys.stderr)
        return 2

    try:
        records = parse_log(log_path)
    except ValueError as e:
        print(f"Error parsing log: {e}", file=sys.stderr)
        return 1

    detectors = [
        detect_oscillation,
        detect_stagnation,
        detect_no_progress,
        detect_cap_reached,
        detect_scope_creep,
        detect_verifier_flapping,
    ]

    patterns = []
    for detector in detectors:
        result = detector(records)
        if result:
            patterns.append(result)

    output = {
        "log_file": str(log_path),
        "iterations": len(records),
        "patterns": patterns,
        "summary": compute_summary(records),
    }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
