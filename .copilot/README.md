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
| `instructions/<topic>.md` | per-file symlinks to `ai-agents/rules/*.md` except `AGENTS.md` (`thinking.md`, `building.md`, `communicating.md`) |
| `instructions/autopilot.instructions.md` | symlink to `.copilot/autopilot.md` (autopilot-mode rules, e.g. a customer-facing `task_complete` summary); auto-loaded every session |
| `copilot-instructions.md` | copy of `~/.agents-local/generated/AGENTS.md` (rendered by `lib/sync-rules.sh`), with its rule index pointing at `~/.copilot/instructions/<topic>.md` |

`copilot-instructions.md` is intentionally a regular file, not a symlink, because Copilot
may rewrite it in place. Re-run this installer after editing rules.

Topic rules omit the `.instructions.md` suffix on purpose: Copilot auto-loads
`~/.copilot/instructions/**/*.instructions.md` into every session, while these load on demand
through the rule index. Other files in `instructions/` (e.g. `captain.instructions.md`) are left alone.

The installer also adds managed `coya` (autopilot + allow-all) and `coy` (allow-all, no autopilot)
alias blocks to `~/.zshrc` and `~/.bashrc`; reruns replace the blocks instead of appending.

## Notes

- Skill discovery comes from the local `~/.copilot/skills` dir, not a plugin.
- The skills directory is a real merge directory, so other repos can add their own symlinks.
- Config such as `~/.copilot/config.json`, hooks, and MCP setup is Copilot-native and is not
  shared with Claude.
