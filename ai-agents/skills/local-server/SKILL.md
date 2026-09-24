---
name: local-server
description: "Start, stop, or check a tiny local HTTP server that serves personal HTML data files at http://localhost:<port>/ and accepts whole-file overwrite saves. Schema-agnostic — the server has no domain knowledge of progress dots, rows, or any specific HTML format. All editing logic lives in the JS embedded in each HTML file (for in-browser interactions) and in the consuming skill's prompt (for batch mutations like sweep/graduate). Trigger phrases: \"preview\", \"open in browser\", \"browse my files\", \"start local server\", \"stop local server\", \"kill local server\", \"local server status\"."
---

# Local HTTP Server for Personal Data Files

A reusable, dependency-free Python server (`server.py`). Three responsibilities:

1. **Serve** the configured directory as static files at `http://localhost:<port>/`.
2. **Receive** whole-file overwrites via `POST /save-file` with body `{"path": "<filename.html>", "content": "<full HTML>"}`.
3. **Hot-reload** via SSE — `GET /sse` streams a `reload` event whenever any `.html` file in the directory changes. `GET /hot-reload.js` serves a tiny listener snippet.

The server **never inspects or rewrites HTML content**. Any in-browser interactivity (dropdowns, click handlers, etc.) is owned by JS embedded in the HTML files themselves. Any batch mutations (sweeping rows, moving entries between files, dedupe) are owned by the consuming skill's prompt.

This keeps the server reusable across any future personal-data skill — they just need to ship HTML with their own JS and follow the same save protocol.

---

## Operations

### Op 1 — Start (Preview)

**Trigger:** "preview", "start local server", "open <dir> in browser".

Idempotent. If a server is already on the requested port, just print URLs.

```bash
PORT=8765
if lsof -nP -iTCP:$PORT -sTCP:LISTEN 2>/dev/null | grep -q LISTEN; then
  echo "server already running on :$PORT"
else
  nohup python3 ~/personal/skills/local-server/server.py --dir <DIR> --port $PORT \
    > /tmp/local-server-$PORT.log 2>&1 &
  disown
fi

for i in 1 2 3 4 5; do
  curl -s -o /dev/null http://localhost:$PORT/ && break
  sleep 0.2
done
```

Then print the URLs from the served directory:

```
➜  http://localhost:$PORT/<file1.html>
➜  http://localhost:$PORT/<file2.html>
…
```

**Defaults:** `--port 8765`. Pass `--dir <path>` to choose the directory.

### Op 2 — Stop

**Trigger:** "stop local server", "kill local server".

```bash
pkill -f "personal/skills/local-server/server.py" \
  && echo "local server stopped" \
  || echo "no local server was running"
```

For a specific port:

```bash
lsof -nP -iTCP:$PORT -sTCP:LISTEN -t | xargs -r kill
```

### Op 3 — Status

**Trigger:** "local server status", "is the local server running".

```bash
lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null | grep "personal/skills/local-server/server.py"
```

Reports any active instances with their ports.

---

## Save Protocol

`POST /save-file` with JSON body:

```json
{
  "path": "page.html",
  "content": "<!DOCTYPE html>\n<html lang=\"en\">…</html>\n"
}
```

- `path` — basename only. Must end with `.html`. Path traversal is rejected.
- `content` — the entire file contents that should replace the file on disk.

Response: `{"status": "ok"|"error", "message": "<details>"}`.

The browser typically gets `content` by cloning `document.documentElement`, normalizing any DOM elements that the HTML uses for interactivity back into their canonical on-disk format, then concatenating `<!DOCTYPE html>\n` + the clone's `outerHTML`.

---

## How Consuming Skills Use This

A skill that stores HTML data references this skill in its own operations:

```bash
python3 ~/personal/skills/local-server/server.py --dir <dir> --port 8765
```

Each consuming skill is responsible for:
- The schema of its HTML files (column conventions, row structure, etc.)
- The JS embedded in each HTML file (interactivity + save logic)
- Any prompt-level operations (sweep, graduate, dedupe, count badges, etc.)

The server is intentionally agnostic to all of the above.

---

## Hot-reload

Add one line to any HTML file that should auto-reload when saved:

```html
<script src="/hot-reload.js"></script>
```

The script opens an SSE connection to `/sse`. The server fires a `reload` event whenever any `.html` file in the served directory changes — either from an external editor or after a successful `POST /save-file`. Heartbeat every 15 s keeps the connection alive.

## Files

- `server.py` — the implementation. Pure stdlib, ~130 lines.
- `SKILL.md` — this file.
