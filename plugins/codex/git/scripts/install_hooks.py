#!/usr/bin/env python3
"""Install Codex and git guardrails for the git commit workflow."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tomllib
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


def mutation_rules(template: str) -> str:
    start = template.index('prefix_rule(\n    pattern = ["git", "add"]')
    end = template.index('prefix_rule(\n    pattern = ["git", "reset"', start)
    allowed = (
        ("git", "add", "--"),
        ("git", "commit", "-m"),
        ("git", "commit", "--amend", "-m"),
        ("git", "commit", "--no-edit"),
        ("git", "commit", "--only", "-m"),
    )
    rules = "".join(
        "prefix_rule(\n"
        f"    pattern = {json.dumps(prefix)},\n"
        '    decision = "allow",\n'
        '    justification = "The user opted in to automatic Git operations for the commit workflow.",\n'
        ")\n\n"
        for prefix in allowed
    )
    return template[:start].replace(
        "# inspection is allowed; staging and committing prompt unless the user changes\n# the policy locally.",
        "# inspection is allowed. The user opted in to the Git command forms below.",
    ) + rules + template[end:]


def install_codex_rules(repo: Path, choice: str | None, recorder: Recorder) -> None:
    src = ASSETS / "rules" / "git-commit.rules"
    dst = repo / ".codex" / "rules" / "git-commit.rules"
    label = str(dst.relative_to(repo))
    prompt = read_text(src)
    automatic = mutation_rules(prompt)
    existing = read_text(dst)
    if dst.exists() and existing not in (prompt, automatic):
        recorder.add("skipped", f"{label} has local changes; existing rules were preserved")
        return
    target = automatic if choice == "allow" or (choice is None and existing == automatic) else prompt
    write_text_if_changed(dst, target, recorder, label)


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


def hooks_enabled(repo: Path) -> bool:
    path = repo / ".codex" / "config.toml"
    try:
        features = tomllib.loads(read_text(path)).get("features", {})
    except tomllib.TOMLDecodeError as error:
        raise SystemExit(f"error: invalid TOML in {path}: {error}") from error
    if not isinstance(features, dict):
        raise SystemExit(f"error: features in {path} must be a TOML table")
    return features.get("hooks", features.get("codex_hooks", True)) is not False


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
    for hook in hooks:
        print(f"  {display_path(repo, git_path(repo, f'hooks/{hook}'))}")


def check_install(repo: Path, hooks: tuple[str, ...]) -> int:
    checks = [
        repo / ".codex" / "rules" / "git-commit.rules",
        repo / ".codex" / "hooks" / "git_command_policy.py",
        repo / ".codex" / "hooks.json",
    ]
    git_hooks = [git_path(repo, f"hooks/{hook}") for hook in hooks]
    checks.extend(git_hooks)

    missing = []
    for path in checks:
        if path.is_file() and (path not in git_hooks or bool(path.stat().st_mode & 0o111)):
            print(f"ok: {display_path(repo, path)}")
        else:
            print(f"missing or inactive: {display_path(repo, path)}")
            missing.append(path)
    rules = read_text(checks[0]) if checks[0].is_file() else ""
    default = read_text(ASSETS / "rules" / "git-commit.rules")
    if rules == mutation_rules(default):
        print("Git rules: workflow allow rules installed")
    elif rules == default:
        print("Git rules: prompts configured")
    elif rules:
        print("Git rules: locally edited")
    enabled = hooks_enabled(repo)
    print("Codex hooks: disabled in project configuration" if not enabled
          else "Codex hooks: check trust and activation in the client")
    return 1 if missing or not enabled else 0


def apply_setup(repo: Path, hooks: tuple[str, ...], force: bool, choice: str | None) -> None:
    recorder = Recorder()
    enabled = hooks_enabled(repo)
    if not enabled and choice == "allow":
        raise SystemExit("error: project disables Codex hooks; keep prompts or enable hooks before opting in")
    install_codex_hook_script(repo, recorder)
    merge_hooks_json(repo, recorder)
    if not enabled:
        recorder.add("disabled", "Codex hooks are disabled in .codex/config.toml")
    for hook in hooks:
        install_git_hook(repo, hook, force, recorder)
    install_codex_rules(repo, choice, recorder)
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
    parser.add_argument("--git-mutations", choices=("prompt", "allow"),
                        help="Set the approval choice made in the Codex setup questionnaire")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.git_mutations and not args.apply:
        raise SystemExit("error: --git-mutations requires --apply")
    hooks = parse_hook_list(args.hooks, args.all)
    repo = run_git_root()

    if args.check:
        return check_install(repo, hooks)
    if args.apply:
        apply_setup(repo, hooks, args.force, args.git_mutations)
        return 0
    show_plan(repo, hooks)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
