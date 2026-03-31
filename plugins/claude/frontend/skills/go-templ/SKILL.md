---
name: go-templ
description: "This skill should be used when the user asks about a-h/templ, \".templ files\", \"templ component\", \"templ generate\", \"templ.Handler\", \"templ.Component\", \"templ partial\", \"templ layout\", \"templ slot\", \"templ children\", \"{ children... }\", \"templ if/for\", \"templ CSS\", compiling templ files, Air live reload with templ, or Go server-side HTML rendering using the templ library. Also triggers on questions about type-safe Go HTML templates, replacing html/template with templ, or generating Go code from .templ files."
---

# Go templ Components

This skill delegates to the `htmx-go` agent, which fetches current templ documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for a-h/templ component patterns and Go integration.

## Why this skill matters

templ is a Go HTML component library that compiles `.templ` files to type-safe Go code at build time. It's 10–15x faster than `html/template` with far fewer allocations, and it produces composable components callable as regular Go functions. The `.templ` syntax has specific rules (especially for expressions, conditionals, and children slots) that differ from html/template and cause compile errors or XSS if misused. Understanding partial components for HTMX fragments is critical — the same component tree must be splittable into a full-page layout and a fragment-only partial.

## When to use this skill

Use for ANY request involving:

- Creating templ components (`.templ` files)
- Layout and base page components (`{ children... }` slots)
- Partial components for HTMX fragment responses
- Compiling templ files (`templ generate`)
- Using `templ.Handler()` in HTTP handlers
- Writing templ conditionals and loops (`if`, `for`)
- templ CSS classes (`templ.KV()`, `templ.Classes()`)
- Passing Go data to templ components (typed props)
- Air live reload configuration with templ
- Migrating from `html/template` to templ

## Common patterns

### Basic component
```go
// components/button.templ
package components

templ Button(label string, variant string) {
    <button class={ templ.KV("btn-primary", variant == "primary"), templ.KV("btn-secondary", variant == "secondary") }>
        { label }
    </button>
}
```

### Layout with children slot
```go
// layouts/base.templ
package layouts

templ Base(title string) {
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{ title }</title>
        <script src="https://unpkg.com/htmx.org@2" defer></script>
        <script defer>
          document.addEventListener("htmx:configRequest", function() {
            htmx.config.responseHandling = [
              {code: "204", swap: false},
              {code: "[23]..", swap: true},
              {code: "422", swap: true},
              {code: "[45]..", swap: false, error: true},
              {code: "...", swap: false, error: true}
            ];
          });
        </script>
        <!-- SSE extension: required for hx-ext="sse". For WebSocket (hx-ext="ws"), add htmx-ext-ws separately -->
        <script src="https://unpkg.com/htmx-ext-sse@2" defer></script>
    </head>
    <body>
        <main>
            { children... }
        </main>
    </body>
    </html>
}
```

### Page using layout
```go
// pages/home.templ
package pages

import "myapp/layouts"
import "myapp/components"

templ HomePage(items []Item) {
    @layouts.Base("Home") {
        <h1>Items</h1>
        @components.ItemList(items)
    }
}
```

### Partial for HTMX fragment
```go
// components/item_list.templ
package components

// Full list — returned for both full page and HTMX fragment
templ ItemList(items []Item) {
    <ul id="items">
        for _, item := range items {
            @ItemRow(item)
        }
    </ul>
}

// Single row — for targeted partial updates
templ ItemRow(item Item) {
    <li id={ "item-" + strconv.Itoa(item.ID) }>
        { item.Name }
    </li>
}
```

### Handler using templ (chi / net/http)
```go
func (h *Handler) List(w http.ResponseWriter, r *http.Request) {
    items, _ := h.store.List(r.Context())

    if r.Header.Get("HX-Request") == "true" {
        templ.Handler(components.ItemList(items)).ServeHTTP(w, r)
        return
    }
    templ.Handler(pages.HomePage(items)).ServeHTTP(w, r)
}
```

### Handler using templ (gin)
```go
// c.Request.Context() is a struct field (not a method call)
// c.Writer implements http.ResponseWriter directly
func (h *Handler) List(c *gin.Context) {
    items, _ := h.store.List(c.Request.Context())

    if c.GetHeader("HX-Request") == "true" {
        components.ItemList(items).Render(c.Request.Context(), c.Writer)
        return
    }
    pages.HomePage(items).Render(c.Request.Context(), c.Writer)
}
```

### Conditional rendering
```go
templ UserCard(user User) {
    <div class="card">
        { user.Name }
        if user.IsAdmin {
            <span class="badge">Admin</span>
        }
    </div>
}
```

### Loop with index
```go
templ Table(rows []Row) {
    <table>
        for i, row := range rows {
            <tr class={ templ.KV("even", i%2 == 0) }>
                <td>{ row.Label }</td>
            </tr>
        }
    </table>
}
```

### Compilation and build
```makefile
# Makefile
.PHONY: generate build

generate:
	templ generate

build: generate
	go build ./...

watch:
	air  # uses .air.toml
```

```toml
# .air.toml
[build]
  cmd = "templ generate && go build -o ./tmp/main ."
  include_ext = ["go", "templ"]
```

## Before delegating

BEFORE dispatching, use AskUserQuestion to clarify the user's intent. Every question to the user MUST go through AskUserQuestion — never ask as plain text. Common things to clarify:
- Whether they're creating a new component or debugging a compile error
- Whether this is a full-page component or a fragment partial for HTMX
- Whether they're using Air for live reload

## How to use

Dispatch the `frontend:htmx-go` agent with the user's question or task. Do not answer templ questions from general knowledge — the agent fetches current documentation for more accurate answers.

The agent will:
1. Check for `.templ` files and `go.mod` to understand the project structure
2. Look up current templ documentation via context7 MCP or WebSearch
3. Answer with complete, compilable `.templ` and `.go` examples
4. Remind about the `templ generate` compilation step when relevant
