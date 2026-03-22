# Security

Source: https://docs.fontawesome.com/web/dig-deeper/security

## Report an Issue

Font Awesome emphasizes responsible disclosure. Security vulnerabilities should be reported privately before public announcement. Contact the Font Awesome team directly via email.

## Content Security Policy (CSP)

CSP helps prevent cross-site scripting and data injection attacks through HTTP headers or meta tags. The SVG with JavaScript library has a known limitation: it automatically adds CSS to the DOM's head element, which violates strict CSP policies.

### Recommended Solutions

1. Disable automatic CSS insertion
2. Reference external CSS files explicitly
3. Extract CSS from bundles when using package managers

### Implementation — Self-Hosting

Add the `data-auto-add-css="false"` attribute to script tags and link to the external stylesheet separately:

```html
<link href="/your-path-to-fontawesome/css/svg-with-js.css" rel="stylesheet" />
<script defer data-auto-add-css="false" src="/your-path-to-fontawesome/js/fontawesome.js"></script>
<script defer data-auto-add-css="false" src="/your-path-to-fontawesome/js/solid.js"></script>
```

### Implementation — npm Packages

For `fontawesome-svg-core`, set `config.autoAddCss = false` before making Font Awesome API calls:

```javascript
import { config } from '@fortawesome/fontawesome-svg-core'
config.autoAddCss = false
```

> **Note:** Web Fonts with CSS don't require these CSP workarounds.
