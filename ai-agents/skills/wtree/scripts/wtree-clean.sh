#!/usr/bin/env bash
# Remove worktrees that are provably disposable. DRY RUN unless --yes is passed.
#
# A worktree is removed only when ALL gates pass:
#   1. no active agent session (copilot / claude / tmux)
#   2. working tree clean: no modified, no untracked, no branch stash
#   3. nothing would be lost: no commit that exists on no remote ref
#      (a merged PR usually has its remote branch deleted, so @{u} is unreliable;
#       override with --allow-local-commits)
#   4. >=1 PR for the branch and EVERY PR is CLOSED or MERGED
#      (--closed-only excludes MERGED; a gh failure => pr_unknown => KEEP)
#
# Usage: wtree-clean.sh [--yes] [--repo-group NAME] [--idle-mins N] [--closed-only] [--keep-branch]
#                       [--allow-local-commits]
set -uo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APPLY=0; CLOSED_ONLY=0; KEEP_BRANCH=0; ALLOW_LOCAL=0; LIST_ARGS=()
while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes) APPLY=1; shift ;;
    --closed-only) CLOSED_ONLY=1; shift ;;
    --keep-branch) KEEP_BRANCH=1; shift ;;
    --allow-local-commits) ALLOW_LOCAL=1; shift ;;
    --repo-group|--idle-mins) LIST_ARGS+=("$1" "$2"); shift 2 ;;
    --m[p]) LIST_ARGS+=(--repo-group "$2"); shift 2 ;; # deprecated hidden alias
    *) echo "wtree-clean: unknown arg $1" >&2; exit 2 ;;
  esac
done

ROWS="$("$SKILL_DIR/wtree-list.sh" ${LIST_ARGS[@]+"${LIST_ARGS[@]}"})"
[[ -z "$ROWS" ]] && { echo "No worktrees to consider."; exit 0; }

VERDICTS="$(jq -c --argjson closed_only "$CLOSED_ONLY" --argjson allow_local "$ALLOW_LOCAL" '
  . as $w
  | (if ($w.state | test("orphan")) then "not a git worktree"
     elif ($w.state | test("detached")) then "detached HEAD"
     elif ($w.state | test("pr_unknown")) then "PR state unknown (gh failed)"
     elif $w.sessions_active then "active agent session (\($w.sessions_detail))"
     elif $w.dirty > 0 then "\($w.dirty) uncommitted change(s)"
     elif $w.stashes > 0 then "\($w.stashes) stash entry(ies)"
     elif ($w.unpushed > 0 and $allow_local == 0) then "\($w.unpushed) commit(s) on no remote"
     elif $w.pr_count == 0 then "no PR for branch"
     else
       ([$w.pr_states | split(",") | .[]
         | select(. != "CLOSED" and (. != "MERGED" or $closed_only == 1))] ) as $bad
       | if ($bad | length) > 0 then "PR still open (\($w.pr_states))" else "" end
     end) as $reason
  | $w + {verdict: (if $reason == "" then "REMOVE" else "KEEP" end), reason: $reason}
' <<<"$ROWS")"

{
  printf 'VERDICT\tMP\tBRANCH\tREASON\tPATH\n'
  jq -r '[.verdict, .repo_group, (if (.branch // "") == "" then "-" else .branch end), (if .reason == "" then "all gates passed" else .reason end), .path] | @tsv' <<<"$VERDICTS"
} | column -t -s $'\t'

REMOVABLE="$(jq -c 'select(.verdict == "REMOVE")' <<<"$VERDICTS")"
COUNT="$(grep -c . <<<"$REMOVABLE" || true)"
[[ -z "$REMOVABLE" ]] && COUNT=0

echo
if [[ $COUNT -eq 0 ]]; then
  echo "Nothing to remove."
  exit 0
fi
if [[ $APPLY -eq 0 ]]; then
  echo "DRY RUN: $COUNT worktree(s) would be removed. Re-run with --yes to apply."
  exit 0
fi

while read -r row; do
  [[ -z "$row" ]] && continue
  path="$(jq -r '.path' <<<"$row")"
  branch="$(jq -r '.branch' <<<"$row")"
  main="$(jq -r '.main_repo' <<<"$row")"
  echo "removing $path"
  if ! git -C "$main" worktree remove "$path"; then
    echo "  FAILED to remove worktree, leaving branch alone" >&2
    continue
  fi
  git -C "$main" worktree prune
  if [[ $KEEP_BRANCH -eq 0 && -n "$branch" && "$branch" != "-" ]]; then
    # safe delete only: never -D, so unmerged work is never destroyed
    if git -C "$main" branch -d "$branch" 2>/dev/null; then
      echo "  deleted branch $branch"
    else
      echo "  kept branch $branch (not fully merged locally)"
    fi
  fi
  rmdir "$(dirname "$path")" 2>/dev/null || true
done <<<"$REMOVABLE"

echo "Done."
