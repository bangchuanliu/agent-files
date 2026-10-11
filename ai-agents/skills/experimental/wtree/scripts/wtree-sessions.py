#!/usr/bin/env python3
"""Report active agent sessions (Copilot CLI, Claude Code, tmux) per worktree path.

Usage: wtree-sessions.py [--idle-mins N] PATH [PATH ...]
Output: JSON object mapping path -> {active, copilot, claude, tmux, detail, last_seen}
"""
import json
import os
import subprocess
import sqlite3
import sys
import time
from datetime import datetime, timezone

HOME = os.path.expanduser("~")
COPILOT_DB = os.path.join(HOME, ".copilot", "session-store.db")
COPILOT_OPEN = os.path.join(HOME, ".copilot", "open-sessions-state.json")
COPILOT_SIDEBAR = os.path.join(HOME, ".copilot", "sidebar-sessions-state")
CLAUDE_PROJECTS = os.path.join(HOME, ".claude", "projects")
AGENT_COMMS = tuple(
    c for c in os.environ.get("WTREE_AGENT_COMMS", "copilot,claude").split(",") if c
)


def under(path, cwd):
    return cwd == path or cwd.startswith(path.rstrip("/") + "/")


def session_cwds():
    """Map session id -> cwd, from the persisted store AND the sidebar index.

    The store is written lazily, so a session that is running right now may be
    missing from it; the sidebar index (filename = sha256(cwd)) covers more.
    """
    out = {}
    if os.path.isdir(COPILOT_SIDEBAR):
        for name in os.listdir(COPILOT_SIDEBAR):
            if not name.endswith(".json"):
                continue
            try:
                with open(os.path.join(COPILOT_SIDEBAR, name)) as fh:
                    blob = json.load(fh)
            except (OSError, ValueError):
                continue
            cwd = blob.get("cwd")
            if not cwd:
                continue
            for sid in blob.get("sessionIds", []):
                out[sid] = cwd
    if os.path.exists(COPILOT_DB):
        try:
            # immutable=1 so a live agent's WAL lock never blocks us
            uri = "file:%s?immutable=1" % COPILOT_DB
            con = sqlite3.connect(uri, uri=True)
            for sid, cwd in con.execute("SELECT id, cwd FROM sessions WHERE cwd IS NOT NULL"):
                out.setdefault(sid, cwd)
            con.close()
        except sqlite3.Error:
            pass
    return out


def copilot_sessions(paths, cutoff):
    """Return {path: (active_count, newest_epoch)} for open Copilot sessions."""
    out = {p: [0, 0.0] for p in paths}
    if not os.path.exists(COPILOT_OPEN):
        return out
    try:
        with open(COPILOT_OPEN) as fh:
            open_state = json.load(fh)
    except (OSError, ValueError):
        return out
    cwds = session_cwds()
    for sid, state in open_state.items():
        cwd = cwds.get(sid)
        if not cwd:
            continue
        seen = 0.0
        stamp = state.get("refreshedAt") or state.get("openedAt")
        if stamp:
            try:
                seen = datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()
            except ValueError:
                seen = 0.0
        if not (state.get("working") or seen >= cutoff):
            continue
        for p in paths:
            if under(p, cwd):
                out[p][0] += 1
                out[p][1] = max(out[p][1], seen)
    return out


def agent_processes(paths):
    """Running copilot/claude processes whose cwd is in a worktree (authoritative)."""
    out = {p: 0 for p in paths}
    try:
        res = subprocess.run(["ps", "-Ao", "pid=,comm="], capture_output=True, text=True, timeout=10)
    except (OSError, subprocess.SubprocessError):
        return out
    pids = []
    for line in res.stdout.splitlines():
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        pid, comm = parts[0], os.path.basename(parts[1].strip())
        if comm in AGENT_COMMS:
            pids.append(pid)
    if not pids:
        return out
    try:
        res = subprocess.run(
            ["lsof", "-a", "-p", ",".join(pids), "-d", "cwd", "-Fn"],
            capture_output=True, text=True, timeout=20,
        )
    except (OSError, subprocess.SubprocessError):
        return out
    for line in res.stdout.splitlines():
        if not line.startswith("n"):
            continue
        cwd = line[1:]
        for p in paths:
            if under(p, cwd):
                out[p] += 1
    return out


def claude_sessions(paths, cutoff):
    out = {p: [0, 0.0] for p in paths}
    if not os.path.isdir(CLAUDE_PROJECTS):
        return out
    for p in paths:
        # Claude encodes the cwd by replacing every '/' and '.' with '-'
        encoded = p.replace("/", "-").replace(".", "-")
        d = os.path.join(CLAUDE_PROJECTS, encoded)
        if not os.path.isdir(d):
            continue
        for name in os.listdir(d):
            if not name.endswith(".jsonl"):
                continue
            try:
                mtime = os.path.getmtime(os.path.join(d, name))
            except OSError:
                continue
            if mtime >= cutoff:
                out[p][0] += 1
                out[p][1] = max(out[p][1], mtime)
    return out


def tmux_panes(paths):
    out = {p: 0 for p in paths}
    try:
        res = subprocess.run(
            ["tmux", "list-panes", "-a", "-F", "#{pane_current_path}\t#{pane_current_command}"],
            capture_output=True, text=True, timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return out
    if res.returncode != 0:
        return out
    for line in res.stdout.splitlines():
        cwd, _, cmd = line.partition("\t")
        if cmd not in ("copilot", "claude", "node", "python3.11"):
            continue
        for p in paths:
            if under(p, cwd):
                out[p] += 1
    return out


def main():
    args = sys.argv[1:]
    idle_mins = 30
    if args and args[0] == "--idle-mins":
        idle_mins = int(args[1])
        args = args[2:]
    paths = [os.path.realpath(a) for a in args]
    if not paths:
        print("{}")
        return
    cutoff = time.time() - idle_mins * 60

    cop = copilot_sessions(paths, cutoff)
    cla = claude_sessions(paths, cutoff)
    tmx = tmux_panes(paths)
    proc = agent_processes(paths)

    result = {}
    for p in paths:
        c, c_seen = cop[p]
        k, k_seen = cla[p]
        t = tmx[p]
        r = proc[p]
        last = max(c_seen, k_seen)
        if r and not last:
            last = time.time()
        result[p] = {
            "active": bool(c or k or t or r),
            "copilot": c,
            "claude": k,
            "tmux": t,
            "procs": r,
            "detail": "proc:%d copilot:%d claude:%d tmux:%d" % (r, c, k, t),
            "last_seen": (
                datetime.fromtimestamp(last, timezone.utc).astimezone().strftime("%Y-%m-%d %H:%M")
                if last else ""
            ),
        }
    print(json.dumps(result))


if __name__ == "__main__":
    main()
