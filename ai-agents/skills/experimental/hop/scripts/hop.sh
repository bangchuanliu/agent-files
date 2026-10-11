#!/usr/bin/env bash
# Resolve a branch / worktree / repo name to a directory, then find or open the
# terminal tab sitting in it.
#
# Usage: hop.sh <branch-or-dir> [--focus] [--no-focus] [--new-tab] [--no-term] [--repo-group NAME]
#
# Prints the destination absolute path as the LAST line of stdout; everything
# else goes to stderr. Pair with the shell function in hop-shell-init.sh:
#   hop() { local d; d="$(hop.sh "$@" | tail -1)" && [ -d "$d" ] && cd "$d"; }
#
# hop never modifies git state. Creating a task stack (worktree + Herdr
# session + agent) is the `start` skill's job; cleaning one up is `wtree clean`.
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WTREE_ROOT="${WTREE_ROOT:-$HOME/.worktree}"

# Roots searched for a plain-name target, in order. DOTFILES_REPO_ROOTS accepts
# colon- or space-separated paths and defaults to $HOME/project.
repo_roots_raw="${DOTFILES_REPO_ROOTS:-$HOME/project}"
repo_roots_raw="${repo_roots_raw//:/ }"
read -r -a REPO_ROOTS <<< "$repo_roots_raw"

TARGET=""; REPO_GROUP_HINT=""
TERM_MODE="on"; FOCUS=0; FORCE_NEW=0; START_MODE="agent"; LAUNCH_CMD=""
# Whether a NEWLY opened tab grabs focus. --focus above is about jumping to an
# EXISTING tab; this is about not being yanked when one is created for you.
ACTIVATE_NEW="--activate"

# Command used to start the agent in a new tab. Defaults to the installer's
# alias for whichever agent CLI is on PATH (`coya` for Copilot CLI, `cla` for
# Claude Code); it runs in an interactive shell that sources your rc file.
# Override with HOP_AGENT_CMD.
if [[ -n "${HOP_AGENT_CMD:-}" ]]; then AGENT_CMD="$HOP_AGENT_CMD"
elif command -v copilot >/dev/null 2>&1; then AGENT_CMD="coya"
else AGENT_CMD="cla"; fi
need_value() {
  [[ $# -ge 2 && -n "$2" ]] || { echo "hop: $1 requires a value" >&2; exit 2; }
}
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-group) need_value "$@"; REPO_GROUP_HINT="$2"; shift 2 ;;
    --no-term) TERM_MODE="off"; shift ;;
    --focus) FOCUS=1; shift ;;
    --no-focus) ACTIVATE_NEW="--no-activate"; shift ;;
    --new-tab) FORCE_NEW=1; shift ;;
    --tmux) START_MODE="tmux"; shift ;;
    --no-agent) START_MODE="none"; shift ;;
    --cmd) need_value "$@"; LAUNCH_CMD="$2"; shift 2 ;;
    -*) echo "hop: unknown flag $1" >&2; exit 2 ;;
    *) [[ -z "$TARGET" ]] && TARGET="$1"; shift ;;
  esac
done

say() { echo "hop: $*" >&2; }

[[ -n "$TARGET" ]] || { echo "usage: hop.sh <branch-or-dir> [--focus|--no-focus] [--new-tab] [--no-term] [--repo-group NAME]" >&2; exit 2; }

SRC="$(git rev-parse --show-toplevel 2>/dev/null || true)"

# ----------------------------------------------------------- resolve target
DEST=""

# 1. an explicit path
if [[ -d "$TARGET" ]]; then
  DEST="$(cd "$TARGET" && pwd)"
fi

# 2. an existing worktree whose CHECKED-OUT BRANCH matches (never parse the path slug)
if [[ -z "$DEST" ]]; then
  for wt in "$WTREE_ROOT"/*/*; do
    [[ -d "$wt" ]] || continue
    [[ -n "$REPO_GROUP_HINT" && "$(basename "$(dirname "$wt")")" != "$REPO_GROUP_HINT" ]] && continue
    b="$(git -C "$wt" rev-parse --abbrev-ref HEAD 2>/dev/null)" || continue
    if [[ "$b" == "$TARGET" || "$b" == */"$TARGET" ]]; then DEST="$wt"; break; fi
  done
fi

# 3. a worktree directory name under the root
if [[ -z "$DEST" ]]; then
  for wt in "$WTREE_ROOT"/*/"$TARGET"; do
    [[ -d "$wt" ]] && { DEST="$wt"; break; }
  done
fi

# 4. a repo checkout under any configured root
if [[ -z "$DEST" ]]; then
  for root in "${REPO_ROOTS[@]}"; do
    case "$root" in "~"/*) root="$HOME/${root#~/}";; esac
    [[ -d "$root/$TARGET" ]] && { DEST="$root/$TARGET"; break; }
  done
fi
# 4b. one level deeper, for nested layouts like <root>/<group>/<repo>
if [[ -z "$DEST" ]]; then
  for root in "${REPO_ROOTS[@]}"; do
    case "$root" in "~"/*) root="$HOME/${root#~/}";; esac
    for cand in "$root"/*/"$TARGET"; do
      [[ -d "$cand/.git" ]] && { DEST="$cand"; break 2; }
    done
  done
fi

if [[ -z "$DEST" || ! -d "$DEST" ]]; then
  say "ERROR: cannot resolve '$TARGET' to a worktree, repo checkout or directory."
  say "       'wtree show' lists what exists; 'start $TARGET' starts a new one."
  exit 1
fi
DEST="$(cd "$DEST" && pwd)"

if [[ "$DEST" == "${SRC:-}" ]]; then
  say "already in $(basename "$DEST")"
  echo "$DEST"; exit 0
fi

# ------------------------------------------------------------------- report
if git -C "$DEST" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  say "-> $(git -C "$DEST" rev-parse --abbrev-ref HEAD) in $DEST"
  changed="$(git -C "$DEST" status --porcelain | grep -c . || true)"
  [[ "$changed" -gt 0 ]] && say "   $changed uncommitted change(s) waiting for you"
else
  say "-> $DEST (not a git repo)"
fi

# ------------------------------------------------------- terminal tab phase
# An agent cannot cd the user's shell, so hop operates on terminal tabs:
# reuse a tab already sitting in the destination, otherwise open one there.
if [[ "$TERM_MODE" != "off" ]]; then
  TERMJSON="$(python3 "$SKILL_DIR/hop-term.py" find "$DEST" 2>/dev/null || echo '{}')"
  TABCOUNT="$(jq -r '(.tabs // []) | length' <<<"$TERMJSON" 2>/dev/null || echo 0)"
  [[ -z "$TABCOUNT" || "$TABCOUNT" == "null" ]] && TABCOUNT=0

  if [[ "$TABCOUNT" -gt 0 ]]; then
    say "found $TABCOUNT terminal tab(s) already in $(basename "$DEST"):"
    while IFS= read -r line; do
      [[ -n "$line" ]] && say "   $line"
    done < <(jq -r '.tabs[] | "pane \(.pane_id)  \(if .has_agent then "AGENT RUNNING (" + ([.agents[] | .comm + (if .status then ":" + .status else "" end)] | join(",")) + ")" else "no agent" end)\(if .in_herdr then " [herdr:" + .herdr_session + "]" else "" end)\(if .in_tmux then " [tmux]" else "" end)  \(.title)"' <<<"$TERMJSON" 2>/dev/null)

    if [[ $FORCE_NEW -eq 0 ]]; then
      if [[ $FOCUS -eq 1 ]]; then
        # prefer a tab that already has an agent running
        pane="$(jq -r '([.tabs[] | select(.has_agent)] + .tabs) | .[0].pane_id' <<<"$TERMJSON" 2>/dev/null)"
        if [[ -n "$pane" && "$pane" != "null" ]]; then
          python3 "$SKILL_DIR/hop-term.py" focus "$pane" >/dev/null 2>&1 \
            && say "focused pane $pane"
        fi
      else
        say "not switching - pass --focus to jump there, or --new-tab to open another"
      fi
      echo "$DEST"; exit 0
    fi
  fi

  # No tab there yet (or --new-tab was asked for).
  #
  # A detached Herdr session is NOT an empty destination: the tab is gone but
  # the session, its cwd and its agent are all still alive. Starting a bare
  # agent here would create a second agent on the same worktree and strand the
  # first, so resume the session instead. `start` owns that path.
  launch="$LAUNCH_CMD"
  if [[ -z "$launch" && "$START_MODE" == "agent" ]]; then
    hsession="$(python3 "$SKILL_DIR/hop-term.py" herdr-session-for "$DEST" 2>/dev/null)"
    if [[ -n "$hsession" ]]; then
      say "no tab, but Herdr session '$hsession' is still alive here - resuming it"
      say "      (its agent and cwd survived the tab closing; not starting a second agent)"
      printf -v launch '%q --session %q' "${HERDR_BIN:-herdr}" "$hsession"
    fi
  fi
  if [[ -z "$launch" ]]; then
    case "$START_MODE" in
      agent)   launch="$AGENT_CMD" ;;
      tmux)    printf -v launch 'tmux new-session -A -s %q' "$(basename "$DEST")" ;;
      none)    launch="" ;;
    esac
  fi
  out="$(python3 "$SKILL_DIR/hop-term.py" open "$DEST" ${launch:+--cmd "$launch"} "$ACTIVATE_NEW" 2>/dev/null || echo '{}')"
  if [[ "$(jq -r '.ok // false' <<<"$out" 2>/dev/null)" == "true" ]]; then
    say "opened a new tab (pane $(jq -r '.pane_id' <<<"$out")) in $DEST${launch:+, running: $launch}"
  else
    say "WARNING: could not open a terminal tab: $(jq -r '.reason // "unknown"' <<<"$out" 2>/dev/null)"
    say "         cd there yourself:  cd $DEST"
  fi
fi

echo "$DEST"
