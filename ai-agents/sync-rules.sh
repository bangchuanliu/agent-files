#!/usr/bin/env bash
# Render global rules plus this machine's optional private overlay.
# The overlay and rendered output live outside this repository:
#   ~/.agent/AGENTS.md.local
#   ~/.agent/generated/AGENTS.md
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CORE="$ROOT/ai-agents/AGENTS.core.md"
LOCAL_AGENT_DIR="${AGENT_FILES_LOCAL_DIR:-$HOME/.agent}"
OVERLAY="$LOCAL_AGENT_DIR/AGENTS.md.local"
GENERATED="$LOCAL_AGENT_DIR/generated/AGENTS.md"

[[ -f "$CORE" ]] || { echo "sync-rules: missing core rules: $CORE" >&2; exit 2; }
mkdir -p "$(dirname "$GENERATED")"
tmp="$GENERATED.$$"
trap 'rm -f "$tmp"' EXIT

cat "$CORE" > "$tmp"
if [[ -s "$OVERLAY" ]]; then
  printf '\n\n## Local Context\n\n' >> "$tmp"
  cat "$OVERLAY" >> "$tmp"
fi
mv "$tmp" "$GENERATED"
trap - EXIT

echo "sync-rules: wrote $GENERATED"
