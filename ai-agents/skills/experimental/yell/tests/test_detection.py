#!/usr/bin/env python3
"""Regression tests for yell's session detection.

Covers missing sessions and false positives in the inventory:
  1. a plain agent tab was dropped because some process named `herdr` shared
     its tty, even though that agent was not Herdr-managed at all;
  2. an agent with no WezTerm pane (other terminal, multiplexer, or a pane
     reported without a tty) was never enumerated in the first place;
  3. tty-less and embedded desktop workers were reported as interactive sessions.

Run: python3 tests/test_detection.py
"""

from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

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
        for target, options in (
            ("run", {"side_effect": AssertionError("Unexpected external command")}),
            ("tty_idle_seconds", {"return_value": 600}),
        ):
            patcher = patch.object(yell, target, **options)
            patcher.start()
            self.addCleanup(patcher.stop)
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

    def test_desktop_app_sdk_workers_are_not_sessions(self):
        table = {
            "12650": {"pid": "12650", "ppid": "1", "tty": "??", "comm": "github", "age": 13488},
            "12735": {"pid": "12735", "ppid": "12650", "tty": "??", "comm": "copilot", "age": 13484},
            "13230": {"pid": "13230", "ppid": "12650", "tty": "??", "comm": "copilot", "age": 245},
            "60443": {"pid": "60443", "ppid": "34890", "tty": "ttys000", "comm": "copilot", "age": 900},
            "34890": {"pid": "34890", "ppid": "1", "tty": "ttys000", "comm": "bash", "age": 999},
        }
        args = {
            "12650": "/Applications/GitHub Copilot.app/Contents/MacOS/github",
            "12735": "/Users/someone/Library/Caches/github-copilot-sdk/cli/1.0.87-0/copilot",
            "13230": "/Users/someone/Library/Caches/github-copilot-sdk/cli/1.0.87-0/copilot",
            "60443": "copilot",
        }
        records = yell.collect_orphans(table, set(), set(), args)
        self.assertEqual([r["id"] for r in records], ["proc:60443"])

    def test_tty_less_agent_is_not_a_session(self):
        for tty_fields in ({}, {"tty": None}, {"tty": ""}, {"tty": "??"}):
            with self.subTest(tty_fields=tty_fields):
                table = {"9001": {"pid": "9001", "ppid": "1", "comm": "copilot", "age": 60, **tty_fields}}
                with patch.object(yell, "pid_cwd") as cwd, patch.object(yell, "git_context") as git:
                    self.assertEqual(yell.collect_orphans(table, set(), set()), [])
                cwd.assert_not_called()
                git.assert_not_called()

    def test_embedded_marker_gate_catches_a_worker_that_owns_a_tty(self):
        table = {"9002": {"pid": "9002", "ppid": "1", "tty": "ttys019", "comm": "copilot", "age": 60}}
        for argv in (
            "/Users/someone/Library/Caches/github-copilot-sdk/cli/1.0.87-0/copilot",
            "/Applications/GitHub Copilot.app/Contents/Resources/copilot",
            "/Users/someone/.vscode/extensions/copilot/bin/copilot",
            "Code Helper copilot",
        ):
            with self.subTest(argv=argv):
                self.assertEqual(yell.collect_orphans(table, set(), set(), {"9002": argv}), [])

    def test_plain_agent_survives_missing_or_unrelated_argv(self):
        for comm in ("copilot", "claude"):
            table = {"9003": {"pid": "9003", "ppid": "1", "tty": "ttys019", "comm": comm, "age": 60}}
            for args in (None, {}, {"9003": ""}, {"9003": f"/usr/local/bin/{comm}"}):
                with self.subTest(comm=comm, args=args):
                    records = yell.collect_orphans(table, set(), set(), args)
                    self.assertEqual([r["id"] for r in records], ["proc:9003"])
                    self.assertEqual(records[0]["status"], "unknown")
        self.assertEqual(yell.collect_orphans({}, set(), set()), [])

    def test_json_inventory_excludes_background_workers(self):
        outputs = {
            ("ps", "-eo", "pid=,tty=,command="): "",
            ("ps", "-eo", "pid=,ppid=,tty=,etime=,comm="): (
                "100 1 ?? 10:00 github\n"
                "101 100 ?? 09:00 copilot\n"
                "102 100 ttys019 08:00 copilot\n"
                "200 1 ttys020 07:00 copilot\n"
                "300 1 ?? 06:00 herdr\n"
                "301 300 ttys021 05:00 copilot\n"
            ),
            ("ps", "-eo", "pid=,args="): (
                "100 /Applications/GitHub Copilot.app/Contents/MacOS/github\n"
                "101 copilot\n"
                "102 /Users/someone/Library/Caches/github-copilot-sdk/cli/copilot\n"
                "200 copilot\n"
                "300 herdr server\n"
                "301 copilot\n"
            ),
            (yell.HERDR, "session", "list", "--json"): '{"sessions": []}',
        }

        def simulated_run(command, timeout=20):
            self.assertIn(tuple(command), outputs, "Unexpected external command")
            return subprocess.CompletedProcess(command, 0, outputs[tuple(command)], "")

        output = io.StringIO()
        with (
            patch.object(yell, "run", side_effect=simulated_run) as run,
            patch.object(yell, "wezterm_panes", return_value=[]),
            patch.object(sys, "argv", ["yell", "--json"]),
            redirect_stdout(output),
        ):
            self.assertEqual(yell.main(), 0)
        data = json.loads(output.getvalue())
        self.assertEqual([r["id"] for r in data["records"]], ["proc:200"])
        self.assertEqual(data["summary"]["total"], 1)
        self.assertEqual(data["records"][0]["status"], "unknown")
        self.assertEqual(
            sum(call.args[0] == ["ps", "-eo", "pid=,args="] for call in run.call_args_list),
            1,
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
