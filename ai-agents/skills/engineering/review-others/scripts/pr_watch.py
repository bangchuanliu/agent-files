#!/usr/bin/env python3
"""Watch a PR you reviewed until it needs your attention again, with no model tokens between polls.

Polls the PR through `gh` and exits with one JSON object on stdout whose `status` is one of:

  addressed    every review thread you took part in is resolved, outdated by a later push,
               or last answered by someone else (bots excluded); with no threads, a new push
  rerequested  the author re-requested your review
  approved     your latest review is an approval
  merged       the PR was merged
  closed       the PR was closed without merging
  timeout      --timeout-hours elapsed; `open_threads` lists what is still waiting
  error        `gh` failed on --max-errors consecutive polls; `error` holds the last message

`--once` prints one snapshot (status `waiting` when nothing is due) and exits.
"""
import argparse
import json
import re
import subprocess
import sys
import time

QUERY = """
query($owner: String!, $repo: String!, $number: Int!) {
  viewer { login }
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $number) {
      state
      headRefOid
      reviewRequests(first: 100) { nodes { requestedReviewer { ... on User { login } } } }
      reviews(last: 100) { nodes { author { login } state commit { oid } } }
      reviewThreads(first: 100) {
        nodes {
          isResolved
          isOutdated
          path
          line
          comments(first: 100) { nodes { url author { __typename login } } }
        }
      }
    }
  }
}
"""


def parse_ref(ref):
    m = re.match(r"(?:https?://[^/]+/)?([^/#\s]+)/([^/#\s]+?)(?:/pull/|#)(\d+)", ref)
    if not m:
        raise ValueError(f"cannot parse PR ref {ref!r}; use a PR URL or owner/repo#n")
    return m.group(1), m.group(2), int(m.group(3))


def fetch(owner, repo, number):
    out = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={QUERY}",
         "-F", f"owner={owner}", "-F", f"repo={repo}", "-F", f"number={number}"],
        capture_output=True, text=True, check=True,
    ).stdout
    data = json.loads(out)["data"]
    return data["viewer"]["login"], data["repository"]["pullRequest"]


def is_bot(author, ignore):
    if not author:
        return True
    login = author.get("login") or ""
    return (author.get("__typename") == "Bot" or login.endswith("[bot]")
            or any(re.search(p, login) for p in ignore))


def evaluate(me, pr, ignore=()):
    """Return (status, details) for one snapshot; status None means keep waiting."""
    if pr["state"] == "MERGED":
        return "merged", {}
    if pr["state"] == "CLOSED":
        return "closed", {}
    mine = [r for r in pr["reviews"]["nodes"]
            if (r.get("author") or {}).get("login") == me and r["state"] != "PENDING"]
    last = mine[-1] if mine else None
    if last and last["state"] == "APPROVED":
        return "approved", {}
    requested = {(n.get("requestedReviewer") or {}).get("login") for n in pr["reviewRequests"]["nodes"]}
    open_threads, involved = [], 0
    for t in pr["reviewThreads"]["nodes"]:
        people = [c for c in t["comments"]["nodes"] if not is_bot(c.get("author"), ignore)]
        if not any(c["author"]["login"] == me for c in people):
            continue
        involved += 1
        if t["isResolved"] or t["isOutdated"] or people[-1]["author"]["login"] != me:
            continue
        open_threads.append({"path": t["path"], "line": t["line"], "url": people[-1]["url"]})
    details = {"open_threads": open_threads}
    if me in requested:
        return "rerequested", details
    if involved and not open_threads:
        return "addressed", details
    if not involved and last and last.get("commit") and last["commit"]["oid"] != pr["headRefOid"]:
        return "addressed", details
    return None, details


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("pr", help="PR URL or owner/repo#n, addressed through the base repo")
    ap.add_argument("--interval-min", type=float, default=20)
    ap.add_argument("--timeout-hours", type=float, default=24)
    ap.add_argument("--max-errors", type=int, default=3)
    ap.add_argument("--ignore-author", action="append", default=[],
                    help="regex for bot-account logins to ignore (repeatable); GitHub Apps are always ignored")
    ap.add_argument("--once", action="store_true", help="take one snapshot and exit")
    args = ap.parse_args()
    owner, repo, number = parse_ref(args.pr)
    deadline = time.time() + args.timeout_hours * 3600
    errors, details, head = 0, {}, None
    while True:
        status = None
        try:
            me, pr = fetch(owner, repo, number)
            errors = 0
            head = pr["headRefOid"]
            status, details = evaluate(me, pr, args.ignore_author)
        except (subprocess.CalledProcessError, KeyError, TypeError, json.JSONDecodeError) as e:
            errors += 1
            msg = (getattr(e, "stderr", None) or repr(e)).strip()
            if errors >= args.max_errors or args.once:
                print(json.dumps({"status": "error", "pr": args.pr, "error": msg}))
                return 1
        if status or args.once:
            print(json.dumps({"status": status or "waiting", "pr": args.pr, "head": head, **details}))
            return 0
        if time.time() >= deadline:
            print(json.dumps({"status": "timeout", "pr": args.pr, "head": head, **details}))
            return 0
        time.sleep(min(args.interval_min * 60, max(deadline - time.time(), 1)))


if __name__ == "__main__":
    sys.exit(main())
