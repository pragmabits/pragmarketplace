"""Gate configuration: defaults, the user's config file, environment overrides.

The config file is optional and partial: any key it sets replaces the default.
Location: $PRAGMA_GATE_CONFIG, else ${XDG_CONFIG_HOME:-~/.config}/pragma/gate.json.
PRAGMA_GATE=off (or 0/false/disabled) disables the gate regardless of the file.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

DEFAULTS = {
    "enabled": True,
    # None: the model the session itself is running (read from the transcript);
    # when the transcript names none, the CLI's own selection.
    "model": None,
    "effort": "low",
    "timeout_s": 30,
    "lock_wait_s": 40,
    "budgets": {
        "question": {"evaluations": 3, "returns": 2},
        "stop": {"evaluations": 3, "returns": 2},
    },
    "package_limit_bytes": 64 * 1024,
    # How long a question review waits for the end of the text being shown
    # with the question, while the transcript does not hold it yet.
    "display_wait_s": 1.5,
    # How long a turn-end review waits for the transcript to hold the final
    # response, which Claude Code writes after the Stop hook has started.
    "stop_wait_s": 2.0,
    "retention_days": 14,
    "max_requests_kept": 30,
    "claude_bin": "claude",
}


def config_path() -> Path:
    explicit = os.environ.get("PRAGMA_GATE_CONFIG")
    if explicit:
        return Path(explicit)
    base = os.environ.get("XDG_CONFIG_HOME") or str(Path.home() / ".config")
    return Path(base) / "pragma" / "gate.json"


def state_root() -> Path:
    explicit = os.environ.get("PRAGMA_GATE_STATE_DIR")
    if explicit:
        return Path(explicit)
    base = os.environ.get("XDG_STATE_HOME") or str(Path.home() / ".local" / "state")
    return Path(base) / "pragma" / "gate"


def load() -> tuple[dict, str | None]:
    """Return (config, problem). A broken file is reported, never fatal."""
    cfg = json.loads(json.dumps(DEFAULTS))
    problem = None
    path = config_path()
    if path.is_file():
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict):
                raise ValueError("top level is not an object")
            for key, value in data.items():
                if key == "budgets" and isinstance(value, dict):
                    for kind, limits in value.items():
                        if kind in cfg["budgets"] and isinstance(limits, dict):
                            cfg["budgets"][kind].update(limits)
                elif key in cfg:
                    cfg[key] = value
        except (OSError, ValueError) as exc:
            problem = f"config {path}: {exc}"
    env = os.environ.get("PRAGMA_GATE", "").strip().lower()
    if env in ("off", "0", "false", "disabled"):
        cfg["enabled"] = False
    if os.environ.get("PRAGMA_GATE_CLAUDE_BIN"):
        cfg["claude_bin"] = os.environ["PRAGMA_GATE_CLAUDE_BIN"]
    return cfg, problem
