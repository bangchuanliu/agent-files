#!/usr/bin/env bash
# Wire shared rules and skills into Pi's user agent directory (~/.pi/agent).
# Pi discovers AGENTS.md and skills/ there automatically.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARED="$REPO/ai-agents"
PI_AGENT_DIR="${PI_CODING_AGENT_DIR:-$HOME/.pi/agent}"
# shellcheck source=../lib/links.sh
source "$REPO/lib/links.sh"
mkdir -p "$PI_AGENT_DIR"

# Pi supports the Agent Skills standard and recursively discovers skill directories.
link_skills "$SHARED/skills" "$PI_AGENT_DIR/skills" pi

# Global, company-agnostic instructions only.
link "$SHARED/AGENTS.core.md" "$PI_AGENT_DIR/AGENTS.md"

echo ""
echo "Pi wired at $PI_AGENT_DIR. Restart Pi (or run /reload) to load the changes."
