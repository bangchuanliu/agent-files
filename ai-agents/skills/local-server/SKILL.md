---
name: local-server
kind: leaf
description: "Server: start, stop, or check a tiny local HTTP server for personal HTML data files at localhost on a chosen port, with static preview, hot reload, and whole-file save-file overwrites. Use when: preview local HTML, open in browser, browse local files, start local server, stop local server, kill local server, or check local server status."
---

# Local HTTP Server for Personal Data Files

A reusable, dependency-free Python server (`server.py`). Three responsibilities:

1. **Serve** the configured directory as static files at `http://localhost:PORT/`.
2. **Receive** whole-file overwrites via `POST /save-file` with body `{"path": "filename.html", "content": "full HTML"}`.
3. **Hot-reload** via SSE - `GET /sse` streams a `reload` event whenever any `.html` file in the directory changes. `GET /hot-reload.js` serves a tiny listener snippet.

The server **never inspects or rewrites HTML content**. Any in-browser interactivity (dropdowns, click handlers, etc.) is owned by JS embedded in the HTML files themselves. Any batch mutations (sweeping rows, moving entries between files, dedupe) are owned by the consuming skill's prompt.

This keeps the server reusable across any future personal-data skill - they just need to ship HTML with their own JS and follow the same save protocol.

`SKILL_DIR` = the directory containing this file.

---

## Operations

### Op 1 - Start (preview)

**Trigger:** preview local HTML, start local server, open a directory in a browser.

Completion criterion: a server answers `GET /` on the requested port, and the response includes either a directory listing or an HTML file.

```bash
PORT=8765
DIR="$PWD"
if lsof -nP -iTCP:"$PORT" -sTCP:LISTEN 2>/dev/null | grep -q LISTEN; then
  echo "server already running on :$PORT"
else
  python3 "$SKILL_DIR/server.py" --dir "$DIR" --port "$PORT" \
    > "$DIR/.local-server-$PORT.log" 2>&1 &
  echo $! > "$DIR/.local-server-$PORT.pid"
fi

for i in 1 2 3 4 5; do
  curl -fsS -o /dev/null "http://localhost:$PORT/" && break
  sleep 0.2
done
```

If your host agent has a background-process tool, keep the process attached there instead of shell-detaching it. If it does not, tell the user the foreground command to run in a separate terminal.

Then print the URLs from the served directory:

```
http://localhost:$PORT/file1.html
http://localhost:$PORT/file2.html
```

**Defaults:** `--port 8765`. Pass `--dir DIR` to choose the directory (default: current directory).

### Op 2 - Stop

**Trigger:** "stop local server", "kill local server".

Completion criterion: no listening PID remains on the requested port.

```bash
PORT=8765
pids=$(lsof -nP -iTCP:"$PORT" -sTCP:LISTEN -t 2>/dev/null || true)
if [ -z "$pids" ]; then
  echo "no local server was running on :$PORT"
else
  for pid in $pids; do
    kill "$pid"
  done
  echo "local server stopped on :$PORT"
fi
```

For a stuck process, re-check the exact PID with `lsof`, then use `kill -9 PID` only for that PID.

### Op 3 - Status

**Trigger:** "local server status", "is the local server running".

```bash
lsof -nP -iTCP -sTCP:LISTEN 2>/dev/null | grep "server.py"
```

Reports active Python server instances and their ports. If none are listed, report that the server is stopped.

---

## Save Protocol

`POST /save-file` with JSON body:

```json
{
  "path": "page.html",
  "content": "<!DOCTYPE html>\n<html lang=\"en\">…</html>\n"
}
```

- `path` - basename only. Must end with `.html`. Path traversal and symlink escapes are rejected.
- `content` - the entire file contents that should replace the file on disk.

Response: `{"status": "ok"|"error", "message": "details"}`.

The browser typically gets `content` by cloning `document.documentElement`, normalizing any DOM elements that the HTML uses for interactivity back into their canonical on-disk format, then concatenating `<!DOCTYPE html>\n` + the clone's `outerHTML`.

---

## How Consuming Skills Use This

A skill that stores HTML data references this skill in its own operations:

```bash
python3 "$SKILL_DIR/../local-server/server.py" --dir "$DIR" --port 8765
```

Each consuming skill is responsible for:
- The schema of its HTML files (column conventions, row structure, etc.)
- The JS embedded in each HTML file (interactivity + save logic)
- Any prompt-level operations (sweep, graduate, dedupe, count badges, etc.)

The server is intentionally agnostic to all of the above.

---

## Hot reload

Add one line to any HTML file that should auto-reload when saved:

```html
<script src="/hot-reload.js"></script>
```

The script opens an SSE connection to `/sse`. The server fires a `reload` event whenever any `.html` file in the served directory changes - either from an external editor or after a successful `POST /save-file`. Heartbeat every 15 s keeps the connection alive.

## Files

- `server.py` - the implementation. Pure stdlib.
- `test_server.py` - path-safety regression tests.
- `SKILL.md` - this file.
