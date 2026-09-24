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
mkdir -p "$COPILOT/agents"

# Skills: a real merge directory of per-skill symlinks (Copilot scans
# ~/.copilot/skills/<name>/SKILL.md). Kept per-skill so other installers can add
# skills to the same dir without either repo's tree containing the other's links.
merged="$COPILOT/skills"
if [ -L "$merged" ]; then rm "$merged"; fi   # retire legacy whole-dir symlink
mkdir -p "$merged"
for d in "$SHARED/skills"/*/; do
  [ -d "$d" ] || continue
  b="$(basename "$d")"
  if supports "${d%/}/SKILL.md" copilot; then
    link "${d%/}" "$merged/$b"
  else
    if [ -L "$merged/$b" ]; then rm "$merged/$b"; fi
    echo "skip: $b (claude-only)"
  fi
done
# Prune dangling links (a skill was renamed/deleted) so re-runs are idempotent.
# Only broken symlinks are removed - live work/personal links are left untouched.
for l in "$merged"/*; do
  if [ -L "$l" ] && [ ! -e "$l" ]; then rm "$l"; echo "prune: $l (dangling)"; fi
done

# Global rules (all sessions). Render first. Copilot must receive a regular file
# because its toolchain rewrites this path in place and would destroy a symlink.
bash "$SHARED/render-rules.sh"

# Agents: per-file symlink with Copilot's .agent.md extension. Optional because
# this standalone repo may not contain shared agents.
if [ -d "$SHARED/agents" ]; then
  for f in "$SHARED/agents"/*.md; do
    [ -e "$f" ] || continue
    base="$(basename "$f" .md)"
    if supports "$f" copilot; then
      link "$f" "$COPILOT/agents/$base.agent.md"
    else
      if [ -L "$COPILOT/agents/$base.agent.md" ]; then rm "$COPILOT/agents/$base.agent.md"; fi
      echo "skip: $base (claude-only)"
    fi
  done
else
  echo "skip: $SHARED/agents missing"
fi

# Shell alias: `coya` launches Copilot CLI in autopilot with all tools allowed.
# Managed as a marker-delimited block in the shell rc files, replaced in place on
# re-run so the installer owns the canonical copy (idempotent).
install_coya_alias() {
  local begin="# >>> agent-files coya alias >>>"
  local end="# <<< agent-files coya alias <<<"
  local block
  block="$(cat <<'EOF_BLOCK'
# >>> agent-files coya alias >>>
# coya = Copilot CLI in autopilot mode with all tools auto-allowed.
alias coya='copilot --autopilot --allow-all'
# <<< agent-files coya alias <<<
EOF_BLOCK
)"
  local rc
  for rc in "$HOME/.zshrc" "$HOME/.bashrc"; do
    touch "$rc"
    if grep -qF "$begin" "$rc"; then
      replace_managed_block "$rc" "$begin" "$end" "$block"
      echo "update: coya alias block in $rc"
    else
      printf '\n%s\n' "$block" >> "$rc"
      echo "add:  coya alias block in $rc"
    fi
  done
}
install_coya_alias

echo ""
echo "Copilot CLI wired. Verify with: copilot plugin list  (skills/agents load from the local dirs above)"
echo "Run 'source ~/.zshrc' / 'source ~/.bashrc' (or open a new shell) to pick up the 'coya' alias."
