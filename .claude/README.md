# Claude Code adapter

Wires shared `ai-agents/` content and Claude-native config into `~/.claude/`.

```bash
.claude/install.sh
```

`install.sh` creates or updates:

| `~/.claude/...` | Source |
|---|---|
| `skills/<name>` | per-skill symlink into `ai-agents/skills/<category>/<name>` |
| `agents/<name>.md` | per-file symlinks from `ai-agents/agents/` and `~/.agents-local/agents/` when present |
| `CLAUDE.md` | symlink to `~/.agents-local/generated/AGENTS.md` (rendered by `lib/sync-rules.sh`) |
| `settings.json`, `statusline-command.sh` | symlinks to `.claude/*` |

The skills directory is a real merge directory so other repos can add their own symlinks.

## Claude-only files here

- `settings.json` - permissions, hooks, statusLine, enabled plugins.
- `statusline-command.sh` - status line script.

The installer also adds a managed `cla` alias block to `~/.zshrc` and `~/.bashrc`; reruns replace the
block instead of appending.

These are not shared with other agents because each agent has its own config schema.
