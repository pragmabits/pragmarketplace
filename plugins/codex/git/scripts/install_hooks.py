#!/usr/bin/env python3
"""Install Codex and git guardrails for the git commit workflow."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
ASSETS = PLUGIN_ROOT / "assets"
DEFAULT_HOOKS = ("commit-msg",)
ALL_HOOKS = ("commit-msg", "pre-commit", "prepare-commit-msg")


class Recorder:
    def __init__(self) -> None:
        self.rows: list[tuple[str, str]] = []

    def add(self, status: str, detail: str) -> None:
        self.rows.append((status, detail))

    def print(self) -> None:
        for status, detail in self.rows:
            print(f"{status}: {detail}")


def run_git_root() -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit("error: run this installer from inside a git repository")
    return Path(result.stdout.strip()).resolve()


def git_path(repo: Path, relative_git_path: str) -> Path:
    result = subprocess.run(
        ["git", "rev-parse", "--git-path", relative_git_path],
        cwd=repo,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        raise SystemExit(f"error: unable to resolve git path {relative_git_path}")
    path = Path(result.stdout.strip())
    return path if path.is_absolute() else (repo / path).resolve()


def display_path(repo: Path, path: Path) -> str:
    try:
        return str(path.relative_to(repo))
    except ValueError:
        return str(path)


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


def write_text_if_changed(path: Path, text: str, recorder: Recorder, label: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and read_text(path) == text:
        recorder.add("unchanged", label)
        return
    status = "updated" if path.exists() else "created"
    path.write_text(text, encoding="utf-8")
    recorder.add(status, label)


def ensure_executable(path: Path) -> None:
    mode = path.stat().st_mode
    path.chmod(mode | 0o755)


def install_codex_rules(repo: Path, recorder: Recorder) -> None:
    src = ASSETS / "rules" / "git-commit.rules"
    dst = repo / ".codex" / "rules" / "git-commit.rules"
    write_text_if_changed(dst, read_text(src), recorder, str(dst.relative_to(repo)))


def install_codex_hook_script(repo: Path, recorder: Recorder) -> None:
    src = PLUGIN_ROOT / "scripts" / "git_command_policy.py"
    dst = repo / ".codex" / "hooks" / "git_command_policy.py"
    write_text_if_changed(dst, read_text(src), recorder, str(dst.relative_to(repo)))
    ensure_executable(dst)


def merge_hooks_json(repo: Path, recorder: Recorder) -> None:
    src = ASSETS / "hooks" / "hooks.json"
    template = json.loads(read_text(src))
    dst = repo / ".codex" / "hooks.json"
    if dst.exists():
        payload = json.loads(read_text(dst))
    else:
        payload = {"hooks": {}}

    if not isinstance(payload, dict):
        raise SystemExit(f"error: {dst} must contain a JSON object")
    hooks = payload.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise SystemExit(f"error: {dst} field 'hooks' must be an object")

    changed = False
    for event, groups in template.get("hooks", {}).items():
        target_groups = hooks.setdefault(event, [])
        if not isinstance(target_groups, list):
            raise SystemExit(f"error: {dst} hooks.{event} must be an array")
        existing_commands = {
            hook.get("command")
            for group in target_groups
            if isinstance(group, dict)
            for hook in group.get("hooks", [])
            if isinstance(hook, dict)
        }
        for group in groups:
            group_commands = {
                hook.get("command")
                for hook in group.get("hooks", [])
                if isinstance(hook, dict)
            }
            if group_commands and group_commands <= existing_commands:
                continue
            target_groups.append(group)
            changed = True

    text = json.dumps(payload, indent=2) + "\n"
    if changed or not dst.exists():
        write_text_if_changed(dst, text, recorder, str(dst.relative_to(repo)))
    else:
        recorder.add("unchanged", str(dst.relative_to(repo)))


def ensure_codex_hooks_feature(repo: Path, recorder: Recorder) -> None:
    path = repo / ".codex" / "config.toml"
    original = read_text(path)
    if not original.strip():
        write_text_if_changed(path, "[features]\ncodex_hooks = true\n", recorder, str(path.relative_to(repo)))
        return

    lines = original.splitlines()
    section_start = None
    for index, line in enumerate(lines):
        if line.strip() == "[features]":
            section_start = index
            break

    if section_start is None:
        updated = original.rstrip() + "\n\n[features]\ncodex_hooks = true\n"
        write_text_if_changed(path, updated, recorder, str(path.relative_to(repo)))
        return

    section_end = len(lines)
    for index in range(section_start + 1, len(lines)):
        stripped = lines[index].strip()
        if stripped.startswith("[") and stripped.endswith("]"):
            section_end = index
            break

    for index in range(section_start + 1, section_end):
        stripped = lines[index].strip()
        if stripped.startswith("codex_hooks"):
            if stripped == "codex_hooks = true":
                recorder.add("unchanged", str(path.relative_to(repo)))
                return
            lines[index] = "codex_hooks = true"
            write_text_if_changed(path, "\n".join(lines) + "\n", recorder, str(path.relative_to(repo)))
            return

    lines.insert(section_start + 1, "codex_hooks = true")
    write_text_if_changed(path, "\n".join(lines) + "\n", recorder, str(path.relative_to(repo)))


def install_git_hook(repo: Path, hook_name: str, force: bool, recorder: Recorder) -> None:
    src = ASSETS / "git-hooks" / hook_name
    dst = git_path(repo, f"hooks/{hook_name}")
    label = display_path(repo, dst)
    source_text = read_text(src)
    existing = read_text(dst)
    marker = f"codex-git-plugin: {hook_name}"

    if dst.exists() and marker not in existing and existing.strip() and not force:
        recorder.add("skipped", f"{label} exists and is not managed by this plugin")
        return

    write_text_if_changed(dst, source_text, recorder, label)
    ensure_executable(dst)


def parse_hook_list(value: str | None, all_hooks: bool) -> tuple[str, ...]:
    if all_hooks:
        return ALL_HOOKS
    if not value:
        return DEFAULT_HOOKS
    requested = tuple(part.strip() for part in value.split(",") if part.strip())
    unknown = sorted(set(requested) - set(ALL_HOOKS))
    if unknown:
        raise SystemExit(f"error: unknown hook(s): {', '.join(unknown)}")
    return requested


def show_plan(repo: Path, hooks: tuple[str, ...]) -> None:
    print("Codex git workflow setup plan")
    print(f"repo: {repo}")
    print("will manage:")
    print("  .codex/rules/git-commit.rules")
    print("  .codex/hooks/git_command_policy.py")
    print("  .codex/hooks.json")
    print("  .codex/config.toml ([features].codex_hooks = true)")
    for hook in hooks:
        print(f"  .git/hooks/{hook}")


def check_install(repo: Path, hooks: tuple[str, ...]) -> int:
    checks = [
        repo / ".codex" / "rules" / "git-commit.rules",
        repo / ".codex" / "hooks" / "git_command_policy.py",
        repo / ".codex" / "hooks.json",
        repo / ".codex" / "config.toml",
    ]
    checks.extend(git_path(repo, f"hooks/{hook}") for hook in hooks)

    missing = []
    for path in checks:
        if path.exists():
            print(f"ok: {display_path(repo, path)}")
        else:
            print(f"missing: {display_path(repo, path)}")
            missing.append(path)
    return 1 if missing else 0


def apply_setup(repo: Path, hooks: tuple[str, ...], force: bool) -> None:
    recorder = Recorder()
    install_codex_rules(repo, recorder)
    install_codex_hook_script(repo, recorder)
    merge_hooks_json(repo, recorder)
    ensure_codex_hooks_feature(repo, recorder)
    for hook in hooks:
        install_git_hook(repo, hook, force, recorder)
    recorder.print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Install Codex git commit workflow guardrails.")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--show", action="store_true", help="Show planned setup without writing files")
    mode.add_argument("--apply", action="store_true", help="Install or update setup files")
    mode.add_argument("--check", action="store_true", help="Check whether setup files are present")
    parser.add_argument("--all", action="store_true", help="Install all bundled native git hooks")
    parser.add_argument("--hooks", help="Comma-separated native git hooks to install")
    parser.add_argument("--force", action="store_true", help="Overwrite third-party git hooks")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    hooks = parse_hook_list(args.hooks, args.all)
    repo = run_git_root()

    if args.check:
        return check_install(repo, hooks)
    if args.apply:
        apply_setup(repo, hooks, args.force)
        return 0
    show_plan(repo, hooks)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
