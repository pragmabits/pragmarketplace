# AI Agent Tools

Source: https://docs.fontawesome.com/web/use-with/ai-agent-tools

Font Awesome now has official agent tools that let AI coding assistants find and add the right icons to projects. They distribute as Skills compatible with Claude Code, Cursor, GitHub Copilot, Windsurf, and additional platforms.

## Installation

```bash
npx skills add fontawesome-agent-tools
```

Two skills become available: `/suggest-icon` and `/add-icon`

### Claude Code Plugin Marketplace

```bash
claude plugin marketplace add FortAwesome/fontawesome-agent-tools
claude plugin install icons@fontawesome-agent-tools
```

### Claude Desktop Installation

Click Customize > Browse plugins > Personal tab > + > Add marketplace from GitHub > Enter `FortAwesome/fontawesome-agent-tools` > Install. Script-based skills require the "Code" tab as of March 2026.

## Suggest an Icon

```
/suggest-icon shopping cart
```

Searches the Font Awesome API, verifies availability, presents recommendations with icon names/families/styles/tier, and offers to add via `/add-icon`.

## Add an Icon

```
/add-icon cart-shopping
/add-icon cart-shopping style:regular location:the checkout button in src/components/Header.tsx
```

Can accept concepts instead of exact icon names.

## Supported Integrations

| Integration | What Gets Generated |
|-------------|---------------------|
| React | `@fortawesome/react-fontawesome` component with individual icon imports |
| Vue | `@fortawesome/vue-fontawesome` component |
| Angular | `<fa-icon>` component |
| SVG+JS Kit | `<i>` tags for Font Awesome Kit script |
| Web Fonts+CSS | `<i>` tags for CDN or npm-based web font packages |
| SVG Sprites | `<svg><use href="..."></use></svg>` references |
| Web Components | `<fa-icon>` custom elements |

## Project Configuration

First `/add-icon` use triggers project scanning (package installations, version info, Free vs Pro licensing, import patterns). Saves to `.font-awesome.md` at project root. Commit this file for team-wide consistency.
