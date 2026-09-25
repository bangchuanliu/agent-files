#!/usr/bin/env bash
# Installer + render-rules smoke test in a throwaway HOME. Never touches the real ~/.claude,
# ~/.copilot or shell rc files.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SANDBOX="$(mktemp -d)"
GEN="$REPO/ai-agents/.generated/AGENTS.md"
GEN_BACKUP=""
cleanup() {
  rm -rf "$SANDBOX"
  if [ -n "$GEN_BACKUP" ]; then mv "$GEN_BACKUP" "$GEN"; fi
}
trap cleanup EXIT
if [ -f "$GEN" ]; then GEN_BACKUP="$(mktemp)"; cp "$GEN" "$GEN_BACKUP"; fi
export HOME="$SANDBOX"

fails=0
pass() { echo "ok   - $1"; }
fail() { echo "FAIL - $1"; fails=$((fails + 1)); }
check() { local msg="$1"; shift; if "$@"; then pass "$msg"; else fail "$msg"; fi; }

bash "$REPO/install.sh" > "$SANDBOX/install1.log" 2>&1 || { cat "$SANDBOX/install1.log"; fail "install.sh exits 0"; }

for d in "$REPO"/ai-agents/skills/*/; do
  b="$(basename "$d")"
  for agent in claude copilot; do
    if (source "$REPO/lib/links.sh"; supports "${d}SKILL.md" "$agent"); then
      check "$agent skill $b linked" test "$(readlink "$HOME/.$agent/skills/$b")" = "${d%/}"
    fi
  done
done

check "CLAUDE.md is a symlink to generated rules" test "$(readlink "$HOME/.claude/CLAUDE.md")" = "$GEN"
check "copilot-instructions.md is a regular file" test -f "$HOME/.copilot/copilot-instructions.md" -a ! -L "$HOME/.copilot/copilot-instructions.md"
check "no layers: generated equals core" cmp -s "$GEN" "$REPO/ai-agents/AGENTS.core.md"
check "render-rules --check in sync" bash "$REPO/ai-agents/render-rules.sh" --check
check "docs/core linked" test "$(readlink "$HOME/.claude/docs/core")" = "$REPO/ai-agents/docs"
check "cla alias block once in .zshrc" test "$(grep -c '>>> agent-files cla alias >>>' "$HOME/.zshrc")" = 1

# Foreign links survive, dangling ones are pruned, and re-runs are idempotent.
foreign="$SANDBOX/foreign-skill"; mkdir -p "$foreign"
ln -s "$foreign" "$HOME/.copilot/skills/foreign"
ln -s "$SANDBOX/does-not-exist" "$HOME/.copilot/skills/gone"
bash "$REPO/install.sh" > "$SANDBOX/install2.log" 2>&1 || { cat "$SANDBOX/install2.log"; fail "second install.sh exits 0"; }
check "foreign skill link kept" test -L "$HOME/.copilot/skills/foreign"
check "dangling skill link pruned" test ! -L "$HOME/.copilot/skills/gone"
check "alias blocks not duplicated on re-run" test "$(grep -c '>>> agent-files coya alias >>>' "$HOME/.bashrc")" = 1
check "re-run makes no new links" bash -c "! grep -q '^link: .*/skills/' '$SANDBOX/install2.log'"

# Drift detection: a hand-edited Copilot copy must fail --check.
echo "drift" >> "$HOME/.copilot/copilot-instructions.md"
check "render-rules --check detects drift" bash -c "! bash '$REPO/ai-agents/render-rules.sh' --check >/dev/null 2>&1"

# A registered layer is appended under its heading.
layer="$SANDBOX/layer"; mkdir -p "$layer" "$HOME/.config/dotfiles"
printf 'LAYER_NAME="Acme"\n' > "$layer/layer.conf"
printf '# Acme rules\n- be acme\n' > "$layer/AGENTS.md"
echo "$layer" > "$HOME/.config/dotfiles/layers"
bash "$REPO/ai-agents/render-rules.sh" > /dev/null
check "layer heading rendered" grep -q '^## Layer: Acme$' "$GEN"
check "layer body rendered" grep -q '^- be acme$' "$GEN"
printf 'LAYER_RULES="../escape.md"\n' > "$layer/layer.conf"
check "unsafe LAYER_RULES rejected" bash -c "! bash '$REPO/ai-agents/render-rules.sh' >/dev/null 2>&1"

echo ""
if [ "$fails" -eq 0 ]; then echo "test_install: all passed"; else echo "test_install: $fails failed"; exit 1; fi
