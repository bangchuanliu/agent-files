#!/usr/bin/env bash
# Shared installer helpers for per-agent adapters.

# link <target> <linkname>: idempotent symlink; backs up a real file/dir, replaces a stale link
link() {
  local target="$1" name="$2"
  if [ ! -e "$target" ]; then echo "skip: $target missing"; return; fi
  if [ -L "$name" ] && [ "$(readlink "$name")" = "$target" ]; then echo "ok:   $name"; return; fi
  if [ -L "$name" ]; then rm "$name"
  elif [ -e "$name" ]; then mv "$name" "$name.bak.$(date +%Y%m%d%H%M%S)"; echo "backup: $name"; fi
  ln -s "$target" "$name"; echo "link: $name -> $target"
}

# supports <manifest-file> <agent>: true unless an 'agents:' frontmatter line is present
# and omits <agent>. Lets a skill/agent opt out of an agent it can't run on.
supports() {
  local f="$1" agent="$2"
  [ -f "$f" ] || return 0
  grep -qiE '^agents:' "$f" || return 0          # no marker -> supported everywhere
  grep -iE '^agents:' "$f" | grep -qiw "$agent"  # marker present -> must list this agent
}

# replace_managed_block <file> <begin-marker> <end-marker> <block>
replace_managed_block() {
  local file="$1" begin="$2" end="$3" block="$4" tmp
  tmp="$file.agent-files.$$"
  awk -v b="$begin" -v e="$end" '$0==b{skip=1} !skip{print} $0==e{skip=0}' "$file" > "$tmp"
  printf '%s\n' "$block" >> "$tmp"
  mv "$tmp" "$file"
}
