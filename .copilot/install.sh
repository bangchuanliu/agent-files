#!/usr/bin/env bash
# Wire the shared ai-agents/ content into ~/.copilot/ (Copilot CLI local dirs).
# Copilot CLI reads skills from ~/.copilot/skills, agents from ~/.copilot/agents
# (as <name>.agent.md), and global rules from ~/.copilot/copilot-instructions.md.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARED="$REPO/ai-agents"
LOCAL_AGENT_DIR="${AGENT_FILES_LOCAL_DIR:-$HOME/.agents-local}"
LOCAL_SKILLS="$LOCAL_AGENT_DIR/skills"
LOCAL_AGENTS="$LOCAL_AGENT_DIR/agents"
GENERATED_RULES="$LOCAL_AGENT_DIR/generated/AGENTS.md"
COPILOT="$HOME/.copilot"
# shellcheck source=../lib/links.sh
source "$REPO/lib/links.sh"
mkdir -p "$COPILOT"

assert_no_skill_collisions "$SHARED/skills" "$LOCAL_SKILLS"
assert_no_agent_collisions "$SHARED/agents" "$LOCAL_AGENTS"
link_skills "$SHARED/skills" "$COPILOT/skills" copilot
if [ -d "$LOCAL_SKILLS" ]; then link_skills "$LOCAL_SKILLS" "$COPILOT/skills" copilot; fi

# Topic rules (thinking.md, building.md, ...) are symlinked into ~/.copilot/instructions. They
# deliberately lack the .instructions.md suffix, which Copilot would auto-load on every
# session; they stay lazy and are loaded on demand through the rule index.
RULES_SRC="$SHARED/rules"
INSTRUCTIONS="$COPILOT/instructions"
mkdir -p "$INSTRUCTIONS"
for f in "$RULES_SRC"/*.md; do
  [ "$(basename "$f")" = AGENTS.md ] && continue
  link "$f" "$INSTRUCTIONS/$(basename "$f")"
done
# Copilot-only autopilot rules must apply in every session, so this one keeps the
# auto-loaded .instructions.md suffix.
link "$REPO/.copilot/autopilot.md" "$INSTRUCTIONS/autopilot.instructions.md"
prune_dangling "$INSTRUCTIONS"

# Copilot rewrites this path in place, so it must be a regular copy rather than a symlink.
# Its rule index points at the ~/.copilot/instructions links instead of this clone.
bash "$REPO/lib/sync-rules.sh"
COPILOT_RULES="$COPILOT/copilot-instructions.md"
if [ -L "$COPILOT_RULES" ]; then rm "$COPILOT_RULES"; fi
sed "s|$RULES_SRC/|$INSTRUCTIONS/|g" "$GENERATED_RULES" > "$COPILOT_RULES"

# Agents: per-file symlinks with Copilot's .agent.md extension, shared then private.
link_agents "$SHARED/agents" "$COPILOT/agents" copilot .agent.md
link_agents "$LOCAL_AGENTS" "$COPILOT/agents" copilot .agent.md
prune_dangling "$COPILOT/agents"

install_shell_alias coya "copilot --autopilot --allow-all" \
  "coya = Copilot CLI in autopilot mode with all tools auto-allowed."
install_shell_alias coy "copilot --allow-all" \
  "coy = Copilot CLI with all tools auto-allowed, without autopilot."

echo ""
echo "Copilot CLI wired. Open a new shell (or source your rc file) to pick up the 'coya' and 'coy' aliases."
