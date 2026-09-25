# agent-files

Personal AI-agent configuration for Claude Code and GitHub Copilot CLI. This repo is
standalone-first: a fresh clone with no company layer installed must render rules,
install skills, and run normally.

The repo owns company-agnostic rules, shared skills, adapter installers, and docs. A
separate company layer can be registered later to append employer-specific rules and add
its own skills/docs without changing this repo.

## Layout

```
ai-agents/
  AGENTS.core.md          # personal, company-agnostic rules source
  render-rules.sh         # renders core + registered layers
  .generated/AGENTS.md    # generated, ignored, deployed to agents
  skills/                 # <name>/SKILL.md, shared by both agents; INDEX.md lists them
  prompts/                # standalone, shareable prompt files; not installed
  experimental/           # parked skills, never installed
  docs/                   # maintainer/reference docs for this repo
.claude/                  # Claude Code adapter and Claude-native config
.copilot/                 # Copilot CLI adapter
lib/links.sh              # shared installer helpers (link, prune, skill merge, alias block)
install.sh                # root installer, delegates to both adapters
tests/
  run.sh                  # all repo checks; run before committing
  test_install.sh         # installers + render-rules against a sandboxed $HOME
```

Shared agents (`ai-agents/agents/`) are optional; the installers skip them when absent.

## Install

```bash
./install.sh
```

The root installer runs both adapters:

- `.claude/install.sh`
- `.copilot/install.sh`

Both adapters first run `ai-agents/render-rules.sh` so the deployed rules are generated
from the current core and any registered layers.

## Checks

```bash
bash tests/run.sh
```

Runs shell syntax, shellcheck (when installed), Python compile, `spec_check.py` over every
skill, each skill's `test_*.py`, and the installer test. The installer test never touches
your real `$HOME`.

## Rules rendering

`ai-agents/AGENTS.core.md` is the authored core. `ai-agents/render-rules.sh` writes
`ai-agents/.generated/AGENTS.md`:

1. core rules first
2. zero or more registered layer rules, each under `## Layer: <name>`

Layer registry: `~/.config/dotfiles/layers`

- one absolute layer directory per line
- blank lines and `#` comments ignored
- missing registry means zero layers

A layer may include `layer.conf`:

```sh
LAYER_NAME="Example Corp"
LAYER_RULES="ai-agents/AGENTS.layer.md"
```

`LAYER_RULES` is relative to the layer root and defaults to `AGENTS.md`. With no layers,
the generated file is byte-identical to `ai-agents/AGENTS.core.md`.

Deployment differs by agent:

| Agent | Deployed rules path | Mechanism |
|---|---|---|
| Claude Code | `~/.claude/CLAUDE.md` | symlink to `ai-agents/.generated/AGENTS.md` |
| Copilot CLI | `~/.copilot/copilot-instructions.md` | copied regular file |

Copilot gets a copy because its toolchain rewrites that path in place and would destroy a
symlink. Run `ai-agents/render-rules.sh --check` to detect drift.

## Merge-directory design

Skills are installed into real merge directories:

- `~/.claude/skills/<skill>`
- `~/.copilot/skills/<skill>`

Each entry is a symlink to one source skill directory; only directories containing a
`SKILL.md` are linked, and a skill whose frontmatter has `agents:` is linked only for the
agents it lists. This allows this repo, personal
skill repos, and company layer repos to contribute side by side without any repo containing
another repo's links. Removing or renaming a skill only prunes broken symlinks owned by that
path; live external links are left alone.

Claude docs use the same layering shape: this repo links its docs at `~/.claude/docs/core`,
so a layer can add `~/.claude/docs/<layer>` alongside it.

## Company layer contract

A company layer should:

1. Add its absolute path to `~/.config/dotfiles/layers`.
2. Provide `layer.conf` with `LAYER_NAME` and, optionally, `LAYER_RULES`.
3. Install its own skills into the same merge directories using per-skill symlinks.
4. Install docs under its own namespace, for example `~/.claude/docs/acme`.
5. Keep company-specific ignores, generated files, and tool configuration in the layer repo.

The personal repo must not depend on any layer being present.
