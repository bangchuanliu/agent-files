#!/usr/bin/env bash
# Wire the shared ai-agents/ content into ~/.copilot/ (Copilot CLI local dirs).
# Copilot CLI reads skills from ~/.copilot/skills, agents from ~/.copilot/agents
# (as <name>.agent.md), and global rules from ~/.copilot/copilot-instructions.md.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARED="$REPO/ai-agents"
LOCAL_AGENT_DIR="${AGENT_FILES_LOCAL_DIR:-$HOME/.agent}"
LOCAL_SKILLS="$LOCAL_AGENT_DIR/skills.local"
GENERATED_RULES="$LOCAL_AGENT_DIR/generated/AGENTS.md"
COPILOT="$HOME/.copilot"
# shellcheck source=../lib/links.sh
source "$REPO/lib/links.sh"
mkdir -p "$COPILOT"

assert_no_skill_collisions "$SHARED/skills" "$LOCAL_SKILLS"
link_skills "$SHARED/skills" "$COPILOT/skills" copilot
if [ -d "$LOCAL_SKILLS" ]; then link_skills "$LOCAL_SKILLS" "$COPILOT/skills" copilot; fi

# Copilot rewrites this path in place, so it must be a regular copy rather than a symlink.
bash "$SHARED/sync-rules.sh"
COPILOT_RULES="$COPILOT/copilot-instructions.md"
if [ -L "$COPILOT_RULES" ]; then rm "$COPILOT_RULES"; fi
cp "$GENERATED_RULES" "$COPILOT_RULES"

# Agents: per-file symlink with Copilot's .agent.md extension.
if [ -d "$SHARED/agents" ]; then
  mkdir -p "$COPILOT/agents"
  for f in "$SHARED/agents"/*.md; do
    [ -e "$f" ] || continue
    base="$(basename "$f" .md)"
    if supports "$f" copilot; then
      link "$f" "$COPILOT/agents/$base.agent.md"
    else
      unlink_if_symlink "$COPILOT/agents/$base.agent.md"
      echo "skip: $base (not for copilot)"
    fi
  done
  prune_dangling "$COPILOT/agents"
else
  echo "skip: $SHARED/agents missing"
fi

install_shell_alias coya "copilot --autopilot --allow-all" \
  "coya = Copilot CLI in autopilot mode with all tools auto-allowed."

echo ""
echo "Copilot CLI wired. Open a new shell (or source your rc file) to pick up the 'coya' alias."
