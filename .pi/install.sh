#!/usr/bin/env bash
# Wire shared rules and skills into Pi's user agent directory (~/.pi/agent).
# Pi discovers AGENTS.md and skills/ there automatically.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARED="$REPO/ai-agents"
LOCAL_AGENT_DIR="${AGENT_FILES_LOCAL_DIR:-$HOME/.agent}"
LOCAL_SKILLS="$LOCAL_AGENT_DIR/skills.local"
GENERATED_RULES="$LOCAL_AGENT_DIR/generated/AGENTS.md"
PI_AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
# shellcheck source=../lib/links.sh
source "$REPO/lib/links.sh"
mkdir -p "$PI_AGENT_DIR"

# Pi supports the Agent Skills standard and recursively discovers skill directories.
assert_no_skill_collisions "$SHARED/skills" "$LOCAL_SKILLS"
link_skills "$SHARED/skills" "$PI_AGENT_DIR/skills" pi
if [ -d "$LOCAL_SKILLS" ]; then link_skills "$LOCAL_SKILLS" "$PI_AGENT_DIR/skills" pi; fi

# Shared core plus this machine's optional private overlay.
bash "$SHARED/sync-rules.sh"
link "$GENERATED_RULES" "$PI_AGENT_DIR/AGENTS.md"

echo ""
echo "Pi wired at $PI_AGENT_DIR. Restart Pi (or run /reload) to load the changes."
