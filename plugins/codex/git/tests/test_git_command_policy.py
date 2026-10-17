#!/usr/bin/env python3
"""Tests for the Codex git plugin's hook policy (scripts/git_command_policy.py).

Usage: python3 -I plugins/codex/git/tests/test_git_command_policy.py [-v]

Each test feeds the policy a fake hook payload on stdin. The repository is
temporary, with git configuration isolated from the user's (GIT_CONFIG_GLOBAL,
GIT_CONFIG_NOSYSTEM). Codex gives hooks the session directory as cwd, not the
command's workdir, so the policy cannot check where a command runs; these
tests cover what the command itself shows.
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
POLICY = PLUGIN / "scripts" / "git_command_policy.py"


class PolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="git-policy-tests.")).resolve()
        self.addCleanup(shutil.rmtree, self.tmp)
        self.env = {
            "PATH": os.environ.get("PATH", ""),
            "HOME": str(self.tmp / "home"),
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": str(self.tmp / "gitconfig"),
            "GIT_CEILING_DIRECTORIES": str(self.tmp),
        }
        self.repo = self.tmp / "repo"
        (self.repo / "web").mkdir(parents=True)
        (self.tmp / "outside").mkdir()
        subprocess.run(["git", "init", "-q", str(self.repo)], env=self.env, check=True)

    def decide(self, command: str, cwd: Path | None = None, event: str = "PreToolUse") -> dict | None:
        payload = {"hook_event_name": event, "cwd": str(cwd or self.repo), "tool_input": {"command": command}}
        result = subprocess.run(
            [sys.executable, "-I", str(POLICY)],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            env=self.env,
            cwd=cwd or self.repo,
            check=True,
        )
        return json.loads(result.stdout) if result.stdout.strip() else None

    def assert_denied(self, command: str, text: str, cwd: Path | None = None) -> None:
        decision = self.decide(command, cwd)
        self.assertIsNotNone(decision, command)
        self.assertEqual(decision["hookSpecificOutput"]["permissionDecision"], "deny")
        self.assertIn(text, decision["hookSpecificOutput"]["permissionDecisionReason"])

    def test_cd_before_git_is_denied_naming_the_root(self) -> None:
        self.assert_denied(f"cd {self.repo} && git commit -m 'fix: x'", f"set to the repository root ({self.repo})")

    def test_cd_before_git_from_the_session_subdirectory_names_the_root(self) -> None:
        self.assert_denied(f"cd {self.repo} && git add web/a.txt", f"({self.repo})", cwd=self.repo / "web")

    def test_every_shape_of_cd_before_git_is_denied(self) -> None:
        for command in ("(cd web && git status)", "cd web; git status", "cd web\ngit status",
                        "pushd web && git status", "cd web && npm test && git status"):
            with self.subTest(command=command):
                self.assert_denied(command, "cd before git in one command is blocked")

    def test_cd_before_git_outside_a_repository_is_denied_without_a_root(self) -> None:
        self.assert_denied(f"cd {self.repo} && git status", "set to the repository root instead", cwd=self.tmp / "outside")

    def test_commands_without_cd_before_git_pass(self) -> None:
        for command in ("git add -- web/a.txt", "cd web", "cd web && npm test", "cd git && ls",
                        "git commit -m 'docs: explain why cd web && git status is blocked'",
                        "git rev-parse --show-toplevel --show-prefix"):
            with self.subTest(command=command):
                self.assertIsNone(self.decide(command))

    def test_permission_request_gets_its_own_shape(self) -> None:
        decision = self.decide("cd web && git status", event="PermissionRequest")
        self.assertEqual(decision["hookSpecificOutput"]["decision"]["behavior"], "deny")

    def test_earlier_checks_are_unchanged(self) -> None:
        self.assert_denied("git -C web status", "run git from the repository root")
        self.assert_denied("git add -p", "Interactive patch staging is blocked")
        self.assert_denied("git commit --no-verify -m 'fix: x'", "Bypassing git hooks is blocked")


if __name__ == "__main__":
    unittest.main()
