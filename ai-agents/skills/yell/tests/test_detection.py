#!/usr/bin/env python3
"""Regression tests for yell's session detection.

Covers the two ways a live agent used to vanish from the inventory:
  1. a plain agent tab was dropped because some process named `herdr` shared
     its tty, even though that agent was not Herdr-managed at all;
  2. an agent with no WezTerm pane (other terminal, multiplexer, or a pane
     reported without a tty) was never enumerated in the first place.

Run: python3 tests/test_detection.py
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "yell.py"
spec = importlib.util.spec_from_file_location("yell", SCRIPT)
yell = importlib.util.module_from_spec(spec)
sys.modules["yell"] = yell
spec.loader.exec_module(yell)

CLEAN_GIT = {"is_git": True, "branch": "feature/x", "dirty_count": 0, "unpushed_count": 0, "summary": "clean"}

PANE = {
    "pane_id": 35,
    "tab_id": 20,
    "window_id": 16,
    "tty_name": "/dev/ttys006",
    "cwd": "file:///Users/someone/work/repo/",
    "title": "Refactor Agents.md Guidelines - GitHub Copilot",
}

BASH = {"pid": "29057", "comm": "bash", "args": "-bash"}
AGENT = {"pid": "88643", "comm": "copilot", "args": "copilot"}
HERDR_CMD = {"pid": "99001", "comm": "herdr", "args": "herdr session list --json"}

TABLE = {
    "88643": {"pid": "88643", "ppid": "29057", "tty": "ttys006", "comm": "copilot", "age": 4800},
    "29057": {"pid": "29057", "ppid": "1", "tty": "ttys006", "comm": "bash", "age": 5000},
}


class DetectionTest(unittest.TestCase):
    def setUp(self) -> None:
        self._git = yell.git_context
        self._ps_tty = yell.ps_tty
        self._cwd = yell.pid_cwd
        yell.git_context = lambda cwd: dict(CLEAN_GIT)
        yell.pid_cwd = lambda pid: "/Users/someone/work/repo"

    def tearDown(self) -> None:
        yell.git_context = self._git
        yell.ps_tty = self._ps_tty
        yell.pid_cwd = self._cwd

    def unmanaged(self, rows, herdr_pids=frozenset()):
        yell.ps_tty = lambda tty: list(rows)
        return yell.collect_unmanaged([PANE], TABLE, set(herdr_pids))

    def test_plain_agent_tab_is_listed(self):
        self.assertEqual(len(self.unmanaged([BASH, AGENT])), 1)

    def test_agent_tab_survives_a_herdr_command_on_its_tty(self):
        """The old code skipped the whole pane when any `herdr` shared the tty."""
        records = self.unmanaged([BASH, AGENT, HERDR_CMD])
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]["branch"], "feature/x")

    def test_herdr_owned_agent_is_not_double_counted(self):
        """An agent Herdr owns is reported from the Herdr API, not from the pane."""
        self.assertEqual(self.unmanaged([BASH, AGENT], {"88643"}), [])

    def test_herdr_managed_pids_uses_server_ancestry(self):
        table = {
            "100": {"pid": "100", "ppid": "1", "tty": "??", "comm": "herdr", "age": 99},
            "101": {"pid": "101", "ppid": "100", "tty": "ttys008", "comm": "copilot", "age": 60},
            "200": {"pid": "200", "ppid": "1", "tty": "ttys006", "comm": "copilot", "age": 60},
            "201": {"pid": "201", "ppid": "200", "tty": "ttys006", "comm": "herdr", "age": 1},
        }
        args = {"100": "/Users/x/.local/bin/herdr server", "201": "herdr session list --json"}
        self.assertEqual(yell.herdr_managed_pids(table, args), {"101"})

    def test_agent_roots_collapses_the_relaunch_chain(self):
        table = {
            "60443": {"pid": "60443", "ppid": "34890", "tty": "ttys000", "comm": "copilot", "age": 900},
            "36172": {"pid": "36172", "ppid": "60443", "tty": "ttys000", "comm": "copilot", "age": 800},
            "34890": {"pid": "34890", "ppid": "1", "tty": "ttys000", "comm": "bash", "age": 999},
        }
        self.assertEqual(set(yell.agent_roots(table)), {"60443"})

    def test_agent_without_a_wezterm_pane_is_still_reported(self):
        """The orphan sweep is what makes detection process-driven, not pane-driven."""
        table = {
            "31786": {"pid": "31786", "ppid": "31784", "tty": "ttys017", "comm": "copilot", "age": 120},
            "31784": {"pid": "31784", "ppid": "1", "tty": "??", "comm": "python3", "age": 130},
        }
        records = yell.collect_orphans(table, herdr_pids=set(), claimed=set())
        self.assertEqual([r["id"] for r in records], ["proc:31786"])
        self.assertTrue(records[0]["no_terminal_pane"])

    def test_orphan_sweep_skips_already_claimed_agents(self):
        table = {"31786": {"pid": "31786", "ppid": "1", "tty": "ttys017", "comm": "copilot", "age": 120}}
        self.assertEqual(yell.collect_orphans(table, set(), {"31786"}), [])
        self.assertEqual(yell.collect_orphans(table, {"31786"}, set()), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
