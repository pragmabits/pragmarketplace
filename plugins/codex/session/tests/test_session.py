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
import runpy
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parent.parent
RECALL = PLUGIN / "scripts" / "session_recall.py"
REPORT = PLUGIN / "scripts" / "session_report.py"
HISTORY = PLUGIN / "scripts" / "session_history.py"

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

### 6.3 Known defects

none
"""

PENDING_ITEMS = """## 6. Pending Items

### 6.1 In progress

| Item | What is missing | Evidence | Resume when | Refs |
|------|-----------------|----------|-------------|------|
| Escape `a \\| b` | rest | evidence | always | — |

### 6.2 Agreed, not started

none

### 6.3 Known defects

| Defect | Status | Evidence | Location |
|--------|--------|----------|----------|
| An empty page ends the export | confirmed | a failing test | `src/a.py` |
"""

# §6.3 under the heading reports carried before the Known defects contract.
PENDING_LEGACY = """## 6. Pending Items

### 6.1 In progress

none

### 6.2 Agreed, not started

none

### 6.3 Known issues and hypotheses

| Issue | Status | Evidence | Location |
|-------|--------|----------|----------|
| Slow on large input | hypothesis | not measured | `src/a.py` |
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

    def run_script(self, script: Path, *args: str, env: dict[str, str] | None = None,
                   cwd: Path | None = None) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-B", "-I", str(script), *args], cwd=cwd or self.repo, env=env or self.env,
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
        for args in ([], ["list"], ["filter", "status:achieved"], ["grep", "x"], ["resume"], ["last", "2"]):
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
        self.assertEqual(items["subsection_states"]["known_issues"]["columns"][0], "Defect")
        self.assertEqual(items["subsections"]["known_issues"][0]["cells"][1], "confirmed")
        self.write("d-2026-05-04T100000.md", report("2026-05-04T100000", pending=PENDING_LEGACY))
        legacy = json.loads(self.recall("resume", "d-").stdout)
        self.assertEqual(legacy["pending_state"], "items")
        self.assertEqual(legacy["subsections"]["known_issues"][0]["cells"][1], "hypothesis")

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

    def test_recent_returns_three_report_views_and_filters_by_git_user(self) -> None:
        for user, date in (("test-user", "01"), ("someone-else", "02"), ("test-user", "03"), ("someone-else", "04")):
            stamp = f"2026-05-{date}T100000"
            self.write(f"{user}-{stamp}.md", report(stamp, pending=PENDING_ITEMS))
        data = json.loads(self.recall().stdout)
        self.assertEqual((data["requested"], data["available"]), (3, 4))
        self.assertEqual([s["session_id"] for s in data["sessions"]], [
            "someone-else-2026-05-04T100000", "test-user-2026-05-03T100000", "someone-else-2026-05-02T100000",
        ])
        self.assertEqual(data["sessions"][0]["subsections"]["known_issues"][0]["cells"][1], "confirmed")
        self.assertEqual(json.loads(self.recall("--me").stdout)["available"], 2)
        self.assertEqual(json.loads(self.recall("--user", "Someone Else").stdout)["user"], "someone-else")
        self.assertEqual(self.recall("--me", "--user", "me").returncode, 2)

    def test_history_matches_worktrees_and_excludes_current_thread(self) -> None:
        module = runpy.run_path(str(HISTORY))
        namespace = module["read_activity"].__globals__
        namespace["rpc"] = lambda *_: {}
        namespace["project_worktrees"] = lambda: ["/project", "/worktree"]
        root = {"cwd": "/project", "updatedAt": 102, "id": "current"}
        related = {"cwd": "/worktree", "updatedAt": 103, "id": "next"}
        unrelated = {"cwd": "/different", "updatedAt": 105, "id": "ignore"}

        def pages(_, method, params):
            if method == "thread/list":
                return iter([] if params["archived"] else [unrelated, related, root])
            self.assertEqual(params["threadId"], "next")
            return iter([{"startedAt": 99, "completedAt": 103, "items": [
                {"id": "before", "type": "userMessage", "startedAtMs": 99000},
                {"id": "after", "type": "userMessage", "startedAtMs": 102000, "content": ["private text"]},
                {"id": "tool", "type": "commandExecution", "startedAtMs": 102500},
            ]}])

        namespace["pages"] = pages
        result = module["read_activity"](None, 100, "current")
        self.assertEqual(result["state"], "read")
        self.assertEqual([(item["ids"], item["prompts_after"]) for item in result["items"]], [(["next"], 1)])
        self.assertNotIn("private text", json.dumps(result))

    def test_recall_keeps_reports_when_the_app_server_is_unavailable(self) -> None:
        stamp = "2026-05-06T100000"
        self.write(f"test-user-{stamp}.md", report(stamp, pending=PENDING_ITEMS))
        binaries = self.tmp / "bin"
        binaries.mkdir()
        (binaries / "git").symlink_to(shutil.which("git"))
        result = self.run_script(RECALL, "--after-report", env={**self.env, "PATH": str(binaries)})
        self.assertEqual(result.returncode, 0, result.stdout)
        data = json.loads(result.stdout)
        self.assertEqual(data["sessions"][0]["pending_state"], "items")
        self.assertEqual(data["after_report"]["sessions"]["state"], "unavailable")

    def test_recall_reports_local_profile_database_failure_without_leaking_diagnostics(self) -> None:
        stamp = "2026-05-06T100000"
        self.write(f"test-user-{stamp}.md", report(stamp, pending=PENDING_ITEMS))
        binaries = self.tmp / "bin"
        binaries.mkdir()
        (binaries / "git").symlink_to(shutil.which("git"))
        codex = binaries / "codex"
        codex.write_text(
            "#!/bin/sh\n"
            "printf '%s\\n' 'failed to initialize sqlite state runtime at /private/example: "
            "unable to open database file' >&2\n"
            "exit 1\n"
        )
        codex.chmod(0o755)
        result = self.run_script(RECALL, "--after-report", env={**self.env, "PATH": str(binaries)})
        self.assertEqual(result.returncode, 0, result.stdout)
        self.assertEqual(json.loads(result.stdout)["after_report"]["sessions"]["reason"], "local-profile-access")
        self.assertNotIn("/private/example", result.stdout)

    def test_updated_thread_without_turns_keeps_history_partial(self) -> None:
        module = runpy.run_path(str(HISTORY))
        namespace = module["read_activity"].__globals__
        namespace["rpc"] = lambda *_: {}
        namespace["project_worktrees"] = lambda: ["/project"]

        def pages(_, method, params):
            if method == "thread/list" and not params["archived"]:
                yield {"cwd": "/project", "updatedAt": 102, "id": "later"}

        namespace["pages"] = pages
        result = module["read_activity"](None, 100, "current")
        self.assertEqual(result["state"], "partial")
        self.assertEqual(result["items"], [])

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

    def valid_report(self, pending: str = PENDING_NONE) -> Path:
        stamp = "2026-05-06T100000"
        headings = "".join(f"## {number}. Section\n\nnone\n\n" for number in range(1, 6))
        text = report(stamp, pending=headings + pending)
        return self.write(f"test-user-{stamp}.md", text)

    def test_report_checker_rejects_sensitive_or_incoherent_content_without_echoing(self) -> None:
        path = self.valid_report(PENDING_ITEMS)
        self.assertEqual(self.run_script(REPORT, "check", str(path)).returncode, 0)
        value = "example_" + "invalid"
        original = path.read_text().replace("100000Z", "100001Z").replace("| confirmed |", "| hypothesis |")
        path.write_text(original + f"\nservice_token={value}\n")
        result = self.run_script(REPORT, "check", str(path))
        self.assertEqual(result.returncode, 3, result.stdout)
        for category in ("sensitive:", "coherence:", "structure:"):
            self.assertIn(category, result.stdout)
        self.assertNotIn(value, result.stdout)

    def test_report_commit_from_subdirectory_is_isolated_and_idempotent(self) -> None:
        path = self.valid_report()
        nested = self.repo / "subdir"
        nested.mkdir()
        same_name = nested / path.relative_to(self.repo)
        same_name.parent.mkdir(parents=True)
        same_name.write_text("unrelated namesake\n")
        (self.repo / "base.txt").write_text("selected by user\n")
        self.git("add", "--", "base.txt")
        planned = self.run_script(REPORT, "plan-commit", str(path), cwd=nested)
        self.assertEqual(planned.returncode, 0, planned.stdout)
        plan = json.loads(planned.stdout)
        self.assertEqual(plan["result"], "ready")
        self.assertEqual(plan["path"], path.relative_to(self.repo).as_posix())
        self.git("add", "--", plan["path"])
        arguments = [plan[key] for key in ("path", "head", "blob", "other_index")]
        staged = self.run_script(REPORT, "check-staged", *arguments)
        self.assertEqual(staged.returncode, 0, staged.stdout)
        self.git("commit", "--only", "-m", plan["message"], "--", plan["path"])
        verified = json.loads(self.run_script(REPORT, "verify-commit", *arguments).stdout)
        self.assertEqual(verified["result"], "committed", verified)
        self.assertEqual(self.git("diff", "--cached", "--name-only").splitlines(), ["base.txt"])
        repeat = json.loads(self.run_script(REPORT, "plan-commit", str(path)).stdout)
        self.assertEqual(repeat["result"], "already-committed")

    def test_report_hook_rejection_preserves_other_staging(self) -> None:
        path = self.valid_report()
        (self.repo / "base.txt").write_text("existing staging\n")
        self.git("add", "--", "base.txt")
        hook = self.repo / ".git" / "hooks" / "commit-msg"
        hook.write_text("#!/bin/sh\nexit 1\n")
        hook.chmod(0o755)
        plan = json.loads(self.run_script(REPORT, "plan-commit", str(path)).stdout)
        self.git("add", "--", plan["path"])
        arguments = [plan[key] for key in ("path", "head", "blob", "other_index")]
        attempt = subprocess.run(["git", "commit", "--only", "-m", plan["message"], "--", plan["path"]],
                                 cwd=self.repo, env=self.env, capture_output=True)
        self.assertNotEqual(attempt.returncode, 0)
        state = json.loads(self.run_script(REPORT, "verify-commit", *arguments).stdout)
        self.assertEqual(state["result"], "no-commit")
        self.assertTrue(state["other_index_preserved"])
        self.assertEqual(state["staged_blob"], plan["blob"])
        self.git("rm", "--cached", "--", plan["path"])
        self.assertEqual(self.git("diff", "--cached", "--name-only").splitlines(), ["base.txt"])
        self.assertTrue(path.exists())


if __name__ == "__main__":
    unittest.main()
