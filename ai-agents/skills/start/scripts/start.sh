#!/usr/bin/env bash
# start.sh - one terminal tab + one Herdr session + one worktree + one coya, per task.
#
#   start.sh <slug> [repo-group] [flags]
#
# The caller (the agent) derives <slug> from the requirement; this script only
# normalizes it. Everything is idempotent: the three reachable states are
# CREATE (nothing exists), RESUME (session exists, nothing attached to it) and
# ALREADY_RUNNING (tab + session both live -> report and change nothing).
#
# The tab is a real terminal (WezTerm) tab, not a Herdr tab: Herdr refuses to
# nest, so a session can only be launched from outside any Herdr pane.
set -euo pipefail

HERDR_BIN="${HERDR_BIN:-herdr}"
WTREE_NEW="${WTREE_NEW:-$HOME/.copilot/skills/wtree/scripts/wtree-new.sh}"
HOP_TERM="${HOP_TERM:-$HOME/.copilot/skills/hop/scripts/hop-term.py}"
AGENT_KIND="${DO_AGENT_KIND:-copilot}"
AGENT_ARGS=(--autopilot --allow-all)
FALLBACK_AGENT_CMD="${START_AGENT_CMD:-${HOP_AGENT_CMD:-coya}}"
START_DIR="${DO_START_DIR:-$HOME}"
WAIT_SECS="${DO_WAIT_SECS:-30}"

usage() {
  cat >&2 <<'EOF'
usage: start.sh <slug> [repo-group] [--repo-group <name>] [--base <ref>] [--no-worktree]
              [--no-agent] [--no-focus] [--dry-run] [--status]

  <slug>          task name; also the Herdr session name and branch topic
                  (wtree prefixes it with $USER/)
  --status        report state only, create nothing
  --no-worktree   skip the wtree step (session starts in $HOME)
  --no-agent      open the session but do not start coya
  --dry-run       print the plan, touch nothing
EOF
  exit 2
}

log() { printf 'start: %s\n' "$*" >&2; }
die() { printf 'start: error: %s\n' "$*" >&2; exit 1; }
need_value() {
  [[ $# -ge 2 && -n "$2" ]] || die "$1 requires a value"
}

# ---------------------------------------------------------------- args
SLUG=""; REPO_GROUP=""; BASE=""; ACTIVATE="--activate"
WANT_WORKTREE=1; WANT_AGENT=1; DRY=0; STATUS_ONLY=0
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo-group) need_value "$@"; REPO_GROUP="$2"; shift 2 ;;
    --m[p]) need_value "$@"; REPO_GROUP="$2"; shift 2 ;; # deprecated hidden alias
    --base) need_value "$@"; BASE="$2"; shift 2 ;;
    --no-worktree) WANT_WORKTREE=0; shift ;;
    --no-agent) WANT_AGENT=0; shift ;;
    --no-focus) ACTIVATE="--no-activate"; shift ;;
    --dry-run) DRY=1; shift ;;
    --status) STATUS_ONLY=1; shift ;;
    -h|--help) usage ;;
    -*) die "unknown flag: $1" ;;
    *) if [[ -z "$SLUG" ]]; then SLUG="$1"
       elif [[ -z "$REPO_GROUP" ]]; then REPO_GROUP="$1"
       else die "unexpected argument: $1"; fi; shift ;;
  esac
done
[[ -n "$SLUG" ]] || usage

# Herdr session names, Herdr agent names and branch topics all tolerate
# [a-z][a-z0-9_-]{0,31}; normalize to that lowest common denominator.
SLUG="$(printf '%s' "$SLUG" \
  | tr '[:upper:]' '[:lower:]' \
  | sed -e 's/[^a-z0-9]\{1,\}/-/g' -e 's/^-*//' -e 's/-*$//' \
  | cut -c1-32 | sed -e 's/-*$//')"
[[ "$SLUG" =~ ^[a-z][a-z0-9_-]*$ ]] || die "slug must start with a letter: '$SLUG'"

command -v "$HERDR_BIN" >/dev/null || die "herdr not found in PATH"
command -v jq >/dev/null || die "jq not found in PATH"

# One slug, three names, all the same string modulo the separators each layer
# allows: branch `<owner>/<slug>`, worktree dir `<owner>-<slug>`, session `<slug>`.
# Sessions created before this convention may be named with the owner prefix, so
# both forms are accepted when looking one up; the bare slug is canonical for
# anything new.
OWNER="${WTREE_BRANCH_PREFIX:-${USER:-}}"
SESSION_ALT=""
[[ -n "$OWNER" && "$SLUG" != "$OWNER-"* ]] && SESSION_ALT="$OWNER-$SLUG"

session_state() { # running | stopped | absent, for $1
  # The producer's output is buffered into a variable rather than piped: jq's
  # `first(...)` short-circuits and closes the pipe, which kills `herdr` with
  # SIGPIPE and, under `set -o pipefail`, fails the whole script intermittently.
  local raw
  raw="$("$HERDR_BIN" session list --json 2>/dev/null)" || return 0
  jq -r --arg n "$1" \
    'first(.sessions[]? | select(.name == $n) | if .running then "running" else "stopped" end) // empty' \
    <<<"$raw"
}

resolve_session() { # echo "<name> <state>"; an existing session wins over the canonical one
  local st
  st="$(session_state "$SLUG")"
  if [[ -z "$st" && -n "$SESSION_ALT" ]]; then
    st="$(session_state "$SESSION_ALT")"
    [[ -n "$st" ]] && { printf '%s %s\n' "$SESSION_ALT" "$st"; return 0; }
  fi
  printf '%s %s\n' "$SLUG" "${st:-absent}"
}

# A Herdr session keeps running with no client attached, so "is there a tab for
# this task" is really "is a herdr client process attached to it". The tty of
# that process identifies the terminal tab it is sitting in.
#
# The match is anchored at end-of-command and requires a real tty: a
# session-scoped API call such as `herdr --session <name> pane list` shares the
# prefix but is a transient, tty-less process, and must not be mistaken for an
# attached client.
attached_tty() { # tty of the client attached to session $1, if any
  local raw
  raw="$(ps -eo pid,tty,command 2>/dev/null)" || return 0
  awk -v s="$1" '$2 != "??" && $0 ~ ("herdr (--session|session attach) " s "$") {print $2; exit}' <<<"$raw"
}

pane_for_tty() { # wezterm pane id whose tty matches, best effort
  local tty="$1" raw
  [[ -n "$tty" && "$tty" != "??" ]] || return 0
  command -v wezterm >/dev/null || return 0
  raw="$(wezterm cli list --format json 2>/dev/null)" || return 0
  [[ -n "$raw" ]] || return 0
  jq -r --arg t "/dev/$tty" 'first(.[]? | select(.tty_name == $t) | .pane_id) // empty' <<<"$raw"
}

read -r NAME SESSION <<<"$(resolve_session)"
TTY="$(attached_tty "$NAME")"
PANE_EXISTING="$(pane_for_tty "$TTY")"

if [[ "$STATUS_ONLY" == 1 ]]; then
  printf 'slug=%s session=%s state=%s attached_tty=%s pane=%s\n' \
    "$SLUG" "$NAME" "$SESSION" "${TTY:-none}" "${PANE_EXISTING:-none}"
  exit 0
fi

# ---------------------------------------------------------------- state 3: already live
if [[ -n "$TTY" && "$SESSION" == "running" ]]; then
  log "session '$NAME' is running and already attached in tty $TTY - nothing to do"
  printf 'ALREADY_RUNNING\tslug=%s\tsession=%s\ttty=%s\tpane=%s\n' \
    "$SLUG" "$NAME" "$TTY" "${PANE_EXISTING:-unknown}"
  exit 0
fi

run() { # echo under --dry-run, execute otherwise
  if [[ "$DRY" == 1 ]]; then printf '  would run: %s\n' "$*" >&2; return 0; fi
  "$@"
}

open_tab() { # new terminal tab at $START_DIR running `herdr --session <session>`
  local cmd
  printf -v cmd '%q --session %q' "$HERDR_BIN" "$NAME"
  if [[ "$DRY" == 1 ]]; then
    printf '  would run: %s open %s --cmd %q %s\n' "$HOP_TERM" "$START_DIR" "$cmd" "$ACTIVATE" >&2
    printf 'dry-pane\n'; return 0
  fi
  [[ -x "$HOP_TERM" ]] || die "hop-term.py not found at $HOP_TERM (hop skill is required)"
  local out pane
  out="$("$HOP_TERM" open "$START_DIR" --cmd "$cmd" "$ACTIVATE")" || die "could not open a terminal tab: $out"
  pane="$(jq -r '.pane_id // empty' <<<"$out")"
  [[ -n "$pane" ]] || die "terminal tab did not report a pane id: $out"
  printf '%s\n' "$pane"
}

wait_for_session() {
  [[ "$DRY" == 1 ]] && return 0
  local i
  for ((i = 0; i < WAIT_SECS * 2; i++)); do
    [[ "$(session_state "$NAME")" == "running" ]] && return 0
    sleep 0.5
  done
  return 1
}

# ---------------------------------------------------------------- state 2: resume
if [[ "$SESSION" != "absent" ]]; then
  log "session '$NAME' exists ($SESSION) but nothing is attached - opening a tab and resuming it"
  PANE="$(open_tab)"
  wait_for_session || log "warning: session '$NAME' did not report running within ${WAIT_SECS}s"
  printf 'RESUMED\tslug=%s\tsession=%s\tpane=%s\n' "$SLUG" "$NAME" "$PANE"
  exit 0
fi

# ---------------------------------------------------------------- state 1: create
log "new task '$SLUG' - creating worktree, tab, session and agent"

WORKTREE=""
if [[ "$WANT_WORKTREE" == 1 ]]; then
  [[ -x "$WTREE_NEW" ]] || die "wtree-new.sh not found at $WTREE_NEW (use --no-worktree to skip)"
  wt_args=("$SLUG"); [[ -n "$REPO_GROUP" ]] && wt_args+=("$REPO_GROUP"); [[ -n "$BASE" ]] && wt_args+=(--base "$BASE")
  if [[ "$DRY" == 1 ]]; then
    printf '  would run: %s %s\n' "$WTREE_NEW" "${wt_args[*]}" >&2
    WORKTREE="<worktree-path>"
  else
    WORKTREE="$("$WTREE_NEW" "${wt_args[@]}" | tail -1)"
    [[ -d "$WORKTREE" ]] || die "wtree-new.sh did not return a directory: '$WORKTREE'"
    log "worktree: $WORKTREE"
  fi
fi

PANE="$(open_tab)"
wait_for_session || die "session '$NAME' did not come up within ${WAIT_SECS}s; terminal pane is $PANE"

# The session's own panes are only reachable through its socket, so every
# command below is session-scoped.
inner_pane() {
  local raw
  raw="$("$HERDR_BIN" --session "$NAME" pane list 2>/dev/null)" || return 0
  jq -r '.result.panes[0].pane_id // empty' <<<"$raw"
}

IPANE="dry-pane"
if [[ "$DRY" != 1 ]]; then
  IPANE=""
  for _ in {1..20}; do IPANE="$(inner_pane)"; [[ -n "$IPANE" ]] && break; sleep 0.5; done
  [[ -n "$IPANE" ]] || die "session '$NAME' is running but exposes no pane"
fi

if [[ -n "$WORKTREE" ]]; then
  printf -v cd_cmd 'cd %q' "$WORKTREE"
  run "$HERDR_BIN" --session "$NAME" pane run "$IPANE" "$cd_cmd"
fi

if [[ "$WANT_AGENT" == 1 ]]; then
  if [[ "$DRY" == 1 ]]; then
    printf '  would run: %s --session %s agent start %s --kind %s --pane %s -- %s\n' \
      "$HERDR_BIN" "$NAME" "$SLUG" "$AGENT_KIND" "$IPANE" "${AGENT_ARGS[*]}" >&2
  elif ! "$HERDR_BIN" --session "$NAME" agent start "$SLUG" \
        --kind "$AGENT_KIND" --pane "$IPANE" -- "${AGENT_ARGS[@]}" >/dev/null 2>&1; then
    # agent start is strict about readiness; run the configured interactive fallback.
    log "agent start did not confirm readiness - falling back to '$FALLBACK_AGENT_CMD' in the pane"
    "$HERDR_BIN" --session "$NAME" pane run "$IPANE" "$FALLBACK_AGENT_CMD" >/dev/null || true
  fi
fi

printf 'CREATED\tslug=%s\tsession=%s\ttab_pane=%s\tsession_pane=%s\tworktree=%s\n' \
  "$SLUG" "$NAME" "$PANE" "$IPANE" "${WORKTREE:-$START_DIR}"
