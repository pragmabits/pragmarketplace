---
name: htmx-attributes
description: "This skill should be used when the user asks about HTMX attributes, \"hx-get\", \"hx-post\", \"hx-put\", \"hx-delete\", \"hx-target\", \"hx-swap\", \"hx-trigger\", \"hx-boost\", \"hx-indicator\", \"hx-push-url\", \"hx-swap-oob\", \"hx-select\", \"hx-include\", \"hx-vals\", \"hx-headers\", \"hx-params\", \"hx-confirm\", \"hx-sync\", \"hx-encoding\", \"hx-on\", \"out-of-band swap\", \"HTMX attribute\", trigger modifiers (delay, throttle, from, changed, once, every, intersect, revealed), swap strategies (innerHTML, outerHTML, beforeend, afterend, delete, none), or needs help with HTMX declarative behavior, unexpected HTMX request behavior, or understanding how HTMX attributes interact."
---

# HTMX Attributes

This skill delegates to the `htmx-go` agent, which fetches current HTMX documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for all HTMX attribute syntax and behavior.

## Why this skill matters

HTMX's entire power is expressed through HTML attributes. The attribute system is deceptively expressive — `hx-trigger` alone supports polling, debounce, throttle, element-cross-listening, and DOM events. Wrong attribute combinations cause silent failures (no error, just no request) that are hard to debug without knowing the specification. Out-of-band swaps and trigger modifiers are particularly non-obvious and frequently misused.

## When to use this skill

Use for ANY request involving:

- Core request attributes: `hx-get`, `hx-post`, `hx-put`, `hx-patch`, `hx-delete`
- Target and swap: `hx-target`, `hx-swap`, `hx-select`
- Trigger configuration: `hx-trigger` with any modifier (delay, throttle, from, changed, once, every, intersect, revealed, load)
- Navigation: `hx-boost`, `hx-push-url`
- Progress/state: `hx-indicator`
- Multi-element updates: `hx-swap-oob` (out-of-band swaps)
- Request data: `hx-include`, `hx-vals`, `hx-headers`, `hx-params`
- UX: `hx-confirm`, `hx-sync`, `hx-disable`
- Event handling: `hx-on`
- Encoding: `hx-encoding` (for file uploads)

## Common patterns

### Basic request and target
```html
<button hx-get="/items" hx-target="#results" hx-swap="innerHTML">
  Load Items
</button>
<div id="results"></div>
```

### Trigger with debounce (live search)
```html
<input type="text" name="q"
       hx-get="/search"
       hx-target="#results"
       hx-trigger="keyup delay:300ms changed">
```

### Out-of-band swap (update two elements)
```html
<!-- Server returns this fragment; #toast is updated OOB -->
<ul id="items"><!-- updated list --></ul>
<div id="toast" hx-swap-oob="true" class="toast">Item saved!</div>
```

### Delete with row removal
```html
<tr id="row-42">
  <td>Item name</td>
  <td>
    <button hx-delete="/items/42"
            hx-target="#row-42"
            hx-swap="outerHTML"
            hx-confirm="Delete this item?">
      Delete
    </button>
  </td>
</tr>
```

### Polling
```html
<div hx-get="/status" hx-trigger="every 3s" hx-target="#status">
  Loading...
</div>
```

### Lazy load on scroll
```html
<div hx-get="/more-items"
     hx-trigger="revealed"
     hx-target="#item-list"
     hx-swap="beforeend">
  Loading more...
</div>
```

## Before delegating

BEFORE dispatching, use AskUserQuestion to clarify the user's intent. Every question to the user MUST go through AskUserQuestion — never ask as plain text. Common things to clarify:
- Which specific attribute or combination they're asking about
- Whether they're building a new feature or debugging unexpected behavior
- What the current HTML structure looks like (for debugging)

## How to use

Dispatch the `frontend:htmx-go` agent with the user's question or task. Do not answer HTMX attribute questions from general knowledge — the agent fetches current documentation for more accurate answers.

The agent will:
1. Check the user's project context (HTMX version, router, template engine)
2. Look up current HTMX documentation via context7 MCP or WebSearch
3. Answer with working HTML and Go examples
4. Flag common pitfalls (wrong trigger syntax, missing hx-target, OOB misuse)
