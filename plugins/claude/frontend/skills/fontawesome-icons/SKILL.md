---
name: fontawesome
description: "This skill should be used when the user asks about Font Awesome icons — selection, animation (fa-spin, fa-beat, fa-bounce, fa-fade, fa-shake, fa-flip), styling, troubleshooting, or project setup. Triggers on: fa-solid, fa-regular, fa-light, fa-duotone, fa-brands, fa-sharp, FontAwesomeIcon, @fortawesome, fa-fw, fa-stack, fa-layers, or any fa- CSS class. Provides FA7 documentation-backed answers via bundled reference files."
---

# Font Awesome Icon Expert

This skill delegates to the `fontawesome` agent, which has access to the complete Font Awesome 7 web documentation (75 reference files covering setup, styling, animations, framework integrations, accessibility, and troubleshooting). The agent provides documentation-backed answers that are more accurate than general knowledge — especially for FA7-specific features.

## Why this skill matters

Font Awesome 7 introduced CSS custom properties (`--fa-animation-duration`, `--fa-beat-scale`, `--fa-flip-angle`, etc.) that replaced the old approach of overriding CSS animation properties directly. Without consulting the documentation, answers will use outdated generic CSS patterns instead of the correct FA7 APIs. This skill ensures every answer uses the right approach.

## When to use this skill

Use this skill for ANY request involving Font Awesome, including but not limited to:

- Choosing icons for UI elements (buttons, navigation, status indicators, settings pages)
- Animating icons (spin, pulse, beat, bounce, fade, shake, flip) or customizing animation timing
- Styling icons (sizing, rotation, flipping, stacking, layering, power transforms, masking, duotone)
- Troubleshooting icons not rendering, wrong icon showing, animation issues, blurry icons
- Diagnosing Free vs Pro issues (fa-light, fa-duotone, fa-thin, fa-sharp require Pro)
- Setting up Font Awesome in React, Vue, Angular, WordPress, or other frameworks
- Replacing emoji or text with proper FA icons
- Planning icon usage across a feature, page, or entire project
- Dark mode icon toggles, notification badges on FA icons, icon swapping on state change
- Comparing webfont vs SVG+JS rendering methods

## Before delegating

BEFORE dispatching, use AskUserQuestion to clarify the user's intent. Every question to the user MUST go through AskUserQuestion — never ask as plain text. Common things to clarify:
- Whether they're using Free or Pro (many icons/features are Pro-only)
- Their integration method (CDN, npm, framework component)
- Whether they need icon selection, animation, styling, or setup help

## How to use

Dispatch the `frontend:fontawesome` agent with the user's question or task. Do not answer Font Awesome questions from general knowledge — the agent has access to the full official FA7 documentation for more accurate answers.

The agent will:
1. Resolve the plugin root path to find the bundled docs
2. Look up the relevant documentation files (style guides, setup docs, framework integration, etc.)
3. Answer with documentation-backed guidance, complete CSS classes, and accessibility best practices
4. Offer 2-3 alternatives with rationale when selecting icons
5. Flag whether icons/features require Font Awesome Pro
