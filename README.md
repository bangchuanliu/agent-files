# agent-files

Shareable AI-agent configuration for Claude Code, GitHub Copilot CLI, and Pi. The repository
contains only general rules and publishable skills. Company or machine-specific instructions and
skills live in `~/.agents-local/`, outside the repository.

## Layout

```text
agent-files/
  ai-agents/
    rules/
      AGENTS.md           # tracked global guardrails plus an index of topic rule files
      *.md                # topic rules (thinking, building, communicating) loaded on demand
    agents/               # tracked shared agents, one <name>.md each (Claude, Copilot)
      skill-auditor.md    # reviews the rule files against the skill-auditor skill
    skills/               # tracked, safe-to-share skills, one level of category folders
      INDEX.md            # human lookup of every skill
      engineering/<skill>/SKILL.md
      general/<skill>/SKILL.md
      experimental/<skill>/SKILL.md  # still changing; installed like the rest
  .claude/                # Claude Code adapter
  .copilot/               # Copilot CLI adapter
  .pi/                    # Pi adapter
  lib/links.sh            # shared installer helpers
  install.sh              # root installer
  tests/run.sh            # all repo checks; run before committing

~/.agents-local/
  AGENTS.md               # optional private company/machine instructions
  skills/                 # optional private skills; each contains SKILL.md
  agents/                 # optional private agents; one <name>.md each (Claude, Copilot)
```

`~/.agents-local/` is local to the machine and is not part of this repository. Shared skills never
read it directly: to give a shared skill company context, point to that context from
`~/.agents-local/AGENTS.md`. Do not put secrets in
its instruction files or skills. Reference the approved secret-management system instead.

## Install

```bash
./install.sh
```

Requires Python 3.9+ and Bash on macOS or Linux. Obtain and authenticate the supported
agent clients through your organization's approved channels first. The installer does not
download clients, packages, plugins, hooks, or MCP servers, and it leaves client settings
and shell aliases unchanged.

The installer runs the Claude, Copilot, and Pi adapters. Each one symlinks its rules path
directly to `ai-agents/rules/AGENTS.md`, with no rendering step, and installs skills into the
agent's normal skill directory. Category folders are flattened: each skill gets one link named
after its folder, so skill names must be unique across categories. The installer also creates
`$WTREE_ROOT` (default `~/.worktree`), which the `wtree` and `hop` skills read.

The rule index in `ai-agents/rules/AGENTS.md` names topic files as `{RULE_DIR}/<topic>.md`. The
installer exports `RULE_DIR` (this clone's `ai-agents/rules`) from a managed block in `~/.zshrc`
and `~/.bashrc`; open a new shell before starting an agent so it inherits the variable.

Edits to any rules file take effect in the next session without re-running the installer.
Earlier installs left rendered copies under `~/.agents-local/generated/`; the installer removes them.

| Agent | Deployed rules path |
|---|---|
| Claude Code | `~/.claude/CLAUDE.md` |
| Copilot CLI | `~/.copilot/copilot-instructions.md` |
| Pi | `~/.pi/agent/AGENTS.md` (or `$PI_CODING_AGENT_DIR/AGENTS.md`) |

## Private company setup

On a company-specific machine, create the optional local overlay:

```bash
mkdir -p ~/.agents-local/skills
$EDITOR ~/.agents-local/AGENTS.md
./install.sh
```

Private skills are installed from `~/.agents-local/skills/<skill>/SKILL.md` alongside the shared
skills. A private skill cannot use the same directory name as a shared skill; installation fails
rather than silently choosing one.

Private agents are installed from `~/.agents-local/agents/<name>.md` into `~/.claude/agents/` and,
as `<name>.agent.md`, into `~/.copilot/agents/`. Pi has no agents. An `agents:` frontmatter line
limits which tools get an agent, and names must not collide with shared agents.

To test a separate local-agent directory without changing `~/.agents-local/`, set:

```bash
AGENT_FILES_LOCAL_DIR=/path/to/private-agent-files ./install.sh
```

## Checks

```bash
bash tests/run.sh
```

Runs shell syntax, shellcheck (when installed), Python compile, skill checks, and a sandboxed
installer test. The installer test never touches your real `$HOME` or `~/.agents-local/`.
