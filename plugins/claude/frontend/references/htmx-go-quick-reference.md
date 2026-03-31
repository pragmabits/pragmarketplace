# HTMX + Go Quick Reference

Quick lookup tables for the htmx-go agent.

---

## HTMX Core Attributes

| Attribute | Description | Example |
|-----------|-------------|---------|
| `hx-get` | GET request on trigger | `hx-get="/items"` |
| `hx-post` | POST request on trigger | `hx-post="/items"` |
| `hx-put` | PUT request on trigger | `hx-put="/items/1"` |
| `hx-patch` | PATCH request on trigger | `hx-patch="/items/1"` |
| `hx-delete` | DELETE request on trigger | `hx-delete="/items/1"` |
| `hx-target` | CSS selector for response target | `hx-target="#results"` |
| `hx-swap` | How to insert the response (see swap table) | `hx-swap="outerHTML"` |
| `hx-trigger` | Event that triggers request | `hx-trigger="click"`, `hx-trigger="change delay:500ms"` |
| `hx-boost` | Progressively enhance `<a>` and `<form>` | `hx-boost="true"` |
| `hx-indicator` | Element to show during request | `hx-indicator="#spinner"` |
| `hx-push-url` | Update browser URL after swap | `hx-push-url="true"` or `hx-push-url="/path"` |
| `hx-swap-oob` | Out-of-band swap (update elsewhere in DOM) | `hx-swap-oob="true"` |
| `hx-select` | CSS selector within response to use | `hx-select="#content"` |
| `hx-include` | Include extra elements in request | `hx-include="#filter-form"` |
| `hx-vals` | Extra values to include in request | `hx-vals='{"key": "value"}'` |
| `hx-headers` | Extra request headers | `hx-headers='{"X-Custom": "val"}'` |
| `hx-params` | Filter which params to send | `hx-params="*"` or `hx-params="none"` |
| `hx-confirm` | Confirm dialog before request | `hx-confirm="Are you sure?"` |
| `hx-disable` | Disable htmx on element | `hx-disable` |
| `hx-encoding` | Encoding type for requests | `hx-encoding="multipart/form-data"` |
| `hx-ext` | Enable HTMX extension | `hx-ext="idiomorph"` |
| `hx-sync` | Synchronize requests from element | `hx-sync="form:abort"` |
| `hx-on` | Event listener (htmx events) | `hx-on:htmx:after-swap="doSomething()"` |

---

## hx-trigger Modifiers

| Modifier | Description | Example |
|----------|-------------|---------|
| `delay:Xms` | Wait before sending | `hx-trigger="keyup delay:300ms"` |
| `throttle:Xms` | Rate-limit requests | `hx-trigger="keyup throttle:500ms"` |
| `from:<selector>` | Listen on different element | `hx-trigger="click from:#btn"` |
| `changed` | Only trigger if value changed | `hx-trigger="change changed"` |
| `once` | Only trigger once | `hx-trigger="load once"` |
| `consume` | Prevent event bubbling | `hx-trigger="click consume"` |
| `queue:first/last/all/none` | Queue strategy | `hx-trigger="click queue:last"` |
| `every Xs` | Polling | `hx-trigger="every 2s"` |
| `intersect` | Trigger when visible | `hx-trigger="intersect"` |
| `load` | On element load | `hx-trigger="load"` |
| `revealed` | When scrolled into view | `hx-trigger="revealed"` |

---

## Swap Strategies

| Value | Description |
|-------|-------------|
| `innerHTML` | Replace target's inner HTML (default) |
| `outerHTML` | Replace target element entirely |
| `beforebegin` | Insert before target element |
| `afterbegin` | Insert as first child of target |
| `beforeend` | Insert as last child of target |
| `afterend` | Insert after target element |
| `delete` | Delete target element (response body ignored) |
| `none` | No swap (useful for side effects only) |

Swap modifiers:
- `innerHTML swap:0.5s` — delay swap (for CSS transitions)
- `innerHTML settle:0.5s` — delay settle phase
- `innerHTML scroll:top` — scroll to top after swap
- `innerHTML show:top` — show top of target after swap

---

## HTMX Request Headers (sent by HTMX)

| Header | Description |
|--------|-------------|
| `HX-Request` | Always `"true"` for HTMX requests |
| `HX-Target` | `id` of the target element |
| `HX-Trigger` | `id` of the triggering element |
| `HX-Trigger-Name` | `name` of the triggering element |
| `HX-Current-URL` | Current browser URL |
| `HX-Prompt` | Value from `hx-prompt` dialog |
| `HX-Boosted` | `"true"` if request via `hx-boost` |
| `HX-History-Restore-Request` | `"true"` on history restoration |

---

## HTMX Response Headers (sent by server)

| Header | Description | Example |
|--------|-------------|---------|
| `HX-Location` | Client-side redirect (no page reload) | `HX-Location: /new-path` |
| `HX-Push-Url` | Push URL to browser history | `HX-Push-Url: /items/1` |
| `HX-Redirect` | Full page redirect | `HX-Redirect: /login` |
| `HX-Refresh` | Force full page refresh | `HX-Refresh: true` |
| `HX-Retarget` | Override hx-target | `HX-Retarget: #error-box` |
| `HX-Reswap` | Override hx-swap | `HX-Reswap: outerHTML` |
| `HX-Trigger` | Trigger client-side event | `HX-Trigger: {"showToast": "Saved!"}` |
| `HX-Trigger-After-Swap` | Trigger event after swap | `HX-Trigger-After-Swap: itemAdded` |
| `HX-Trigger-After-Settle` | Trigger event after settle | `HX-Trigger-After-Settle: formReset` |

---

## HX-Request Detection in Go

### stdlib net/http
```go
func isHTMX(r *http.Request) bool {
    return r.Header.Get("HX-Request") == "true"
}
```

### chi
```go
func handler(w http.ResponseWriter, r *http.Request) {
    if r.Header.Get("HX-Request") == "true" {
        // return fragment
        return
    }
    // return full page
}
```

### echo
```go
func handler(c echo.Context) error {
    if c.Request().Header.Get("HX-Request") == "true" {
        return c.HTML(http.StatusOK, fragmentHTML)
    }
    return c.Render(http.StatusOK, "page", data)
}
```

### gin
```go
func handler(c *gin.Context) {
    if c.GetHeader("HX-Request") == "true" {
        c.HTML(http.StatusOK, "fragment.html", gin.H{})
        return
    }
    c.HTML(http.StatusOK, "page.html", gin.H{})
}
```

### htmx-go library helper
```go
import "github.com/angelofallars/htmx-go"

func handler(w http.ResponseWriter, r *http.Request) {
    if htmx.IsHTMX(r) {
        // fragment response
        return
    }
    // full page response
}
```

---

## HTTP Status Codes for HTMX

| Status | HTMX Behavior | When to Use |
|--------|---------------|-------------|
| 200 | Swap response body into target | Success fragment |
| 204 No Content | No swap occurs | Side-effect only (delete, etc.) |
| 422 Unprocessable Entity | **No swap by default in HTMX 2.x** — requires `responseHandling` opt-in (see below) | Form validation failure |
| 3xx | HTMX follows redirect | (use HX-Redirect instead for HTMX-aware redirects) |
| 4xx/5xx | Triggers `htmx:responseError` event | Errors; no automatic swap |

---

## HTMX 2.x: Enabling 422 Swaps

HTMX 2.x blocks swaps for all 4xx/5xx responses by default (`[45]..` rule). To use 422 for form validation errors, add an explicit opt-in to your base layout. Place the config in a `defer` script **after** the HTMX `defer` src tag so both run in order after DOM parsing:

```html
<script src="https://unpkg.com/htmx.org@2" defer></script>
<script defer>
  htmx.config.responseHandling = [
    {code: "204", swap: false},
    {code: "[23]..", swap: true},
    {code: "422", swap: true},         // enable swap for form validation errors
    {code: "[45]..", swap: false, error: true},
    {code: "...", swap: false}
  ];
</script>
```

> **HTMX 1.x**: Use the `htmx:beforeSwap` event instead:
> ```javascript
> document.body.addEventListener('htmx:beforeSwap', (e) => {
>   if (e.detail.xhr.status === 422) {
>     e.detail.shouldSwap = true;
>     e.detail.isError = false;
>   }
> });
> ```

---

## templ Quick Reference

### Component definition
```go
// components/card.templ
package components

templ Card(title string, content string) {
    <div class="card">
        <h2>{ title }</h2>
        <p>{ content }</p>
    </div>
}
```

### Layout component
```go
// layouts/base.templ
package layouts

templ Base(title string) {
    <!DOCTYPE html>
    <html lang="en">
    <head>
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
        { children... }
    </body>
    </html>
}
```

### Partial / fragment (for HTMX)
```go
// components/item_list.templ
package components

templ ItemList(items []Item) {
    <ul id="items">
        for _, item := range items {
            @ItemRow(item)
        }
    </ul>
}

templ ItemRow(item Item) {
    <li id={ fmt.Sprintf("item-%d", item.ID) }>
        { item.Name }
        <button hx-delete={ fmt.Sprintf("/items/%d", item.ID) }
                hx-target={ fmt.Sprintf("#item-%d", item.ID) }
                hx-swap="outerHTML">
            Delete
        </button>
    </li>
}
```

### Render in handler (chi)
```go
// Render component directly
templ.Handler(components.ItemList(items)).ServeHTTP(w, r)

// Or write to response writer
err := components.ItemList(items).Render(r.Context(), w)
```

### Render in echo handler
```go
return components.ItemList(items).Render(c.Request().Context(), c.Response().Writer)
```

### Render in gin handler
```go
// c.Request.Context() is a field (not a method); c.Writer implements http.ResponseWriter
component.Render(c.Request.Context(), c.Writer)
```

### Compilation
```bash
# Install
go install github.com/a-h/templ/cmd/templ@latest

# Generate (run before go build)
templ generate

# Watch mode (with Air)
# .air.toml: cmd = "templ generate && go build ..."
```

---

## Router Patterns (chi / echo / gin / stdlib)

### chi
```go
import "github.com/go-chi/chi/v5"

r := chi.NewRouter()
r.Use(middleware.Logger)
r.Use(middleware.Recoverer)

r.Get("/items", h.ListItems)
r.Post("/items", h.CreateItem)
r.Delete("/items/{id}", func(w http.ResponseWriter, r *http.Request) {
    id := chi.URLParam(r, "id")
    // ...
})

http.ListenAndServe(":8080", r)
```

### echo
```go
import "github.com/labstack/echo/v4"

e := echo.New()
e.Use(middleware.Logger())
e.Use(middleware.Recover())

e.GET("/items", h.ListItems)
e.POST("/items", h.CreateItem)
e.DELETE("/items/:id", h.DeleteItem)

e.Start(":8080")
```

### gin
```go
import "github.com/gin-gonic/gin"

r := gin.Default()

r.GET("/items", h.ListItems)
r.POST("/items", h.CreateItem)
r.DELETE("/items/:id", h.DeleteItem)

r.Run(":8080")
```

### stdlib (Go 1.22+ method patterns)
```go
mux := http.NewServeMux()
mux.HandleFunc("GET /items", h.ListItems)
mux.HandleFunc("POST /items", h.CreateItem)
mux.HandleFunc("DELETE /items/{id}", h.DeleteItem)

http.ListenAndServe(":8080", mux)
```

---

## Common Go Project Layout (HTMX + templ)

```
myapp/
├── main.go
├── go.mod
├── go.sum
├── .air.toml              # live reload config
├── Makefile               # templ generate + build
├── cmd/
│   └── server/
│       └── main.go
├── internal/
│   ├── handler/           # http handlers
│   │   ├── item.go
│   │   └── handler.go
│   ├── store/             # data layer
│   │   └── item.go
│   └── middleware/        # custom middleware
│       └── htmx.go
├── components/            # templ components
│   ├── layout/
│   │   └── base.templ
│   ├── item/
│   │   ├── list.templ
│   │   └── row.templ
│   └── shared/
│       └── loading.templ
└── static/
    ├── css/
    └── js/
```

---

## SSE Pattern (Server-Sent Events)

### Go SSE handler
```go
func (h *Handler) SSEEvents(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "text/event-stream")
    w.Header().Set("Cache-Control", "no-cache")
    w.Header().Set("Connection", "keep-alive")

    flusher, ok := w.(http.Flusher)
    if !ok {
        http.Error(w, "SSE not supported", http.StatusInternalServerError)
        return
    }

    ctx := r.Context()
    ticker := time.NewTicker(2 * time.Second)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            return
        case t := <-ticker.C:
            fmt.Fprintf(w, "event: update\ndata: %s\n\n", t.Format(time.RFC3339))
            flusher.Flush()
        }
    }
}
```

> **Gin note**: With gin, use `c.Stream()` instead of `http.Flusher` — gin wraps the response writer and `http.Flusher` assertions may not work reliably.
>
> ```go
> func (h *Handler) SSEEvents(c *gin.Context) {
>     c.Stream(func(w io.Writer) bool {
>         select {
>         case <-c.Request.Context().Done():
>             return false
>         case t := <-time.After(2 * time.Second):
>             c.SSEvent("update", t.Format(time.RFC3339))
>             return true
>         }
>     })
> }
> ```

### HTMX SSE HTML
```html
<!-- Enable SSE extension -->
<div hx-ext="sse"
     sse-connect="/sse/events"
     sse-swap="update"
     hx-target="#live-feed"
     hx-swap="beforeend">
</div>

<div id="live-feed"></div>
```

---

## CSRF Setup (gorilla/csrf + chi)

```go
import "github.com/gorilla/csrf"

csrfMiddleware := csrf.Protect(
    []byte("32-byte-long-auth-key"),
    csrf.Secure(true),
    csrf.RequestHeader("X-CSRF-Token"),
)

r := chi.NewRouter()
r.Use(csrfMiddleware)
```

HTMX config (add to base layout):

In templ, template parameters are passed as component arguments and interpolated with `{ }` syntax — not `{{ }}`:
```go
// templ component receives csrfToken as a parameter:
templ Base(title string, csrfToken string) {
    // ...
    <meta name="csrf-token" content={ csrfToken }/>
    // ...
}
```

```html
<script>
  document.body.addEventListener('htmx:configRequest', (e) => {
    e.detail.headers['X-CSRF-Token'] =
      document.querySelector('meta[name="csrf-token"]').content;
  });
</script>
```
