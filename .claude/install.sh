#!/usr/bin/env bash
# Wire the shared ai-agents/ content + Claude-native config into ~/.claude/.
# Claude Code reads skills/agents/docs and the global CLAUDE.md from ~/.claude/.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARED="$REPO/ai-agents"
LOCAL_AGENT_DIR="${AGENT_FILES_LOCAL_DIR:-$HOME/.agents-local}"
LOCAL_SKILLS="$LOCAL_AGENT_DIR/skills"
LOCAL_AGENTS="$LOCAL_AGENT_DIR/agents"
GENERATED_RULES="$LOCAL_AGENT_DIR/generated/AGENTS.md"
CLAUDE="$HOME/.claude"
# shellcheck source=../lib/links.sh
source "$REPO/lib/links.sh"
mkdir -p "$CLAUDE"

assert_no_skill_collisions "$SHARED/skills" "$LOCAL_SKILLS"
assert_no_agent_collisions "$SHARED/agents" "$LOCAL_AGENTS"
link_skills "$SHARED/skills" "$CLAUDE/skills" claude
if [ -d "$LOCAL_SKILLS" ]; then link_skills "$LOCAL_SKILLS" "$CLAUDE/skills" claude; fi

# Rules: shared core plus this machine's optional private overlay.
bash "$SHARED/sync-rules.sh"
link "$GENERATED_RULES" "$CLAUDE/CLAUDE.md"

# Agents: a real merge directory of per-file symlinks, shared then private.
link_agents "$SHARED/agents" "$CLAUDE/agents" claude .md
link_agents "$LOCAL_AGENTS" "$CLAUDE/agents" claude .md
prune_dangling "$CLAUDE/agents"
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
