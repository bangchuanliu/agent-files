---
name: review-others
kind: orchestrator
agents: claude, copilot
description: "Peer PR review: review someone else's GitHub PR, a requested-review queue, or a repo batch. Branches: single PR; batch queue; confirmed publish. NOT for: your own PR or comments on it -> use review-self."
---

# Review Others' PRs

Orchestrator for the **queue around** a code review, not the review itself. This skill finds the PRs, hands each one to **your own code-review capability**, and posts what comes back.

It owns finding PRs, classifying Initial vs Follow-up, gating on human confirmation, routing findings into existing reviewer threads or new inline comments, and posting each one inline at its `file:line`. It owns **no review criteria**: what counts as a bug, which language conventions apply, and how severe a finding is are yours to judge from the diff and the repo's own guidelines.

Reviews read the remote diff through `gh pr diff`, so the local working tree stays untouched - no checkout, and nothing this skill writes ever lands inside the reviewed repo. Every GitHub interaction goes through `gh`; when a `gh` call fails mid-review (auth expiry, rate limit), stop and report it rather than continuing on partial data.

Each finding you produce carries this shape, which is all Steps 5-6 need:

| Field | Meaning |
|---|---|
| `file` | path relative to the repo root |
| `line` | `L42`, or `L29-L31` for a range. **Always on lines the diff marks `+`** - GitHub rejects an inline comment anywhere else |
| `description` | the concern, in prose |
| `suggestion` | a committable fix, when you have one under ~6 lines |
| `label` | short tag rendered as `**[{label}]**` on the comment - `bug`, `logic-error`, `security`, `guideline-violation`, `nit`, or whatever fits |
| `class` | `blocking`, `non-blocking`, or `nit` - the only severity vocabulary this skill uses |
| `thread_reply_to` | set only when the finding continues another reviewer's thread: their comment's `top_id`, per Step 4c |
| `thread_reply_reviewer` | set alongside `thread_reply_to`: that reviewer's login, which the reply template names |

## Autonomy and the posting gate

Steps 1-4 and 6-7 run **hands-free**: infer every unspecified knob from the defaults below and keep going, with no clarifying questions, no plan mode, and no "should I continue?" pauses. When an input is genuinely unresolvable, fail fast with a one-line error naming the fix. Verify anything you need to check by running it yourself via Bash.

Step 5 is the **single gate**, and it is **fail-closed**. Posting writes to someone else's PR, an irreversible side effect on another person's work, so it proceeds only on an explicit affirmative human response. Every other outcome is a **dry run**: present the findings, write the report, stop.

| Step 5 outcome | Result |
|---|---|
| `yes` / `y` / `post` / `drop #N then post` / an edit instruction | post (Step 6) |
| `no`, silence, an ambiguous reply, or an autopilot sentinel ("The user is not available to respond", "work autonomously") | dry run |
| the request contains "stop before post", "don't post", "dry run", "review only", or `--no-post` | dry run; the gate is never asked |

Fail-closed **overrides autopilot**: "bias to action" never authorizes writing to another person's PR. When you are unsure whether a response authorizes posting, it does not.

## Usage

```bash
/review-others                                    # PRs awaiting your review in the current repo
/review-others all                                # every open PR in the current repo that isn't yours
/review-others example-repo                       # bare name -> $REVIEW_DEFAULT_ORG/example-repo
/review-others org/example-repo
/review-others https://github.com/org/repo/pull/123
/review-others org/repo#123
/review-others #123                               # current repo
/review-others "review this PR"                   # PR for the current branch
/review-others --author=someone-else              # PRs by a specific author
```

Flags: `--ship` (approve after confirmation, single PR only), `--no-post` (dry run), `--limit=N` (default 20), `--author=NAME`.

---

## Step 1: Determine your identity

```bash
gh api user --jq '.login'
```

This is `MY_LOGIN`. Every PR authored by this user is excluded from review.

If `gh` is missing from PATH, try `/opt/homebrew/bin/gh` and `/usr/local/bin/gh` and use the full path. If `gh` is absent or unauthenticated, stop and tell the user to run `brew install gh && gh auth login`.

## Step 2: Parse arguments and build the queue

**Mode selection is fail-closed toward single PR mode.** Look for a single-PR reference first, before any batch handling. Batch mode is reachable only when the request carries **no** PR identifier at all. When the user named one PR, exactly one PR is reviewed - related, stale or convenient neighbours stay out of the queue.

### Tokenize first

Strip and record, in order, before deciding the mode:

1. **Flags** - `--ship`, `--no-post`, `--limit=N`, `--author=NAME`. Modifiers, never repo names or PR references.
2. **Reserved mode token** - a standalone `all`.
3. What remains is the positional argument: a PR reference, a repo, or nothing.

A flag or `all` is never a repo: `--limit=3` and `all` are parse bugs, not repository names.

### Single PR mode

Scan the **entire** user request for the forms below, not just a lone argument token - surrounding prose does not disable single PR mode. The first match wins; extract `REPO` and `PR_NUMBER` from it.

| Reference form | Example | Resolves to |
|---|---|---|
| PR URL, any suffix (`/files`, `/commits`, `#discussion_r...`, `?w=1`) | `https://github.com/org/repo/pull/123/files` | `org/repo` #123 |
| Qualified ref | `org/repo#123` | `org/repo` #123 |
| Bare ref | `#123`, `PR 123`, `pull 123`, `pr/123` | current repo, #123 |
| Current branch | "this PR", "the PR I'm on" | `gh pr view --json number,url,baseRepository,author` |

`REPO` is always the **base** repo that owns the PR, never the head or fork repo: a fork PR from `alice/fork` into `org/repo` is `org/repo#123`. Take it from the PR URL or from `baseRepository`, since `headRepository` would target the wrong `/pulls/` endpoint.

**Author gate - every single-PR form, current-branch included.** Before Step 4:

```bash
gh pr view {PR_NUMBER} --repo {REPO} --json author,state,headRefOid
```

When `author.login == MY_LOGIN`, stop and route the user to `review-self`: this skill never reviews your own PR, and the batch author filter does not run here. When `state` is not `OPEN`, report it and stop.

Once the reference matches and the author gate passes, set `REVIEW_LIMIT=1` and bind `PR_LIST` to that one PR. Single PR mode then runs no `gh pr list` and no PR search query (`review-requested:@me`, `is:open`, `--author`), skips the already-reviewed filter entirely (the user asked for this PR, so review it even when you already reviewed or approved it, and note the prior review in the output), and expands the queue for no other reason.

`--ship` is a **modifier**, not a reference. It sets `SHIP_MODE=true` (approve after review, per Step 6) and requires a single PR:

| `--ship` combined with | Behaviour |
|---|---|
| a single-PR reference | single mode, ship |
| no reference at all | resolve the current-branch PR; when that fails, stop with a one-line error |
| a batch trigger (`all`, `--author=`, a repo name) | ignore `--ship` and warn |

An unresolvable reference (bare `#123` outside a git repo, no current-branch PR) stops with a one-line error naming the fix - "rerun as `org/repo#123`". Steps 1-4 are question-free, so open no dialogue, and never fall back to batch mode.

### Batch mode

Reachable only when tokenization left no single-PR reference. Bare repository names are allowed only when `REVIEW_DEFAULT_ORG` is set; otherwise require `owner/repo`. Repo resolution, the per-mode `gh pr list` queries, the post-fetch pipeline, the already-reviewed filter, and Step 3's announcement are in [`references/batch-queue.md`](references/batch-queue.md).

## Step 3: Announce the PR list

Batch mode only, per `references/batch-queue.md`. Single PR mode goes straight to Step 4.

## Step 4: Review each queued PR

`4a` classifies the mode and `4b` gathers the other reviewers' comments; both feed `4c`, so run them for every queued PR before reviewing any of it.

### 4a: Classify the review mode

In batch mode the already-reviewed filter already fetched the history. In single PR mode that filter never ran, so fetch it here - for classification only, never to skip. Fetch **all** comments rather than just your own: a reply from the author is what makes a PR Mode B, and the author is someone else.

```bash
gh api repos/{REPO}/pulls/{PR_NUMBER}/reviews  --jq '[.[] | select(.user.login == "'$MY_LOGIN'")]'
gh api repos/{REPO}/pulls/{PR_NUMBER}/comments --jq '[.[] | {id, user: .user.login, in_reply_to_id, path, line, body}]'
```

Your prior concerns are the comments where `user == MY_LOGIN`; a concern has been replied to when some other comment's `in_reply_to_id` equals its `id`.

- **Mode A - Initial Review** - no prior review or comment from `MY_LOGIN` on this PR.
- **Mode B - Follow-up Review** - any prior review or comment from `MY_LOGIN` exists. Keep those prior concerns: `4d` scores its audit against them. Reply state only scopes that audit, never the mode - an unreplied concern is audited as `REPLY_ONLY` / `NOT_ADDRESSED` rather than excluded.

For **Mode B only**, confirm something meaningful changed:

```bash
MY_LAST_SHA=$(gh api repos/{REPO}/pulls/{PR_NUMBER}/reviews \
  --jq '[.[] | select(.user.login == "'$MY_LOGIN'")] | sort_by(.submitted_at) | last | .commit_id // empty')
HEAD_SHA=$(gh api repos/{REPO}/pulls/{PR_NUMBER} --jq '.head.sha')
```

When `MY_LAST_SHA == HEAD_SHA` and no new replies-to-me exist, skip the PR with reason "no meaningful updates since last review" - **batch mode only**. In single PR mode the user asked for this PR explicitly: review it anyway and note "no new commits since my last review" in the Step 5 presentation.

### 4b: Fetch existing review context

For every PR selected for review, fetch the reviews and inline comments belonging to **other** users, so `4c` can defer to them and Step 6 can thread replies correctly. Step 2's already-reviewed filter already called these endpoints; when those responses are cached, partition them by `user.login != MY_LOGIN` instead of calling again.

```bash
gh api repos/{REPO}/pulls/{PR_NUMBER}/reviews \
  --jq '[.[] | select(.user.login != "MY_LOGIN") | {reviewer: .user.login, state: .state, body: .body}]'

gh api repos/{REPO}/pulls/{PR_NUMBER}/comments \
  --jq '[.[] | select(.user.login != "MY_LOGIN") | {id: .id, top_id: (.in_reply_to_id // .id), reviewer: .user.login, path: .path, line: .line, body: .body, is_reply: (.in_reply_to_id != null)}]'
```

Store the pair as `PR_REVIEW_CONTEXT[PR_NUMBER]`. `top_id` is the thread root, which `4c` copies into `thread_reply_to`. A comment whose `line` is null is detached from the current diff - keep the null and match threads only against the rest.

### 4c: Review, using your own code-review capability

**You are the reviewer.** Read the diff and apply your own judgement - this skill delegates the reviewing to you, not to a named agent.

For a batch, fan out if your host supports parallel workers: one worker per PR, all launched in a single message, each given the constraints below. Review in sequence otherwise. Use any worker that can read the remote PR diff; if none exists, do the review directly.

Worker selection trap: prefer a worker that reviews **a pull request**. A worker that reviews staged, unstaged, or branch-local changes reads the local checkout, which this skill never updates, so it can report on the wrong branch. If only branch-local review exists, fetch and review the PR diff directly in the current session.

Fetch the diff and metadata:

```bash
gh pr diff {PR_NUMBER} --repo {REPO}
gh pr view {PR_NUMBER} --repo {REPO} --json title,body,files,headRefOid,labels
```

Then apply your own judgement, under four constraints - each about **what this skill can post**, never about what counts as good code:

- **Read the repo's own rules first.** Load whichever of `AGENTS.md`, `CLAUDE.md`, `.github/copilot-instructions.md`, and other repository-local review guideline files exist. They are the source of truth for the project's conventions.
- **Anchor where the concern lives.** Point `line` at the call, expression or block your description actually names - not at an import or declaration that merely happens to be the first added line in the hunk. (That the anchor must be an added line is a posting constraint; see the finding shape above.)
- **Reserve `blocking`** for what you can name a concrete failure mode or quote a rule for. Everything softer is `non-blocking` or `nit`, and anything you cannot confirm from the diff stays unreported.
- **Defer to whoever raised it first.** Check `PR_REVIEW_CONTEXT[PR_NUMBER]` before recording a finding. When someone already raised the concern, drop yours; when you have a real addendum, set `thread_reply_to` to their `top_id` and `thread_reply_reviewer` to their login, and Step 6 posts it inside their thread. Thread only a genuine continuation - same code, same property - since a misplaced reply costs more than a fresh comment.

**Mode B scopes down**: review the incremental diff since your last review, via `gh api repos/{REPO}/compare/{MY_LAST_SHA}...{HEAD_SHA}`. Skip what your earlier pass would already have caught; flag what is new.

The step is done when every PR in the queue has been reviewed and **every finding carries a `class` and a `label`** - Steps 5 and 6 read both, and an untagged finding has no verdict and no comment prefix.

### 4d: Mode B only - audit resolution

For each prior concern of yours on this PR, answer:

1. **Was the original issue addressed?** `RESOLVED` / `PARTIAL` / `NOT_ADDRESSED` / `REPLY_ONLY`.
2. **Did the fix introduce a regression?** A new finding in the same file near the original concern is a likely regression. A finding whose `thread_reply_to` points at that concern's own thread is a continuation of the conversation, not a regression.

Append the answers as a "Resolution Audit" section in the Step 5 presentation.

## Step 5: Write the report, then ask

Consolidate each PR's findings. This is the sole user checkpoint in the skill; posting is fail-closed per the Autonomy contract above.

### 5a: Write the review report file

Write the consolidated findings to a markdown file **before** presenting anything - in every mode (`--no-post`, `--ship`, batch, single PR), and regardless of what the user later authorizes. Writing first is what lets the report survive a "no", a no-human sentinel, and a dry run.

```bash
REPO_SLUG={REPO with / replaced by __}        # e.g. org__example-repo
STAMP=$(date +%Y%m%d-%H%M%S)
REVIEW_DIR=~/code-reviews/$REPO_SLUG
mkdir -p "$REVIEW_DIR"
# single PR  -> pr-123-<stamp>.md
# batch      -> batch-<stamp>.md
```

- The report always lives under `~/code-reviews/`, keeping it outside the reviewed repo.
- One file per run: a batch of PRs produces one file holding every PR's section.
- Write it with your file-write tool rather than a shell heredoc, so finding text containing backticks, `$` or quotes survives verbatim.
- The body is exactly the 5b skeleton, prefixed with:

```
# Review Findings - {REPO}
Generated: {ISO timestamp} - Reviewer: @{you} - Mode: {post | --no-post} - PRs: {#123, #789}
```

- When the write fails (permissions, disk), report the error and carry on: a failed report never blocks the review.

### 5b: Present to stdout

Print the **full report content to stdout as well**, every run. The file is a durable copy, never a replacement: the findings themselves always appear on screen, so "see the report at <path>" never stands in for them.

One line per finding, each tagged with its routing (`-> Inline @ file:line` or `-> Thread reply to @reviewer (top_id=N)`):

```
# Review Findings - Consolidated

## PR #123 - {title} (@{author}) - Mode {A: Initial | B: Follow-up}

### Blocking (N)          # **[{label}] file:line** - description + suggestion + routing
### Non-blocking (N)
### Nits (N)
### Resolution Audit      # Mode B only - prior concern, verdict, regression check

## PR #789 - {title} (@{author}) - Skipped: {reason}

**Decision:** {per-PR verdict and why}.

Report written to: {path}
Post these reviews? (y/n, or tell me which to drop/edit)
```

**Dry run** (`--no-post`, explicit or inferred): present the findings and stop. Omit the "Post these reviews?" question, since there is nothing to confirm, and end with `Dry-run complete - no reviews posted. Report: {path}`

**Otherwise:** ask for confirmation through the host's user-prompt capability and **wait**. If the host has no such capability or is non-interactive, treat that as dry run. Proceed to Step 6 only on an explicit affirmative response per the Autonomy contract's table. On any other outcome, end with `Awaiting confirmation - no reviews posted. Report: {path}` This hard stop holds under autopilot and in `--ship` mode alike.

## Step 6: Publish confirmed reviews

**Every finding posts as an inline file comment at its `file:line`**, so the author reads it beside the code. The top-level review body carries only the verdict line and, for Mode B, the Resolution Audit. Split the findings two ways:

- **Thread replies** - findings carrying `thread_reply_to` from `4c`. Posted as replies via `POST /pulls/{pr}/comments` with `in_reply_to`.
- **New inline comments** - everything else, whatever its `class`. Posted through the `comments[]` array on `POST /pulls/{pr}/reviews`, in the same call as the verdict.

### Decision table

**Compute the verdict over ALL kept findings - new inline comments and thread replies alike.** Routing decides only *where* a finding lands, never its severity: a blocking finding that happened to match an existing thread still forces `COMMENT`. Approving a PR whose one blocker was routed into someone else's thread is a correctness bug.

| Condition (over all kept findings) | `event` | Verdict body |
|---|---|---|
| no findings at all | `APPROVE` | `LGTM.` |
| `nit` only | `APPROVE` | `LGTM. {N} nit(s) inline.` |
| `non-blocking` present, no `blocking` | `APPROVE` | `LGTM with {N} non-blocking suggestion(s) inline.` |
| any `blocking` | `COMMENT` | `Code Review: {N_BLOCK} blocking, {N_NONBLOCK} suggestion(s) inline.` |
| `--ship` (any findings) | `APPROVE` | `LGTM - shipping with {N} observation(s) inline.` - only after the user confirms |

Zero kept findings of any kind post the LGTM `APPROVE` with the empty verdict. Zero new inline comments plus at least one **non-blocking** thread reply post `APPROVE` `LGTM` with the note `({N} thread reply(ies) posted inline)`. Any blocking thread reply forces `COMMENT`, per the rule above.

### Dispatch

Body templates, the `comments[]` construction, the per-PR publisher instructions, and 422 handling are in [`references/publish.md`](references/publish.md). Dispatch one publisher worker per confirmed PR when the host supports workers; otherwise run the same publishing steps directly, one PR at a time.

## Step 7: Summary report

Print this to stdout **and** append it to the Step 5a report file under a `## Posting Outcome` heading, so the file ends up holding both the findings and what was actually posted.

```
# Review Queue Summary - Reviewed N PRs in {REPO}

| PR | Author | Mode | Findings (block/non-block) | Action |
|----|--------|------|----------------------------|--------|
| [#123](url) | @alice | A | 2 / 1 | Commented (2 blockers) |
| [#101](url) | @dave | A | - | Skipped (already approved) |

Total: {N} COMMENT, {N} APPROVE across {N} reviewed PRs ({N} skipped)
Report: {path}
```

Include skipped PRs, with `-` for findings and the skip reason in the Action column.
