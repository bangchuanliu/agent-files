#!/usr/bin/env python3
"""Unit tests for pr_watch.evaluate and parse_ref; no network."""
import unittest

from pr_watch import evaluate, parse_ref

ME = "me"


def comment(login, typename="User"):
    return {"url": f"https://x/{login}", "author": {"__typename": typename, "login": login}}


def thread(*logins, resolved=False, outdated=False):
    return {"isResolved": resolved, "isOutdated": outdated, "path": "a.py", "line": 3,
            "comments": {"nodes": [comment(*l) if isinstance(l, tuple) else comment(l) for l in logins]}}


def pr(threads=(), state="OPEN", reviews=None, requested=(), head="h2"):
    return {
        "state": state,
        "headRefOid": head,
        "reviewRequests": {"nodes": [{"requestedReviewer": {"login": r}} for r in requested]},
        "reviews": {"nodes": reviews if reviews is not None
                    else [{"author": {"login": ME}, "state": "COMMENTED", "commit": {"oid": "h1"}}]},
        "reviewThreads": {"nodes": list(threads)},
    }


class Evaluate(unittest.TestCase):
    def test_merged_and_closed(self):
        self.assertEqual(evaluate(ME, pr(state="MERGED"))[0], "merged")
        self.assertEqual(evaluate(ME, pr(state="CLOSED"))[0], "closed")

    def test_my_approval_stops(self):
        reviews = [{"author": {"login": ME}, "state": "APPROVED", "commit": {"oid": "h1"}}]
        self.assertEqual(evaluate(ME, pr(reviews=reviews))[0], "approved")

    def test_waits_while_my_comment_is_last(self):
        status, details = evaluate(ME, pr([thread(ME), thread(ME, "author")]))
        self.assertIsNone(status)
        self.assertEqual(len(details["open_threads"]), 1)

    def test_addressed_by_reply_resolve_or_outdated(self):
        threads = [thread(ME, "author"), thread(ME, resolved=True), thread(ME, outdated=True)]
        self.assertEqual(evaluate(ME, pr(threads))[0], "addressed")

    def test_my_reply_after_theirs_reopens(self):
        self.assertIsNone(evaluate(ME, pr([thread(ME, "author", ME)]))[0])

    def test_reply_in_others_thread_counts(self):
        self.assertIsNone(evaluate(ME, pr([thread("other", ME)]))[0])
        self.assertEqual(evaluate(ME, pr([thread("other", ME, "author")]))[0], "addressed")

    def test_bot_replies_do_not_address(self):
        threads = [thread(ME, ("ci", "Bot")), thread(ME, "svc-review_X"), thread(ME, "lint[bot]")]
        self.assertIsNone(evaluate(ME, pr(threads[:1]))[0])
        self.assertIsNone(evaluate(ME, pr(threads[1:2]), ignore=[r"^svc-"])[0])
        self.assertIsNone(evaluate(ME, pr(threads[2:]))[0])

    def test_unrelated_threads_ignored(self):
        self.assertIsNone(evaluate(ME, pr([thread("other")], head="h1"))[0])

    def test_rerequest_fires_even_with_open_threads(self):
        status, details = evaluate(ME, pr([thread(ME)], requested=[ME]))
        self.assertEqual(status, "rerequested")
        self.assertEqual(len(details["open_threads"]), 1)

    def test_no_threads_waits_for_push(self):
        self.assertIsNone(evaluate(ME, pr(head="h1"))[0])
        self.assertEqual(evaluate(ME, pr(head="h2"))[0], "addressed")

    def test_pending_review_ignored(self):
        reviews = [{"author": {"login": ME}, "state": "COMMENTED", "commit": {"oid": "h1"}},
                   {"author": {"login": ME}, "state": "PENDING", "commit": {"oid": "h2"}}]
        self.assertEqual(evaluate(ME, pr(reviews=reviews, head="h2"))[0], "addressed")


class ParseRef(unittest.TestCase):
    def test_forms(self):
        self.assertEqual(parse_ref("https://github.com/o/r/pull/12"), ("o", "r", 12))
        self.assertEqual(parse_ref("o/r#12"), ("o", "r", 12))
        with self.assertRaises(ValueError):
            parse_ref("#12")


if __name__ == "__main__":
    unittest.main()
