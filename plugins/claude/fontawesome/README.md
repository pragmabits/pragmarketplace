# Font Awesome Plugin

Font Awesome icon expert agent — selection, animation, styling, and integration guidance powered by the official FA 7 documentation.

## Overview

The Font Awesome plugin provides a **specialized agent** (fontawesome) that helps with icon selection, animation, styling, troubleshooting, and project-wide icon planning. The agent reads from the bundled FA 7 web documentation on demand rather than embedding it inline.

### Architecture

```
/fontawesome (gateway) -> fontawesome (all logic)
```

**How it works:**
1. User runs `/fontawesome <question>`
2. Command delegates to the fontawesome agent with the plugin root path
3. Agent looks up relevant docs from `docs/web/` using Read/Glob/Grep
4. Agent answers with verified, documentation-backed guidance

### Features

- **Icon Selection**: Semantically appropriate icon recommendations with alternatives
- **Animation & Styling**: Built-in FA animation classes and CSS variable customization
- **Project Planning**: Comprehensive icon plans mapping UI elements to icons
- **Framework Integration**: React, Vue, Angular, WordPress, and more
- **Accessibility**: Proper aria attributes and semantic markup
- **Free vs Pro**: Clear indication of which features require Pro
- **On-demand Docs**: Reads from 75 official FA 7 docs files as needed

## Available Commands

### `/fontawesome`

Ask any Font Awesome question or request icon guidance.

**Usage:**
```
/fontawesome [question or task]
```

**Examples:**
```bash
# Icon selection
/fontawesome suggest an icon for a delete button

# Animation help
/fontawesome how to make an icon spin while loading

# Project planning
/fontawesome plan all icons for a dashboard sidebar

# Styling
/fontawesome how to use duotone icons with custom colors

# Troubleshooting
/fontawesome icons not rendering in my React app
```

## Documentation

The `docs/` directory contains the complete Font Awesome 7 web documentation:

- `docs/web/setup/` — Installation and setup guides
- `docs/web/add-icons/` — Methods for adding icons
- `docs/web/style/` — Styling, animation, sizing, transforms
- `docs/web/use-with/` — Framework integrations (React, Vue, Angular, etc.)
- `docs/web/dig-deeper/` — Accessibility, performance, security
- `docs/web/upload-icons/` — Custom icon uploads
- `docs/web/troubleshoot/` — Troubleshooting guides

## Installation

This plugin is automatically loaded by Claude Code when present in the plugins directory.

**Expected location:**
- `<project>/plugins/claude/fontawesome/` (project installation)

## Versioning

- **Current version:** 1.0.0
- **Versioning:** Semantic Versioning (MAJOR.MINOR.PATCH)

### Version History

#### v1.0.0 - March 2026
- **Initial release** as a plugin (migrated from standalone agent)
- fontawesome agent with on-demand documentation lookup
- `/fontawesome` command as gateway
- Bundled FA 7 web documentation (75 files)
- Slim agent manifest (~150 lines vs ~400 inline)

## License

Property of Pragmabits.

## Contact

**Author:** Leonardo Leoncio
**Email:** leonardoleoncio96@gmail.com
**Company:** Pragmabits

---

**Version:** 1.0.0
**Updated:** March 2026
**Status:** Active
