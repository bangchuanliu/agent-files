#!/usr/bin/env bash
# Shared installer helpers for the per-agent adapters (.claude/install.sh, .copilot/install.sh).
# Sourced, not executed. Every function is idempotent so installers can be re-run safely.

# link <target> <linkname>: symlink linkname -> target. Leaves a correct link alone, replaces a
# stale link, and backs up a real file/dir before replacing it.
link() {
  local target="$1" name="$2"
  if [ ! -e "$target" ]; then echo "skip: $target missing"; return 0; fi
  if [ -L "$name" ] && [ "$(readlink "$name")" = "$target" ]; then echo "ok:   $name"; return 0; fi
  if [ -L "$name" ]; then rm "$name"
  elif [ -e "$name" ]; then mv "$name" "$name.bak.$(date +%Y%m%d%H%M%S)"; echo "backup: $name"; fi
  ln -s "$target" "$name"; echo "link: $name -> $target"
}

# supports <manifest-file> <agent>: true unless an 'agents:' frontmatter line is present and
# omits <agent>. Lets a skill/agent opt out of an agent it can't run on.
supports() {
  local f="$1" agent="$2"
  [ -f "$f" ] || return 0
  grep -qiE '^agents:' "$f" || return 0
  grep -iE '^agents:' "$f" | grep -qiw "$agent"
}

# unlink_if_symlink <path>: remove path only when it is a symlink (never a real file/dir).
unlink_if_symlink() {
  if [ -L "$1" ]; then rm "$1"; fi
}

# prune_dangling <dir>: remove broken symlinks in dir (a source was renamed/deleted). Live links
# owned by other repos are left untouched.
prune_dangling() {
  local l
  for l in "$1"/* "$1"/.[!.]*; do
    if [ -L "$l" ] && [ ! -e "$l" ]; then rm "$l"; echo "prune: $l (dangling)"; fi
  done
}

# link_skills <src-skills-dir> <merge-dir> <agent>: one symlink per skill directory into a real
# merge directory, so other repos can add their own skills alongside. Skills whose SKILL.md
# opts out of <agent> are unlinked. Dangling links are pruned afterwards.
link_skills() {
  local src="$1" merged="$2" agent="$3" d b
  unlink_if_symlink "$merged"   # retire legacy whole-dir symlink
  mkdir -p "$merged"
  for d in "$src"/*/; do
    [ -f "${d}SKILL.md" ] || continue
    b="$(basename "$d")"
    if supports "${d}SKILL.md" "$agent"; then
      link "${d%/}" "$merged/$b"
    else
      unlink_if_symlink "$merged/$b"
      echo "skip: $b (not for $agent)"
    fi
  done
  prune_dangling "$merged"
}

# assert_no_skill_collisions <shared-skills> <local-skills>: fail rather than silently choosing
# one source when a private skill uses the same name as a shared skill.
assert_no_skill_collisions() {
  local shared="$1" local_skills="$2" d b
  [ -d "$local_skills" ] || return 0
  for d in "$local_skills"/*/; do
    [ -f "${d}SKILL.md" ] || continue
    b="$(basename "$d")"
    if [ -f "$shared/$b/SKILL.md" ]; then
      echo "skill collision: $b exists in both $shared and $local_skills" >&2
      return 2
    fi
  done
}

# link_agents <src-agents-dir> <merge-dir> <agent> <suffix>: one symlink per <name>.md agent file
# into a real merge directory as <name><suffix> (Copilot needs ".agent.md"). Agents whose
# frontmatter opts out of <agent> are unlinked. A missing source dir is a no-op.
link_agents() {
  local src="$1" merged="$2" agent="$3" suffix="$4" f base
  unlink_if_symlink "$merged"   # retire legacy whole-dir symlink
  mkdir -p "$merged"
  [ -d "$src" ] || return 0
  for f in "$src"/*.md; do
    [ -e "$f" ] || continue
    base="$(basename "$f" .md)"
    if supports "$f" "$agent"; then
      link "$f" "$merged/$base$suffix"
    else
      unlink_if_symlink "$merged/$base$suffix"
      echo "skip: $base (not for $agent)"
    fi
  done
}

# assert_no_agent_collisions <shared-agents> <local-agents>: fail when a private agent uses the
# same file name as a shared agent.
assert_no_agent_collisions() {
  local shared="$1" local_agents="$2" f b
  [ -d "$local_agents" ] || return 0
  for f in "$local_agents"/*.md; do
    [ -e "$f" ] || continue
    b="$(basename "$f")"
    if [ -f "$shared/$b" ]; then
      echo "agent collision: $b exists in both $shared and $local_agents" >&2
      return 2
    fi
  done
}

# replace_managed_block <file> <begin-marker> <end-marker> <block>: replace the lines between
# (and including) the markers with block, appended at the end of file.
replace_managed_block() {
  local file="$1" begin="$2" end="$3" block="$4" tmp
  tmp="$file.agent-files.$$"
  awk -v b="$begin" -v e="$end" '$0==b{skip=1} !skip{print} $0==e{skip=0}' "$file" > "$tmp"
  printf '%s\n' "$block" >> "$tmp"
  mv "$tmp" "$file"
}

# install_shell_alias <name> <command> <comment>: own a marker-delimited alias block in
# ~/.zshrc and ~/.bashrc, replacing it in place on re-run.
install_shell_alias() {
  local name="$1" cmd="$2" comment="$3" rc begin end block
  begin="# >>> agent-files $name alias >>>"
  end="# <<< agent-files $name alias <<<"
  case "$cmd" in *"'"*) echo "install_shell_alias: command must not contain a single quote" >&2; return 2 ;; esac
  block="$(printf "%s\n# %s\nalias %s='%s'\n%s" "$begin" "$comment" "$name" "$cmd" "$end")"
  for rc in "$HOME/.zshrc" "$HOME/.bashrc"; do
    touch "$rc"
    if grep -qF "$begin" "$rc"; then
      replace_managed_block "$rc" "$begin" "$end" "$block"
      echo "update: $name alias block in $rc"
    else
      printf '\n%s\n' "$block" >> "$rc"
      echo "add:  $name alias block in $rc"
    fi
  done
}
