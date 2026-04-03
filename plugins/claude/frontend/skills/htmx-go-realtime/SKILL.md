---
name: htmx-go-realtime
description: "This skill should be used when the user asks about real-time features with HTMX and Go — server-sent events (SSE), WebSocket, polling, live updates, push notifications, streaming HTML responses, real-time dashboards, or any pattern where the server pushes data to the browser in an HTMX+Go project."
---

# HTMX + Go Real-Time Patterns

This skill delegates to the `htmx-go` agent, which fetches current HTMX SSE/WebSocket extension documentation at runtime via context7 MCP and WebSearch. The agent provides documentation-backed answers for real-time patterns in HTMX+Go projects.

## Why this skill matters

HTMX has first-class real-time support via its SSE and WebSocket extensions, but both require specific Go server-side implementation patterns that are not obvious:

- **SSE requires `http.Flusher`** — without it, data is buffered and never reaches the client
- **SSE connection management** — each connection is a goroutine; leaks accumulate without proper context cancellation
- **HTMX SSE extension uses named events** — `event: name\ndata: html\n\n` format; HTMX swaps into targets based on event name via `sse-swap="eventName"`
- **WebSocket extension sends form data** — `ws-send` on a form sends its values as a JSON object by default
- **SSE data fields must be single-line** — the SSE protocol assigns each newline-terminated line to a separate field; HTML fragments rendered by templ contain newlines that must be stripped (`strings.ReplaceAll(html, "\n", " ")`) before writing to the `data:` field, or the HTMX extension receives malformed events silently
- **Polling as simple fallback** — `hx-trigger="every 5s"` is simpler than SSE for infrequent updates

Implementing SSE without `http.Flusher` results in responses that arrive all at once after the connection closes, not as a stream.

## When to use this skill

Use for ANY request involving:

- Server-sent events (SSE) with HTMX: `hx-ext="sse"`, `sse-connect`, `sse-swap`
- Go SSE handler: `text/event-stream`, `http.Flusher`, `fmt.Fprintf(w, "data: ...\n\n")`
- WebSocket with HTMX: `hx-ext="ws"`, `ws-connect`, `ws-send`
- Go WebSocket handler: `gorilla/websocket` or `nhooyr.io/websocket`
- HTMX polling: `hx-trigger="every Xs"`
- SSE broadcast to multiple clients (pub/sub pattern in Go)
- Real-time dashboard, live feed, notification system, chat
- Streaming HTML chunks from Go to HTMX

## Common patterns

### Go SSE handler (simple)
```go
func (h *Handler) SSEEvents(w http.ResponseWriter, r *http.Request) {
    // Required headers
    w.Header().Set("Content-Type", "text/event-stream")
    w.Header().Set("Cache-Control", "no-cache")
    w.Header().Set("Connection", "keep-alive")
    w.Header().Set("X-Accel-Buffering", "no") // disable nginx buffering

    flusher, ok := w.(http.Flusher)
    if !ok {
        http.Error(w, "SSE not supported", http.StatusInternalServerError)
        return
    }

    ctx := r.Context()
    ticker := time.NewTicker(3 * time.Second)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            return // client disconnected
        case <-ticker.C:
            // Named event — HTMX listens on sse-swap="tick"
            fmt.Fprintf(w, "event: tick\ndata: <span>%s</span>\n\n",
                time.Now().Format("15:04:05"))
            flusher.Flush()
        }
    }
}
```

### Go SSE handler (gin)

Gin wraps the response writer, so `http.Flusher` type assertions may not work. Use gin's
`c.Stream()` instead — it handles flushing internally:

```go
func (h *Handler) SSEEvents(c *gin.Context) {
    c.Header("Content-Type", "text/event-stream")
    c.Header("Cache-Control", "no-cache")
    c.Header("Connection", "keep-alive")
    c.Header("X-Accel-Buffering", "no")

    ctx := c.Request.Context()
    ticker := time.NewTicker(3 * time.Second)
    defer ticker.Stop()

    // c.Stream blocks; return false to close the connection.
    c.Stream(func(w io.Writer) bool {
        select {
        case <-ctx.Done():
            return false // client disconnected
        case <-ticker.C:
            fmt.Fprintf(w, "event: tick\ndata: <span>%s</span>\n\n",
                time.Now().Format("15:04:05"))
            return true
        }
    })
}
```

> **Note**: `c.Stream()` is gin-only. For net/http, chi, or echo use the `http.Flusher` pattern above.

### HTMX SSE HTML
```html
<!-- The sse-swap value matches the SSE event name -->
<div hx-ext="sse"
     sse-connect="/sse/events"
     sse-swap="tick"
     hx-target="#clock"
     hx-swap="innerHTML">
</div>

<div id="clock">Connecting...</div>
```

### SSE with templ fragments
```go
func (h *Handler) SSEFeed(w http.ResponseWriter, r *http.Request) {
    w.Header().Set("Content-Type", "text/event-stream")
    w.Header().Set("Cache-Control", "no-cache")
    flusher, ok := w.(http.Flusher)
    if !ok {
        http.Error(w, "SSE not supported", http.StatusInternalServerError)
        return
    }

    sub := h.broker.Subscribe()
    defer h.broker.Unsubscribe(sub)

    ctx := r.Context()
    for {
        select {
        case <-ctx.Done():
            return
        case item := <-sub:
            // Render templ component to string, then send as SSE
            var buf bytes.Buffer
            components.FeedItem(item).Render(ctx, &buf)
            // SSE wire format: each "data:" field must be a single line.
            // Rendered HTML contains newlines; a raw newline in a data field
            // starts a NEW data field, producing malformed multi-frame events.
            // Collapse all newlines to spaces before sending.
            html := strings.ReplaceAll(buf.String(), "\n", " ")
            fmt.Fprintf(w, "event: newItem\ndata: %s\n\n", html)
            flusher.Flush()
        }
    }
}
```

```html
<div id="feed"
     hx-ext="sse"
     sse-connect="/sse/feed"
     sse-swap="newItem"
     hx-swap="afterbegin">
</div>
```

### Simple SSE broker (pub/sub)
```go
type Broker struct {
    clients map[chan string]struct{}
    mu      sync.RWMutex
}

func (b *Broker) Subscribe() chan string {
    ch := make(chan string, 10)
    b.mu.Lock()
    b.clients[ch] = struct{}{}
    b.mu.Unlock()
    return ch
}

func (b *Broker) Unsubscribe(ch chan string) {
    b.mu.Lock()
    delete(b.clients, ch)
    b.mu.Unlock()
    close(ch)
}

func (b *Broker) Publish(data string) {
    b.mu.RLock()
    for ch := range b.clients {
        select {
        case ch <- data:
        default: // skip slow clients
        }
    }
    b.mu.RUnlock()
}
```

### HTMX polling (simple alternative)
```html
<!-- Poll every 5 seconds -->
<div hx-get="/status"
     hx-trigger="load, every 5s"
     hx-target="this"
     hx-swap="outerHTML">
  Loading...
</div>
```

### WebSocket with HTMX
```html
<div hx-ext="ws" ws-connect="/ws/chat">
  <div id="messages"></div>
  <form ws-send>
    <input type="text" name="message" autocomplete="off">
    <button type="submit">Send</button>
  </form>
</div>
```

```go
// Using gorilla/websocket
import "github.com/gorilla/websocket"

var upgrader = websocket.Upgrader{
    CheckOrigin: func(r *http.Request) bool { return true },
}

func (h *Handler) WSChat(w http.ResponseWriter, r *http.Request) {
    conn, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        return
    }
    defer conn.Close()

    for {
        _, msg, err := conn.ReadMessage()
        if err != nil {
            break
        }
        // Parse JSON from HTMX: {"message": "hello"}
        // Broadcast HTML fragment back to all clients
        htmlFragment := fmt.Sprintf(`<div class="message">%s</div>`, string(msg))
        conn.WriteMessage(websocket.TextMessage, []byte(htmlFragment))
    }
}
```

## Before delegating

BEFORE dispatching, use AskUserQuestion to clarify the user's intent. Every question to the user MUST go through AskUserQuestion — never ask as plain text. Common things to clarify:
- Whether this is one-directional server→client (SSE) or bidirectional (WebSocket)
- Whether they need broadcasting to multiple clients or just per-connection
- Whether frequency of updates warrants SSE/WS vs simple polling

## How to use

Dispatch the `frontend:htmx-go` agent with the user's question or task. Do not answer real-time pattern questions from general knowledge — the agent fetches current documentation for more accurate answers.

The agent will:
1. Determine whether SSE, WebSocket, or polling best fits the use case
2. Look up current HTMX extension and Go documentation via context7 MCP or WebSearch
3. Provide both the Go server handler and HTMX HTML configuration
4. Flag the `http.Flusher` requirement and connection management patterns
