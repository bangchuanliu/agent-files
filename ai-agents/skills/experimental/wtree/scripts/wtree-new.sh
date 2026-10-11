#!/usr/bin/env bash
# Create (or reuse) a git worktree at ~/.worktree/<repo-group>/<branch-with-slashes-flattened>.
#
# Usage: wtree-new.sh <branch> [repo-group] [--base <ref>] [--no-prefix]
# Prints the worktree path as the LAST line, so: cd "$(wtree-new.sh my-branch | tail -1)"
set -euo pipefail

WTREE_ROOT="${WTREE_ROOT:-$HOME/.worktree}"
repo_roots_raw="${DOTFILES_REPO_ROOTS:-$HOME/project}"
repo_roots_raw="${repo_roots_raw//:/ }"
read -r -a REPO_ROOTS <<< "$repo_roots_raw"

BRANCH=""; REPO_GROUP=""; BASE=""; FROM_CURRENT=0; PREFIX=1
need_value() {
  [[ $# -ge 2 && -n "$2" ]] || { echo "wtree-new: $1 requires a value" >&2; exit 2; }
}
while [[ $# -gt 0 ]]; do
  case "$1" in
    --base) need_value "$@"; BASE="$2"; shift 2 ;;
    --repo-group) need_value "$@"; REPO_GROUP="$2"; shift 2 ;;
    --from-current) FROM_CURRENT=1; shift ;;
    --no-prefix) PREFIX=0; shift ;;
    -*) echo "wtree-new: unknown flag $1" >&2; exit 2 ;;
    *) if [[ -z "$BRANCH" ]]; then BRANCH="$1"; elif [[ -z "$REPO_GROUP" ]]; then REPO_GROUP="$1"; fi; shift ;;
  esac
done
[[ -n "$BRANCH" ]] || { echo "usage: wtree-new.sh <branch> [repo-group] [--base <ref>] [--from-current] [--no-prefix]" >&2; exit 2; }

# The current checkout is never consulted: a new worktree is always cut from the
# remote default branch, so it works from a feature branch or a dirty tree.
if [[ $FROM_CURRENT -eq 1 ]]; then
  [[ -n "$BASE" ]] && { echo "wtree-new: --base and --from-current are mutually exclusive" >&2; exit 2; }
  BASE="$(git rev-parse HEAD 2>/dev/null)" || { echo "wtree-new: --from-current outside a git repo" >&2; exit 1; }
fi

find_repo_group() {
  local group="$1" root cand
  for root in "${REPO_ROOTS[@]}"; do
    [[ -n "$root" ]] || continue
    case "$root" in "~"/*) root="$HOME/${root#~/}";; esac
    for cand in "$root/$group" "$root"/*/"$group"; do
      [[ -d "$cand/.git" ]] && { (cd "$cand" && pwd); return 0; }
    done
  done
  return 1
}

# ---- resolve the main clone ----
if [[ -n "$REPO_GROUP" ]]; then
  MAIN="$(find_repo_group "$REPO_GROUP")" || {
    echo "wtree-new: no git repo named '$REPO_GROUP' under configured repo roots" >&2
    exit 1
  }
else
  MAIN="$(git rev-parse --show-toplevel 2>/dev/null || true)"
  [[ -n "$MAIN" ]] || { echo "wtree-new: not in a git repo; pass the repo group explicitly" >&2; exit 1; }
  # if invoked from inside a worktree, hop back to the main clone
  common="$(git -C "$MAIN" rev-parse --path-format=absolute --git-common-dir)"
  MAIN="$(dirname "$common")"
  REPO_GROUP="$(basename "$MAIN")"
fi

# ---- apply the <user>/<topic> branch convention ----
# A bare name becomes "$USER/<name>". An existing local or remote ref wins as-is,
# so `wtree-new.sh master` can never become banliu/master. Opt out with --no-prefix,
# override the owner with WTREE_BRANCH_PREFIX.
if [[ $PREFIX -eq 1 && "$BRANCH" != */* ]]; then
  owner="${WTREE_BRANCH_PREFIX:-${USER:-}}"
  if [[ -n "$owner" ]] \
     && ! git -C "$MAIN" show-ref --verify --quiet "refs/heads/$BRANCH" \
     && ! git -C "$MAIN" show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
    BRANCH="$owner/$BRANCH"
    echo "wtree-new: using branch $BRANCH (<user>/<topic> convention; --no-prefix to opt out)" >&2
  fi
fi

SLUG="${BRANCH//\//-}"
DEST="$WTREE_ROOT/$REPO_GROUP/$SLUG"

if git -C "$DEST" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "wtree-new: reusing existing worktree" >&2
  echo "$DEST"; exit 0
fi
[[ -e "$DEST" ]] && { echo "wtree-new: $DEST exists but is not a worktree" >&2; exit 1; }

mkdir -p "$(dirname "$DEST")"
git -C "$MAIN" fetch --prune origin >&2 || echo "wtree-new: fetch failed, continuing offline" >&2

if git -C "$MAIN" show-ref --verify --quiet "refs/heads/$BRANCH"; then
  # branch already exists locally; if another worktree has it checked out, say so plainly
  existing="$(git -C "$MAIN" worktree list --porcelain | awk -v b="refs/heads/$BRANCH" '
    /^worktree /{wt=$2} /^branch /{if ($2 == b) print wt}')"
  if [[ -n "$existing" ]]; then
    echo "wtree-new: branch $BRANCH is already checked out at $existing" >&2
    echo "$existing"; exit 0
  fi
  git -C "$MAIN" worktree add "$DEST" "$BRANCH" >&2
elif git -C "$MAIN" show-ref --verify --quiet "refs/remotes/origin/$BRANCH"; then
  git -C "$MAIN" worktree add --track -b "$BRANCH" "$DEST" "origin/$BRANCH" >&2
else
  if [[ -z "$BASE" ]]; then
    # remote default branch, never the current checkout
    default="$(git -C "$MAIN" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null | sed 's|^origin/||')"
    for cand in "origin/$default" origin/master origin/main; do
      [[ "$cand" == "origin/" ]] && continue
      if git -C "$MAIN" rev-parse --verify --quiet "${cand}^{commit}" >/dev/null 2>&1; then
        BASE="$cand"; break
      fi
    done
    if [[ -z "$BASE" ]]; then
      echo "wtree-new: cannot resolve origin's default branch; pass --base <ref> (or --from-current)" >&2
      exit 1
    fi
  fi
  echo "wtree-new: branching $BRANCH from $BASE" >&2
  git -C "$MAIN" worktree add -b "$BRANCH" "$DEST" "$BASE" >&2
fi

echo "$DEST"
