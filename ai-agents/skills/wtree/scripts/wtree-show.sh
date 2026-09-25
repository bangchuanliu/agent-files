#!/usr/bin/env bash
# Print a table of every worktree under $WTREE_ROOT plus its agent sessions.
#
# Usage: wtree-show.sh [--repo-group NAME] [--idle-mins N] [--no-pr] [--json]
set -euo pipefail

SKILL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WTREE_ROOT="${WTREE_ROOT:-$HOME/.worktree}"
JSON=0; ARGS=()
for a in "$@"; do
  if [[ "$a" == "--json" ]]; then JSON=1; else ARGS+=("$a"); fi
done

ROWS="$("$SKILL_DIR/wtree-list.sh" ${ARGS[@]+"${ARGS[@]}"})"

if [[ $JSON -eq 1 ]]; then
  jq -s '.' <<<"$ROWS"
  exit 0
fi

if [[ -z "$ROWS" ]]; then
  echo "No worktrees under $WTREE_ROOT"
else
  {
    printf 'GROUP\tBRANCH\tGIT\tAHEAD/BEHIND\tUNPUSHED\tPR\tSESSIONS\tLAST SEEN\tPATH\n'
    jq -r '
      def git_col:
        if .state | test("orphan") then "ORPHAN"
        elif .state | test("detached") then "DETACHED"
        elif .dirty > 0 then "dirty(\(.dirty))"
        elif .stashes > 0 then "stash(\(.stashes))"
        else "clean" end;
      def pr_col:
        if .state | test("pr_unknown") then "unknown"
        elif .pr_count == 0 then "none"
        else .pr_states end;
      [.repo_group, (if (.branch // "") == "" then "-" else .branch end), git_col,
       "\(.ahead)/\(.behind)",
       "\(.unpushed)",
       pr_col,
       (if .sessions_active then "ACTIVE \(.sessions_detail)" else "-" end),
       (if .last_seen == "" then "-" else .last_seen end),
       .path] | @tsv' <<<"$ROWS"
  } | column -t -s $'\t'
fi

# ---- registered-but-missing worktrees (prunable) ----
mapfile -t MAINS < <(jq -r 'select(.main_repo != "") | .main_repo' <<<"$ROWS" | sort -u)
missing=()
for main in "${MAINS[@]}"; do
  while read -r wt; do
    [[ "$wt" == "$WTREE_ROOT"/* ]] || continue
    [[ -d "$wt" ]] || missing+=("$wt")
  done < <(git -C "$main" worktree list --porcelain 2>/dev/null | awk '/^worktree /{print $2}')
done
if [[ ${#missing[@]} -gt 0 ]]; then
  echo
  echo "Registered but missing on disk (run 'git worktree prune' in the main clone):"
  printf '  %s\n' "${missing[@]}"
fi
