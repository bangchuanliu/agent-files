#!/usr/bin/env bash
# Enumerate every worktree under $WTREE_ROOT and emit one JSON object per line.
#
# Usage: wtree-list.sh [--repo-group NAME] [--idle-mins N] [--no-pr]
#
# Fields: repo_group branch path state dirty stashes ahead behind upstream
#         pr_count pr_states pr_url sessions_active sessions_detail last_seen main_repo
set -uo pipefail

WTREE_ROOT="${WTREE_ROOT:-$HOME/.worktree}"
SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_GROUP_FILTER=""
IDLE_MINS=30
WANT_PR=1

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-group) REPO_GROUP_FILTER="$2"; shift 2 ;;
    --m[p]) REPO_GROUP_FILTER="$2"; shift 2 ;; # deprecated hidden alias
    --idle-mins) IDLE_MINS="$2"; shift 2 ;;
    --no-pr) WANT_PR=0; shift ;;
    *) echo "wtree-list: unknown arg $1" >&2; exit 2 ;;
  esac
done

[[ -d "$WTREE_ROOT" ]] || exit 0

# ---- collect candidate paths (exactly depth 2: <root>/<repo-group>/<branch>) ----
paths=()
for repo_group_dir in "$WTREE_ROOT"/*/; do
  [[ -d "$repo_group_dir" ]] || continue
  repo_group="$(basename "$repo_group_dir")"
  [[ -n "$REPO_GROUP_FILTER" && "$repo_group" != "$REPO_GROUP_FILTER" ]] && continue
  for wt in "$repo_group_dir"*/; do
    [[ -d "$wt" ]] || continue
    paths+=("${wt%/}")
  done
done
[[ ${#paths[@]} -eq 0 ]] && exit 0

# ---- one batched session lookup for all paths ----
SESSIONS="$(python3 "$SKILL_DIR/wtree-sessions.py" --idle-mins "$IDLE_MINS" "${paths[@]}" 2>/dev/null)"
[[ -z "$SESSIONS" ]] && SESSIONS='{}'

for path in "${paths[@]}"; do
  repo_group="$(basename "$(dirname "$path")")"
  state="ok"; branch=""; dirty=0; stashes=0; ahead=0; behind=0; unpushed=0; upstream=""
  pr_count=0; pr_states=""; pr_url=""; main_repo=""

  if ! git -C "$path" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    state="orphan"   # directory exists but is not a git worktree
  else
    branch="$(git -C "$path" rev-parse --abbrev-ref HEAD 2>/dev/null)"
    [[ "$branch" == "HEAD" ]] && state="detached"
    common="$(git -C "$path" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)"
    main_repo="$(dirname "$common")"
    dirty="$(git -C "$path" status --porcelain 2>/dev/null | grep -c . || true)"
    if [[ -n "$branch" && "$branch" != "HEAD" ]]; then
      stashes="$(git -C "$path" stash list 2>/dev/null | grep -c "on $branch:\|On $branch:" || true)"
    fi
    # commits that exist on no remote ref at all - the only true "would be lost" metric,
    # since a merged PR usually has its remote branch deleted
    unpushed="$(git -C "$path" rev-list --count HEAD --not --remotes 2>/dev/null || echo 0)"
    upstream="$(git -C "$path" rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null || true)"
    if [[ -n "$upstream" ]]; then
      counts="$(git -C "$path" rev-list --left-right --count "$upstream...HEAD" 2>/dev/null || echo "0	0")"
      behind="$(awk '{print $1}' <<<"$counts")"
      ahead="$(awk '{print $2}' <<<"$counts")"
    fi
    if [[ $WANT_PR -eq 1 && -n "$branch" && "$branch" != "HEAD" ]]; then
      prjson="$(cd "$path" && gh pr list --head "$branch" --state all --limit 20 \
                  --json number,state,url 2>/dev/null </dev/null || true)"
      if [[ -n "$prjson" && "$prjson" != "null" ]]; then
        pr_count="$(jq 'length' <<<"$prjson")"
        pr_states="$(jq -r '[.[].state] | join(",")' <<<"$prjson")"
        pr_url="$(jq -r '.[0].url // ""' <<<"$prjson")"
      else
        state="${state}${state:+,}pr_unknown"   # gh failed / unauthenticated: fail closed
      fi
    fi
  fi

  jq -nc \
    --arg repo_group "$repo_group" --arg branch "$branch" --arg path "$path" --arg state "$state" \
    --argjson dirty "${dirty:-0}" --argjson stashes "${stashes:-0}" \
    --argjson ahead "${ahead:-0}" --argjson behind "${behind:-0}" \
    --argjson unpushed "${unpushed:-0}" \
    --arg upstream "$upstream" --argjson pr_count "${pr_count:-0}" \
    --arg pr_states "$pr_states" --arg pr_url "$pr_url" --arg main_repo "$main_repo" \
    --argjson sessions "$SESSIONS" '
    {repo_group:$repo_group, branch:$branch, path:$path, state:$state, dirty:$dirty, stashes:$stashes,
     ahead:$ahead, behind:$behind, unpushed:$unpushed, upstream:$upstream, pr_count:$pr_count,
     pr_states:$pr_states, pr_url:$pr_url, main_repo:$main_repo,
     sessions_active: (($sessions[$path].active) // false),
     sessions_detail: (($sessions[$path].detail) // "proc:0 copilot:0 claude:0 tmux:0"),
     last_seen: (($sessions[$path].last_seen) // "")}'
done
