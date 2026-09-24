#!/usr/bin/env bash
# Pull latest for each given git working tree, applying safe rules.
# Usage: pull-repos.sh REPO_PATH [REPO_PATH ...]
#
# Rules (priority order, per repo):
#   1. DIRTY            - local changes (git status --porcelain non-empty):
#                         DO NOT pull/fetch. Report changed files.
#   2. SKIPPED          - no upstream OR upstream gone (deleted on remote):
#                         git fetch --prune only. Never switch branches.
#   3. git pull --ff-only (with retry/backoff on SSH throttle) ->
#                         UPDATED | UP-TO-DATE | FAILED
#
# Output: one machine-readable line per repo:
#   STATUS<TAB>path<TAB>detail
# STATUS in: UPDATED UP-TO-DATE DIRTY SKIPPED FAILED
# For DIRTY, detail is a ';'-joined list of "XY file" porcelain entries.
set -uo pipefail

TAB=$'\t'

emit() { printf '%s\t%s\t%s\n' "$1" "$2" "${3:-}"; }

is_throttle() {
  printf '%s' "$1" | grep -qiE 'connection reset|kex_exchange_identification|connection closed|timed out'
}

pull_one() {
  local repo="$1"
  case "$repo" in "~"/*) repo="$HOME/${repo#~/}";; esac

  if ! git -C "$repo" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    emit "FAILED" "$repo" "not a git work tree"
    return
  fi

  # Rule 1: local changes -> never touch.
  local porcelain
  porcelain=$(git -C "$repo" status --porcelain 2>/dev/null)
  if [ -n "$porcelain" ]; then
    local files
    files=$(printf '%s\n' "$porcelain" | sed 's/^/  /' | paste -sd';' -)
    emit "DIRTY" "$repo" "$files"
    return
  fi

  # Rule 2: no upstream / upstream gone.
  local upstream
  if ! upstream=$(git -C "$repo" rev-parse --abbrev-ref --symbolic-full-name '@{u}' 2>/dev/null); then
    git -C "$repo" fetch --prune --quiet origin 2>/dev/null || true
    local cur merge_ref
    cur=$(git -C "$repo" rev-parse --abbrev-ref HEAD 2>/dev/null)
    merge_ref=$(git -C "$repo" config --get "branch.$cur.merge" 2>/dev/null || true)
    if [ -n "$merge_ref" ]; then
      emit "SKIPPED" "$repo" "upstream ${merge_ref#refs/heads/} deleted/unreachable on remote"
    else
      emit "SKIPPED" "$repo" "no upstream (local-only branch '$cur')"
    fi
    return
  fi
  # Detect a tracking branch whose remote ref is gone.
  if git -C "$repo" status -sb 2>/dev/null | head -1 | grep -q '\[gone\]'; then
    git -C "$repo" fetch --prune --quiet origin 2>/dev/null || true
    emit "SKIPPED" "$repo" "upstream $upstream deleted on remote ([gone])"
    return
  fi

  # Rule 3: ff-only pull with retry/backoff on throttle.
  local out rc attempt
  for attempt in 1 2 3; do
    out=$(git -C "$repo" pull --ff-only 2>&1)
    rc=$?
    if [ $rc -eq 0 ]; then
      if printf '%s' "$out" | grep -qi 'Already up to date'; then
        emit "UP-TO-DATE" "$repo" ""
      else
        emit "UPDATED" "$repo" "$(printf '%s' "$out" | tail -1)"
      fi
      return
    fi
    if is_throttle "$out"; then
      sleep $((attempt * 3))
      continue
    fi
    emit "FAILED" "$repo" "$(printf '%s' "$out" | tr '\n' ' ' | sed 's/  */ /g' | cut -c1-200)"
    return
  done
  emit "FAILED" "$repo" "throttled after 3 attempts (SSH rate-limit)"
}

if [ $# -eq 0 ]; then
  echo "usage: pull-repos.sh REPO_PATH [REPO_PATH ...]" >&2
  exit 2
fi

for r in "$@"; do
  pull_one "$r"
done
