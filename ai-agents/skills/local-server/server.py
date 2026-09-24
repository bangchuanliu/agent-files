#!/usr/bin/env python3
"""Generic local HTTP server for personal data files.

Pure dumb server — has no domain knowledge of progress dots, rows, or any
particular HTML schema. Three responsibilities:

  1. GET  /<file.html>  — serve a static file from the configured directory.
  2. POST /save-file    — overwrite a file in the configured directory with
                          the body's content. Refuses path traversal.
  3. GET  /sse          — Server-Sent Events stream; fires "reload" whenever
                          any .html file in the directory changes on disk.
     GET  /hot-reload.js — tiny JS snippet; add to HTML to enable hot-reload.

All HTML mutation logic lives in the consuming skill's prompt and in the JS
embedded in the HTML files themselves. The server is intentionally
schema-agnostic so new consuming skills don't need to fork it.

Hot-reload usage: add to each HTML file that should auto-reload:
    <script src="/hot-reload.js"></script>

Run:
    python3 server.py                              # serves the default dir on :8765
    python3 server.py --dir ~/personal/notes       # serve a different dir
    python3 server.py --port 9000                  # different port

Stop with Ctrl-C, or `pkill -f personal/skills/local-server/server.py`.
"""

import argparse
import json
import queue
import threading
import time
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path


# ---------------------------------------------------------------------------
# SSE client registry
# ---------------------------------------------------------------------------

_sse_clients: list[queue.Queue] = []
_sse_lock = threading.Lock()

_HOT_RELOAD_JS = b"""\
(function () {
  var es = new EventSource('/sse');
  es.onmessage = function () { location.reload(); };
  es.onerror = function () { es.close(); setTimeout(function () { location.reload(); }, 1000); };
})();
"""


def _notify_reload():
    with _sse_lock:
        for q in _sse_clients:
            try:
                q.put_nowait("reload")
            except queue.Full:
                pass


def _watch_files(serve_dir: Path, interval: float = 0.5):
    """Poll serve_dir/*.html for mtime changes; notify SSE clients on change."""
    mtimes: dict[Path, float] = {}
    while True:
        try:
            current = {p: p.stat().st_mtime for p in serve_dir.glob("*.html")}
            if mtimes and current != mtimes:
                _notify_reload()
            mtimes = current
        except Exception:
            pass
        time.sleep(interval)


# ---------------------------------------------------------------------------
# File save helper
# ---------------------------------------------------------------------------

def save_file(serve_dir: Path, file_path: str, content: str):
    """Overwrite serve_dir/file_path with content. Refuses path traversal."""
    if not file_path:
        return "error", "missing path"
    if not file_path.endswith(".html"):
        return "error", f"only .html files allowed: {file_path!r}"
    if "/" in file_path or "\\" in file_path or ".." in file_path:
        return "error", f"invalid path: {file_path!r}"
    target = serve_dir / file_path
    target.write_text(content)
    return "ok", f"saved {file_path}"


# ---------------------------------------------------------------------------
# Request handler
# ---------------------------------------------------------------------------

def make_handler(serve_dir: Path):
    class Handler(SimpleHTTPRequestHandler):
        def end_headers(self):
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            super().end_headers()

        def do_OPTIONS(self):
            self.send_response(204)
            self.end_headers()

        def do_GET(self):
            if self.path == "/sse":
                self._handle_sse()
                return
            if self.path == "/hot-reload.js":
                self.send_response(200)
                self.send_header("Content-Type", "application/javascript")
                self.send_header("Cache-Control", "no-cache")
                self.end_headers()
                self.wfile.write(_HOT_RELOAD_JS)
                return
            super().do_GET()

        def _handle_sse(self):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.end_headers()

            q: queue.Queue = queue.Queue(maxsize=10)
            with _sse_lock:
                _sse_clients.append(q)
            try:
                while True:
                    try:
                        q.get(timeout=15)
                        self.wfile.write(b"data: reload\n\n")
                    except queue.Empty:
                        self.wfile.write(b": heartbeat\n\n")
                    self.wfile.flush()
            except Exception:
                pass
            finally:
                with _sse_lock:
                    try:
                        _sse_clients.remove(q)
                    except ValueError:
                        pass

        def do_POST(self):
            if self.path != "/save-file":
                self.send_error(404, "POST only at /save-file")
                return
            length = int(self.headers.get("Content-Length", 0))
            try:
                body = json.loads(self.rfile.read(length))
                status, message = save_file(
                    serve_dir, body.get("path"), body.get("content", "")
                )
                if status == "ok":
                    _notify_reload()
            except Exception as e:
                status, message = "error", f"{type(e).__name__}: {e}"
            code = 200 if status == "ok" else 400
            self.send_response(code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": status, "message": message}).encode())

        def translate_path(self, path):
            return str(serve_dir / path.lstrip("/").split("?")[0])

        def log_message(self, fmt, *args):
            # Suppress noisy SSE heartbeat logs
            if args and "/sse" in str(args[0]):
                return
            super().log_message(fmt, *args)

    return Handler


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument(
        "--dir",
        type=lambda s: Path(s).expanduser(),
        default=Path.home() / "personal/dict",
        help="Directory to serve (default: ~/personal/dict)",
    )
    p.add_argument("--port", type=int, default=8765)
    args = p.parse_args()

    if not args.dir.exists():
        print(f"error: {args.dir} does not exist")
        raise SystemExit(1)

    watcher = threading.Thread(target=_watch_files, args=(args.dir,), daemon=True)
    watcher.start()

    print(f"Serving {args.dir} on http://localhost:{args.port}/")
    for html in sorted(args.dir.glob("*.html")):
        print(f"  ➜  http://localhost:{args.port}/{html.name}")
    print("Stop with Ctrl-C.")

    server = ThreadingHTTPServer(("127.0.0.1", args.port), make_handler(args.dir))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nshutting down")
