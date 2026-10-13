# Copilot CLI adapter

Wires shared `ai-agents/` content into GitHub Copilot CLI's local discovery dirs.

```bash
.copilot/install.sh
```

`install.sh` creates or updates:

| `~/.copilot/...` | Source or content |
|---|---|
| `skills/<name>` | per-skill symlink into `ai-agents/skills/<category>/<name>` |
| `agents/<name>.agent.md` | per-file symlinks from `ai-agents/agents/` and `~/.agents-local/agents/` when present |
| `instructions/autopilot.instructions.md` | symlink to `.copilot/autopilot.md` (autopilot-mode rules, e.g. a customer-facing `task_complete` summary); auto-loaded every session |
| `copilot-instructions.md` | symlink to `ai-agents/rules/AGENTS.md`, the same file Claude and Pi use |

Rule edits take effect in the next session without re-running the installer. An existing regular
`copilot-instructions.md` is moved aside as `.bak.<timestamp>` on first run. Re-runs remove
`instructions/<topic>.md` links and rendered copies left by earlier installs. Other files in
`instructions/` (e.g. `captain.instructions.md`) are left alone.

The installer also adds managed `coya` (autopilot + allow-all) and `coy` (allow-all, no autopilot)
alias blocks to `~/.zshrc` and `~/.bashrc`; reruns replace the blocks instead of appending.

## Notes

- Skill discovery comes from the local `~/.copilot/skills` dir, not a plugin.
- The skills directory is a real merge directory, so other repos can add their own symlinks.
- Config such as `~/.copilot/config.json`, hooks, and MCP setup is Copilot-native and is not
  shared with Claude.
