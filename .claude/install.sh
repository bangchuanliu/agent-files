#!/usr/bin/env bash
# Wire the shared ai-agents/ content + Claude-native config into ~/.claude/.
# Claude Code reads skills/agents/docs and the global CLAUDE.md from ~/.claude/.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARED="$REPO/ai-agents"
CLAUDE="$HOME/.claude"
# shellcheck source=../lib/links.sh
source "$REPO/lib/links.sh"
mkdir -p "$CLAUDE"

link_skills "$SHARED/skills" "$CLAUDE/skills" claude

# Rules: render-rules.sh owns ~/.claude/CLAUDE.md (symlink to the generated file).
bash "$SHARED/render-rules.sh"

if [ -d "$SHARED/agents" ]; then
  link "$SHARED/agents" "$CLAUDE/agents"
else
  echo "skip: $SHARED/agents missing"
fi
if [ -d "$SHARED/commands" ]; then link "$SHARED/commands" "$CLAUDE/commands"; fi

# Docs are namespaced under docs/core so a company layer can add docs/<layer> alongside.
unlink_if_symlink "$CLAUDE/docs"   # retire legacy whole-dir symlink
mkdir -p "$CLAUDE/docs"
link "$SHARED/docs" "$CLAUDE/docs/core"

# Claude-native config (per-agent; not shared)
link "$REPO/.claude/settings.json"         "$CLAUDE/settings.json"
link "$REPO/.claude/statusline-command.sh" "$CLAUDE/statusline-command.sh"

# Old layout used ~/.claude/rules; rules now live in CLAUDE.md -> generated AGENTS.md
if [ -L "$CLAUDE/rules" ]; then rm "$CLAUDE/rules"; echo "removed stale ~/.claude/rules"; fi

install_shell_alias cla "claude --dangerously-skip-permissions" \
  "cla = Claude Code with all permission prompts skipped."

echo ""
echo "Claude Code wired. Open a new shell (or source your rc file) to pick up the 'cla' alias."
