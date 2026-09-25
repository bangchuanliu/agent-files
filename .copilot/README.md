# Copilot CLI adapter

Wires shared `ai-agents/` content into GitHub Copilot CLI's local discovery dirs.

```bash
.copilot/install.sh
```

`install.sh` creates or updates:

| `~/.copilot/...` | Source or content |
|---|---|
| `skills/<name>` | per-skill symlink into `ai-agents/skills/<name>` |
| `agents/<name>.agent.md` | optional symlink into `ai-agents/agents/<name>.md` when present |
| `copilot-instructions.md` | copied rendered rules from `ai-agents/.generated/AGENTS.md` |

`copilot-instructions.md` is intentionally a regular file, not a symlink, because Copilot
may rewrite it in place. Re-run `ai-agents/render-rules.sh` or this installer after editing
rules.

The installer also adds a managed `coya` alias block to `~/.zshrc` and `~/.bashrc`; reruns replace
the block instead of appending.

## Notes

- Skill discovery comes from the local `~/.copilot/skills` dir, not a plugin.
- The skills directory is a real merge directory, so other repos can add their own symlinks.
- Config such as `~/.copilot/config.json`, hooks, and MCP setup is Copilot-native and is not
  shared with Claude.
