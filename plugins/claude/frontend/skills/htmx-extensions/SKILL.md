---
name: htmx-extensions
description: "This skill should be used when the user asks about HTMX extensions, \"hx-ext\", \"idiomorph\", \"morphdom\", \"alpine-morph\", \"multi-swap\", \"json-enc\", \"loading-states\", \"path-deps\", \"preload\", \"remove-me\", \"restored\", \"debug\", HTMX extension configuration, writing a custom HTMX extension, WebSocket via HTMX extension, SSE via HTMX extension, or morphing-based DOM updates to preserve Alpine.js or other client state."
---

# HTMX Extensions

This skill delegates to the `htmx-go` agent, which fetches current HTMX extension documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for HTMX extension configuration and use.

## Why this skill matters

HTMX's default `innerHTML` swap destroys and recreates DOM elements, wiping Alpine.js reactive state, form focus, scroll position, and CSS transitions. Morphing extensions (idiomorph, morphdom) solve this by diffing the DOM and making surgical updates. SSE and WebSocket extensions provide first-class real-time support without custom JavaScript. Using the wrong extension — or not using one when needed — leads to subtle state loss bugs and broken animations.

## When to use this skill

Use for ANY request involving:

- Enabling extensions: `hx-ext="extension-name"` (global or per-element)
- **Morphing**: idiomorph (recommended), morphdom, alpine-morph — preserves client state on swap
- **Real-time**: SSE extension (`hx-ext="sse"`), WebSocket extension (`hx-ext="ws"`)
- **Multi-swap**: `hx-ext="multi-swap"` — update multiple targets with one response
- **Utility**: `json-enc` (JSON request body), `loading-states`, `preload`, `remove-me`
- Writing custom HTMX extensions
- Alpine.js state loss after HTMX swap (morphing fix)

## Common patterns

### Idiomorph (recommended morphing extension)
```html
<!-- Enable globally on body -->
<body hx-ext="idiomorph">
  <div hx-get="/component" hx-swap="morph:innerHTML">
    <!-- Alpine.js state preserved on swap -->
    <div x-data="{ count: 0 }">
      <button @click="count++">Clicks: <span x-text="count"></span></button>
    </div>
  </div>
</body>
```

### SSE extension
```html
<div hx-ext="sse"
     sse-connect="/events"
     sse-swap="message"
     hx-target="#feed"
     hx-swap="beforeend">
</div>
<div id="feed"></div>
```

### WebSocket extension
```html
<div hx-ext="ws" ws-connect="/ws">
  <form ws-send>
    <input name="message" type="text">
    <button type="submit">Send</button>
  </form>
  <div id="messages"></div>
</div>
```

### Multi-swap extension
```html
<!-- Server returns: <div id="a">...</div><div id="b">...</div> -->
<button hx-get="/update-two"
        hx-ext="multi-swap"
        hx-swap="multi:#a:innerHTML,#b:outerHTML">
  Update Both
</button>
```

### Custom extension skeleton
```javascript
htmx.defineExtension('my-ext', {
  onEvent: function(name, evt) {
    if (name === 'htmx:beforeRequest') {
      evt.detail.headers['X-Custom'] = 'value';
    }
  }
});
```

## Before delegating

BEFORE dispatching, use AskUserQuestion to clarify the user's intent. Every question to the user MUST go through AskUserQuestion — never ask as plain text. Common things to clarify:
- Whether the issue is Alpine.js state loss (morphing extension), real-time updates (SSE/WS), or other
- Which HTMX version they're using (extension API differs between HTMX 1.x and 2.x)
- Whether Alpine.js is in use (affects morphing extension choice)

## How to use

Dispatch the `frontend:htmx-go` agent with the user's question or task. Do not answer HTMX extension questions from general knowledge — the agent fetches current documentation for more accurate answers.

The agent will:
1. Identify which extension solves the user's problem
2. Look up current extension documentation via context7 MCP or WebSearch
3. Provide HTML configuration and (for SSE/WS) Go server-side code
4. Explain extension installation (CDN vs npm vs bundled)
