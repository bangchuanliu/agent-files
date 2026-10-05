# Global agent configuration (maintainer notes)

This is documentation for the human maintainer, not instructions for an agent. It explains how
this repository's company-agnostic guide reaches each agent.

## Layout

| Path | Kind | Contents |
|---|---|---|
| `ai-agents/AGENTS.core.md` | git-tracked source | Global, company-agnostic guide |
| `.context/context.md` | ignored, checkout-local reference | Optional company, client, or project notes; never globally installed |
| `~/.claude/CLAUDE.md` | symlink | Points to `AGENTS.core.md` |
| `~/.copilot/copilot-instructions.md` | tool-owned regular file | Copied from `AGENTS.core.md` |
| `~/.pi/agent/AGENTS.md` | symlink | Points to `AGENTS.core.md` |

## Installation

Run the root installer after changing global rules:

```sh
./install.sh
```

Claude and Pi read live symlinks to the core guide. Copilot receives a regular copy because its
toolchain rewrites its instructions file in place, which would destroy a symlink. Re-run the
installer after editing `AGENTS.core.md` to refresh Copilot.

## Local context

For a new company or working context, create `.context/context.md` in that checkout. It is
excluded by `.gitignore`; only `.context/README.md` is tracked.

The file is intentionally not merged into global agent memory. Refer to it while working in this
checkout, and keep codebase-specific instructions in the relevant codebase's own agent
instruction file.

## Authoring conventions

- Keep `AGENTS.core.md` limited to rules that apply in almost every session.
- Do not add company-specific or client-specific instructions to global agent configuration.
- Put situational or lengthy reusable material in `ai-agents/docs/` or in the relevant skill.
