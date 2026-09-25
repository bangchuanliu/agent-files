#!/usr/bin/env bash
# Root installer: runs every per-agent adapter (.claude/, .copilot/). Each adapter symlinks
# this clone's ai-agents/ content into the agent's home dir and renders the shared rules, so
# edits to skills are live without re-running. Re-run after adding, renaming or removing a
# skill, or after editing rules. Safe to re-run; safe as a post-clone bootstrap hook.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "=== agent-files setup ($REPO) ==="

for adapter in copilot claude; do
  echo ""
  echo "--- $adapter ---"
  bash "$REPO/.$adapter/install.sh"
done

echo ""
echo "=== Setup complete ==="
