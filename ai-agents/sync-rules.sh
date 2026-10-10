#!/usr/bin/env bash
# Render global rules plus this machine's optional private overlay. {{RULES_DIR}} in the core
# rules becomes this clone's ai-agents/rules path.
# The overlay and rendered output live outside this repository:
#   ~/.agents-local/AGENTS.md
#   ~/.agents-local/generated/AGENTS.md
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RULES_DIR="$ROOT/ai-agents/rules"
CORE="$RULES_DIR/AGENTS.core.md"
LOCAL_AGENT_DIR="${AGENT_FILES_LOCAL_DIR:-$HOME/.agents-local}"
OVERLAY="$LOCAL_AGENT_DIR/AGENTS.md"
GENERATED="$LOCAL_AGENT_DIR/generated/AGENTS.md"

[[ -f "$CORE" ]] || { echo "sync-rules: missing core rules: $CORE" >&2; exit 2; }
mkdir -p "$(dirname "$GENERATED")"
tmp="$GENERATED.$$"
trap 'rm -f "$tmp"' EXIT

# Topic rule files are referenced by absolute path so every agent can read them in place.
sed "s|{{RULES_DIR}}|$RULES_DIR|g" "$CORE" > "$tmp"
if [[ -s "$OVERLAY" ]]; then
  printf '\n\n## Local Context\n\n' >> "$tmp"
  cat "$OVERLAY" >> "$tmp"
fi
mv "$tmp" "$GENERATED"
trap - EXIT

echo "sync-rules: wrote $GENERATED"
