---
name: htmx-go-forms
description: "This skill should be used when the user asks about form handling with HTMX and Go — server-side validation, inline field validation, form error display, file uploads, multi-step forms, or any pattern combining HTML forms with HTMX attributes and Go server-side processing."
---

# HTMX + Go Form Handling

This skill delegates to the `htmx-go` agent, which fetches current HTMX and Go documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for form patterns in HTMX+Go projects.

## Why this skill matters

HTMX form handling differs fundamentally from traditional form submissions and from SPA (React/Vue) form patterns:

- **Validation errors use 422 status** (not 200 with error JSON) — in HTMX 2.x, 422 does **not** swap by default (`[45]..` blocks all 4xx/5xx); re-rendering the form on error requires adding `responseHandling` config to the base layout explicitly
- **Fragment responses replace the form** — the error response must include the entire form with validation messages, not just the error data
- **Inline validation uses `hx-trigger="blur"`** — per-field validation fires individually; requires separate handler endpoints per field or a shared validation handler
- **File uploads need `hx-encoding="multipart/form-data"`** — easy to forget when HTMX's default is `application/x-www-form-urlencoded`

These patterns are non-obvious and produce silent failures without specific knowledge.

## When to use this skill

Use for ANY request involving:

- `hx-post`, `hx-put`, `hx-patch` forms with Go handlers
- Server-side form validation and 422 error responses
- Inline/real-time field validation (`hx-trigger="blur"`)
- Form re-rendering with validation errors using templ
- File upload: `hx-encoding="multipart/form-data"` + `r.FormFile()`
- Multi-step / wizard forms with HTMX
- CSRF protection on HTMX form submissions
- Progress indicators during form submission (`hx-indicator`)
- Success redirects after form submission (`HX-Location` / `HX-Redirect`)

## Common patterns

### Basic form with validation

**Prerequisite** — add this to your base layout `<head>`. Place the config in a `defer` script **after** the HTMX `defer` src tag so both run in order after DOM parsing (HTMX 2.x only):

```html
<script src="https://unpkg.com/htmx.org@2" defer></script>
<script defer>
  htmx.config.responseHandling = [
    {code: "204", swap: false},
    {code: "[23]..", swap: true},
    {code: "422", swap: true},         // required for form validation error swaps
    {code: "[45]..", swap: false, error: true},
    {code: "...", swap: false}
  ];
</script>
```

```html
<!-- Form targets itself: on error, the whole form (with inline errors) replaces itself -->
<form id="create-item-form"
      hx-post="/items"
      hx-target="#create-item-form"
      hx-swap="outerHTML">
  <input type="text" name="name" value="">
  <button type="submit">Create</button>
</form>
```

```go
// Go handler — returns 422 + form with errors on failure
func (h *Handler) CreateItem(w http.ResponseWriter, r *http.Request) {
    if err := r.ParseForm(); err != nil {
        http.Error(w, "bad request", http.StatusBadRequest)
        return
    }

    name := r.FormValue("name")
    errs := map[string]string{}
    if strings.TrimSpace(name) == "" {
        errs["name"] = "Name is required"
    }

    if len(errs) > 0 {
        w.WriteHeader(http.StatusUnprocessableEntity)
        templ.Handler(ItemFormErrors(name, errs)).ServeHTTP(w, r)
        return
    }

    item, _ := h.store.Create(r.Context(), name)
    w.Header().Set("HX-Trigger", "itemCreated")
    templ.Handler(ItemRow(item)).ServeHTTP(w, r)
}
```

```go
// templ components — returns the whole form so outerHTML swap replaces it entirely
templ ItemForm(name string, errs map[string]string) {
    <form id="create-item-form"
          hx-post="/items"
          hx-target="#create-item-form"
          hx-swap="outerHTML">
        <input type="text" name="name" value={ name }
               class={ templ.KV("input-error", errs["name"] != "") }>
        if errs["name"] != "" {
            <p class="error">{ errs["name"] }</p>
        }
        <button type="submit">Create</button>
    </form>
}
```

### Inline blur validation
```html
<input type="email"
       name="email"
       hx-post="/validate/email"
       hx-trigger="blur"
       hx-target="#email-error"
       hx-swap="innerHTML">
<span id="email-error"></span>
```

```go
// Validation endpoint — returns empty string or error message
func (h *Handler) ValidateEmail(w http.ResponseWriter, r *http.Request) {
    if err := r.ParseForm(); err != nil {
        http.Error(w, "bad request", http.StatusBadRequest)
        return
    }
    email := r.FormValue("email")

    if !isValidEmail(email) {
        w.WriteHeader(http.StatusUnprocessableEntity)
        fmt.Fprint(w, `<span class="error">Invalid email address</span>`)
        return
    }
    // 200 with empty body clears the error
    w.WriteHeader(http.StatusOK)
}
```

### File upload
```html
<form hx-post="/upload"
      hx-encoding="multipart/form-data"
      hx-indicator="#upload-spinner">
  <input type="file" name="file">
  <button type="submit">Upload</button>
  <span id="upload-spinner" class="htmx-indicator">Uploading...</span>
</form>
```

```go
func (h *Handler) Upload(w http.ResponseWriter, r *http.Request) {
    r.ParseMultipartForm(10 << 20) // 10 MB limit
    file, header, err := r.FormFile("file")
    if err != nil {
        http.Error(w, "no file", http.StatusBadRequest)
        return
    }
    defer file.Close()
    // process file...
}
```

### Multi-step form (state in URL params)
```html
<!-- Step 1 -->
<form hx-post="/wizard/step2" hx-target="#wizard" hx-swap="outerHTML">
  <input type="text" name="step1_data">
  <button type="submit">Next</button>
</form>
```

```go
func (h *Handler) WizardStep2(w http.ResponseWriter, r *http.Request) {
    r.ParseForm()
    step1Data := r.FormValue("step1_data")
    // Pass data to next step via hidden inputs or session
    templ.Handler(WizardStep2Form(step1Data)).ServeHTTP(w, r)
}
```

## Before delegating

BEFORE dispatching, use AskUserQuestion to clarify the user's intent. Every question to the user MUST go through AskUserQuestion — never ask as plain text. Common things to clarify:
- Whether they need basic form submission or inline real-time validation
- Whether they're using templ or html/template for error rendering
- Whether CSRF is already configured in their project

## How to use

Dispatch the `frontend:htmx-go` agent with the user's question or task. Do not answer HTMX form questions from general knowledge — the agent fetches current documentation for more accurate answers.

The agent will:
1. Understand the form's purpose and validation requirements
2. Look up current HTMX and Go documentation via context7 MCP or WebSearch
3. Provide the complete pattern: HTML form + Go handler + templ error component
4. Flag the 422 status code pattern and CSRF requirements
