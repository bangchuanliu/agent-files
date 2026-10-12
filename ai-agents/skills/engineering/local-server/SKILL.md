---
name: local-server
kind: leaf
description: "Use when: start, stop, or check a small local HTTP server that serves a directory of personal HTML files at localhost, with hot reload and whole-file saves from the page - preview local HTML or open it in a browser, stop or kill the local server, check whether it is running. NOT for: building the HTML page itself (html-report), or previewing a Docusaurus docs site."
---

# Local HTTP Server for Personal Data Files

## Objective

Start, stop, or check `server.py`, a dependency-free local server that serves one directory at `http://localhost:PORT/`, hot-reloads open pages when an `.html` file changes, and lets a page save itself back to disk. It exists so any skill or user can preview and edit personal HTML data files in a browser without a build step; the server stays schema-agnostic so every consumer can share it.

Success: start - the server answers `GET /` on the port and the user has the URL of each HTML file; stop - nothing listens on the port; status - the user knows which `server.py` instances are listening and on which ports.

## Context & Tools

`SKILL_DIR` is the directory containing this file. `python3 "$SKILL_DIR/server.py" --help` gives the flags (`--dir`, default the current directory; `--port`, default 8765); its docstring covers the endpoints. It binds `127.0.0.1` and prints each top-level HTML file's URL on startup.

Save protocol, the contract a page's own JS calls:

- `POST /save-file` with `{"path": "page.html", "content": "<full file>"}`. `path` is a bare `.html` filename directly in the served directory; traversal, subdirectories, and symlink escapes are rejected. `content` replaces the whole file, and creates it if absent.
- Reply: `{"status": "ok"|"error", "message": "..."}`, HTTP 200 or 400.
- A page usually builds `content` by cloning `document.documentElement`, normalizing interactive elements back to their on-disk form, and prefixing `<!DOCTYPE html>\n` to the clone's `outerHTML`.
- `<script src="/hot-reload.js"></script>` in a page reloads it whenever any top-level `.html` file in the directory changes, from an editor or a save.

## Guardrails & Constraints

- MUST serve the narrowest directory that holds the files, because the server exposes every file under it and sends `Access-Control-Allow-Origin: *`, so any web page open in the browser can read those files and overwrite `.html` files through `/save-file`. IF the requested directory is the home directory, a repo root, or holds credentials or other secrets, ask before serving it.
- IF the user names no directory or port, proceed on the current directory and port 8765 and state both.
- Before starting, check the port. IF a `server.py` already listens there for the same directory, reuse it. IF anything else holds it, ask when the user named that port; otherwise use the next free port and state it.
- SHOULD run the server through the host's background-process tool so it stays attached; IF the host has none, give the user the foreground command to run in a separate terminal.
- MUST stop only processes confirmed to be `server.py` on the requested port, checked with `lsof -nP -iTCP:<port> -sTCP:LISTEN -t` and `ps -p <pid> -o command=`. IF the listener is any other program, ask before stopping it. Send a normal `kill <pid>` first, and use `kill -9` only on that same re-checked PID if it does not exit.
- For status, identify instances by process command line (`ps -p <pid> -o command=` for each listening PID), because `lsof` shows the command as `Python`, so filtering its output for `server.py` finds nothing.
- IF a page needs domain behaviour (interactivity, row schemas, sweeps, dedupe), MUST put it in the page's own JS or in the consuming skill's instructions, keeping `server.py` free of content inspection or rewriting, because every consumer shares one server.

## Verification

- Start: `curl -fsS -o /dev/null http://localhost:<port>/` succeeds (retry briefly while the server boots).
- Stop: `lsof -nP -iTCP:<port> -sTCP:LISTEN -t` prints nothing.
- IF `server.py` changed, `python3 "$SKILL_DIR/test_server.py"` passes (path-safety regressions for save and serve).
