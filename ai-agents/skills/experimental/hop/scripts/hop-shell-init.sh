# hop shell integration - source this from ~/.zshrc (or ~/.bashrc):
#
#   source <skill-dir>/scripts/hop-shell-init.sh
#
# A child process cannot change your shell's directory, so `hop` is a shell
# function: the script prints the destination, the function cd's to it.

if [ -n "${ZSH_VERSION:-}" ]; then
  _HOP_INIT_DIR="$(cd "$(dirname "${(%):-%x}")" && pwd)"
else
  _HOP_INIT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
fi

hop() {
  local _out _dest _script
  _script="${HOP_SCRIPT:-$_HOP_INIT_DIR/hop.sh}"
  if [ ! -x "$_script" ]; then
    echo "hop: $_script not found" >&2
    return 1
  fi
  _out="$("$_script" "$@")" || return $?
  _dest="$(printf '%s\n' "$_out" | tail -1)"
  if [ -d "$_dest" ]; then
    cd "$_dest" || return 1
  else
    printf '%s\n' "$_out"
  fi
}

# tab-complete on existing worktree directory names
if [ -n "${ZSH_VERSION:-}" ]; then
  _hop_complete() {
    local root="${WTREE_ROOT:-$HOME/.worktree}"
    reply=(${(f)"$(ls -1 "$root"/*/ 2>/dev/null)"})
  }
  compctl -K _hop_complete hop 2>/dev/null
fi
