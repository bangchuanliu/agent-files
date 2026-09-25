---
name: docs-preview
kind: leaf
description: "Docs preview: build and serve a Docusaurus site locally. Use when: docs preview, preview docs, docusaurus, serve docs, or docs dev server."
---

# Preview Docs Site

Build and serve a Docusaurus site locally.

## Modes

```bash
dev     # Dev server with hot reload, default
build   # Production build, then serve
```

## Workflow

1. **Find docs directory.**
   ```bash
   find . -maxdepth 2 -name "docusaurus.config.*" -not -path "*/node_modules/*"
   ```
   Completion criterion: exactly one parent directory is selected. If several configs exist, use the one matching the user's target; if none match, ask for the docs directory.

2. **Install dependencies when missing.**
   ```bash
   cd "$DOCS_DIR" && { [ -d node_modules ] || npm install; }
   ```
   Completion criterion: `node_modules/` exists and the package manager command succeeded.

3. **Free port 3000 safely.**
   ```bash
   pids=$(lsof -nP -iTCP:3000 -sTCP:LISTEN -t 2>/dev/null || true)
   for pid in $pids; do
     kill "$pid"
   done
   ```
   Completion criterion: no listener remains on port 3000. Use `kill -9 PID` only after re-checking the exact stuck PID.

4. **Start**:
   - Dev (default): `npm start` - keep it running in the host's background-process facility, or tell the user the foreground command for a separate terminal.
   - Build: `npm run build && npm run serve`
   Completion criterion: the command is still running and the local URL responds.

5. **Report URL** (typically http://localhost:3000)

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Port in use | Find the listener with `lsof -nP -iTCP:3000 -sTCP:LISTEN`, then terminate that PID. |
| Broken links | Fix links. Many configs use `onBrokenLinks: 'throw'`. |
| Missing deps | `rm -rf node_modules package-lock.json && npm install` |
