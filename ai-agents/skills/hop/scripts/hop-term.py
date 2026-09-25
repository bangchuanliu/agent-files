#!/usr/bin/env python3
"""Terminal-tab awareness for the hop skill.

An agent cannot change the user's shell directory, so hop works at the
*terminal tab* level instead: find a tab already sitting in a directory, or open
a new one there and start an agent in it.

Subcommands
  find  <dir>   report tabs whose cwd is at/under <dir>, as JSON
  herdr-session-for <dir>
                name of a live Herdr session sitting at/under <dir>, if any
  open  <dir>   open a new tab at <dir> and optionally launch a command
                  --cmd <shell-cmd>   what to run (default: none, just a shell)
                  --activate          focus the new tab (default on)
  focus <pane>  focus an existing pane id

Supported terminals: WezTerm (via `wezterm cli`, exact cwd + tty), and a
best-effort AppleScript path for iTerm2 / Terminal.app / Ghostty.
"""
import json
import os
import shutil
import shlex
import subprocess
import sys
from urllib.parse import unquote, urlparse

WEZTERM = os.environ.get("WEZTERM_BIN", "/Applications/WezTerm.app/Contents/MacOS/wezterm")
AGENT_COMMS = tuple(
    c for c in os.environ.get("WTREE_AGENT_COMMS", "copilot,claude").split(",") if c
)
# Resolved via PATH so the skill is portable; override with HERDR_BIN.
HERDR = os.environ.get("HERDR_BIN", "herdr")



def _herdr_available() -> bool:
    """True when the herdr binary is resolvable, by PATH name or explicit path."""
    return shutil.which(HERDR) is not None or os.path.exists(HERDR)


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=20, **kw)


def have_wezterm():
    if not os.path.exists(WEZTERM):
        return False
    try:
        return run([WEZTERM, "cli", "list", "--format", "json"]).returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def wez_panes():
    res = run([WEZTERM, "cli", "list", "--format", "json"])
    if res.returncode != 0:
        return []
    try:
        return json.loads(res.stdout)
    except ValueError:
        return []


def cwd_of(pane):
    """WezTerm reports cwd as file://host/path; the host part must be stripped."""
    raw = pane.get("cwd") or ""
    if not raw:
        return ""
    if raw.startswith("file://"):
        return unquote(urlparse(raw).path)
    return unquote(raw)


def tty_procs(tty_name):
    """Processes attached to a tty, as (pid, comm, args) - used to spot agents."""
    if not tty_name:
        return []
    short = tty_name.replace("/dev/", "")
    res = run(["ps", "-t", short, "-o", "pid=,comm=,args="])
    if res.returncode != 0:
        return []
    out = []
    for line in res.stdout.splitlines():
        parts = line.split(None, 2)
        if len(parts) < 2:
            continue
        out.append((parts[0], os.path.basename(parts[1]), parts[2] if len(parts) > 2 else ""))
    return out


def herdr_agents(session):
    """Agents inside a Herdr session, as (kind, status) pairs.

    A Herdr-managed tab runs `herdr` on the tty; the real agent lives inside
    Herdr's own pty and is invisible to `ps -t`. Herdr is the lifecycle
    authority for those agents, so ask it rather than guessing from the tty.
    """
    if not _herdr_available():
        return []
    cmd = [HERDR]
    if session:
        cmd += ["--session", session]
    cmd += ["agent", "list"]
    try:
        res = run(cmd)
    except (OSError, subprocess.SubprocessError):
        return []
    if res.returncode != 0:
        return []
    try:
        agents = json.loads(res.stdout).get("result", {}).get("agents", [])
    except ValueError:
        return []
    return [(a.get("agent") or "agent", a.get("agent_status") or "unknown") for a in agents]


def herdr_pane_cwds(session):
    """cwds of the panes inside a Herdr session."""
    if not _herdr_available():
        return []
    cmd = [HERDR]
    if session:
        cmd += ["--session", session]
    cmd += ["pane", "list"]
    try:
        res = run(cmd)
    except (OSError, subprocess.SubprocessError):
        return []
    if res.returncode != 0:
        return []
    try:
        panes = json.loads(res.stdout).get("result", {}).get("panes", [])
    except ValueError:
        return []
    out = []
    for pane in panes:
        for key in ("foreground_cwd", "cwd"):
            if pane.get(key):
                out.append(pane[key])
    return out


def herdr_sessions():
    """Names of Herdr sessions the server knows about (running first)."""
    if not _herdr_available():
        return []
    try:
        res = run([HERDR, "session", "list", "--json"])
    except (OSError, subprocess.SubprocessError):
        return []
    if res.returncode != 0:
        return []
    try:
        sessions = json.loads(res.stdout).get("sessions", [])
    except ValueError:
        return []
    names = [s for s in sessions if s.get("running")] + [s for s in sessions if not s.get("running")]
    return [s.get("name", "") for s in names if s.get("name")]


def herdr_session_for(target):
    """A Herdr session whose panes sit at/under target, if any.

    Used when no terminal tab exists: the session may still be alive with its
    agent intact, and must be resumed rather than replaced by a new agent.
    """
    for name in herdr_sessions():
        for cwd in herdr_pane_cwds("" if name == "default" else name):
            if under(target, cwd):
                return name
    return ""


def herdr_session_of(args):
    """Session name from a `herdr` client command line; "" means the default."""
    parts = shlex.split(args) if args else []
    if "--session" in parts:
        i = parts.index("--session")
        if i + 1 < len(parts):
            return parts[i + 1]
    if "attach" in parts:
        i = parts.index("attach")
        if i + 1 < len(parts):
            return parts[i + 1]
    return ""


def under(root, path):
    if not path:
        return False
    root = os.path.realpath(root).rstrip("/")
    path = os.path.realpath(path).rstrip("/")
    return path == root or path.startswith(root + "/")


def find(target):
    target = os.path.realpath(target)
    result = {"terminal": None, "tabs": []}
    if not have_wezterm():
        result["terminal"] = "unknown"
        return result
    result["terminal"] = "wezterm"
    for pane in wez_panes():
        cwd = cwd_of(pane)
        procs = tty_procs(pane.get("tty_name", ""))
        # A tab opened by `start` stays at $HOME; the worktree lives in the
        # Herdr session running inside it. Match on the session's pane cwds too,
        # or every start-created task would look like it has no tab.
        session_cwd = ""
        if not under(target, cwd):
            hit = False
            for _p, c, a in procs:
                if c != "herdr":
                    continue
                for inner in herdr_pane_cwds(herdr_session_of(a)):
                    if under(target, inner):
                        hit, session_cwd = True, inner
                        break
                break
            if not hit:
                continue
        agents = [
            {"pid": p, "comm": c}
            for p, c, _ in procs
            if c in AGENT_COMMS
        ]
        # A Herdr client on the tty hides its agent inside Herdr's own pty, so
        # the tty scan above sees nothing. Ask Herdr for the truth.
        herdr_session = None
        for p, c, a in procs:
            if c != "herdr":
                continue
            herdr_session = herdr_session_of(a)
            for kind, status in herdr_agents(herdr_session):
                agents.append({"pid": p, "comm": kind, "via": "herdr",
                               "session": herdr_session or "default",
                               "status": status})
            break
        # a tmux client on the tty means the real agent may live inside tmux
        tmux = any(c == "tmux" for _, c, _ in procs)
        result["tabs"].append({
            "pane_id": pane.get("pane_id"),
            "tab_id": pane.get("tab_id"),
            "window_id": pane.get("window_id"),
            "cwd": session_cwd or cwd,
            "tab_cwd": cwd,
            "title": pane.get("title", ""),
            "tty": pane.get("tty_name", ""),
            "is_active": pane.get("is_active", False),
            "agents": agents,
            "has_agent": bool(agents),
            "in_herdr": herdr_session is not None,
            "herdr_session": (herdr_session or "default") if herdr_session is not None else "",
            "in_tmux": tmux,
        })
    return result


def open_tab(target, cmd=None, activate=True):
    if not have_wezterm():
        return {"ok": False, "reason": "wezterm cli unavailable; open a terminal manually and cd there"}
    target = os.path.realpath(target)
    res = run([WEZTERM, "cli", "spawn", "--cwd", target])
    if res.returncode != 0:
        return {"ok": False, "reason": (res.stderr or res.stdout).strip()}
    pane_id = res.stdout.strip()
    if cmd:
        # send-text with a trailing newline executes it in the new shell
        run([WEZTERM, "cli", "send-text", "--pane-id", pane_id, "--no-paste"],
            input=cmd + "\n")
    if activate:
        run([WEZTERM, "cli", "activate-pane", "--pane-id", pane_id])
    return {"ok": True, "pane_id": pane_id, "cwd": target, "cmd": cmd or ""}


def focus(pane_id):
    if not have_wezterm():
        return {"ok": False, "reason": "wezterm cli unavailable"}
    res = run([WEZTERM, "cli", "activate-pane", "--pane-id", str(pane_id)])
    return {"ok": res.returncode == 0, "pane_id": pane_id,
            "reason": (res.stderr or "").strip()}


def main():
    args = sys.argv[1:]
    if not args:
        print(json.dumps({"error": "usage: hop-term.py find|open|focus ..."}))
        return 2
    sub, args = args[0], args[1:]

    if sub == "find":
        if not args:
            print(json.dumps({"error": "find needs a directory"}))
            return 2
        print(json.dumps(find(args[0]), indent=2))
        return 0

    if sub == "open":
        if not args:
            print(json.dumps({"error": "open needs a directory"}))
            return 2
        target, cmd, activate = args[0], None, True
        rest = args[1:]
        while rest:
            if rest[0] == "--cmd":
                cmd = rest[1]; rest = rest[2:]
            elif rest[0] == "--no-activate":
                activate = False; rest = rest[1:]
            elif rest[0] == "--activate":
                activate = True; rest = rest[1:]
            else:
                rest = rest[1:]
        out = open_tab(target, cmd, activate)
        print(json.dumps(out, indent=2))
        return 0 if out.get("ok") else 1

    if sub == "herdr-session-for":
        if not args:
            return 2
        name = herdr_session_for(args[0])
        if name:
            print(name)
            return 0
        return 1

    if sub == "focus":
        if not args:
            print(json.dumps({"error": "focus needs a pane id"}))
            return 2
        out = focus(args[0])
        print(json.dumps(out, indent=2))
        return 0 if out.get("ok") else 1

    print(json.dumps({"error": "unknown subcommand %r" % sub}))
    return 2


if __name__ == "__main__":
    sys.exit(main())
