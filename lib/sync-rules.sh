#!/usr/bin/env bash
# Render global rules plus this machine's optional private overlay. Placeholders in
# ai-agents/rules/AGENTS.md:
#   {{RULES_DIR}}      -> this clone's ai-agents/rules path
#   {{WORKTREE_ROOT}}  -> $WTREE_ROOT, default ~/.worktree (created if missing)
# The overlay and rendered output live outside this repository:
#   ~/.agents-local/AGENTS.md
#   ~/.agents-local/generated/AGENTS.md
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
RULES_DIR="$ROOT/ai-agents/rules"
CORE="$RULES_DIR/AGENTS.md"
WORKTREE_ROOT="${WTREE_ROOT:-$HOME/.worktree}"
LOCAL_AGENT_DIR="${AGENT_FILES_LOCAL_DIR:-$HOME/.agents-local}"
OVERLAY="$LOCAL_AGENT_DIR/AGENTS.md"
GENERATED="$LOCAL_AGENT_DIR/generated/AGENTS.md"

[[ -f "$CORE" ]] || { echo "sync-rules: missing core rules: $CORE" >&2; exit 2; }
mkdir -p "$(dirname "$GENERATED")" "$WORKTREE_ROOT"
tmp="$GENERATED.$$"
trap 'rm -f "$tmp"' EXIT

# Topic rule files are referenced by absolute path so every agent can read them in place.
sed -e "s|{{RULES_DIR}}|$RULES_DIR|g" -e "s|{{WORKTREE_ROOT}}|$WORKTREE_ROOT|g" "$CORE" > "$tmp"
if [[ -s "$OVERLAY" ]]; then
  printf '\n\n## Local Context\n\n' >> "$tmp"
  cat "$OVERLAY" >> "$tmp"
fi
mv "$tmp" "$GENERATED"
trap - EXIT

echo "sync-rules: wrote $GENERATED"
