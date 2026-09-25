#!/usr/bin/env python3
"""Read-only inventory of local coding-agent sessions."""

from __future__ import annotations

import argparse
import difflib
import json
import os
import re
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlparse

HERDR = os.environ.get("HERDR_BIN", "herdr")
WEZTERM = os.environ.get("WEZTERM_BIN", "/Applications/WezTerm.app/Contents/MacOS/wezterm")
AGENT_COMMS = tuple(c for c in os.environ.get("YELL_AGENT_COMMS", "copilot,claude").split(",") if c)
READY_STATUSES = {"blocked", "idle", "done"}
ALL_STATUSES = READY_STATUSES | {"working", "unknown"}


def run(cmd: list[str], timeout: int = 20) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except (OSError, subprocess.SubprocessError) as exc:
        return subprocess.CompletedProcess(cmd, 127, "", str(exc))


def load_json(cmd: list[str], timeout: int = 20) -> dict[str, Any]:
    res = run(cmd, timeout=timeout)
    if res.returncode != 0:
        return {"_error": (res.stderr or res.stdout).strip(), "_cmd": cmd}
    try:
        return json.loads(res.stdout or "{}")
    except ValueError as exc:
        return {"_error": f"invalid json: {exc}", "_cmd": cmd, "_stdout": res.stdout[:500]}


def wezterm_panes() -> list[dict[str, Any]]:
    if not os.path.exists(WEZTERM):
        return []
    data = load_json([WEZTERM, "cli", "list", "--format", "json"])
    if isinstance(data, list):
        return data
    return []


def decode_cwd(raw: str | None) -> str:
    if not raw:
        return ""
    if raw.startswith("file://"):
        return unquote(urlparse(raw).path)
    return unquote(raw)


def ps_rows() -> list[dict[str, str]]:
    res = run(["ps", "-eo", "pid=,tty=,command="], timeout=20)
    rows: list[dict[str, str]] = []
    for line in res.stdout.splitlines():
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue
        rows.append({"pid": parts[0], "tty": parts[1], "command": parts[2]})
    return rows


def ps_tty(short_tty: str) -> list[dict[str, str]]:
    if not short_tty:
        return []
    res = run(["ps", "-t", short_tty, "-o", "pid=,comm=,args="], timeout=10)
    rows: list[dict[str, str]] = []
    for line in res.stdout.splitlines():
        parts = line.split(None, 2)
        if len(parts) < 2:
            continue
        rows.append({"pid": parts[0], "comm": os.path.basename(parts[1]), "args": parts[2] if len(parts) > 2 else ""})
    return rows


def parse_etime(text: str) -> int | None:
    """macOS ps elapsed time -> seconds. Format: [[dd-]hh:]mm:ss."""
    text = (text or "").strip()
    if not text:
        return None
    days = 0
    if "-" in text:
        day_part, _, text = text.partition("-")
        try:
            days = int(day_part)
        except ValueError:
            return None
    bits = text.split(":")
    try:
        nums = [int(b) for b in bits]
    except ValueError:
        return None
    if len(nums) == 2:
        hours, minutes, seconds = 0, nums[0], nums[1]
    elif len(nums) == 3:
        hours, minutes, seconds = nums
    else:
        return None
    return days * 86400 + hours * 3600 + minutes * 60 + seconds


def ps_args() -> dict[str, str]:
    """pid -> full argv.

    Kept as its own `ps` call on purpose: asking for `comm=` and `args=` in one
    invocation makes macOS truncate `comm` to 16 characters, which silently
    turns `/opt/homebrew/Caskroom/copilot-cli/1.0.54/copilot` into a basename
    that no longer matches AGENT_COMMS.
    """
    res = run(["ps", "-eo", "pid=,args="], timeout=20)
    out: dict[str, str] = {}
    for line in res.stdout.splitlines():
        parts = line.split(None, 1)
        if len(parts) == 2:
            out[parts[0]] = parts[1]
    return out


def herdr_managed_pids(table: dict[str, dict[str, Any]], args: dict[str, str]) -> set[str]:
    """Agent pids that Herdr already owns.

    A Herdr agent always runs inside a pty owned by a `herdr server`, so
    descending from a server process is the authoritative test. The previous
    proxy - "some process named herdr shares this tty" - was wrong in both
    directions: a herdr *client* tab has no agent on its tty to begin with, and
    a plain agent tab that merely shells out to `herdr` was dropped entirely.
    """
    servers = {pid for pid, row in table.items() if row["comm"] == "herdr" and " server" in args.get(pid, "")}
    if not servers:
        return set()
    managed: set[str] = set()
    for pid, row in table.items():
        if row["comm"] not in AGENT_COMMS:
            continue
        seen: set[str] = set()
        cur = row["ppid"]
        while cur in table and cur not in seen:
            seen.add(cur)
            if cur in servers:
                managed.add(pid)
                break
            cur = table[cur]["ppid"]
    return managed


def agent_roots(table: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """One entry per logical agent session.

    The CLI launcher re-execs itself, so a single session shows up as an agent
    process parented by another agent process; only the topmost one counts.
    """
    agents = {pid: row for pid, row in table.items() if row["comm"] in AGENT_COMMS}
    roots: dict[str, dict[str, Any]] = {}
    for pid, row in agents.items():
        seen: set[str] = set()
        cur = row["ppid"]
        nested = False
        while cur in table and cur not in seen:
            seen.add(cur)
            if cur in agents:
                nested = True
                break
            cur = table[cur]["ppid"]
        if not nested:
            roots[pid] = row
    return roots


def pid_cwd(pid: str) -> str:
    res = run(["lsof", "-a", "-p", pid, "-d", "cwd", "-Fn"], timeout=10)
    for line in res.stdout.splitlines():
        if line.startswith("n"):
            return line[1:]
    return ""


def proc_table() -> dict[str, dict[str, Any]]:
    """pid -> {ppid, tty, comm, age} for every process, used for agent age."""
    res = run(["ps", "-eo", "pid=,ppid=,tty=,etime=,comm="], timeout=20)
    table: dict[str, dict[str, Any]] = {}
    for line in res.stdout.splitlines():
        parts = line.split(None, 4)
        if len(parts) < 5:
            continue
        pid, ppid, tty, etime, comm = parts
        table[pid] = {
            "pid": pid,
            "ppid": ppid,
            "tty": tty,
            "comm": os.path.basename(comm),
            "age": parse_etime(etime),
        }
    return table


def agent_descendant(root_pid: str, table: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    """Oldest agent process below root_pid.

    A Herdr-managed agent lives inside the server's own pty, so it never shows
    up on the tab's tty; it is only reachable by walking the process tree down
    from the attached client.
    """
    children: dict[str, list[str]] = {}
    for pid, row in table.items():
        children.setdefault(row["ppid"], []).append(pid)
    seen: set[str] = set()
    stack = [root_pid]
    found: list[dict[str, Any]] = []
    while stack:
        pid = stack.pop()
        if pid in seen:
            continue
        seen.add(pid)
        row = table.get(pid)
        if row and row["comm"] in AGENT_COMMS:
            found.append(row)
        stack.extend(children.get(pid, []))
    if not found:
        return None
    return max(found, key=lambda r: r.get("age") or 0)


def birth_age_seconds(path: str | None) -> int | None:
    if not path or not os.path.exists(path):
        return None
    try:
        st = os.stat(path)
    except OSError:
        return None
    birth = getattr(st, "st_birthtime", None) or st.st_ctime
    return max(0, int(time.time() - birth))


def fmt_started(age_seconds: int | None) -> str:
    """'Sep 14 (9d)' - when this agent came up, and how long ago."""
    if age_seconds is None:
        return "?"
    started = datetime.fromtimestamp(time.time() - age_seconds)
    stamp = started.strftime("%b %-d")
    if age_seconds < 86400:
        stamp = started.strftime("%b %-d %H:%M")
    return f"{stamp} ({fmt_age(age_seconds)})"


def herdr_client_session(command: str, default_name: str | None) -> str | None:
    try:
        args = shlex.split(command)
    except ValueError:
        return None
    if not args or os.path.basename(args[0]) != "herdr":
        return None
    if len(args) == 1:
        return default_name
    if len(args) == 3 and args[1] == "--session":
        return args[2]
    if len(args) == 4 and args[1:3] == ["session", "attach"]:
        return args[3]
    return None


def attached_clients(sessions: list[dict[str, Any]], panes: list[dict[str, Any]], rows: list[dict[str, str]]) -> dict[str, list[dict[str, Any]]]:
    default_name = next((s.get("name") for s in sessions if s.get("default")), None)
    by_tty = {p.get("tty_name", "").replace("/dev/", ""): p for p in panes if p.get("tty_name")}
    out: dict[str, list[dict[str, Any]]] = {s.get("name", ""): [] for s in sessions}
    for row in rows:
        tty = row["tty"]
        if tty == "??":
            continue
        session = herdr_client_session(row["command"], default_name)
        if not session or session not in out:
            continue
        pane = by_tty.get(tty, {})
        out[session].append({
            "pid": row["pid"],
            "tty": f"/dev/{tty}",
            "wezterm_pane_id": pane.get("pane_id"),
            "wezterm_tab_id": pane.get("tab_id"),
            "wezterm_window_id": pane.get("window_id"),
            "title": pane.get("title", ""),
        })
    return out


def git_context(cwd: str) -> dict[str, Any]:
    if not cwd or not os.path.isdir(cwd):
        return {"is_git": False, "branch": "", "dirty_count": 0, "unpushed_count": 0, "summary": ""}
    inside = run(["git", "-C", cwd, "rev-parse", "--is-inside-work-tree"], timeout=8)
    if inside.returncode != 0 or inside.stdout.strip() != "true":
        return {"is_git": False, "branch": "", "dirty_count": 0, "unpushed_count": 0, "summary": ""}
    branch_res = run(["git", "-C", cwd, "rev-parse", "--abbrev-ref", "HEAD"], timeout=8)
    branch = branch_res.stdout.strip() if branch_res.returncode == 0 else ""
    status = run(["git", "-C", cwd, "status", "--porcelain"], timeout=12)
    dirty = len([line for line in status.stdout.splitlines() if line]) if status.returncode == 0 else 0
    unpushed_res = run(["git", "-C", cwd, "rev-list", "--count", "HEAD", "--not", "--remotes"], timeout=12)
    try:
        unpushed = int((unpushed_res.stdout or "0").strip()) if unpushed_res.returncode == 0 else 0
    except ValueError:
        unpushed = 0
    parts = []
    if dirty:
        parts.append(f"dirty:{dirty}")
    if unpushed:
        parts.append(f"unpushed:{unpushed}")
    return {"is_git": True, "branch": branch, "dirty_count": dirty, "unpushed_count": unpushed, "summary": ",".join(parts) or "clean"}


def tty_idle_seconds(tty: str | None) -> int | None:
    if not tty:
        return None
    try:
        return max(0, int(time.time() - os.stat(tty).st_mtime))
    except OSError:
        return None


def path_idle_seconds(path: str | None) -> int | None:
    if not path:
        return None
    try:
        return max(0, int(time.time() - os.stat(path).st_mtime))
    except OSError:
        return None


def fmt_age(seconds: int | None) -> str:
    if seconds is None:
        return "?"
    if seconds < 60:
        return f"{seconds}s"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes}m"
    hours = minutes // 60
    if hours < 48:
        return f"{hours}h"
    return f"{hours // 24}d"


def short_path(path: str) -> str:
    home = str(Path.home())
    if path == home:
        return "~"
    if path.startswith(home + "/"):
        return "~/" + path[len(home) + 1:]
    return path


def importance(record: dict[str, Any]) -> tuple[int, str]:
    status = record.get("status", "unknown")
    git = record.get("git", {})
    if status == "blocked":
        return 0, "blocked"
    if status in {"done", "idle"} and (git.get("dirty_count", 0) or git.get("unpushed_count", 0)):
        return 1, "ready+work"
    if status in {"done", "idle"} and not record.get("attached"):
        return 2, "ready+hidden"
    if status in {"done", "idle"}:
        return 3, "ready+clean"
    if status == "unknown":
        return 4, "unknown"
    return 5, "working"


ACTIVE_SECS = 300  # an unmanaged agent touched this recently is probably mid-turn


def next_step(record: dict[str, Any]) -> tuple[str, str]:
    """What the human should do: follow-up | waiting | clean-up.

    Herdr reports a real lifecycle status; an unmanaged agent only proves a
    process exists. For those, recent tty activity is the only evidence of a
    live turn, so a quiet one is treated as parked rather than working.
    """
    status = record.get("status", "unknown")
    git = record.get("git", {})
    has_work = bool(git.get("dirty_count", 0) or git.get("unpushed_count", 0))
    idle = record.get("idle_seconds")

    if status == "blocked":
        return "follow-up", "waiting on your approval/answer"
    if status == "working":
        return "waiting", "agent is mid-turn"
    if status == "unknown" and idle is not None and idle < ACTIVE_SECS:
        return "waiting", "not Herdr-managed; recent activity suggests a live turn"
    if has_work:
        detail = git.get("summary", "")
        if status == "unknown":
            return "follow-up", f"quiet with uncommitted work ({detail})"
        return "follow-up", f"ready with uncommitted work ({detail})"
    if status == "unknown":
        return "clean-up", "quiet, clean tree, not Herdr-managed"
    if not record.get("attached"):
        return "follow-up", "finished but has no terminal tab"
    return "clean-up", "finished, clean tree"


def clean_title(text: str) -> str:
    for suffix in (" - GitHub Copilot", " - Claude"):
        if text.endswith(suffix):
            text = text[: -len(suffix)]
    return text.strip()


def title_of(pane: dict[str, Any]) -> str:
    return pane.get("terminal_title_stripped") or pane.get("terminal_title") or pane.get("title") or ""


def collect_herdr(panes: list[dict[str, Any]], ps: list[dict[str, str]], table: dict[str, dict[str, Any]]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    root = load_json([HERDR, "session", "list", "--json"], timeout=20)
    sessions = root.get("sessions", []) if isinstance(root, dict) else []
    attached = attached_clients(sessions, panes, ps)
    records: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for session in sessions:
        name = session.get("name", "")
        if not name:
            continue
        pane_data = load_json([HERDR, "--session", name, "pane", "list"], timeout=20)
        agent_data = load_json([HERDR, "--session", name, "agent", "list"], timeout=20)
        tab_data = load_json([HERDR, "--session", name, "tab", "list"], timeout=20)
        if pane_data.get("_error"):
            errors.append({"session": name, "step": "pane list", "error": pane_data.get("_error")})
        agents = agent_data.get("result", {}).get("agents", []) if isinstance(agent_data, dict) else []
        session_panes = pane_data.get("result", {}).get("panes", []) if isinstance(pane_data, dict) else []
        if not agents:
            agent_panes = [p for p in session_panes if p.get("agent")]
            agents = agent_panes
        if not agents and session.get("running"):
            agents = [{"agent": "", "agent_status": "unknown", "cwd": "", "pane_id": "", "terminal_title_stripped": name}]
        for agent in agents:
            cwd = agent.get("foreground_cwd") or agent.get("cwd") or ""
            clients = attached.get(name, [])
            idle = None
            if clients:
                idle = min((tty_idle_seconds(c.get("tty")) for c in clients), default=None)
            if idle is None:
                idle = path_idle_seconds(session.get("session_dir"))
            git = git_context(cwd)
            status = agent.get("agent_status") or "unknown"
            if status not in ALL_STATUSES:
                status = "unknown"
            # Prefer the real agent process; fall back to when the session dir
            # was created, which is within seconds of the agent starting.
            proc = None
            for client in clients:
                proc = agent_descendant(client.get("pid", ""), table)
                if proc:
                    break
            age = proc.get("age") if proc else None
            if age is None:
                age = birth_age_seconds(session.get("session_dir"))
            record = {
                "id": f"herdr:{name}:{agent.get('pane_id') or 'session'}",
                "type": "herdr",
                "session": name,
                "name": name,
                "agent": agent.get("agent") or "agent",
                "status": status,
                "cwd": cwd,
                "branch": git.get("branch", ""),
                "git": git,
                "attached": bool(clients),
                "attached_clients": clients,
                "idle_seconds": idle,
                "idle": fmt_age(idle),
                "pane_id": agent.get("pane_id", ""),
                "tab_id": agent.get("tab_id", ""),
                "title": title_of(agent),
                "agent_age_seconds": age,
                "agent_age": fmt_started(age),
                "session_running": session.get("running", False),
                "herdr_session_dir": session.get("session_dir", ""),
                "tabs": tab_data.get("result", {}).get("tabs", []) if isinstance(tab_data, dict) else [],
            }
            rank, label = importance(record)
            record["importance_rank"] = rank
            record["importance"] = label
            record["next_step"], record["next_reason"] = next_step(record)
            records.append(record)
    return records, {"sessions": sessions, "errors": errors}


def collect_unmanaged(panes: list[dict[str, Any]], table: dict[str, dict[str, Any]], herdr_pids: set[str] | None = None) -> list[dict[str, Any]]:
    herdr_pids = herdr_pids or set()
    records: list[dict[str, Any]] = []
    for pane in panes:
        tty_name = pane.get("tty_name") or ""
        rows = ps_tty(tty_name.replace("/dev/", "")) if tty_name else []
        # Agents Herdr owns are reported from the Herdr API instead. Anything
        # else on this tty is irrelevant, including a `herdr` command the agent
        # itself happens to be running.
        agents = [r for r in rows if r.get("comm") in AGENT_COMMS and r.get("pid") not in herdr_pids]
        if not agents:
            continue
        cwd = decode_cwd(pane.get("cwd"))
        git = git_context(cwd)
        title = pane.get("title") or ""
        name = Path(cwd).name if cwd else f"pane-{pane.get('pane_id')}"
        record = {
            "id": f"wezterm:{pane.get('pane_id')}",
            "type": "wezterm",
            "session": name,
            "name": name,
            "agent": "+".join(sorted({a["comm"] for a in agents})),
            "status": "unknown",
            "cwd": cwd,
            "branch": git.get("branch", ""),
            "git": git,
            "attached": True,
            "attached_clients": [{"tty": tty_name, "wezterm_pane_id": pane.get("pane_id"), "wezterm_tab_id": pane.get("tab_id"), "wezterm_window_id": pane.get("window_id"), "title": title}],
            "idle_seconds": tty_idle_seconds(tty_name),
            "idle": fmt_age(tty_idle_seconds(tty_name)),
            "pane_id": pane.get("pane_id"),
            "tab_id": pane.get("tab_id"),
            "title": title,
            "pids": [a.get("pid") for a in agents],
        }
        ages = [table.get(a.get("pid", ""), {}).get("age") for a in agents]
        ages = [a for a in ages if a is not None]
        age = max(ages) if ages else None
        record["agent_age_seconds"] = age
        record["agent_age"] = fmt_started(age)
        rank, label = importance(record)
        record["importance_rank"] = rank
        record["importance"] = label
        record["next_step"], record["next_reason"] = next_step(record)
        records.append(record)
    return records


def collect_orphans(table: dict[str, dict[str, Any]], herdr_pids: set[str], claimed: set[str]) -> list[dict[str, Any]]:
    """Agents that neither collector claimed.

    Pane enumeration is the weak link: an agent is invisible to it when it runs
    outside WezTerm, inside tmux or another multiplexer, or in a pane WezTerm
    reports without a tty. Sweeping the process table last means a running agent
    can never be missing from the inventory, only described less richly.
    """
    records: list[dict[str, Any]] = []
    for pid, row in sorted(agent_roots(table).items(), key=lambda kv: kv[0]):
        if pid in herdr_pids or pid in claimed:
            continue
        tty = row.get("tty") or ""
        tty_path = f"/dev/{tty}" if tty and tty != "??" else ""
        cwd = pid_cwd(pid)
        git = git_context(cwd)
        name = Path(cwd).name if cwd else f"pid-{pid}"
        idle = tty_idle_seconds(tty_path)
        record = {
            "id": f"proc:{pid}",
            "type": "process",
            "session": name,
            "name": name,
            "agent": row.get("comm", "agent"),
            "status": "unknown",
            "cwd": cwd,
            "branch": git.get("branch", ""),
            "git": git,
            "attached": bool(tty_path),
            "attached_clients": [{"tty": tty_path}] if tty_path else [],
            "idle_seconds": idle,
            "idle": fmt_age(idle),
            "pane_id": "",
            "tab_id": "",
            "title": "",
            "pids": [pid],
            "agent_age_seconds": row.get("age"),
            "agent_age": fmt_started(row.get("age")),
            "no_terminal_pane": True,
        }
        rank, label = importance(record)
        record["importance_rank"] = rank
        record["importance"] = label
        record["next_step"], record["next_reason"] = next_step(record)
        records.append(record)
    return records


def collect() -> dict[str, Any]:
    panes = wezterm_panes()
    rows = ps_rows()
    table = proc_table()
    herdr_pids = herdr_managed_pids(table, ps_args())
    herdr_records, meta = collect_herdr(panes, rows, table)
    unmanaged = collect_unmanaged(panes, table, herdr_pids)
    claimed = {str(p) for r in unmanaged for p in r.get("pids", []) if p}
    orphans = collect_orphans(table, herdr_pids, claimed)
    records = herdr_records + unmanaged + orphans
    # Sort once for stable JSON and human output.
    records.sort(key=lambda r: (NEXT_ORDER.get(r.get("next_step", ""), 9), r.get("importance_rank", 9), -(r.get("idle_seconds") or -1), r.get("name", "")))
    return {
        "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "records": records,
        "summary": summarize(records),
        "herdr": meta,
    }


def summarize(records: list[dict[str, Any]]) -> dict[str, Any]:
    counts = {s: 0 for s in ["blocked", "idle", "done", "working", "unknown"]}
    for r in records:
        status = r.get("status", "unknown")
        counts[status if status in counts else "unknown"] += 1
    ready = [r for r in records if r.get("status") in READY_STATUSES]
    unknown = [r for r in records if r.get("status") == "unknown"]
    return {
        "total": len(records),
        "ready_follow_up": len(ready),
        "working": counts["working"],
        "blocked": counts["blocked"],
        "unknown": len(unknown),
        "by_status": counts,
        "by_next_step": {step: len([r for r in records if r.get("next_step") == step]) for step in NEXT_ORDER},
        "unattached_ready": len([r for r in ready if not r.get("attached")]),
        "ready_with_work": len([r for r in ready if r.get("git", {}).get("dirty_count", 0) or r.get("git", {}).get("unpushed_count", 0)]),
    }


def row_values(r: dict[str, Any]) -> list[str]:
    attach = "yes" if r.get("attached") else "no"
    git = r.get("git", {}).get("summary") or "-"
    branch = r.get("branch") or "-"
    loc = r.get("title") or short_path(r.get("cwd", ""))
    if len(loc) > 38:
        loc = loc[:35] + "..."
    return [
        r.get("importance", ""),
        r.get("status", ""),
        r.get("name", ""),
        r.get("agent", ""),
        branch,
        git,
        attach,
        r.get("idle", "?"),
        loc,
    ]


def print_table(rows: list[dict[str, Any]], headers: list[str]) -> None:
    vals = [row_values(r) for r in rows]
    widths = [len(h) for h in headers]
    for row in vals:
        for i, cell in enumerate(row):
            widths[i] = min(max(widths[i], len(str(cell))), 38 if i == len(headers) - 1 else 24)
    fmt = "  ".join("{:<" + str(w) + "}" for w in widths)
    print(fmt.format(*headers))
    print(fmt.format(*["-" * w for w in widths]))
    for row in vals:
        print(fmt.format(*[str(c)[:widths[i]] for i, c in enumerate(row)]))


NEXT_ORDER = {"follow-up": 0, "waiting": 1, "clean-up": 2}

TABLE_COLS: list[tuple[str, str, int]] = [
    ("branch", "branch", 26),
    ("directory", "Directory", 36),
    ("doing", "What it was doing", 38),
    ("agent_age", "Agent age", 18),
    ("state", "Status", 16),
    ("next_step", "Next step", 10),
]


def table_cells(r: dict[str, Any]) -> dict[str, str]:
    status = r.get("status", "unknown")
    idle = r.get("idle", "?")
    state = status if status == "working" else f"{status} {idle}"
    return {
        "branch": r.get("branch") or short_path(r.get("cwd", "")) or "-",
        "directory": short_path(r.get("cwd", "")) or "-",
        "doing": clean_title(r.get("title", "")) or r.get("name", "") or "-",
        "agent_age": r.get("agent_age", "?"),
        "state": state,
        "next_step": r.get("next_step", "?"),
    }


def print_box_table(records: list[dict[str, Any]]) -> None:
    rows = [table_cells(r) for r in records]
    widths = []
    for key, header, cap in TABLE_COLS:
        width = max([len(header)] + [len(row[key]) for row in rows]) if rows else len(header)
        widths.append(min(width, cap))

    def line(left: str, mid: str, right: str) -> str:
        return left + mid.join("─" * (w + 2) for w in widths) + right

    def render(cells: list[str]) -> str:
        out = []
        for i, cell in enumerate(cells):
            text = cell if len(cell) <= widths[i] else cell[: widths[i] - 1] + "…"
            out.append(" " + text.ljust(widths[i]) + " ")
        return "│" + "│".join(out) + "│"

    print(line("┌", "┬", "┐"))
    print(render([h for _, h, _ in TABLE_COLS]))
    print(line("├", "┼", "┤"))
    for row in rows:
        print(render([row[key] for key, _, _ in TABLE_COLS]))
    print(line("└", "┴", "┘"))


def print_overview(data: dict[str, Any]) -> None:
    records = data["records"]
    summary = data["summary"]
    counts = summary.get("by_next_step", {})
    print(
        f"yell @ {data['generated_at']}: {len(records)} agent session(s) - "
        f"{counts.get('follow-up', 0)} follow-up, {counts.get('waiting', 0)} waiting, {counts.get('clean-up', 0)} clean-up"
    )
    print()
    if not records:
        print("No coding-agent sessions found.")
        return
    print_box_table(records)
    followups = [r for r in records if r.get("next_step") == "follow-up"]
    if followups:
        print()
        print("Why follow-up:")
        for r in followups:
            label = r.get("branch") or r.get("name")
            managed = "" if r.get("type") == "herdr" else "  [not Herdr-managed]"
            print(f"  {label}: {r.get('next_reason', '')}{managed}")


def haystack(r: dict[str, Any]) -> list[str]:
    return [
        str(r.get("name", "")),
        str(r.get("session", "")),
        str(r.get("cwd", "")),
        str(Path(r.get("cwd", "")).name if r.get("cwd") else ""),
        str(r.get("branch", "")),
        str(r.get("title", "")),
        str(r.get("pane_id", "")),
    ]


def match_records(records: list[dict[str, Any]], query: str) -> list[dict[str, Any]]:
    q = query.strip().lower()
    if not q:
        return []
    exact = [r for r in records if q in {str(v).lower() for v in [r.get("name", ""), r.get("session", ""), r.get("branch", ""), r.get("pane_id", "")] if v}]
    if exact:
        return exact
    substring = []
    for r in records:
        if any(q in h.lower() for h in haystack(r) if h):
            substring.append(r)
    if substring:
        return substring
    scored: list[tuple[float, dict[str, Any]]] = []
    tokens = re.findall(r"[a-z0-9]+", q)
    for r in records:
        best = 0.0
        for h in haystack(r):
            hl = h.lower()
            if not hl:
                continue
            score = difflib.SequenceMatcher(None, q, hl).ratio()
            if tokens and all(t in hl for t in tokens):
                score = max(score, 0.72)
            best = max(best, score)
        if best >= 0.55:
            scored.append((best, r))
    scored.sort(key=lambda x: (-x[0], x[1].get("importance_rank", 9), x[1].get("name", "")))
    return [r for _, r in scored[:8]]


def print_candidates(query: str, matches: list[dict[str, Any]]) -> None:
    print(f"Multiple sessions match {query!r}; choose a more specific name/context:")
    print_box_table(matches)


def print_detail(r: dict[str, Any]) -> None:
    git = r.get("git", {})
    print(f"{r.get('name')} [{r.get('type')}] - {r.get('status')} ({r.get('importance')})")
    print(f"agent:    {r.get('agent')}")
    print(f"cwd:      {short_path(r.get('cwd', ''))}")
    print(f"branch:   {r.get('branch') or '-'}")
    print(f"git:      {git.get('summary') or '-'}")
    print(f"attached: {'yes' if r.get('attached') else 'no'}")
    print(f"age:      {r.get('agent_age', '?')}")
    print(f"idle:     {r.get('idle', '?')}")
    print(f"next:     {r.get('next_step', '?')} - {r.get('next_reason', '')}")
    if r.get("pane_id"):
        print(f"pane:     {r.get('pane_id')}  tab: {r.get('tab_id') or '-'}")
    if r.get("title"):
        print(f"title:    {r.get('title')}")
    clients = r.get("attached_clients") or []
    if clients:
        print("clients:")
        for c in clients:
            print(f"  - tty {c.get('tty', '-')} wezterm pane {c.get('wezterm_pane_id', '-')} tab {c.get('wezterm_tab_id', '-')} title={c.get('title', '')}")
    if r.get("type") == "herdr" and r.get("status") in READY_STATUSES and r.get("pane_id"):
        print(f"read:     {HERDR} --session {shlex.quote(r.get('session', ''))} agent read {shlex.quote(str(r.get('pane_id')))} --source recent-unwrapped --lines 80")
    print("note:     yell is read-only; it did not focus, prompt, start, stop, kill, or mutate anything.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Find local coding-agent sessions that need follow-up.")
    parser.add_argument("query", nargs="*", help="session name or free-text context")
    parser.add_argument("--json", action="store_true", help="print machine-readable JSON")
    args = parser.parse_args()

    data = collect()
    query = " ".join(args.query).strip()

    if args.json:
        if query:
            matches = match_records(data["records"], query)
            data["query"] = query
            data["matches"] = matches
        print(json.dumps(data, indent=2, sort_keys=True))
        return 0

    if not query:
        print_overview(data)
        return 0

    matches = match_records(data["records"], query)
    if not matches:
        print(f"No session matched {query!r}.")
        return 1
    if len(matches) > 1:
        print_candidates(query, matches)
        return 2
    print_detail(matches[0])
    return 0


if __name__ == "__main__":
    sys.exit(main())
