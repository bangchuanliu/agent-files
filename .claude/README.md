# Claude Code adapter

Wires shared `ai-agents/` content and Claude-native config into `~/.claude/`.

```bash
.claude/install.sh
```

`install.sh` creates or updates:

| `~/.claude/...` | Source |
|---|---|
| `skills/<name>` | per-skill symlink into `ai-agents/skills/<name>` |
| `agents` | optional symlink to `ai-agents/agents` when present |
| `docs/core` | symlink to `ai-agents/docs` |
| `CLAUDE.md` | symlink to `ai-agents/.generated/AGENTS.md` |
| `settings.json`, `statusline-command.sh` | symlinks to `.claude/*` |

The skills directory is a real merge directory so other repos can add their own symlinks.
Docs are namespaced under `docs/core` so a company layer can add `docs/<layer>` alongside.

## Claude-only files here

- `settings.json` - permissions, hooks, statusLine, enabled plugins.
- `statusline-command.sh` - status line script.

These are not shared with other agents because each agent has its own config schema.
