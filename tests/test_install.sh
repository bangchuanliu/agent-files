#!/usr/bin/env bash
# Installer smoke test in a throwaway HOME. Never touches the real ~/.claude,
# ~/.copilot, ~/.pi, or shell rc files.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SANDBOX="$(mktemp -d)"
CORE="$REPO/ai-agents/AGENTS.core.md"
cleanup() {
  rm -rf "$SANDBOX"
}
trap cleanup EXIT
export HOME="$SANDBOX"

fails=0
pass() { echo "ok   - $1"; }
fail() { echo "FAIL - $1"; fails=$((fails + 1)); }
check() { local msg="$1"; shift; if "$@"; then pass "$msg"; else fail "$msg"; fi; }

bash "$REPO/install.sh" > "$SANDBOX/install1.log" 2>&1 || { cat "$SANDBOX/install1.log"; fail "install.sh exits 0"; }

for d in "$REPO"/ai-agents/skills/*/; do
  b="$(basename "$d")"
  for agent in claude copilot pi; do
    if (source "$REPO/lib/links.sh"; supports "${d}SKILL.md" "$agent"); then
      case "$agent" in
        pi) skills_dir="$HOME/.pi/agent/skills" ;;
        *)  skills_dir="$HOME/.$agent/skills" ;;
      esac
      check "$agent skill $b linked" test "$(readlink "$skills_dir/$b")" = "${d%/}"
    fi
  done
done

for agent in claude copilot pi; do
  case "$agent" in
    pi) skills_dir="$HOME/.pi/agent/skills" ;;
    *)  skills_dir="$HOME/.$agent/skills" ;;
  esac
  check "$agent experimental skills are not installed" test ! -e "$skills_dir/code-simplify"
done

check "CLAUDE.md is a symlink to core rules" test "$(readlink "$HOME/.claude/CLAUDE.md")" = "$CORE"
check "Pi AGENTS.md is a symlink to core rules" test "$(readlink "$HOME/.pi/agent/AGENTS.md")" = "$CORE"
check "copilot-instructions.md is a regular file" test -f "$HOME/.copilot/copilot-instructions.md" -a ! -L "$HOME/.copilot/copilot-instructions.md"
check "Copilot instructions equal core rules" cmp -s "$HOME/.copilot/copilot-instructions.md" "$CORE"
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

# Re-running restores a hand-edited Copilot copy from the core rules.
echo "drift" >> "$HOME/.copilot/copilot-instructions.md"
bash "$REPO/install.sh" > "$SANDBOX/install3.log" 2>&1 || { cat "$SANDBOX/install3.log"; fail "third install.sh exits 0"; }
check "re-run refreshes Copilot rules" cmp -s "$HOME/.copilot/copilot-instructions.md" "$CORE"

echo ""
if [ "$fails" -eq 0 ]; then echo "test_install: all passed"; else echo "test_install: $fails failed"; exit 1; fi
