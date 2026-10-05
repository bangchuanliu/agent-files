# agent-files

Personal, company-agnostic AI-agent configuration for Claude Code, GitHub Copilot CLI, and Pi.
Each checkout can also carry private working notes in `.context/context.md`, without adding them
to any agent's global instructions.

## Layout

```
.context/
  README.md               # how to add the ignored context.md file
  context.md              # local company/project reference notes (created by you, ignored)
ai-agents/
  AGENTS.core.md          # git-tracked, company-agnostic global rules
  skills/                 # <name>/SKILL.md, shared by all supported agents
  prompts/                # standalone, shareable prompt files; not installed
  experimental/           # parked skills, never installed
  docs/                   # maintainer/reference docs for this repo
.claude/                  # Claude Code adapter and Claude-native config
.copilot/                 # Copilot CLI adapter
.pi/                      # Pi adapter
lib/links.sh              # shared installer helpers
install.sh                # root installer, delegates to all adapters
tests/                    # repository checks
```

Shared agents (`ai-agents/agents/`) are optional; installers skip them when absent.

## Use a checkout for a new context

```bash
git clone <repository-url> agent-files-acme
cd agent-files-acme
mkdir -p .context
$EDITOR .context/context.md
./install.sh
```

`.context/context.md` is ignored by Git and is local reference material only. It is never merged
into Claude, Copilot, or Pi global instruction files, preventing company-specific guidance from
leaking into unrelated work. Put instructions that must apply to a codebase in that codebase's
own agent instruction file.

## Install

```bash
./install.sh
```

The root installer runs all adapters:

- `.claude/install.sh`
- `.copilot/install.sh`
- `.pi/install.sh`

All three install only `ai-agents/AGENTS.core.md`, the shared company-agnostic rules.

| Agent | Deployed rules path | Mechanism |
|---|---|---|
| Claude Code | `~/.claude/CLAUDE.md` | symlink to `ai-agents/AGENTS.core.md` |
| Copilot CLI | `~/.copilot/copilot-instructions.md` | copied regular file |
| Pi | `~/.pi/agent/AGENTS.md` (or `$PI_CODING_AGENT_DIR/AGENTS.md`) | symlink to `ai-agents/AGENTS.core.md` |

Copilot gets a copy because its toolchain rewrites that path in place and would destroy a
symlink. Re-run `./install.sh` after changing the core rules to refresh its copy.

## Merge-directory design

Skills are installed into real merge directories:

- `~/.claude/skills/<skill>`
- `~/.copilot/skills/<skill>`
- `~/.pi/agent/skills/<skill>` (or `$PI_CODING_AGENT_DIR/skills/<skill>`)

Each entry is a symlink to one source skill directory; only directories containing a
`SKILL.md` are linked, and a skill whose frontmatter has `agents:` is linked only for the
agents it lists. This allows this repo and other local skill repos to contribute side by side
without any repo containing another repo's links. Removing or renaming a skill only prunes
broken symlinks owned by that path; live external links are left alone.

Claude docs use the same merge shape: this repo links its docs at `~/.claude/docs/core`, so
other local sources can add their own namespaced directories alongside it.

## Checks

```bash
bash tests/run.sh
```

Runs shell syntax, shellcheck (when installed), Python compile, `spec_check.py` over every
skill, each skill's `test_*.py`, and the installer test. The installer test never touches your
real `$HOME`.
