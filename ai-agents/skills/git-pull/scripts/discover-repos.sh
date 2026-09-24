#!/usr/bin/env bash
# Discover git working trees under one or more root dirs.
# Usage: discover-repos.sh [ROOT ...]
# Defaults: DOTFILES_REPO_ROOTS, or ~/project when unset.
# Prints one absolute working-tree path per line, sorted & unique.
# Handles flat and nested repo layouts.
set -euo pipefail

roots=("$@")
if [ ${#roots[@]} -eq 0 ]; then
  roots_raw="${DOTFILES_REPO_ROOTS:-$HOME/project}"
  roots_raw="${roots_raw//:/ }"
  read -r -a roots <<< "$roots_raw"
fi

for root in "${roots[@]}"; do
  # Expand a leading ~ if passed literally.
  case "$root" in "~"/*) root="$HOME/${root#~/}";; esac
  [ -d "$root" ] || { echo "WARN: root not found: $root" >&2; continue; }
  # Find .git dirs (and gitfile-linked worktrees), prune descent into them.
  find "$root" -maxdepth 4 -name .git \( -type d -o -type f \) -prune 2>/dev/null \
    | while IFS= read -r g; do dirname "$g"; done
done | sort -u | awk '
  # Keep only top-most repo roots: drop any path nested under an already-kept one
  # (e.g. config/external sub-clones, vendored submodules, build dirs).
  { keep = 1
    for (i = 1; i <= n; i++) {
      if (index($0, kept[i] "/") == 1) { keep = 0; break }
    }
    if (keep) { kept[++n] = $0; print }
  }'
