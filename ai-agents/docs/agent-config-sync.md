# Agent configuration sync (maintainer notes)

This repository contains only shared configuration. The optional private overlay is machine-local
and lives outside the repository.

## Sources and outputs

| Path | Kind | Contents |
|---|---|---|
| `ai-agents/rules/AGENTS.core.md` | tracked source | Shared company-agnostic global rules and topic rule index |
| `ai-agents/rules/<topic>.md` | tracked source | Topic rules read on demand via the index |
| `~/.agents-local/AGENTS.md` | optional private source | Company or machine-specific rules |
| `~/.agents-local/skills/<name>/SKILL.md` | optional private source | Company or machine-specific skills |
| `~/.agents-local/agents/<name>.md` | optional private source | Company or machine-specific agents (Claude, Copilot) |
| `~/.agents-local/docs/` | optional private docs | Reference docs read by path from the local rules; not installed |
| `~/.agents-local/docs/skill-context/<skill>/context.md` | optional private docs | Company notes a shared skill reads before its generic steps |
| `~/.agents-local/generated/AGENTS.md` | generated local file | Core rules plus optional local overlay |

Set `AGENT_FILES_LOCAL_DIR` to replace `~/.agents-local/`, for example in tests or on a machine that
uses a different local configuration directory.

## Rule sync

`ai-agents/sync-rules.sh` writes the generated rules file. It always starts with
`AGENTS.core.md`, replacing `{{RULES_DIR}}` with the absolute `ai-agents/rules` path. If the overlay `AGENTS.md` exists and is non-empty, it appends it under a
`## Local Context` heading. Without an overlay, the result is the rendered core source alone.

Each adapter runs the sync script during `./install.sh`:

- Claude links `~/.claude/CLAUDE.md` to the generated file.
- Pi links `~/.pi/agent/AGENTS.md` to the generated file.
- Copilot copies the generated file to `~/.copilot/copilot-instructions.md`, because Copilot
  rewrites that file and would destroy a symlink.

## Skills

The adapters merge skills from the tracked `ai-agents/skills/` directory and optional
`~/.agents-local/skills/` into each agent's skill directory. Experimental skills are never
installed. Shared and private skill names must not collide; the installer exits with an error if
they do.

## Agents

Claude and Copilot merge per-file agent links from the tracked `ai-agents/agents/` directory (if
present) and optional `~/.agents-local/agents/` into `~/.claude/agents/` and `~/.copilot/agents/`
(Copilot as `<name>.agent.md`). Pi has no agents. Name collisions fail the install, and links to
removed agents are pruned.

Keep private skills and company instructions out of this repository. Never put secret values in
agent instructions or skills; use approved secret-management tooling.
