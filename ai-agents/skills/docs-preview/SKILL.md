---
name: docs-preview
kind: leaf
description: "Build and serve a Docusaurus docs site locally for preview. Use when: docs preview, preview docs, docusaurus, serve docs, docs dev server."
---

# Preview Docs Site

Build and serve a Docusaurus site locally.

## Usage

```bash
/docs-preview          # Dev server with hot-reload (default)
/docs-preview dev      # Dev server explicitly
/docs-preview build    # Production build and serve
```

## Workflow

1. **Find docs directory**: `find . -maxdepth 2 -name "docusaurus.config.*" -not -path "*/node_modules/*"`. Parent of config file is the docs dir. If not found, ask user.

2. **Install deps**: `cd <docs-dir> && [ ! -d "node_modules" ] && npm install`

3. **Kill existing**: `lsof -ti:3000 | xargs kill -9 2>/dev/null`

4. **Start**:
   - Dev (default): `npm start` — run in background
   - Build: `npm run build && npm run serve`

5. **Report URL** (typically http://localhost:3000)

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Port in use | `lsof -ti:3000 \| xargs kill -9` |
| Broken links | Fix links — many configs use `onBrokenLinks: 'throw'` |
| Missing deps | `rm -rf node_modules package-lock.json && npm install` |
