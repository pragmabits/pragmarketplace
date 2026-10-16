#!/usr/bin/env python3
"""Tests for the Codex session plugin's scripts.

Usage: python3 -I plugins/codex/session/tests/test_session.py [-v]

Every test runs in a temporary git repository, with git configuration isolated
from the user's (GIT_CONFIG_GLOBAL, GIT_CONFIG_NOSYSTEM) and fictitious reports.
Cross-reading with the Claude Code plugin's reader is covered by that plugin's
suite (plugins/claude/session/tests/run.sh, case A05).
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
RECALL = PLUGIN / "scripts" / "session_recall.py"
REPORT = PLUGIN / "scripts" / "session_report.py"

HEADER = """# Session Report: {title}

**Timestamp (UTC):** {ts}Z
**Git user:** Test User
{origin}**HEAD observed at generation:** `0000000`
**Commits made in this session:** none
**Context coverage:** full

---

## Session contract

**User goal (entering session):** Exercise the tests
**Direction changes:** none
**Goal status:** {status}
**Status evidence:** fictitious

"""

PENDING_NONE = """## 6. Pending Items

### 6.1 In progress

none

### 6.2 Agreed, not started

none

### 6.3 Known issues and hypotheses

none
"""

PENDING_ITEMS = """## 6. Pending Items

### 6.1 In progress

| Item | What is missing | Evidence | Resume when | Refs |
|------|-----------------|----------|-------------|------|
| Escape `a \\| b` | rest | evidence | always | — |

### 6.2 Agreed, not started

none

### 6.3 Known issues and hypotheses

none
"""


def report(ts: str, title: str = "Fictitious", status: str = "achieved", pending: str = PENDING_NONE,
           origin: str = "**Harness:** codex\n") -> str:
    return HEADER.format(title=title, ts=ts, status=status, origin=origin) + pending


class SessionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="codex-session-tests."))
        self.env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=str(self.tmp / "gitconfig"),
                        GIT_CEILING_DIRECTORIES=str(self.tmp))
        for key in ("CODEX_PROJECT_DIR", "GIT_DIR", "GIT_WORK_TREE"):
            self.env.pop(key, None)
        for key, value in (("user.name", "Test User"), ("user.email", "test@example.invalid"),
                           ("init.defaultBranch", "main")):
            subprocess.run(["git", "config", "--file", self.env["GIT_CONFIG_GLOBAL"], key, value], check=True)
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.git("init", "-q")
        (self.repo / "base.txt").write_text("base\n")
        self.git("add", "base.txt")
        self.git("commit", "-q", "-m", "chore: base")
        self.sessions = self.repo / ".harness" / "sessions"

    def tearDown(self) -> None:
        for path in self.tmp.rglob("*"):
            try:
                path.chmod(0o755)
            except OSError:
                pass
        shutil.rmtree(self.tmp, ignore_errors=True)

    def git(self, *args: str) -> str:
        return subprocess.run(["git", *args], cwd=self.repo, env=self.env, check=True, text=True,
                              stdout=subprocess.PIPE).stdout

    def run_script(self, script: Path, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-I", str(script), *args], cwd=self.repo, env=env or self.env,
                              text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

    def recall(self, *args: str) -> subprocess.CompletedProcess:
        return self.run_script(RECALL, *args)

    def write(self, name: str, text: str) -> Path:
        self.sessions.mkdir(parents=True, exist_ok=True)
        path = self.sessions / name
        path.write_text(text, encoding="utf-8")
        return path

    def tree(self) -> list[str]:
        return sorted(str(p.relative_to(self.repo)) for p in self.repo.rglob("*"))

    # --- recall -----------------------------------------------------------

    def test_queries_create_nothing_and_ignore_old_directories(self) -> None:
        (self.repo / ".sessions").mkdir()
        (self.repo / ".sessions" / "a-2026-05-01T100000.md").write_text(report("2026-05-01T100000"))
        before = self.tree()
        for args in (["list"], ["filter", "status:achieved"], ["grep", "x"], ["resume"], ["last", "2"]):
            result = self.recall(*args)
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("No sessions found in .harness/sessions/ (the directory does not exist)", result.stdout)
        self.assertEqual(before, self.tree())

    @unittest.skipIf(os.geteuid() == 0, "permission bits do not apply to root")
    def test_unreadable_directory_is_an_error(self) -> None:
        self.write("a-2026-05-01T100000.md", report("2026-05-01T100000"))
        self.sessions.chmod(0)
        result = self.recall("list")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("error: cannot read .harness/sessions/", result.stdout)
        self.assertNotIn("No sessions found", result.stdout)

    def test_pending_states(self) -> None:
        self.write("a-2026-05-01T100000.md", report("2026-05-01T100000"))
        self.write("b-2026-05-02T100000.md", report("2026-05-02T100000", pending=""))
        self.write("c-2026-05-03T100000.md", report("2026-05-03T100000", pending=PENDING_ITEMS))
        none = json.loads(self.recall("resume", "a-").stdout)
        self.assertEqual((none["pending_state"], none.get("empty")), ("none", True))
        missing = json.loads(self.recall("resume", "b-").stdout)
        self.assertEqual(missing["pending_state"], "incomplete")
        self.assertNotIn("empty", missing)
        items = json.loads(self.recall("resume", "c-", "--item", "the escape").stdout)
        self.assertEqual(items["pending_state"], "items")
        self.assertEqual(items["subsections"]["in_progress"][0]["label"], "Escape `a | b`")
        self.assertEqual(items["requested_item"], "the escape")

    def test_order_ids_and_errors(self) -> None:
        self.write("zed-2026-05-01T100000.md", report("2026-05-01T100000"))
        self.write("al-2026-05-03T090000.md", report("2026-05-03T090000"))
        self.write("al-2026-05-03T090000-2.md", report("2026-05-03T090000"))
        listing = self.recall("list").stdout
        order = [line.split(" | ")[0][2:] for line in listing.splitlines()[2:]]
        self.assertEqual(order, ["al-2026-05-03T090000-2", "al-2026-05-03T090000", "zed-2026-05-01T100000"])
        self.assertNotIn("Branch", listing.splitlines()[0])
        exact = json.loads(self.recall("resume", "al-2026-05-03T090000").stdout)
        self.assertEqual(exact["session_id"], "al-2026-05-03T090000")
        ambiguous = self.recall("resume", "al")
        self.assertEqual(ambiguous.returncode, 2)
        self.assertIn('Ambiguous reference "al" matches:', ambiguous.stdout)
        for args in (["last", "0"], ["list", "--limit"], ["filter", "status:done"], ["grep", "re:("], ["resume", "a", "b"]):
            result = self.recall(*args)
            self.assertNotEqual(result.returncode, 0, args)

    def test_authorship_states(self) -> None:
        self.write("a-2026-05-01T100000.md", report("2026-05-01T100000", origin=""))
        self.write("b-2026-05-02T100000.md", report("2026-05-02T100000", origin="**Harness:** claude-code\n**Model:** alias: opus\n"))
        self.write("c-2026-05-03T100000.md", report("2026-05-03T100000", origin="**Harness:** next-tool\n**Model:** m-9\n"))
        legacy = json.loads(self.recall("resume", "a-").stdout)["origin"]
        self.assertEqual((legacy["harness"], legacy["model"]["state"]), (None, "absent"))
        alias = json.loads(self.recall("resume", "b-").stdout)["origin"]["model"]
        self.assertEqual(alias, {"state": "alias", "value": "opus"})
        future = json.loads(self.recall("resume", "c-").stdout)["origin"]
        self.assertEqual((future["harness"], future["model"]["state"], future["agent"]), ("next-tool", "confirmed", None))

    # --- prepare ----------------------------------------------------------

    def test_prepare(self) -> None:
        result = self.run_script(REPORT, "prepare", "--lang", "pt-BR", "title", "hint")
        self.assertEqual(result.returncode, 0, result.stdout)
        data = json.loads(result.stdout)
        self.assertEqual(Path(data["output_path"]).parent, self.sessions)
        self.assertTrue(self.sessions.is_dir())
        self.assertFalse((self.repo / ".sessions").exists())
        self.assertEqual(Path(data["output_path"]).stem, data["session_id"])
        self.assertTrue(data["session_id"].endswith(data["timestamp_utc"][:-1]))
        self.assertNotIn("branch", data)
        self.assertNotIn("commits_last_day", data)
        self.assertEqual(data["origin"]["lines"][0], "**Harness:** codex")
        self.assertFalse(any(line.startswith("**Model:**") for line in data["origin"]["lines"]))
        self.assertEqual((data["language"], data["title_hint"]), ("pt-BR", "title hint"))

    def test_prepare_never_reuses_a_name(self) -> None:
        import datetime
        now = datetime.datetime.now(datetime.timezone.utc)
        for offset in range(6):
            stamp = (now + datetime.timedelta(seconds=offset)).strftime("%Y-%m-%dT%H%M%S")
            self.write(f"test-user-{stamp}.md", report(stamp))
        data = json.loads(self.run_script(REPORT, "prepare").stdout)
        self.assertRegex(data["session_id"], r"-\d+$")
        self.assertFalse(Path(data["output_path"]).exists())


if __name__ == "__main__":
    unittest.main()
