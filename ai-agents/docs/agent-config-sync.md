# Agent rules rendering (maintainer notes)

This is documentation for the human maintainer, not instructions for an agent. It explains
how the shared guide reaches each agent.

## Layout

| Path | Kind | Contents |
|---|---|---|
| `ai-agents/AGENTS.core.md` | git-tracked source | Company-agnostic core guide |
| `~/.config/dotfiles/layers` | optional registry | Absolute layer directories, one per line |
| `<layer>/layer.conf` | optional layer metadata | `LAYER_NAME` and optional `LAYER_RULES` |
| `ai-agents/.generated/AGENTS.md` | ignored generated file | Core plus registered layers |
| `~/.claude/CLAUDE.md` | symlink | Points to the generated file |
| `~/.copilot/copilot-instructions.md` | tool-owned regular file | Copied from the generated file |

## Render pipeline

Run the renderer after every rules edit or layer registry change:

```sh
ai-agents/render-rules.sh          # render and deploy
ai-agents/render-rules.sh --check  # verify only, non-zero on drift
```

The renderer always writes core rules first. If `~/.config/dotfiles/layers` is missing, the
render has zero layers and `ai-agents/.generated/AGENTS.md` is byte-identical to
`ai-agents/AGENTS.core.md`. If layers are registered, each layer's rules are appended under a
generated `## Layer: <LAYER_NAME>` heading.

## Why Copilot can't just be a symlink

Something in the Copilot toolchain rewrites `~/.copilot/copilot-instructions.md` in place.
That destroys any symlink placed at that path. So the rendered rules have to be copied
there, and they silently drift whenever you edit rules or layers and forget to render.

Claude can use a symlink because `~/.claude/CLAUDE.md` is read as a normal file and is not
rewritten by the toolchain.

## Historical sentinel bug

The old sync script stripped a generated trailing block from a monolithic rules file. Its
first inline verify command used a loose search like:

```sh
grep -n 'DO NOT EDIT THIS SECTION' AGENTS.md | cut -d: -f1
```

That matched the preamble's own mention of the sentinel before the real sentinel. The
script then truncated the source near the top and compared a tiny prefix against the whole
Copilot file, so it could never report drift correctly.

`render-rules.sh` keeps the defensive fix for backward compatibility with old layer files:
it anchors the sentinel at start-of-line, takes the last match, and refuses to strip if the
computed shared portion is implausibly small (`shared_end -gt 20`). New core files should not
contain any generated trailing block.

## Authoring conventions

- Keep `AGENTS.core.md` to always-on, company-agnostic behaviour.
- Put employer-specific rules in a registered layer.
- Put situational or lengthy material in `ai-agents/docs/` or in the relevant skill.
- Do not edit `ai-agents/.generated/AGENTS.md` by hand.
