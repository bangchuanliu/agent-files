# agent-files

Shareable AI-agent configuration for Claude Code, GitHub Copilot CLI, and Pi. The repository
contains only general rules and publishable skills. Company or machine-specific instructions and
skills live in `~/.agent/`, outside the repository.

## Layout

```text
agent-files/
  ai-agents/
    AGENTS.core.md        # tracked shared rules
    sync-rules.sh         # combines core rules with the optional private overlay
    skills/               # tracked, safe-to-share skills
    experimental/         # parked skills, never installed
    docs/                 # maintainer/reference docs
  .claude/                # Claude Code adapter
  .copilot/               # Copilot CLI adapter
  .pi/                    # Pi adapter
  lib/links.sh            # shared installer helpers
  install.sh              # root installer
  tests/run.sh            # all repo checks; run before committing

~/.agent/
  AGENTS.md.local         # optional private company/machine instructions
  skills.local/           # optional private skills; each contains SKILL.md
  generated/AGENTS.md     # generated combined rules, never source-controlled
```

`~/.agent/` is local to the machine and is not part of this repository. Do not put secrets in
its instruction files or skills. Reference the approved secret-management system instead.

## Install

```bash
./install.sh
```

Requires Python 3.9+ and Bash on macOS or Linux. Obtain and authenticate the supported
agent clients through your organization's approved channels first. The installer does not
download clients, packages, plugins, hooks, or MCP servers, and it leaves client settings
and shell aliases unchanged.

The installer runs the Claude, Copilot, and Pi adapters. It renders rules to
`~/.agent/generated/AGENTS.md` (or `$AGENT_FILES_LOCAL_DIR/generated/AGENTS.md`) and installs
skills into each agent's normal skill directory.

Rules render as follows:

1. `ai-agents/AGENTS.core.md` is always included.
2. `~/.agent/AGENTS.md.local` is appended under `## Local Context` when it exists and is
   non-empty.

Without a local overlay, the generated file is byte-for-byte identical to `AGENTS.core.md`.
Claude and Pi link to the generated file; Copilot receives a regular copy because it rewrites
its instructions file in place.

| Agent | Deployed rules path |
|---|---|
| Claude Code | `~/.claude/CLAUDE.md` |
| Copilot CLI | `~/.copilot/copilot-instructions.md` |
| Pi | `~/.pi/agent/AGENTS.md` (or `$PI_CODING_AGENT_DIR/AGENTS.md`) |

## Private company setup

On a company-specific machine, create the optional local overlay:

```bash
mkdir -p ~/.agent/skills.local
$EDITOR ~/.agent/AGENTS.md.local
./install.sh
```

Private skills are installed from `~/.agent/skills.local/<skill>/SKILL.md` alongside the shared
skills. A private skill cannot use the same directory name as a shared skill; installation fails
rather than silently choosing one.

To test a separate local-agent directory without changing `~/.agent/`, set:

```bash
AGENT_FILES_LOCAL_DIR=/path/to/private-agent-files ./install.sh
```

## Checks

```bash
bash tests/run.sh
```

Runs shell syntax, shellcheck (when installed), Python compile, skill checks, and a sandboxed
installer test. The installer test never touches your real `$HOME` or `~/.agent/`.
