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
INSTALLER = PLUGIN / "scripts" / "install_hooks.py"
HOOKS = PLUGIN / "assets" / "git-hooks"


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
        self.assertIsNone(self.decide("git status --short", cwd=self.repo / "web"))

    def test_permission_request_gets_its_own_shape(self) -> None:
        decision = self.decide("cd web && git status", event="PermissionRequest")
        self.assertEqual(decision["hookSpecificOutput"]["decision"]["behavior"], "deny")

    def test_earlier_checks_are_unchanged(self) -> None:
        self.assert_denied("git -C web status", "run git from the repository root")
        self.assert_denied("git add -p", "Interactive patch staging is blocked")
        self.assert_denied("git commit --no-verify -m 'fix: x'", "Bypassing git hooks is blocked")

    def run_plugin(self, script: Path, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-B", "-I", str(script), *args],
                              env=self.env, cwd=self.repo, text=True, capture_output=True)

    def test_setup_checks_custom_hook_path_and_preserves_approval_choice(self) -> None:
        subprocess.run(["git", "config", "core.hooksPath", "custom-hooks"],
                       env=self.env, cwd=self.repo, check=True)
        self.assertEqual(self.run_plugin(INSTALLER, "--apply", "--all", "--git-mutations", "allow").returncode, 0)
        self.assertEqual(self.run_plugin(INSTALLER, "--check", "--all").returncode, 0)
        self.assertFalse((self.repo / ".codex" / "config.toml").exists())
        self.assertTrue(os.access(self.repo / "custom-hooks" / "commit-msg", os.X_OK))
        policy = self.repo / ".codex" / "rules" / "git-commit.rules"
        automatic = policy.read_text()
        self.assertIn('pattern = ["git", "add", "--"]', automatic)
        self.assertEqual(self.run_plugin(INSTALLER, "--apply").returncode, 0)
        self.assertEqual(policy.read_text(), automatic)
        self.assertEqual(self.run_plugin(INSTALLER, "--apply", "--git-mutations", "prompt").returncode, 0)
        self.assertEqual(policy.read_text(), (PLUGIN / "assets" / "rules" / "git-commit.rules").read_text())

    def test_setup_preserves_disabled_hooks_and_custom_rules(self) -> None:
        config = self.repo / ".codex" / "config.toml"
        config.parent.mkdir()
        config.write_text("[features]\nhooks = false\n")
        policy = config.parent / "rules" / "git-commit.rules"
        policy.parent.mkdir()
        policy.write_text("# custom rules\n")
        self.assertNotEqual(self.run_plugin(INSTALLER, "--apply", "--git-mutations", "allow").returncode, 0)
        result = self.run_plugin(INSTALLER, "--apply")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("disabled", result.stdout)
        self.assertEqual(config.read_text(), "[features]\nhooks = false\n")
        self.assertEqual(policy.read_text(), "# custom rules\n")

    def test_native_hooks_accept_unicode_number_and_use_reference_size_and_draft(self) -> None:
        message = self.tmp / "message"
        message.write_text("docs: ⅓ dos exemplos\n", encoding="utf-8")
        self.assertEqual(self.run_plugin(HOOKS / "commit-msg", str(message)).returncode, 0)
        message.write_text("docs: exemplos\n\nline\vvalue\n")
        self.assertNotEqual(self.run_plugin(HOOKS / "commit-msg", str(message)).returncode, 0)
        path = self.repo / "tsconfig.json"
        path.write_bytes(b"a" * (1024 * 1024 + 1) + b"\n")
        subprocess.run(["git", "add", "--", path.name], env=self.env, cwd=self.repo, check=True)
        self.assertEqual(self.run_plugin(HOOKS / "prepare-commit-msg", str(message)).returncode, 0)
        self.assertEqual(message.read_text().splitlines()[0], "chore: ")
        self.assertEqual(self.run_plugin(HOOKS / "pre-commit").returncode, 0)
        path.write_bytes(b"a" * (1025 * 1024))
        self.assertNotEqual(self.run_plugin(HOOKS / "pre-commit").returncode, 0)


if __name__ == "__main__":
    unittest.main()
