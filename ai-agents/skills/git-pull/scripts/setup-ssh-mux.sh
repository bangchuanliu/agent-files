#!/usr/bin/env bash
# Idempotently enable SSH ControlMaster multiplexing for github.com so that
# many concurrent git-over-SSH sessions (from parallel pull agents) reuse a
# single connection instead of opening N connections that GitHub rate-limits
# ("Connection reset by 140.82.112.3" / kex_exchange_identification).
set -euo pipefail

SSH_DIR="$HOME/.ssh"
CFG="$SSH_DIR/config"
SOCK_DIR="$SSH_DIR/cm"
MARKER="# >>> pull-skill github.com multiplexing >>>"
END="# <<< pull-skill github.com multiplexing <<<"

mkdir -p "$SSH_DIR" "$SOCK_DIR"
chmod 700 "$SSH_DIR" "$SOCK_DIR"
touch "$CFG"
chmod 600 "$CFG"

if grep -qF "$MARKER" "$CFG"; then
  echo "SSH multiplexing already configured."
  exit 0
fi

cat >>"$CFG" <<EOF

$MARKER
Host github.com
    ControlMaster auto
    ControlPath $SOCK_DIR/%r@%h:%p
    ControlPersist 60s
$END
EOF
echo "SSH multiplexing enabled for github.com."
