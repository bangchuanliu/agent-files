#!/usr/bin/env bash
# Installer smoke test in a throwaway HOME. Never touches the real ~/.claude,
# ~/.copilot, ~/.pi, or shell rc files.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SANDBOX="$(mktemp -d)"
CORE="$REPO/ai-agents/AGENTS.core.md"
LOCAL_AGENT_DIR="$SANDBOX/custom-overlay"
GENERATED="$LOCAL_AGENT_DIR/generated/AGENTS.md"
cleanup() {
  rm -rf "$SANDBOX"
}
trap cleanup EXIT
export HOME="$SANDBOX"
export AGENT_FILES_LOCAL_DIR="$LOCAL_AGENT_DIR"

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

check "no overlay: generated rules equal core" cmp -s "$GENERATED" "$CORE"
check "CLAUDE.md is a symlink to generated rules" test "$(readlink "$HOME/.claude/CLAUDE.md")" = "$GENERATED"
check "Pi AGENTS.md is a symlink to generated rules" test "$(readlink "$HOME/.pi/agent/AGENTS.md")" = "$GENERATED"
check "copilot-instructions.md is a regular file" test -f "$HOME/.copilot/copilot-instructions.md" -a ! -L "$HOME/.copilot/copilot-instructions.md"
check "Copilot instructions equal generated rules" cmp -s "$HOME/.copilot/copilot-instructions.md" "$GENERATED"
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

# Re-running restores a hand-edited Copilot copy from the generated rules.
echo "drift" >> "$HOME/.copilot/copilot-instructions.md"
bash "$REPO/install.sh" > "$SANDBOX/install3.log" 2>&1 || { cat "$SANDBOX/install3.log"; fail "third install.sh exits 0"; }
check "re-run refreshes Copilot rules" cmp -s "$HOME/.copilot/copilot-instructions.md" "$GENERATED"

# A private overlay and private skill are installed only from the local agent directory.
mkdir -p "$LOCAL_AGENT_DIR/skills/acme-helper"
printf '# Acme context\n- use Acme conventions\n' > "$LOCAL_AGENT_DIR/AGENTS.md"
printf '%s\n' '---' 'name: acme-helper' '---' '# Acme helper' > "$LOCAL_AGENT_DIR/skills/acme-helper/SKILL.md"
bash "$REPO/install.sh" > "$SANDBOX/install4.log" 2>&1 || { cat "$SANDBOX/install4.log"; fail "install with local overlay exits 0"; }
check "local context heading rendered" grep -q '^## Local Context$' "$GENERATED"
check "local context rendered" grep -q '^- use Acme conventions$' "$GENERATED"
check "local context copied to Copilot" grep -q '^- use Acme conventions$' "$HOME/.copilot/copilot-instructions.md"
for agent in claude copilot pi; do
  case "$agent" in
    pi) skills_dir="$HOME/.pi/agent/skills" ;;
    *)  skills_dir="$HOME/.$agent/skills" ;;
  esac
  check "$agent private skill linked" test "$(readlink "$skills_dir/acme-helper")" = "$LOCAL_AGENT_DIR/skills/acme-helper"
done

# Private agents install from the overlay agents/ dir as per-file links; opt-outs are honoured.
mkdir -p "$LOCAL_AGENT_DIR/agents"
printf '%s\n' '---' 'name: acme-agent' '---' '# Acme agent' > "$LOCAL_AGENT_DIR/agents/acme-agent.md"
printf '%s\n' '---' 'name: acme-claude' 'agents: claude' '---' '# Claude only' > "$LOCAL_AGENT_DIR/agents/acme-claude.md"
bash "$REPO/install.sh" > "$SANDBOX/install5.log" 2>&1 || { cat "$SANDBOX/install5.log"; fail "install with local agents exits 0"; }
check "claude agents dir is a real dir" test -d "$HOME/.claude/agents" -a ! -L "$HOME/.claude/agents"
check "claude private agent linked" test "$(readlink "$HOME/.claude/agents/acme-agent.md")" = "$LOCAL_AGENT_DIR/agents/acme-agent.md"
check "copilot private agent linked as .agent.md" test "$(readlink "$HOME/.copilot/agents/acme-agent.agent.md")" = "$LOCAL_AGENT_DIR/agents/acme-agent.md"
check "claude-only private agent linked for claude" test -L "$HOME/.claude/agents/acme-claude.md"
check "claude-only private agent skipped for copilot" test ! -e "$HOME/.copilot/agents/acme-claude.agent.md"
rm "$LOCAL_AGENT_DIR/agents/acme-agent.md"
bash "$REPO/install.sh" > "$SANDBOX/install6.log" 2>&1 || { cat "$SANDBOX/install6.log"; fail "install after removing agent exits 0"; }
check "removed private agent pruned (claude)" test ! -L "$HOME/.claude/agents/acme-agent.md"
check "removed private agent pruned (copilot)" test ! -L "$HOME/.copilot/agents/acme-agent.agent.md"

# A private agent cannot silently override a shared agent.
mkdir -p "$SANDBOX/shared-agents" "$SANDBOX/local-agents"
printf '# shared\n' > "$SANDBOX/shared-agents/dup.md"
printf '# private\n' > "$SANDBOX/local-agents/dup.md"
printf '# private\n' > "$SANDBOX/local-agents/unique.md"
check "private agent collision rejected" bash -c "source '$REPO/lib/links.sh'; ! assert_no_agent_collisions '$SANDBOX/shared-agents' '$SANDBOX/local-agents' 2>/dev/null"
rm "$SANDBOX/local-agents/dup.md"
check "distinct private agent accepted" bash -c "source '$REPO/lib/links.sh'; assert_no_agent_collisions '$SANDBOX/shared-agents' '$SANDBOX/local-agents'"
check "missing shared agents dir accepted" bash -c "source '$REPO/lib/links.sh'; assert_no_agent_collisions '$SANDBOX/none' '$SANDBOX/local-agents'"

# A private skill cannot silently override a shared skill.
mkdir -p "$LOCAL_AGENT_DIR/skills/docs-preview"
printf '# duplicate\n' > "$LOCAL_AGENT_DIR/skills/docs-preview/SKILL.md"
check "private skill collision rejected" bash -c "! bash '$REPO/install.sh' >/dev/null 2>&1"

# Without AGENT_FILES_LOCAL_DIR the overlay defaults to ~/.agents-local.
mkdir -p "$HOME/.agents-local/skills/default-helper"
printf '%s\n' '---' 'name: default-helper' '---' '# Default helper' > "$HOME/.agents-local/skills/default-helper/SKILL.md"
printf -- '- default overlay rule\n' > "$HOME/.agents-local/AGENTS.md"
env -u AGENT_FILES_LOCAL_DIR bash "$REPO/install.sh" > "$SANDBOX/install7.log" 2>&1 || { cat "$SANDBOX/install7.log"; fail "install with default overlay dir exits 0"; }
check "default overlay skill linked" test "$(readlink "$HOME/.copilot/skills/default-helper")" = "$HOME/.agents-local/skills/default-helper"
check "default overlay rules rendered" grep -q '^- default overlay rule$' "$HOME/.agents-local/generated/AGENTS.md"
check "default overlay rules copied to Copilot" grep -q '^- default overlay rule$' "$HOME/.copilot/copilot-instructions.md"

echo ""
if [ "$fails" -eq 0 ]; then echo "test_install: all passed"; else echo "test_install: $fails failed"; exit 1; fi
