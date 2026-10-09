# Agent configuration sync (maintainer notes)

This repository contains only shared configuration. The optional private overlay is machine-local
and lives outside the repository.

## Sources and outputs

| Path | Kind | Contents |
|---|---|---|
| `ai-agents/AGENTS.core.md` | tracked source | Shared company-agnostic rules |
| `~/.agent/AGENTS.md.local` | optional private source | Company or machine-specific rules |
| `~/.agent/skills.local/<name>/SKILL.md` | optional private source | Company or machine-specific skills |
| `~/.agent/agents.local/<name>.md` | optional private source | Company or machine-specific agents (Claude, Copilot) |
| `~/.agent/docs/` | optional private docs | Reference docs read by path from the local rules; not installed |
| `~/.agent/docs/skill-context/<skill>/context.md` | optional private docs | Company notes a shared skill reads before its generic steps |
| `~/.agent/generated/AGENTS.md` | generated local file | Core rules plus optional local overlay |

Set `AGENT_FILES_LOCAL_DIR` to replace `~/.agent/`, for example in tests or on a machine that
uses a different local configuration directory.

## Rule sync

`ai-agents/sync-rules.sh` writes the generated rules file. It always starts with
`AGENTS.core.md`. If `AGENTS.md.local` exists and is non-empty, it appends it under a
`## Local Context` heading. Without an overlay, the result is byte-identical to the core source.

Each adapter runs the sync script during `./install.sh`:

- Claude links `~/.claude/CLAUDE.md` to the generated file.
- Pi links `~/.pi/agent/AGENTS.md` to the generated file.
- Copilot copies the generated file to `~/.copilot/copilot-instructions.md`, because Copilot
  rewrites that file and would destroy a symlink.

## Skills

The adapters merge skills from the tracked `ai-agents/skills/` directory and optional
`~/.agent/skills.local/` into each agent's skill directory. Experimental skills are never
installed. Shared and private skill names must not collide; the installer exits with an error if
they do.

## Agents

Claude and Copilot merge per-file agent links from the tracked `ai-agents/agents/` directory (if
present) and optional `~/.agent/agents.local/` into `~/.claude/agents/` and `~/.copilot/agents/`
(Copilot as `<name>.agent.md`). Pi has no agents. Name collisions fail the install, and links to
removed agents are pruned.

Keep private skills and company instructions out of this repository. Never put secret values in
agent instructions or skills; use approved secret-management tooling.
