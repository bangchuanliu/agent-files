#!/usr/bin/env bash
# Wire the shared ai-agents/ content + Claude-native config into ~/.claude/.
# Claude Code reads skills/agents/docs and the global CLAUDE.md from ~/.claude/.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SHARED="$REPO/ai-agents"
CLAUDE="$HOME/.claude"
# shellcheck source=../lib/links.sh
source "$REPO/lib/links.sh"
mkdir -p "$CLAUDE"

# Skills: a real merge directory of per-skill symlinks (one symlink per work skill),
# so other installers can add skills to the same dir without either repo's tree
# containing the other's links.
merged="$CLAUDE/skills"
if [ -L "$merged" ]; then rm "$merged"; fi   # retire legacy whole-dir symlink
mkdir -p "$merged"
for d in "$SHARED/skills"/*/; do
  [ -d "$d" ] || continue
  b="$(basename "$d")"
  if supports "${d%/}/SKILL.md" claude; then
    link "${d%/}" "$merged/$b"
  else
    if [ -L "$merged/$b" ]; then rm "$merged/$b"; fi
    echo "skip: $b (not for claude)"
  fi
done
# Prune dangling links (a skill was renamed/deleted) so re-runs are idempotent.
# Only broken symlinks are removed - live work/personal links are left untouched.
for l in "$merged"/*; do
  if [ -L "$l" ] && [ ! -e "$l" ]; then rm "$l"; echo "prune: $l (dangling)"; fi
done

# Shared content (Claude reads these natively). Render rules first.
bash "$SHARED/render-rules.sh"
if [ -d "$SHARED/agents" ]; then
  link "$SHARED/agents" "$CLAUDE/agents"
else
  echo "skip: $SHARED/agents missing"
fi
if [ -L "$CLAUDE/docs" ]; then rm "$CLAUDE/docs"; fi
mkdir -p "$CLAUDE/docs"
link "$SHARED/docs" "$CLAUDE/docs/core"
link "$SHARED/.generated/AGENTS.md" "$CLAUDE/CLAUDE.md"
[ -d "$SHARED/commands" ] && link "$SHARED/commands" "$CLAUDE/commands"

# Claude-native config (per-agent; not shared)
link "$REPO/.claude/settings.json"         "$CLAUDE/settings.json"
link "$REPO/.claude/statusline-command.sh" "$CLAUDE/statusline-command.sh"

# Old layout used ~/.claude/rules; rules now live in CLAUDE.md -> generated AGENTS.md
if [ -L "$CLAUDE/rules" ]; then rm "$CLAUDE/rules"; echo "removed stale ~/.claude/rules"; fi

# Shell alias: `cla` launches Claude Code skipping all permission prompts.
# Managed as a marker-delimited block in the shell rc files, replaced in place on
# re-run so the installer owns the canonical copy (idempotent).
install_cla_alias() {
  local begin="# >>> agent-files cla alias >>>"
  local end="# <<< agent-files cla alias <<<"
  local block
  block="$(cat <<'EOF_BLOCK'
# >>> agent-files cla alias >>>
# cla = Claude Code with all permission prompts skipped.
alias cla="claude --dangerously-skip-permissions"
# <<< agent-files cla alias <<<
EOF_BLOCK
)"
  local rc
  for rc in "$HOME/.zshrc" "$HOME/.bashrc"; do
    touch "$rc"
    if grep -qF "$begin" "$rc"; then
      replace_managed_block "$rc" "$begin" "$end" "$block"
      echo "update: cla alias block in $rc"
    else
      printf '\n%s\n' "$block" >> "$rc"
      echo "add:  cla alias block in $rc"
    fi
  done
}
install_cla_alias

echo ""
echo "Claude Code wired. Additional skills from an installed company layer are merged into the same dirs."
echo "Run 'source ~/.zshrc' / 'source ~/.bashrc' (or open a new shell) to pick up the 'cla' alias."
