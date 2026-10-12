#!/usr/bin/env python3
"""Poll a GitHub PR and report the review comments, failed checks and conflicts that need attention.

Subcommands (all print one JSON object to stdout):
  status  One snapshot of the PR: stop reason, actionable items, pending checks.
  wait    Poll every --interval seconds until something is actionable, a stop
          condition is hit, or --max-seconds elapses (then status is "idle").
  mark    Record item keys as handled (and optionally count a pushed fix round).
  reset   Forget handled items, round count and watch start time for the PR.

Status values: "stop" (approved/merged/closed/max_rounds/expired), "action"
(new review threads, comments, failed checks or merge conflicts) or "idle".
State lives in $POST_PR_STATE_DIR (default ~/.cache/post-pr), one file per PR.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

FAILED_CONCLUSIONS = {"failure", "timed_out", "cancelled", "action_required", "startup_failure"}
FAILED_STATUS_STATES = {"failure", "error"}
# Human-gated checks: they stay pending/failed until a reviewer approves, so code changes cannot fix them.
DEFAULT_IGNORE_CHECKS = r"^(Owner Approval)$"
JOB_URL_RE = re.compile(r"/actions/runs/(\d+)/job/(\d+)")
PR_URL_RE = re.compile(r"github\.com/([^/]+)/([^/]+)/pull/(\d+)")
# Service accounts named svc-*, GitHub Apps ending in [bot], and *-bot logins.
BOT_LOGIN_RE = re.compile(r"^svc-|\[bot\]$|-bot$")
SUMMARY_LIMIT = 1500

THREADS_QUERY = """
query($owner: String!, $name: String!, $number: Int!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    pullRequest(number: $number) {
      reviewThreads(first: 100, after: $cursor) {
        pageInfo { hasNextPage endCursor }
        nodes {
          id isResolved isOutdated path line
          comments(first: 50) {
            nodes { databaseId author { login } body createdAt url }
          }
        }
      }
    }
  }
}
"""


class GhError(RuntimeError):
    pass


def gh(args: list[str]) -> str:
    proc = subprocess.run(["gh", *args], capture_output=True, text=True)
    if proc.returncode != 0:
        raise GhError(f"gh {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout


def gh_json_lines(args: list[str]) -> list[dict]:
    return [json.loads(line) for line in gh(args).splitlines() if line.strip()]


# ---------------------------------------------------------------- state

def state_path(owner: str, repo: str, number: int) -> Path:
    root = Path(os.environ.get("POST_PR_STATE_DIR", Path.home() / ".cache" / "post-pr"))
    return root / f"{owner}__{repo}__{number}.json"


def load_state(path: Path) -> dict:
    if path.exists():
        return json.loads(path.read_text())
    return {"started_at": None, "handled": [], "rounds": 0}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=2, sort_keys=True))
    tmp.replace(path)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


# ---------------------------------------------------------------- fetch

def resolve_pr(pr: str | None, repo: str | None) -> tuple[str, str, int]:
    if pr and PR_URL_RE.search(pr):
        owner, name, number = PR_URL_RE.search(pr).groups()
        return owner, name, int(number)
    args = ["pr", "view", "--json", "url"]
    if pr:
        args.insert(2, pr)
    if repo:
        args += ["-R", repo]
    url = json.loads(gh(args))["url"]
    owner, name, number = PR_URL_RE.search(url).groups()
    return owner, name, int(number)


def fetch(owner: str, repo: str, number: int) -> dict:
    """Collect everything classify() needs, using only read-only gh calls."""
    fields = "number,url,title,state,isDraft,reviewDecision,headRefName,headRefOid,mergeable,author,comments,reviews"
    pr = json.loads(gh(["pr", "view", str(number), "-R", f"{owner}/{repo}", "--json", fields]))

    threads: list[dict] = []
    cursor = None
    while True:
        args = ["api", "graphql", "-f", f"query={THREADS_QUERY}", "-F", f"owner={owner}",
                "-F", f"name={repo}", "-F", f"number={number}"]
        if cursor:
            args += ["-F", f"cursor={cursor}"]
        page = json.loads(gh(args))["data"]["repository"]["pullRequest"]["reviewThreads"]
        threads += page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]

    sha = pr["headRefOid"]
    check_runs = gh_json_lines(["api", "--paginate", f"repos/{owner}/{repo}/commits/{sha}/check-runs?per_page=100",
                                "--jq", ".check_runs[]"])
    statuses = gh_json_lines(["api", f"repos/{owner}/{repo}/commits/{sha}/status", "--jq", ".statuses[]"])
    me = gh(["api", "user", "--jq", ".login"]).strip()
    return {"owner": owner, "repo": repo, "pr": pr, "threads": threads,
            "check_runs": check_runs, "statuses": statuses, "me": me}


# ---------------------------------------------------------------- classify (pure)

def is_approved(pr: dict, me: str) -> bool:
    decision = pr.get("reviewDecision") or ""
    if decision:
        return decision == "APPROVED"
    # No branch protection: fall back to each reviewer's latest decisive review.
    latest: dict[str, str] = {}
    for review in pr.get("reviews") or []:
        login = (review.get("author") or {}).get("login", "")
        if login != me and review.get("state") in {"APPROVED", "CHANGES_REQUESTED", "DISMISSED"}:
            latest[login] = review["state"]
    return "APPROVED" in latest.values() and "CHANGES_REQUESTED" not in latest.values()


def latest_check_runs(check_runs: list[dict]) -> list[dict]:
    """Reruns create several runs with the same name; keep the newest of each."""
    newest: dict[str, dict] = {}
    for run in check_runs:
        key = run["name"]
        if key not in newest or (run.get("started_at") or "", run.get("id", 0)) > (
                newest[key].get("started_at") or "", newest[key].get("id", 0)):
            newest[key] = run
    return list(newest.values())


def is_bot(login: str | None) -> bool:
    return bool(login and BOT_LOGIN_RE.search(login))


def check_item(run: dict, sha: str) -> dict:
    output = run.get("output") or {}
    summary = "\n".join(s for s in (output.get("title"), output.get("summary"), output.get("text")) if s)
    url = run.get("details_url") or run.get("html_url") or ""
    # Run id in the key: a rerun that fails again is a new item, not an already-handled one.
    item = {"key": f"ck:{run['name']}@{sha[:12]}#{run.get('id')}", "type": "failed_check", "name": run["name"],
            "conclusion": run.get("conclusion"), "app": (run.get("app") or {}).get("slug"),
            "url": url, "summary": summary[:SUMMARY_LIMIT]}
    match = JOB_URL_RE.search(url)
    if match:
        item["run_id"], item["job_id"] = match.groups()
        item["log_cmd"] = f"gh run view {item['run_id']} --job {item['job_id']} --log-failed"
    return item


def classify(data: dict, state: dict, now: datetime, ignore_checks: str = DEFAULT_IGNORE_CHECKS,
             max_rounds: int = 5, max_hours: float = 24) -> dict:
    pr, me = data["pr"], data["me"]
    sha = pr["headRefOid"]
    handled = set(state.get("handled", []))
    ignore_re = re.compile(ignore_checks) if ignore_checks else None
    items: list[dict] = []

    for thread in data["threads"]:
        comments = thread["comments"]["nodes"]
        if thread["isResolved"] or not comments:
            continue
        last = comments[-1]
        key = f"th:{last['databaseId']}"
        # The ball is in the reviewer's court once our reply is the latest comment.
        if (last.get("author") or {}).get("login") == me or key in handled:
            continue
        items.append({"key": key, "type": "review_thread", "thread_id": thread["id"],
                      "reply_to_comment_id": comments[0]["databaseId"], "path": thread.get("path"),
                      "line": thread.get("line"), "outdated": thread.get("isOutdated", False),
                      "url": last.get("url"), "is_bot": is_bot((comments[0].get("author") or {}).get("login")),
                      "comments": [{"author": (c.get("author") or {}).get("login"), "body": c["body"],
                                    "at": c["createdAt"]} for c in comments]})

    for comment in pr.get("comments") or []:
        author = (comment.get("author") or {}).get("login")
        key = f"ic:{comment['id']}"
        if author == me or key in handled:
            continue
        items.append({"key": key, "type": "issue_comment", "author": author, "is_bot": is_bot(author), "body": comment.get("body", ""),
                      "at": comment.get("createdAt"), "url": comment.get("url")})

    for review in pr.get("reviews") or []:
        author = (review.get("author") or {}).get("login")
        key = f"rv:{review['id']}"
        if author == me or key in handled or not (review.get("body") or "").strip():
            continue
        if review.get("state") not in {"COMMENTED", "CHANGES_REQUESTED"}:
            continue
        items.append({"key": key, "type": "review_body", "author": author, "is_bot": is_bot(author), "state": review["state"],
                      "body": review["body"], "at": review.get("submittedAt")})

    pending: list[str] = []
    for run in latest_check_runs(data["check_runs"]):
        if ignore_re and ignore_re.search(run["name"]):
            continue
        if run.get("status") != "completed":
            pending.append(run["name"])
        elif (run.get("conclusion") or "").lower() in FAILED_CONCLUSIONS:
            item = check_item(run, sha)
            if item["key"] not in handled:
                items.append(item)
    for status in data["statuses"]:
        name = status["context"]
        if ignore_re and ignore_re.search(name):
            continue
        if status["state"] == "pending":
            pending.append(name)
        elif status["state"] in FAILED_STATUS_STATES:
            key = f"ck:{name}@{sha[:12]}"
            if key not in handled:
                items.append({"key": key, "type": "failed_check", "name": name, "conclusion": status["state"],
                              "url": status.get("target_url") or "", "summary": status.get("description") or ""})

    if pr.get("mergeable") == "CONFLICTING" and f"cf:{sha[:12]}" not in handled:
        items.append({"key": f"cf:{sha[:12]}", "type": "merge_conflict"})

    started = parse_ts(state["started_at"]) if state.get("started_at") else now
    stop = None
    if pr["state"] == "MERGED":
        stop = "merged"
    elif pr["state"] == "CLOSED":
        stop = "closed"
    elif is_approved(pr, me):
        stop = "approved"
    elif state.get("rounds", 0) >= max_rounds:
        stop = "max_rounds"
    elif (now - started).total_seconds() > max_hours * 3600:
        stop = "expired"

    return {"status": "stop" if stop else ("action" if items else "idle"), "stop_reason": stop,
            "pr": {"url": pr["url"], "title": pr.get("title"), "state": pr["state"], "draft": pr.get("isDraft"),
                   "review_decision": pr.get("reviewDecision"), "head_branch": pr.get("headRefName"),
                   "head_sha": sha, "mergeable": pr.get("mergeable")},
            "me": me, "rounds": state.get("rounds", 0), "max_rounds": max_rounds,
            "pending_checks": sorted(set(pending)), "items": items}


# ---------------------------------------------------------------- commands

def snapshot(args, path: Path, owner: str, repo: str, number: int) -> dict:
    state = load_state(path)
    if not state.get("started_at"):
        state["started_at"] = now_utc().isoformat()
        save_state(path, state)
    return classify(fetch(owner, repo, number), state, now_utc(), args.ignore_checks,
                    args.max_rounds, args.max_hours)


def cmd_wait(args, path, owner, repo, number) -> dict:
    deadline = time.monotonic() + args.max_seconds
    errors = 0
    while True:
        try:
            result = snapshot(args, path, owner, repo, number)
            errors = 0
        except GhError as exc:
            # Tolerate transient network/API blips during long watches; fail loudly if they persist.
            errors += 1
            if errors >= 3:
                raise
            print(f"warning: {exc}", file=sys.stderr)
            result = None
        if result and result["status"] != "idle":
            return result
        if time.monotonic() + args.interval > deadline:
            return result or {"status": "idle", "items": [], "error": "last poll failed"}
        time.sleep(args.interval)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("command", choices=["status", "wait", "mark", "reset"])
    parser.add_argument("keys", nargs="*", help="item keys for 'mark'")
    parser.add_argument("--pr", help="PR number or URL (default: PR of the current branch)")
    parser.add_argument("--repo", help="owner/repo (default: current repo)")
    parser.add_argument("--interval", type=int, default=180, help="seconds between polls (wait)")
    parser.add_argument("--max-seconds", type=int, default=540, help="max seconds one 'wait' call blocks")
    parser.add_argument("--max-rounds", type=int, default=5, help="stop after this many pushed fix rounds")
    parser.add_argument("--max-hours", type=float, default=24, help="stop watching after this many hours")
    parser.add_argument("--ignore-checks", default=DEFAULT_IGNORE_CHECKS, help="regex of check names to ignore")
    parser.add_argument("--pushed", action="store_true", help="with 'mark': count one pushed fix round")
    args = parser.parse_args(argv)

    try:
        owner, repo, number = resolve_pr(args.pr, args.repo)
        path = state_path(owner, repo, number)
        if args.command == "reset":
            path.unlink(missing_ok=True)
            result = {"reset": str(path)}
        elif args.command == "mark":
            state = load_state(path)
            state["handled"] = sorted(set(state.get("handled", [])) | set(args.keys))
            state["rounds"] = state.get("rounds", 0) + (1 if args.pushed else 0)
            save_state(path, state)
            result = {"marked": args.keys, "rounds": state["rounds"]}
        elif args.command == "status":
            result = snapshot(args, path, owner, repo, number)
        else:
            result = cmd_wait(args, path, owner, repo, number)
    except GhError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}))
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
