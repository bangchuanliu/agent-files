import sys
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import pr_watch  # noqa: E402

NOW = datetime(2026, 10, 9, 22, 0, tzinfo=timezone.utc)
SHA = "abc123def4567890"


def make_data(**overrides):
    pr = {"url": "https://github.com/o/r/pull/7", "title": "t", "state": "OPEN", "isDraft": False,
          "reviewDecision": "REVIEW_REQUIRED", "headRefName": "me/x", "headRefOid": SHA,
          "mergeable": "MERGEABLE", "comments": [], "reviews": []}
    pr.update(overrides.pop("pr", {}))
    data = {"pr": pr, "threads": [], "check_runs": [], "statuses": [], "me": "me"}
    data.update(overrides)
    return data


def thread(*authors, resolved=False, first_id=100):
    return {"id": "T1", "isResolved": resolved, "isOutdated": False, "path": "a.py", "line": 3,
            "comments": {"nodes": [{"databaseId": first_id + i, "author": {"login": a}, "body": f"c{i}",
                                    "createdAt": "2026-10-09T21:00:00Z", "url": "u"}
                                   for i, a in enumerate(authors)]}}


def run(name, status="completed", conclusion="success", started="2026-10-09T21:00:00Z", rid=1, url=""):
    return {"id": rid, "name": name, "status": status, "conclusion": conclusion, "started_at": started,
            "details_url": url, "app": {"slug": "github-actions"}, "output": {"title": f"{name} out"}}


def classify(data, state=None, **kw):
    return pr_watch.classify(data, state or {"started_at": NOW.isoformat(), "handled": [], "rounds": 0}, NOW, **kw)


class ThreadTests(unittest.TestCase):
    def test_unresolved_thread_from_reviewer_is_actionable(self):
        result = classify(make_data(threads=[thread("rev")]))
        self.assertEqual(result["status"], "action")
        self.assertEqual(result["items"][0]["key"], "th:100")
        self.assertEqual(result["items"][0]["reply_to_comment_id"], 100)

    def test_thread_where_i_replied_last_is_not_actionable(self):
        self.assertEqual(classify(make_data(threads=[thread("rev", "me")]))["status"], "idle")

    def test_reviewer_follow_up_after_my_reply_is_actionable_again(self):
        result = classify(make_data(threads=[thread("rev", "me", "rev")]),
                          {"started_at": NOW.isoformat(), "handled": ["th:100"], "rounds": 0})
        self.assertEqual([i["key"] for i in result["items"]], ["th:102"])

    def test_resolved_thread_is_ignored(self):
        self.assertEqual(classify(make_data(threads=[thread("rev", resolved=True)]))["items"], [])


class CommentTests(unittest.TestCase):
    def test_others_comments_actionable_until_marked(self):
        data = make_data(pr={"comments": [{"id": "IC1", "author": {"login": "rev"}, "body": "add lift?"},
                                          {"id": "IC2", "author": {"login": "me"}, "body": "mine"}]})
        self.assertEqual([i["key"] for i in classify(data)["items"]], ["ic:IC1"])
        marked = {"started_at": NOW.isoformat(), "handled": ["ic:IC1"], "rounds": 0}
        self.assertEqual(classify(data, marked)["items"], [])

    def test_bot_authors_are_flagged(self):
        data = make_data(pr={"comments": [{"id": "A", "author": {"login": "svc-reviewer"}, "body": "x"},
                                          {"id": "B", "author": {"login": "dependabot[bot]"}, "body": "x"},
                                          {"id": "C", "author": {"login": "alice"}, "body": "x"}]})
        self.assertEqual([i["is_bot"] for i in classify(data)["items"]], [True, True, False])

    def test_empty_review_bodies_and_approvals_are_skipped(self):
        data = make_data(pr={"reviews": [
            {"id": "R1", "author": {"login": "bot"}, "state": "COMMENTED", "body": ""},
            {"id": "R2", "author": {"login": "rev"}, "state": "CHANGES_REQUESTED", "body": "please split"},
            {"id": "R3", "author": {"login": "rev2"}, "state": "APPROVED", "body": "nice"}]})
        self.assertEqual([i["key"] for i in classify(data)["items"]], ["rv:R2"])


class CheckTests(unittest.TestCase):
    def test_failed_actions_check_includes_log_command(self):
        url = "https://github.com/o/r/actions/runs/111/job/222"
        result = classify(make_data(check_runs=[run("Pre-merge", conclusion="failure", url=url)]))
        item = result["items"][0]
        self.assertEqual(item["key"], f"ck:Pre-merge@{SHA[:12]}#1")
        self.assertEqual(item["log_cmd"], "gh run view 111 --job 222 --log-failed")

    def test_owner_approval_pending_is_ignored_and_not_pending(self):
        result = classify(make_data(check_runs=[run("Owner Approval", status="in_progress", conclusion=None),
                                                run("Build", status="queued", conclusion=None)]))
        self.assertEqual(result["status"], "idle")
        self.assertEqual(result["pending_checks"], ["Build"])

    def test_skipped_and_success_are_not_failures(self):
        result = classify(make_data(check_runs=[run("A", conclusion="skipped"), run("B")]))
        self.assertEqual(result["items"], [])

    def test_failed_rerun_resurfaces_after_first_failure_was_handled(self):
        runs = [run("Pre-merge", conclusion="failure", started="2026-10-09T20:00:00Z", rid=1),
                run("Pre-merge", conclusion="failure", started="2026-10-09T21:00:00Z", rid=2)]
        state = {"started_at": NOW.isoformat(), "handled": [f"ck:Pre-merge@{SHA[:12]}#1"], "rounds": 0}
        self.assertEqual([i["key"] for i in classify(make_data(check_runs=runs), state)["items"]],
                         [f"ck:Pre-merge@{SHA[:12]}#2"])

    def test_rerun_success_supersedes_older_failure(self):
        runs = [run("Pre-merge", conclusion="failure", started="2026-10-09T20:00:00Z", rid=1),
                run("Pre-merge", conclusion="success", started="2026-10-09T21:00:00Z", rid=2)]
        self.assertEqual(classify(make_data(check_runs=runs))["items"], [])

    def test_failed_commit_status_is_actionable(self):
        statuses = [{"context": "ci/legacy", "state": "error", "target_url": "x", "description": "boom"}]
        self.assertEqual(classify(make_data(statuses=statuses))["items"][0]["type"], "failed_check")

    def test_merge_conflict_is_actionable(self):
        result = classify(make_data(pr={"mergeable": "CONFLICTING"}))
        self.assertEqual(result["items"][0]["type"], "merge_conflict")


class StopTests(unittest.TestCase):
    def test_review_decision_approved_stops_even_with_open_items(self):
        result = classify(make_data(pr={"reviewDecision": "APPROVED"}, threads=[thread("rev")]))
        self.assertEqual((result["status"], result["stop_reason"]), ("stop", "approved"))
        self.assertEqual(len(result["items"]), 1)

    def test_one_approval_does_not_stop_when_more_reviews_are_required(self):
        data = make_data(pr={"reviews": [{"id": "R", "author": {"login": "rev"}, "state": "APPROVED", "body": ""}]})
        self.assertIsNone(classify(data)["stop_reason"])

    def test_latest_review_approval_without_branch_protection(self):
        reviews = [{"id": "R1", "author": {"login": "rev"}, "state": "CHANGES_REQUESTED", "body": ""},
                   {"id": "R2", "author": {"login": "rev"}, "state": "APPROVED", "body": ""}]
        data = make_data(pr={"reviewDecision": "", "reviews": reviews})
        self.assertEqual(classify(data)["stop_reason"], "approved")

    def test_self_approval_does_not_count(self):
        reviews = [{"id": "R1", "author": {"login": "me"}, "state": "APPROVED", "body": ""}]
        self.assertIsNone(classify(make_data(pr={"reviewDecision": None, "reviews": reviews}))["stop_reason"])

    def test_merged_and_closed_stop(self):
        self.assertEqual(classify(make_data(pr={"state": "MERGED"}))["stop_reason"], "merged")
        self.assertEqual(classify(make_data(pr={"state": "CLOSED"}))["stop_reason"], "closed")

    def test_max_rounds_and_expiry_stop(self):
        self.assertEqual(classify(make_data(), {"started_at": NOW.isoformat(), "handled": [], "rounds": 5})
                         ["stop_reason"], "max_rounds")
        old = (NOW - timedelta(hours=25)).isoformat()
        self.assertEqual(classify(make_data(), {"started_at": old, "handled": [], "rounds": 0})
                         ["stop_reason"], "expired")


class CliTests(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.env = mock.patch.dict("os.environ", {"POST_PR_STATE_DIR": self.tmp.name})
        self.env.start()

    def tearDown(self):
        self.env.stop()
        self.tmp.cleanup()

    def test_mark_accumulates_keys_and_rounds_then_reset_clears(self):
        url = "https://github.com/o/r/pull/7"
        with mock.patch("builtins.print"):
            pr_watch.main(["mark", "th:1", "--pr", url, "--pushed"])
            pr_watch.main(["mark", "ic:2", "--pr", url])
        state = pr_watch.load_state(pr_watch.state_path("o", "r", 7))
        self.assertEqual((state["handled"], state["rounds"]), (["ic:2", "th:1"], 1))
        with mock.patch("builtins.print"):
            pr_watch.main(["reset", "--pr", url])
        self.assertFalse(pr_watch.state_path("o", "r", 7).exists())

    def test_wait_returns_on_first_actionable_poll(self):
        data = make_data(threads=[thread("rev")])
        with mock.patch.object(pr_watch, "fetch", return_value=data), mock.patch("time.sleep") as sleep, \
                mock.patch("builtins.print") as out:
            pr_watch.main(["wait", "--pr", "https://github.com/o/r/pull/7"])
        sleep.assert_not_called()
        self.assertIn('"status": "action"', out.call_args[0][0])

    def test_wait_polls_until_idle_budget_runs_out(self):
        with mock.patch.object(pr_watch, "fetch", return_value=make_data()), \
                mock.patch("time.sleep") as sleep, mock.patch("builtins.print") as out:
            pr_watch.main(["wait", "--pr", "https://github.com/o/r/pull/7", "--interval", "0",
                           "--max-seconds", "0"])
        self.assertIn('"status": "idle"', out.call_args[0][0])
        self.assertLessEqual(sleep.call_count, 1)

    def test_wait_tolerates_transient_gh_errors(self):
        data = make_data(threads=[thread("rev")])
        effects = [pr_watch.GhError("blip"), data]
        with mock.patch.object(pr_watch, "fetch", side_effect=effects), mock.patch("time.sleep"), \
                mock.patch("builtins.print") as out, mock.patch("sys.stderr"):
            pr_watch.main(["wait", "--pr", "https://github.com/o/r/pull/7", "--interval", "0"])
        self.assertIn('"status": "action"', out.call_args[0][0])


if __name__ == "__main__":
    unittest.main()
