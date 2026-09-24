#!/usr/bin/env bash
# Render agent rules from the personal core plus any registered company layers.
#
#   render-rules.sh          render, deploy Claude symlink, copy Copilot rules
#   render-rules.sh --check  verify generated output and Copilot copy; exit 1 on drift
#
# Layer registry: ~/.config/dotfiles/layers, one absolute layer directory per line.
# Blank lines and full-line comments are ignored. A missing registry means zero layers.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
AGENTS_DIR="$ROOT/ai-agents"
CORE="$AGENTS_DIR/AGENTS.core.md"
GENERATED_DIR="$AGENTS_DIR/.generated"
GENERATED="$GENERATED_DIR/AGENTS.md"
REGISTRY="${HOME}/.config/dotfiles/layers"
CLAUDE_DEST="${HOME}/.claude/CLAUDE.md"
COPILOT_DEST="${HOME}/.copilot/copilot-instructions.md"
# Some toolchains append a machine-generated block to the rules file in place. If such a
# block exists, it is stripped before the copy so it is not duplicated. Anchored at
# start-of-line and taking the LAST match, so a prose mention of the marker earlier in a
# file cannot be picked up by mistake. A company layer whose tooling uses a different
# marker can override this via RULES_SENTINEL.
SENTINEL="${RULES_SENTINEL:-^# Generated Instructions - DO NOT EDIT THIS SECTION MANUALLY}"

usage() {
  echo "usage: $(basename "$0") [--check]" >&2
}

trim() {
  local s="$1"
  s="${s#"${s%%[!$' \t\r\n']*}"}"
  s="${s%"${s##*[!$' \t\r\n']}"}"
  printf '%s' "$s"
}

parse_conf_value() {
  local v
  v="$(trim "$1")"
  if [[ "$v" == "\""*"\"" && "$v" == *"\"" ]]; then
    v="${v:1:${#v}-2}"
  elif [[ "$v" == "'"*"'" && "$v" == *"'" ]]; then
    v="${v:1:${#v}-2}"
  fi
  printf '%s' "$v"
}

read_layer_conf() {
  local layer_dir="$1" conf="$1/layer.conf" line key value
  LAYER_NAME="$(basename "$layer_dir")"
  LAYER_RULES="AGENTS.md"
  if [[ ! -f "$conf" ]]; then
    return 0
  fi
  while IFS= read -r line || [[ -n "$line" ]]; do
    line="$(trim "$line")"
    [[ -z "$line" || "${line:0:1}" == "#" ]] && continue
    case "$line" in
      LAYER_NAME=*|LAYER_RULES=*)
        key="${line%%=*}"
        value="${line#*=}"
        value="$(parse_conf_value "$value")"
        case "$key" in
          LAYER_NAME) LAYER_NAME="$value" ;;
          LAYER_RULES) LAYER_RULES="$value" ;;
        esac
        ;;
      *)
        echo "render-rules: unsupported line in $conf: $line" >&2
        exit 2
        ;;
    esac
  done < "$conf"
}

validate_relative_path() {
  local path="$1" layer_dir="$2"
  if [[ -z "$path" || "$path" == /* || "$path" == *../* || "$path" == ../* || "$path" == *'/..' ]]; then
    echo "render-rules: LAYER_RULES must be a safe path relative to $layer_dir: $path" >&2
    exit 2
  fi
}

emit_rules_file() {
  local src="$1" line shared_end
  [[ -f "$src" ]] || { echo "render-rules: missing rules file $src" >&2; exit 2; }
  line=$(grep -n "$SENTINEL" "$src" | tail -1 | cut -d: -f1 || true)
  if [[ -n "${line:-}" ]]; then
    # Drop the sentinel line, its rule above it, and the blank padding. Keep the
    # historical sanity check so a bad match cannot silently truncate the rules.
    shared_end=$((line - 2))
    [[ "$shared_end" -gt 20 ]] || { echo "render-rules: implausible shared portion ($shared_end lines) in $src" >&2; exit 2; }
    head -n "$shared_end" "$src" | sed -e :a -e '/^[[:space:]]*$/{$d;N;ba' -e '}'
  else
    cat "$src"
  fi
}

build_rules() {
  local layer_dir rules_file first_layer=1
  emit_rules_file "$CORE"
  [[ -f "$REGISTRY" ]] || return 0
  while IFS= read -r layer_dir || [[ -n "$layer_dir" ]]; do
    layer_dir="$(trim "$layer_dir")"
    [[ -z "$layer_dir" || "${layer_dir:0:1}" == "#" ]] && continue
    if [[ "$layer_dir" != /* || ! -d "$layer_dir" ]]; then
      echo "render-rules: registry entry is not an existing absolute directory: $layer_dir" >&2
      exit 2
    fi
    read_layer_conf "$layer_dir"
    validate_relative_path "$LAYER_RULES" "$layer_dir"
    rules_file="$layer_dir/$LAYER_RULES"
    [[ "$first_layer" -eq 1 ]] && printf '\n\n' || printf '\n'
    first_layer=0
    printf '## Layer: %s\n\n' "$LAYER_NAME"
    emit_rules_file "$rules_file"
  done < "$REGISTRY"
}

mode="${1:-}"
case "$mode" in
  ""|--check) ;;
  -h|--help) usage; exit 0 ;;
  *) usage; exit 2 ;;
esac

[[ -f "$CORE" ]] || { echo "render-rules: missing core $CORE" >&2; exit 2; }
mkdir -p "$GENERATED_DIR"
scratch="$GENERATED_DIR/AGENTS.md.$$"
trap 'rm -f "$scratch"' EXIT
build_rules > "$scratch"

if [[ "$mode" == "--check" ]]; then
  status=0
  if [[ ! -f "$GENERATED" ]]; then
    echo "render-rules: DRIFT - $GENERATED does not exist" >&2
    status=1
  elif ! diff -q "$scratch" "$GENERATED" >/dev/null; then
    echo "render-rules: DRIFT between expected render and $GENERATED" >&2
    diff -u "$GENERATED" "$scratch" | head -80 >&2
    status=1
  fi
  if [[ ! -f "$COPILOT_DEST" ]]; then
    echo "render-rules: DRIFT - $COPILOT_DEST does not exist" >&2
    status=1
  elif ! diff -q "$scratch" "$COPILOT_DEST" >/dev/null; then
    echo "render-rules: DRIFT between expected render and $COPILOT_DEST" >&2
    diff -u "$COPILOT_DEST" "$scratch" | head -80 >&2
    status=1
  fi
  if [[ "$status" -eq 0 ]]; then
    echo "render-rules: in sync"
  fi
  exit "$status"
fi

mv "$scratch" "$GENERATED"
trap - EXIT
mkdir -p "$(dirname "$CLAUDE_DEST")" "$(dirname "$COPILOT_DEST")"
if [[ -L "$CLAUDE_DEST" || -e "$CLAUDE_DEST" ]]; then rm -f "$CLAUDE_DEST"; fi
ln -s "$GENERATED" "$CLAUDE_DEST"
if [[ -L "$COPILOT_DEST" ]]; then rm -f "$COPILOT_DEST"; fi
cp "$GENERATED" "$COPILOT_DEST"
echo "render-rules: wrote $GENERATED"
echo "render-rules: linked $CLAUDE_DEST -> $GENERATED"
echo "render-rules: copied $COPILOT_DEST"
