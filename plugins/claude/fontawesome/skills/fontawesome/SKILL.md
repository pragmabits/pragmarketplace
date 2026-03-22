---
name: fontawesome
description: "Font Awesome 7 icon expert with access to the complete official FA7 web documentation (75 reference files). This skill provides verified, documentation-backed answers that are more accurate than general knowledge — especially for FA7-specific APIs like CSS custom properties (--fa-animation-duration, --fa-beat-scale), the Pro vs Free icon family matrix, framework integrations (React, Vue, Angular), and accessibility patterns.\n\nYou MUST use this skill whenever a user's request involves Font Awesome icons in any way: selecting icons for UI elements, animating icons (fa-spin, fa-beat, fa-bounce, fa-fade, fa-shake, fa-flip), styling icons (sizing, rotation, stacking, layering, duotone, power transforms, masking), troubleshooting icons not rendering, diagnosing Free vs Pro issues, setting up Font Awesome in a project, replacing emoji with FA icons, or planning icon usage across a feature or page.\n\nAlso use this skill when the user mentions fa-solid, fa-regular, fa-light, fa-thin, fa-duotone, fa-brands, fa-sharp, FontAwesomeIcon, @fortawesome, fa-fw, fa-stack, fa-layers, or any fa- CSS class — even in passing. The skill's documentation access makes it strictly superior to answering from general knowledge for any Font Awesome question."
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

## How to use

Invoke the `/fontawesome` command, passing the user's question or task as the argument:

```
/fontawesome <user's question or task>
```

The agent will:
1. Resolve the plugin root path to find the bundled docs
2. Look up the relevant documentation files (style guides, setup docs, framework integration, etc.)
3. Answer with documentation-backed guidance, complete CSS classes, and accessibility best practices
4. Offer 2-3 alternatives with rationale when selecting icons
5. Flag whether icons/features require Font Awesome Pro

Do not attempt to answer Font Awesome questions yourself — the agent has access to the full official FA7 documentation and will provide more accurate, up-to-date answers. Let the agent handle it.
