---
name: go-handlers
description: "This skill should be used when the user asks about Go HTTP handlers for HTMX, \"http.HandlerFunc\", \"HX-Request header\", \"fragment vs full page\", HTMX request detection in Go, chi router handlers, echo handlers, gin handlers, Go middleware for HTMX, CORS in Go, HTMX response headers in Go (HX-Location, HX-Redirect, HX-Trigger, HX-Retarget), setting up routes for HTMX, handler structure for HTMX responses, or Go server routing patterns in an HTMX project."
---

# Go Handlers for HTMX

This skill delegates to the `htmx-go` agent, which fetches current Go router and HTMX documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for Go handler patterns in HTMX projects.

## Why this skill matters

HTMX endpoints must handle two distinct modes: direct browser navigation (return full HTML page) and HTMX requests (return HTML fragment). Forgetting to branch on `HX-Request` results in full `<html>` pages being swapped into fragments, breaking layouts. Additionally, HTMX response headers (`HX-Trigger`, `HX-Redirect`, `HX-Retarget`) allow server-driven navigation and event dispatch that are not obvious without documentation. Middleware patterns for CSRF, gzip compression, and authentication also have HTMX-specific considerations.

## When to use this skill

Use for ANY request involving:

- Handler structure: `HX-Request` detection, full-page vs fragment branching
- Router setup: chi, echo, gin, stdlib net/http route registration
- HTMX response headers: `HX-Location`, `HX-Redirect`, `HX-Refresh`, `HX-Trigger`, `HX-Retarget`, `HX-Reswap`, `HX-Push-Url`
- HTTP status codes for HTMX: 200, 204 (no swap), 422 (validation error)
- Middleware: CSRF, gzip, logger, rate limiting — HTMX-specific behavior
- URL parameters: chi `{id}`, echo `:id`, gin `:id` pattern differences
- Serving static files alongside HTMX routes
- Handler organization (struct-based handlers, dependency injection)
- CORS configuration for HTMX requests

## Common patterns

### Full-page vs fragment handler (chi)
```go
type Handler struct {
    store Store
}

func (h *Handler) ListItems(w http.ResponseWriter, r *http.Request) {
    items, err := h.store.List(r.Context())
    if err != nil {
        http.Error(w, "error loading items", http.StatusInternalServerError)
        return
    }

    if r.Header.Get("HX-Request") == "true" {
        templ.Handler(components.ItemList(items)).ServeHTTP(w, r)
        return
    }
    templ.Handler(pages.ItemPage(items)).ServeHTTP(w, r)
}
```

### Setting HTMX response headers
```go
func (h *Handler) CreateItem(w http.ResponseWriter, r *http.Request) {
    // ... create item ...

    // Redirect without page reload
    w.Header().Set("HX-Location", "/items")

    // Or trigger a client-side event
    w.Header().Set("HX-Trigger", `{"itemCreated": {"id": 42}}`)

    w.WriteHeader(http.StatusOK)
}
```

### 422 validation response
```go
func (h *Handler) CreateItem(w http.ResponseWriter, r *http.Request) {
    if err := r.ParseForm(); err != nil {
        http.Error(w, "bad request", http.StatusBadRequest)
        return
    }

    name := r.FormValue("name")
    errs := validateName(name)
    if len(errs) > 0 {
        w.WriteHeader(http.StatusUnprocessableEntity)
        templ.Handler(components.CreateFormErrors(name, errs)).ServeHTTP(w, r)
        return
    }

    // success...
    w.Header().Set("HX-Trigger", "itemCreated")
    templ.Handler(components.ItemRow(newItem)).ServeHTTP(w, r)
}
```

### chi router setup
```go
func NewRouter(h *Handler) http.Handler {
    r := chi.NewRouter()

    r.Use(middleware.Logger)
    r.Use(middleware.Recoverer)
    r.Use(middleware.Compress(5))  // gzip compression

    // Static files
    fileServer := http.FileServer(http.Dir("static"))
    r.Handle("/static/*", http.StripPrefix("/static/", fileServer))

    // Routes
    r.Get("/", h.Home)
    r.Get("/items", h.ListItems)
    r.Post("/items", h.CreateItem)
    r.Get("/items/{id}", h.GetItem)
    r.Delete("/items/{id}", h.DeleteItem)

    return r
}
```

### Full-page vs fragment handler (gin)
```go
func (h *Handler) ListItems(c *gin.Context) {
    items, err := h.store.List(c.Request.Context())
    if err != nil {
        c.Status(http.StatusInternalServerError)
        return
    }

    if c.GetHeader("HX-Request") == "true" {
        // HTMX request — return fragment only
        // c.Request.Context() is a field; c.Writer implements http.ResponseWriter
        components.ItemList(items).Render(c.Request.Context(), c.Writer)
        return
    }
    // Direct navigation — wrap fragment in full-page layout
    pages.ItemPage(items).Render(c.Request.Context(), c.Writer)
}
```

### gin router setup
```go
func NewGinServer(h *Handler) *gin.Engine {
    r := gin.Default()

    r.Static("/static", "static")

    r.GET("/items", h.ListItems)
    r.POST("/items", h.CreateItem)
    r.DELETE("/items/:id", h.DeleteItem)

    return r
}
```

### echo router setup
```go
func NewEchoServer(h *Handler) *echo.Echo {
    e := echo.New()

    e.Use(echomiddleware.Logger())
    e.Use(echomiddleware.Recover())
    e.Use(echomiddleware.GzipWithConfig(echomiddleware.GzipConfig{Level: 5}))

    e.Static("/static", "static")

    e.GET("/items", h.ListItems)
    e.POST("/items", h.CreateItem)
    e.DELETE("/items/:id", h.DeleteItem)

    return e
}
```

### Struct-based handler with dependencies
```go
type Handler struct {
    db     *sql.DB
    logger *slog.Logger
    tmpl   *template.Template
}

func NewHandler(db *sql.DB, logger *slog.Logger) *Handler {
    return &Handler{db: db, logger: logger}
}

func (h *Handler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
    // can implement http.Handler directly
}
```

## Before delegating

BEFORE dispatching, use AskUserQuestion to clarify the user's intent. Every question to the user MUST go through AskUserQuestion — never ask as plain text. Common things to clarify:
- Which Go router they're using (chi, echo, gin, stdlib)
- Whether they need middleware setup or just handler logic
- Whether the question is about routing or about HTMX response headers

## How to use

Dispatch the `frontend:htmx-go` agent with the user's question or task. Do not answer Go handler questions from general knowledge — the agent fetches current documentation for more accurate answers.

The agent will:
1. Detect which router is in use from `go.mod` and project files
2. Look up current router documentation via context7 MCP or WebSearch
3. Answer with working Go handler code including `HX-Request` detection
4. Flag HTMX-specific pitfalls (status codes, response headers, CSRF)
