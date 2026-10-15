#!/usr/bin/env bash
# Installer smoke test in a throwaway HOME. Never touches the real ~/.claude,
# ~/.copilot, ~/.pi, or shell rc files.
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SANDBOX="$(mktemp -d)"
CORE="$REPO/ai-agents/rules/AGENTS.md"
export WTREE_ROOT="$SANDBOX/worktrees"
LOCAL_AGENT_DIR="$SANDBOX/custom-overlay"
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

shared_skills="$(source "$REPO/lib/links.sh"; skill_dirs "$REPO/ai-agents/skills")"
check "shared skills discovered in category folders" test "$(printf '%s\n' "$shared_skills" | grep -c .)" -gt 0
while IFS= read -r d; do
  b="$(basename "$d")"
  for agent in claude copilot pi; do
    if (source "$REPO/lib/links.sh"; supports "$d/SKILL.md" "$agent"); then
      case "$agent" in
        pi) skills_dir="$HOME/.pi/agent/skills" ;;
        *)  skills_dir="$HOME/.$agent/skills" ;;
      esac
      case "$d" in
        "$REPO/ai-agents/skills/experimental/"*)
          check "$agent experimental skill $b not linked" test ! -L "$skills_dir/$b" ;;
        *)
          check "$agent skill $b linked" test "$(readlink "$skills_dir/$b")" = "$d" ;;
      esac
    fi
  done
done <<< "$shared_skills"

# Experimental skills are never installed, and a link left by an earlier install is removed.
mkdir -p "$SANDBOX/exp-skills/experimental/exp" "$SANDBOX/exp-skills/general/kept" "$SANDBOX/exp-out"
touch "$SANDBOX/exp-skills/experimental/exp/SKILL.md" "$SANDBOX/exp-skills/general/kept/SKILL.md"
ln -s "$SANDBOX/exp-skills/experimental/exp" "$SANDBOX/exp-out/exp"
(source "$REPO/lib/links.sh"; link_skills "$SANDBOX/exp-skills" "$SANDBOX/exp-out" claude) > /dev/null
check "experimental skill not linked" test ! -L "$SANDBOX/exp-out/exp"
check "non-experimental skill beside it still linked" test "$(readlink "$SANDBOX/exp-out/kept")" = "$SANDBOX/exp-skills/general/kept"
for cat_dir in "$REPO"/ai-agents/skills/*/; do
  [ -f "${cat_dir}SKILL.md" ] && continue
  check "category $(basename "$cat_dir") is not linked as a skill" test ! -e "$HOME/.copilot/skills/$(basename "$cat_dir")"
done

# Two categories holding the same skill name are rejected (agents install skills flat).
mkdir -p "$SANDBOX/dup-skills/a/same" "$SANDBOX/dup-skills/b/same"
touch "$SANDBOX/dup-skills/a/same/SKILL.md" "$SANDBOX/dup-skills/b/same/SKILL.md"
check "duplicate skill name across categories rejected" bash -c "source '$REPO/lib/links.sh'; ! (link_skills '$SANDBOX/dup-skills' '$SANDBOX/dup-out' claude) 2>/dev/null"

check "topic rules have no placeholders" bash -c "! grep -q '{' '$REPO'/ai-agents/rules/[!A]*.md"
check "worktree root created" test -d "$WTREE_ROOT"
check "rule index lists every rule file" test "$(grep -oF '{RULE_DIR}/' "$CORE" | wc -l | tr -d ' ')" = "$(find "$REPO/ai-agents/rules" -name '*.md' ! -name AGENTS.md | wc -l | tr -d ' ')"
for f in $(grep -o '{RULE_DIR}/[a-z-]*\.md' "$CORE"); do check "indexed rule file exists: $(basename "$f")" test -f "$REPO/ai-agents/rules/$(basename "$f")"; done
for rc in .zshrc .bashrc; do
  check "RULE_DIR exported once in $rc" test "$(grep -c "^export RULE_DIR=\"$REPO/ai-agents/rules\"$" "$HOME/$rc")" = 1
done
check "CLAUDE.md is a symlink to core rules" test "$(readlink "$HOME/.claude/CLAUDE.md")" = "$CORE"
check "Pi AGENTS.md is a symlink to core rules" test "$(readlink "$HOME/.pi/agent/AGENTS.md")" = "$CORE"
check "copilot-instructions.md is a symlink to core rules" test "$(readlink "$HOME/.copilot/copilot-instructions.md")" = "$CORE"
check "no generated rules dir under the local overlay" test ! -e "$LOCAL_AGENT_DIR/generated"
for f in "$REPO"/ai-agents/rules/*.md; do
  check "no Copilot instructions copy of $(basename "$f")" test ! -e "$HOME/.copilot/instructions/$(basename "$f")"
done
check "Copilot topic rules are not auto-loaded (.instructions.md)" bash -c "! ls '$HOME/.copilot/instructions/' | grep -v '^autopilot\.instructions\.md$' | grep -q '\.instructions\.md$'"
check "Copilot autopilot rules linked and auto-loaded" test "$(readlink "$HOME/.copilot/instructions/autopilot.instructions.md")" = "$REPO/.copilot/autopilot.md"
check "shared skill-auditor agent linked for Copilot" test "$(readlink "$HOME/.copilot/agents/skill-auditor.agent.md")" = "$REPO/ai-agents/agents/skill-auditor.md"
check "shared skill-auditor agent linked for Claude" test "$(readlink "$HOME/.claude/agents/skill-auditor.md")" = "$REPO/ai-agents/agents/skill-auditor.md"
check "cla alias block once in .zshrc" test "$(grep -c '>>> agent-files cla alias >>>' "$HOME/.zshrc")" = 1

# Foreign links survive, dangling ones are pruned, and re-runs are idempotent.
foreign="$SANDBOX/foreign-skill"; mkdir -p "$foreign"
ln -s "$foreign" "$HOME/.copilot/skills/foreign"
ln -s "$SANDBOX/does-not-exist" "$HOME/.copilot/skills/gone"
bash "$REPO/install.sh" > "$SANDBOX/install2.log" 2>&1 || { cat "$SANDBOX/install2.log"; fail "second install.sh exits 0"; }
check "foreign skill link kept" test -L "$HOME/.copilot/skills/foreign"
check "dangling skill link pruned" test ! -L "$HOME/.copilot/skills/gone"
check "alias blocks not duplicated on re-run" test "$(grep -c '>>> agent-files coya alias >>>' "$HOME/.bashrc")" = 1
check "RULE_DIR block not duplicated on re-run" test "$(grep -c '>>> agent-files RULE_DIR env >>>' "$HOME/.zshrc")" = 1
check "coy alias block once, without autopilot" test "$(grep -c "^alias coy='copilot --allow-all'$" "$HOME/.bashrc")" = 1
check "re-run makes no new links" bash -c "! grep -q '^link: .*/skills/' '$SANDBOX/install2.log'"

# Re-running retires topic links and rendered copies left by earlier installs.
ln -s "$REPO/ai-agents/rules/thinking.md" "$HOME/.copilot/instructions/thinking.md"
echo old > "$HOME/.copilot/instructions/AGENTS.md"
mkdir -p "$LOCAL_AGENT_DIR/generated"
echo old > "$LOCAL_AGENT_DIR/generated/copilot-instructions.md"
echo old > "$LOCAL_AGENT_DIR/generated/AGENTS.md"
bash "$REPO/install.sh" > "$SANDBOX/install3b.log" 2>&1 || { cat "$SANDBOX/install3b.log"; fail "migration install.sh exits 0"; }
check "stale Copilot topic link removed" test ! -e "$HOME/.copilot/instructions/thinking.md"
check "stale Copilot render removed" test ! -e "$HOME/.copilot/instructions/AGENTS.md"
check "stale ~/.agents-local generated dir removed" test ! -e "$LOCAL_AGENT_DIR/generated"

# A private overlay and private skill are installed only from the local agent directory.
mkdir -p "$LOCAL_AGENT_DIR/skills/acme-helper"
printf '# Acme context\n- use Acme conventions\n' > "$LOCAL_AGENT_DIR/AGENTS.md"
printf '%s\n' '---' 'name: acme-helper' '---' '# Acme helper' > "$LOCAL_AGENT_DIR/skills/acme-helper/SKILL.md"
bash "$REPO/install.sh" > "$SANDBOX/install4.log" 2>&1 || { cat "$SANDBOX/install4.log"; fail "install with local overlay exits 0"; }
check "local overlay leaves core rules untouched" bash -c "! grep -q 'Acme' '$CORE'"
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
mkdir -p "$LOCAL_AGENT_DIR/skills/slack-msg"
printf '# duplicate\n' > "$LOCAL_AGENT_DIR/skills/slack-msg/SKILL.md"
check "private skill collision rejected" bash -c "! bash '$REPO/install.sh' >/dev/null 2>&1"

# Without AGENT_FILES_LOCAL_DIR the overlay defaults to ~/.agents-local.
mkdir -p "$HOME/.agents-local/skills/default-helper"
printf '%s\n' '---' 'name: default-helper' '---' '# Default helper' > "$HOME/.agents-local/skills/default-helper/SKILL.md"
printf -- '- default overlay rule\n' > "$HOME/.agents-local/AGENTS.md"
env -u AGENT_FILES_LOCAL_DIR bash "$REPO/install.sh" > "$SANDBOX/install7.log" 2>&1 || { cat "$SANDBOX/install7.log"; fail "install with default overlay dir exits 0"; }
check "default overlay skill linked" test "$(readlink "$HOME/.copilot/skills/default-helper")" = "$HOME/.agents-local/skills/default-helper"

echo ""
if [ "$fails" -eq 0 ]; then echo "test_install: all passed"; else echo "test_install: $fails failed"; exit 1; fi
