#!/usr/bin/env bash
# Root dotfiles entrypoint.
#
# This script is safe to use as a generic bootstrap hook after cloning this
# dotfiles repo locally or into a remote development environment. The caller
# should invoke it from the repo root or by absolute path.
#
# It delegates to the per-agent adapters that wire the shared ai-agents/ content
# (skills, optional agents, docs, rules) into ~/.copilot/ and ~/.claude/. Each
# adapter creates live symlinks into THIS cloned repo's ai-agents/ tree where the
# agent supports symlinks, so both agents pick up every skill without a rebuild.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== agent-files - Setup ==="
echo "repo: $REPO"
echo ""

# --- Copilot CLI adapter ---
echo "--- Copilot CLI ---"
if [ -x "$REPO/.copilot/install.sh" ] || [ -f "$REPO/.copilot/install.sh" ]; then
    bash "$REPO/.copilot/install.sh"
else
    echo "[copilot] .copilot/install.sh not found, skipping."
fi
echo ""

# --- Claude Code adapter ---
echo "--- Claude Code ---"
if [ -x "$REPO/.claude/install.sh" ] || [ -f "$REPO/.claude/install.sh" ]; then
    bash "$REPO/.claude/install.sh"
else
    echo "[claude] .claude/install.sh not found, skipping."
fi
echo ""

echo "=== Setup complete ==="
echo "Skills wired into ~/.copilot/skills and ~/.claude/skills (symlinks into $REPO/ai-agents)."
