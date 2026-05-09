#!/usr/bin/env python3
"""
marketplace_inventory.py — List plugins installed from the pragmatic marketplace.

Reads the user's Claude Code plugin install state and returns metadata
for every plugin installed from the pragmatic marketplace, including
the components (skills, commands, agents) each plugin contributes.

This is the mechanical layer of `capability-radar`. It answers:
"what installed-and-from-pragmatic plugins exist on this machine, and
what do they offer?" The skill then judges which ones (if any)
substantially fit the user's task.

Plugins from other marketplaces are ignored. Uninstalled plugins
in the pragmatic marketplace catalog are NOT inspected — install-mid-task
is too disruptive to recommend.

USAGE
    python3 marketplace_inventory.py

OUTPUT
    A JSON object on stdout:
    {
      "marketplace": "pragmatic",
      "marketplace_known": true | false,
      "plugins": [
        {
          "name": "<plugin name>",
          "version": "<version>",
          "install_path": "<absolute path>",
          "description": "<from plugin.json, or null>",
          "keywords": ["...", ...],
          "components": {
            "commands": [{"name": "...", "description": "..."}],
            "agents": [{"name": "...", "description": "..."}],
            "skills": [{"name": "...", "description": "..."}]
          }
        }
      ]
    }

EXIT CODES
    0   Always. Corrupted plugin state files (malformed JSON in
        installed_plugins.json or known_marketplaces.json) fall back
        to empty results without erroring.

NOTES
    - Plugin install state is at ~/.claude/plugins/installed_plugins.json
    - Marketplace state is at ~/.claude/plugins/known_marketplaces.json
    - If neither file exists, the script returns an empty plugins list with
      marketplace_known=false. This is normal for a fresh install.
    - Component descriptions are extracted from frontmatter `description:`
      fields. Files without frontmatter are still listed by name.
"""

import json
import os
import re
import sys
from pathlib import Path

MARKETPLACE_NAME = "pragmatic"


def home_claude_plugins() -> Path:
    """Return ~/.claude/plugins/, the standard install root."""
    return Path.home() / ".claude" / "plugins"


def is_marketplace_known(plugins_root: Path) -> bool:
    """Check whether the pragmatic marketplace is configured."""
    known_path = plugins_root / "known_marketplaces.json"
    if not known_path.exists():
        return False
    try:
        with open(known_path) as f:
            known = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False

    # The shape of known_marketplaces.json varies across Claude Code versions.
    # Try a few plausible shapes.
    if isinstance(known, dict):
        if "marketplaces" in known and isinstance(known["marketplaces"], dict):
            return MARKETPLACE_NAME in known["marketplaces"]
        if MARKETPLACE_NAME in known:
            return True
    return False


def list_installed_pragmatic_plugins(plugins_root: Path) -> list[dict]:
    """Read installed_plugins.json and return entries from pragmatic only."""
    installed_path = plugins_root / "installed_plugins.json"
    if not installed_path.exists():
        return []

    try:
        with open(installed_path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return []

    plugins_dict = data.get("plugins", {}) if isinstance(data, dict) else {}
    results = []

    for key, entries in plugins_dict.items():
        # Keys look like "plugin-name@marketplace-name"
        if not key.endswith(f"@{MARKETPLACE_NAME}"):
            continue
        plugin_name = key.rsplit("@", 1)[0]

        # entries may be a list (most common) or a single dict
        if isinstance(entries, list):
            entry = entries[0] if entries else {}
        elif isinstance(entries, dict):
            entry = entries
        else:
            continue

        install_path = entry.get("installPath")
        version = entry.get("version", "unknown")
        if install_path:
            results.append({
                "name": plugin_name,
                "version": version,
                "install_path": install_path,
            })

    return results


def extract_frontmatter_description(file_path: Path) -> str | None:
    """Pull the 'description' field from a markdown file's frontmatter."""
    try:
        with open(file_path) as f:
            content = f.read(4096)  # Frontmatter is at the top; read first 4KB
    except OSError:
        return None

    fm_match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return None
    desc_match = re.search(r"^description:\s*(.+?)$", fm_match.group(1), re.MULTILINE)
    if desc_match:
        # Description may be multi-line in YAML; we take just the first line
        return desc_match.group(1).strip()[:300]
    return None


def discover_components(plugin_dir: Path) -> dict:
    """List skills, commands, and agents contributed by a plugin."""
    components = {"commands": [], "agents": [], "skills": []}

    commands_dir = plugin_dir / "commands"
    if commands_dir.is_dir():
        for cmd_file in sorted(commands_dir.glob("*.md")):
            components["commands"].append({
                "name": cmd_file.stem,
                "description": extract_frontmatter_description(cmd_file),
            })

    agents_dir = plugin_dir / "agents"
    if agents_dir.is_dir():
        for agent_file in sorted(agents_dir.glob("*.md")):
            components["agents"].append({
                "name": agent_file.stem,
                "description": extract_frontmatter_description(agent_file),
            })

    skills_dir = plugin_dir / "skills"
    if skills_dir.is_dir():
        for skill_dir in sorted(skills_dir.iterdir()):
            if skill_dir.is_dir():
                skill_md = skill_dir / "SKILL.md"
                if skill_md.exists():
                    components["skills"].append({
                        "name": skill_dir.name,
                        "description": extract_frontmatter_description(skill_md),
                    })

    return components


def read_plugin_metadata(install_path: str) -> dict:
    """Read plugin.json and return name, description, keywords."""
    plugin_dir = Path(install_path)
    manifest = plugin_dir / ".claude-plugin" / "plugin.json"
    if not manifest.exists():
        return {"description": None, "keywords": []}

    try:
        with open(manifest) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return {"description": None, "keywords": []}

    return {
        "description": data.get("description"),
        "keywords": data.get("keywords", []),
    }


def main() -> int:
    plugins_root = home_claude_plugins()
    marketplace_known = is_marketplace_known(plugins_root)
    installed = list_installed_pragmatic_plugins(plugins_root)

    plugins_output = []
    for plugin in installed:
        try:
            metadata = read_plugin_metadata(plugin["install_path"])
            components = discover_components(Path(plugin["install_path"]))
        except Exception as e:
            print(f"Warning: could not read {plugin['name']}: {e}", file=sys.stderr)
            metadata = {"description": None, "keywords": []}
            components = {"commands": [], "agents": [], "skills": []}

        plugins_output.append({
            "name": plugin["name"],
            "version": plugin["version"],
            "install_path": plugin["install_path"],
            "description": metadata["description"],
            "keywords": metadata["keywords"],
            "components": components,
        })

    output = {
        "marketplace": MARKETPLACE_NAME,
        "marketplace_known": marketplace_known,
        "plugins": plugins_output,
    }
    print(json.dumps(output, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
