#!/usr/bin/env bash
# Wire the shared ai-agents/ content into ~/.copilot/ (Copilot CLI local dirs).
# Copilot CLI reads skills from ~/.copilot/skills, agents from ~/.copilot/agents
# (as <name>.agent.md), and global rules from ~/.copilot/copilot-instructions.md.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARED="$REPO/ai-agents"
COPILOT="$HOME/.copilot"
# shellcheck source=../lib/links.sh
source "$REPO/lib/links.sh"
mkdir -p "$COPILOT"

link_skills "$SHARED/skills" "$COPILOT/skills" copilot

# Rules: render-rules.sh copies (not links) ~/.copilot/copilot-instructions.md, because the
# Copilot toolchain rewrites that path in place and would destroy a symlink.
bash "$SHARED/render-rules.sh"

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
