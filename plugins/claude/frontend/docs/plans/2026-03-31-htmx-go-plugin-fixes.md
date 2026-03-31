# HTMX+Go Plugin Fixes Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fix three correctness issues found during validation of the new HTMX+Go features in the frontend plugin: a critical HTMX 2.x 422 swap behavior bug, a missing SSE extension `<script>` tag in layout scaffolds, and an undocumented SSE newline-stripping requirement.

**Architecture:** All changes are documentation/content fixes to plugin markdown files — no Go code or compiled assets are involved. Each task targets a specific file or pair of files and is independently verifiable by reading the result.

**Tech Stack:** Markdown, HTMX 2.x, a-h/templ, Go, SSE protocol

---

## Files to Modify

| File | Issue | Change |
|------|-------|--------|
| `plugins/claude/frontend/references/htmx-go-quick-reference.md` | 422 row is wrong for HTMX 2.x; layout scaffold missing SSE script tag | Fix 422 table row + add pitfall note; add `htmx-ext-sse@2` `<script>` |
| `plugins/claude/frontend/agents/htmx-go.md` | 422 claim in Defaults section; Form Validation Pattern missing opt-in config; Pitfalls table misleads | Update defaults, add responseHandling block, fix pitfall row |
| `plugins/claude/frontend/skills/htmx-go-forms/SKILL.md` | "Why this skill matters" says 422 swaps by default; code patterns lack responseHandling | Update prose + add config block to HTML form example |
| `plugins/claude/frontend/skills/go-templ/SKILL.md` | Layout scaffold missing `htmx-ext-sse@2` `<script>` tag | Add SSE script tag to Base layout example |
| `plugins/claude/frontend/skills/htmx-go-realtime/SKILL.md` | `strings.ReplaceAll` newline strip has no explanation; risks silent deletion | Add inline comment explaining SSE wire format requirement |

> **Note on test copy:** The plugin is deployed to `demo/htmx-go-dashboard/.claude/` for testing. After fixing the source files above, apply the identical changes to the corresponding files under `.claude/` in the same commit, or re-sync from source.

---

## Task 1: Fix 422 Status Code Row in Quick Reference

**Files:**
- Modify: `plugins/claude/frontend/references/htmx-go-quick-reference.md` (lines 163–173)

### Background

The HTTP Status Codes table currently states:

```
| 422 Unprocessable Entity | Swap response body (shows errors) | Form validation failure |
```

In HTMX 2.x the default `responseHandling` config is:

```javascript
responseHandling: [
  {code:"204", swap: false},
  {code:"[23]..", swap: true},
  {code:"[45]..", swap: false, error:true},
  {code:"...", swap: false}
]
```

The `[45]..` pattern matches 422, so **HTMX 2.x does NOT swap 422 responses by default**. The row is actively misleading.

---

- [ ] **Step 1: Replace the 422 table row**

In `plugins/claude/frontend/references/htmx-go-quick-reference.md`, find the HTTP Status Codes table and replace:

```markdown
| 422 Unprocessable Entity | Swap response body (shows errors) | Form validation failure |
```

with:

```markdown
| 422 Unprocessable Entity | **No swap by default in HTMX 2.x** — requires `responseHandling` opt-in (see Pitfalls below) | Form validation failure |
```

- [ ] **Step 2: Add a Pitfalls section after the status codes table**

Immediately after the closing `---` of the HTTP Status Codes section (line 173), insert a new section:

```markdown
## HTMX 2.x: Enabling 422 Swaps

HTMX 2.x blocks swaps for all 4xx/5xx responses by default (`[45]..` rule). To use 422 for form validation errors, add an explicit opt-in to your base layout **before** HTMX loads:

```html
<script>
  htmx.config.responseHandling = [
    {code: "204", swap: false},
    {code: "[23]..", swap: true},
    {code: "422", swap: true},         // enable swap for form validation errors
    {code: "[45]..", swap: false, error: true},
    {code: "...", swap: false}
  ];
</script>
<script src="https://unpkg.com/htmx.org@2" defer></script>
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
```

- [ ] **Step 3: Verify the section reads correctly**

Read `references/htmx-go-quick-reference.md` lines 163–210 and confirm:
- The 422 row no longer says "Swap response body"
- The new HTMX 2.x section appears between the status codes table and the templ Quick Reference section
- The `<script>` block shows config defined **before** the HTMX script tag

---

## Task 2: Fix 422 Guidance in the htmx-go Agent

**Files:**
- Modify: `plugins/claude/frontend/agents/htmx-go.md`
  - Line 49 (Go + templ Defaults)
  - Lines 212–232 (Form Validation Pattern)
  - Lines 248–259 (Common Pitfalls table)

---

- [ ] **Step 1: Fix the Defaults section (line 49)**

Find:

```markdown
- **HTTP status codes**: use 422 Unprocessable Entity for validation errors (HTMX will swap the response body); use 200 for success fragments
```

Replace with:

```markdown
- **HTTP status codes**: use 422 Unprocessable Entity for validation errors — **HTMX 2.x requires explicit `responseHandling` opt-in for 422 swaps** (add config to base layout); use 200 for success fragments
```

- [ ] **Step 2: Update the Form Validation Pattern section**

Find the Form Validation Pattern section header and its Go handler example:

```markdown
### Form Validation Pattern

Return 422 with the form fragment containing inline errors:

```go
func (h *Handler) CreatePost(w http.ResponseWriter, r *http.Request) {
```

Prepend a required HTML config block **before** the Go handler example:

```markdown
### Form Validation Pattern

Return 422 with the form fragment containing inline errors. **First**, add the HTMX 2.x `responseHandling` opt-in to your base layout:

```html
<!-- In your base layout <head>, before the HTMX script tag -->
<script>
  htmx.config.responseHandling = [
    {code: "204", swap: false},
    {code: "[23]..", swap: true},
    {code: "422", swap: true},         // enable swap for form validation errors
    {code: "[45]..", swap: false, error: true},
    {code: "...", swap: false}
  ];
</script>
<script src="https://unpkg.com/htmx.org@2" defer></script>
```

Then the Go handler returns 422 with the re-rendered form:

```go
func (h *Handler) CreatePost(w http.ResponseWriter, r *http.Request) {
```

- [ ] **Step 3: Fix the "200 on validation error" pitfall row**

Find the Common Pitfalls table and the row:

```markdown
| 200 on validation error | HTMX swaps success content | Return 422 for validation failures |
```

Replace with:

```markdown
| 200 on validation error | HTMX swaps success content on 200 | Return 422 for validation failures — and add `responseHandling` opt-in for HTMX 2.x (see Form Validation Pattern) |
```

- [ ] **Step 4: Verify agent file consistency**

Read `agents/htmx-go.md` lines 45–60 and 210–260 and confirm all three locations are updated and internally consistent (no mention of "HTMX will swap" without the 2.x caveat).

---

## Task 3: Fix 422 Guidance in htmx-go-forms Skill

**Files:**
- Modify: `plugins/claude/frontend/skills/htmx-go-forms/SKILL.md`
  - Lines 14–15 (Why this skill matters)
  - Lines 38–48 (Basic form HTML example)

---

- [ ] **Step 1: Fix the "Why this skill matters" prose**

Find:

```markdown
- **Validation errors use 422 status** (not 200 with error JSON) — HTMX swaps the response body only on 200 by default, but re-render-on-error via 422 requires explicit knowledge
```

Replace with:

```markdown
- **Validation errors use 422 status** (not 200 with error JSON) — in HTMX 2.x, 422 does **not** swap by default (`[45]..` blocks all 4xx/5xx); re-rendering the form on error requires adding `responseHandling` config to the base layout explicitly
```

- [ ] **Step 2: Prepend responseHandling config to the Basic form example**

Find the `### Basic form with validation` section. It currently starts directly with the HTML `<form>` block. Insert the base layout config snippet **before** the form HTML:

```markdown
### Basic form with validation

**Prerequisite** — add this to your base layout `<head>` before HTMX loads (HTMX 2.x only):

```html
<script>
  htmx.config.responseHandling = [
    {code: "204", swap: false},
    {code: "[23]..", swap: true},
    {code: "422", swap: true},         // required for form validation error swaps
    {code: "[45]..", swap: false, error: true},
    {code: "...", swap: false}
  ];
</script>
<script src="https://unpkg.com/htmx.org@2" defer></script>
```

```html
<!-- Form with hx-post -->
<form hx-post="/items"
```

- [ ] **Step 3: Verify the skill reads correctly**

Read `skills/htmx-go-forms/SKILL.md` lines 1–50 and confirm:
- "Why this skill matters" no longer claims 422 swaps by default
- The Basic form example leads with the `responseHandling` prerequisite
- The Go handler code (lines 51–74) is unchanged

---

## Task 4: Add SSE Script Tag to Layout Scaffold Examples

**Files:**
- Modify: `plugins/claude/frontend/references/htmx-go-quick-reference.md` (templ layout example, ~line 200)
- Modify: `plugins/claude/frontend/skills/go-templ/SKILL.md` (Base layout example, ~line 54)

SSE requires the `htmx-ext-sse` extension to be loaded separately. Layout scaffolds that show only the HTMX core script will produce silent failures when developers try to use `hx-ext="sse"`.

---

- [ ] **Step 1: Fix the layout example in htmx-go-quick-reference.md**

Find the `### Layout component` example in the templ Quick Reference section:

```go
templ Base(title string) {
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>{ title }</title>
        <script src="https://unpkg.com/htmx.org@2"></script>
    </head>
```

Replace with:

```go
templ Base(title string) {
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <title>{ title }</title>
        <script src="https://unpkg.com/htmx.org@2" defer></script>
        // Include if using SSE (hx-ext="sse") or WebSocket (hx-ext="ws") extensions
        <script src="https://unpkg.com/htmx-ext-sse@2" defer></script>
    </head>
```

> Note: The original lacked `defer` on the HTMX script. Adding it here for correctness — `defer` ensures the script loads after HTML parsing without blocking render.

- [ ] **Step 2: Fix the layout example in go-templ/SKILL.md**

Find the `### Layout with children slot` example:

```go
templ Base(title string) {
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{ title }</title>
        <script src="https://unpkg.com/htmx.org@2" defer></script>
    </head>
```

Replace with:

```go
templ Base(title string) {
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>{ title }</title>
        <script src="https://unpkg.com/htmx.org@2" defer></script>
        // Include if using SSE (hx-ext="sse") or WebSocket (hx-ext="ws") extensions
        <script src="https://unpkg.com/htmx-ext-sse@2" defer></script>
    </head>
```

- [ ] **Step 3: Verify both layout examples**

Read lines 190–210 of `references/htmx-go-quick-reference.md` and lines 48–65 of `skills/go-templ/SKILL.md`. Confirm both now show:
- HTMX core script with `defer`
- SSE extension script on the next line with a comment explaining when to include it

---

## Task 5: Document the SSE Newline-Stripping Requirement

**Files:**
- Modify: `plugins/claude/frontend/skills/htmx-go-realtime/SKILL.md` (SSE with templ fragments pattern, ~lines 83–107)

The `strings.ReplaceAll(buf.String(), "\n", "")` step is present but unexplained. The SSE protocol requires each `data:` field to be a single line — a newline within a `data:` value starts a new field, causing the SSE event to be malformed. Without explanation, this looks like optional cleanup and is likely to be deleted.

---

- [ ] **Step 1: Add an explanatory comment to the SSE templ fragment handler**

Find the `### SSE with templ fragments` Go handler:

```go
        var buf bytes.Buffer
        components.FeedItem(item).Render(ctx, &buf)
        fmt.Fprintf(w, "event: newItem\ndata: %s\n\n",
            strings.ReplaceAll(buf.String(), "\n", ""))
        flusher.Flush()
```

Replace with:

```go
        var buf bytes.Buffer
        components.FeedItem(item).Render(ctx, &buf)
        // SSE wire format: each "data:" field must be a single line.
        // Rendered HTML contains newlines; a raw newline in a data field
        // starts a NEW data field, producing malformed multi-frame events.
        // Collapse all newlines to spaces before sending.
        html := strings.ReplaceAll(buf.String(), "\n", " ")
        fmt.Fprintf(w, "event: newItem\ndata: %s\n\n", html)
        flusher.Flush()
```

- [ ] **Step 2: Add a bullet to "Why this skill matters"**

Find the `## Why this skill matters` section and append a new bullet after the existing four:

```markdown
- **SSE data fields must be single-line** — the SSE protocol assigns each newline-terminated line to a separate field; HTML fragments rendered by templ contain newlines that must be stripped (`strings.ReplaceAll(html, "\n", " ")`) before writing to the `data:` field, or the HTMX extension receives malformed events silently
```

- [ ] **Step 3: Verify the skill reads correctly**

Read `skills/htmx-go-realtime/SKILL.md` lines 10–30 (Why this skill matters) and 83–110 (SSE with templ fragments). Confirm:
- The new bullet appears in the why section
- The Go handler has the four-line comment block
- The `strings.ReplaceAll` call is now on its own line with a named variable

---

## Task 6: Sync Fixes to Test Copy

**Files:**
- Modify: `demo/htmx-go-dashboard/.claude/references/htmx-go-quick-reference.md`
- Modify: `demo/htmx-go-dashboard/.claude/agents/htmx-go.md`
- Modify: `demo/htmx-go-dashboard/.claude/skills/htmx-go-forms/SKILL.md`
- Modify: `demo/htmx-go-dashboard/.claude/skills/go-templ/SKILL.md`
- Modify: `demo/htmx-go-dashboard/.claude/skills/htmx-go-realtime/SKILL.md`

The `.claude/` directory in the demo project is the test deployment of the plugin. It must mirror the fixed source files.

---

- [ ] **Step 1: Apply all Task 1–5 changes to the test copy**

Repeat every edit from Tasks 1–5 verbatim on the corresponding files under `demo/htmx-go-dashboard/.claude/`. The files are structurally identical to the source — same line numbers, same content.

- [ ] **Step 2: Diff source vs test copy to confirm they match**

```bash
diff plugins/claude/frontend/references/htmx-go-quick-reference.md \
     demo/htmx-go-dashboard/.claude/references/htmx-go-quick-reference.md

diff plugins/claude/frontend/agents/htmx-go.md \
     demo/htmx-go-dashboard/.claude/agents/htmx-go.md

diff plugins/claude/frontend/skills/htmx-go-forms/SKILL.md \
     demo/htmx-go-dashboard/.claude/skills/htmx-go-forms/SKILL.md

diff plugins/claude/frontend/skills/go-templ/SKILL.md \
     demo/htmx-go-dashboard/.claude/skills/go-templ/SKILL.md

diff plugins/claude/frontend/skills/htmx-go-realtime/SKILL.md \
     demo/htmx-go-dashboard/.claude/skills/htmx-go-realtime/SKILL.md
```

Expected output: no diff (all files identical).

---

## Task 7: Commit

- [ ] **Step 1: Stage all modified files**

```bash
git add \
  plugins/claude/frontend/references/htmx-go-quick-reference.md \
  plugins/claude/frontend/agents/htmx-go.md \
  plugins/claude/frontend/skills/htmx-go-forms/SKILL.md \
  plugins/claude/frontend/skills/go-templ/SKILL.md \
  plugins/claude/frontend/skills/htmx-go-realtime/SKILL.md \
  demo/htmx-go-dashboard/.claude/references/htmx-go-quick-reference.md \
  demo/htmx-go-dashboard/.claude/agents/htmx-go.md \
  demo/htmx-go-dashboard/.claude/skills/htmx-go-forms/SKILL.md \
  demo/htmx-go-dashboard/.claude/skills/go-templ/SKILL.md \
  demo/htmx-go-dashboard/.claude/skills/htmx-go-realtime/SKILL.md
```

- [ ] **Step 2: Commit**

```bash
git commit -m "fix(htmx-go): correct 422 swap behavior for HTMX 2.x, add SSE script tag, document newline stripping

- Fix critical: 422 status code does not swap in HTMX 2.x by default;
  add responseHandling opt-in config to quick-reference, agent, and
  htmx-go-forms skill
- Fix minor: add htmx-ext-sse@2 script tag to layout scaffold examples
  in quick-reference and go-templ skill
- Fix minor: document SSE wire format newline requirement in
  htmx-go-realtime skill with inline comment and why-section bullet"
```

- [ ] **Step 3: Verify git status is clean**

```bash
git status
```

Expected: nothing to commit, working tree clean.

---

## Self-Review

**Spec coverage:**

| Finding from validation report | Task that fixes it |
|-------------------------------|-------------------|
| 422 row wrong in quick-reference status table | Task 1, Step 1 |
| No HTMX 2.x opt-in config shown anywhere | Task 1, Step 2; Task 2, Step 2; Task 3, Step 2 |
| Agent defaults say "HTMX will swap" on 422 | Task 2, Step 1 |
| Agent pitfalls table misleads on 422 | Task 2, Step 3 |
| htmx-go-forms "Why" section says swap is automatic | Task 3, Step 1 |
| SSE extension script tag missing from layout examples | Task 4, Steps 1–2 |
| SSE newline stripping unexplained | Task 5, Steps 1–2 |
| Test copy must match source | Task 6 |

**Placeholder scan:** No TBDs, TODOs, or "similar to Task N" references. All edits show the exact old string and the exact replacement string.

**Type consistency:** No shared types or function signatures — all changes are prose and code snippets. The `responseHandling` config block is identical across all three locations it appears.
