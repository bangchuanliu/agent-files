---
name: review-self
kind: leaf
agents: claude, copilot
description: "Use when: review my code, self review, review changes, pre-PR check, PR comment triage. Covers code, docs, and agent/skill domains, with optional domain-specific checks supplied by local context."
---

# Code Review

Two modes:
- **Pre-PR review** (default): Self-review before creating a PR
- **PR comment triage**: Evaluate reviewer comments - justify or queue fixes

## Usage

```bash
/review-self                    # Pre-PR review (default)
/review-self domain=docs        # Force domain
/review-self domain=agent       # Force domain
/review-self comments           # PR comment triage
/review-self comments #1234     # Triage specific PR
```

## Step 0 - company context

Read `~/.config/dotfiles/context/review-self/context.md` if it exists; it may route to further
files in that directory. If it does not exist, skip this step - its absence is normal and the
generic checks below are complete on their own.

Company context may define additional domains, repository-specific risk rules, review helper
capabilities, or reference files. Treat those additions as optional. The generic review must still
work when no company context is present.

## Mode 1: Pre-PR Review

Run two passes: first a broad review of the changed files, then targeted diff-based checks this
skill owns.

### Step 1: Detect Changes + Classify Risk

If `domain=<name>` is provided, skip detection and use that domain.

Otherwise, detect the merge base using a configurable base ref:

```bash
BASE_REF="${REVIEW_BASE_REF:-}"
if [ -z "$BASE_REF" ]; then
  BASE_REF=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')
fi
if [ -z "$BASE_REF" ]; then
  BASE_REF=$(git branch --format='%(refname:short)' --list main master | head -n 1)
fi
BASE_REF=${BASE_REF:-HEAD~1}
git diff --name-only "$(git merge-base HEAD "$BASE_REF")"..HEAD
```

| Domain | Patterns | Reference |
|--------|----------|-----------|
| Agent/Skill | agent configuration, skill files, command files, plan files | `references/agent-skill.md` |
| Company-loaded domains | Patterns supplied by Step 0 context | References supplied by Step 0 context |

Classify risk generically:

| Risk | Triggers | Review depth |
|---|---|---|
| **L0 - Tiny** | Small, localized change with no public API, schema, config, persistence, or operational behavior change | Broad review plus quick scope hygiene |
| **L1 - Standard** | New behavior, moderate refactor, config changes, tests or docs with user impact | Broad review plus relevant domain reference checks |
| **L2 - High risk** | Data migration, security/privacy handling, public API/schema/output path changes, broad refactor, irreversible write path, rollout or rollback complexity | Full domain checks, second pass after a break, explicit validation and rollback review |

### Step 2: Broad reviewer pass

If Step 0 supplied a parallel multi-reviewer review capability, delegate the broad file-by-file
pass to that capability and read its structured findings. Name the capability by what it does,
not by a company-specific skill or plugin identifier.

If no such capability exists, review the diff directly against the merge base:

```bash
git diff "$BASE_REF"...HEAD --stat
git diff "$BASE_REF"...HEAD
```

For each changed file, check:
- Correctness: changed control flow, null/empty handling, boundary conditions, error handling, and concurrency assumptions.
- Behavior preservation: removed or moved logic still executes at every affected call site.
- Tests: new or changed behavior has regression coverage, including edge and error cases.
- Operability: logs, metrics, retries, idempotency, validation evidence, and rollback path where relevant.
- Scope hygiene: no debug code, unrelated changes, generated-file churn, formatter noise, or stale TODOs introduced by the change.

### Step 3: Domain-specific extras

Run only the domain checks that are available:

- **Agent/Skill** -> read `references/agent-skill.md` and apply the full checklist.
- **Company-loaded domains** -> apply any reference files and decision logic loaded in Step 0.
- **No matching domain context** -> skip domain-specific passes and rely on the generic review from Step 2. This is normal.

For any refactor, regardless of domain, run these diff-based checks:

1. **Refactor parity** - every removed helper's behavior survives at each replacement call site.
2. **Cross-caller symmetry** - when several callers migrate similarly, compare each caller's old and new steps.
3. **Validation coverage** - every changed code path has test or validation evidence, or an explicit follow-up risk note.
4. **Regression tests** - if a tested callable is removed, callers inherit tests for the removed callable's observable effect.

### Step 4: Summary

Merge broad-review findings with domain-specific extras. De-duplicate issues reported by multiple
sources.

```markdown
# Pre-PR Review Summary

## Domains: [x] Agent/Skill (N files), [x] Company-loaded: <name>, [ ] Generic only
## Sources: broad diff review + available domain references

## Blockers (P0) - must fix
## High Priority (P1) - should fix
## Suggestions (P2) - consider

## Recommendation: READY FOR PR / FIX BEFORE PR / NEEDS REWORK
```

## Mode 2: PR Comment Triage

> **Red flag - summaries are not the comment set.** `gh pr view --json reviews,comments` returns review bodies and top-level conversation comments only. Reviewers anchor substantive findings inline at file:line, and those appear via `gh api .../pulls/{n}/comments`. Always fetch inline comments first, then reconcile with summaries.
>
> **Replies go inline, never top-level.** Use `/pulls/{n}/comments` with `in_reply_to`. A top-level PR comment is unanchored and does not resolve the reviewer's thread.

### Step 1: Fetch Comments

Determine PR: user-provided or `gh pr view --json number`. Fetch both comment surfaces and keep them separated:

```bash
# Inline review comments - anchored to file:line. Reply via /pulls/{n}/comments with in_reply_to.
gh api repos/{owner}/{repo}/pulls/{number}/comments   --jq '[.[] | {id, top_id: (.in_reply_to_id // .id), user: .user.login, path, line: (.line // .original_line), body, is_reply: (.in_reply_to_id != null)}]'

# Top-level PR conversation comments + review summaries. Reply via /issues/{n}/comments only when no inline thread exists.
gh pr view <number> --json reviews,comments
```

For each inline comment, capture `id`, `top_id`, `path`, `line`, `body`, and `user`. Skip replies (`is_reply: true`) and comments where `line` is null.

### Step 2: Evaluate Each Comment

| Verdict | When | Action |
|---------|------|--------|
| Agree - fix needed | Real bug, performance, correctness, or maintainability issue | Queue for fix |
| Agree - minor | Valid but cosmetic | Queue as P2 |
| Disagree - justify | Misunderstanding or intentional choice | Draft inline reply |
| Question - clarify | Needs context | Draft inline reply |

Be rigorous. Do not blindly agree or disagree.

### Step 3: Reply to Non-Fix Comments - Inline Threads

Replies always go inline in the existing thread, never as a new top-level PR comment. Draft each
reply with specific reasoning and present drafts for approval before posting.

After approval, post each reply via `in_reply_to` against the thread root from Step 1:

```bash
gh api repos/{owner}/{repo}/pulls/{number}/comments --method POST   -F in_reply_to={top_id}   -f body="{reply_body}"
```

If a reviewer left only a review-level summary comment, there is no inline thread. Either reply to
one of their inline comments on the same topic or post a top-level PR comment and call out that it
is unanchored.

### Step 4: Write Fix List

Write `plans/features/<feature>/pr-comments.md` only when that path exists or the project already
uses that planning convention. Otherwise, write the fix list in the user's requested location or
return it inline.

```markdown
# PR Comment Fixes
PR: #<number> | Reviewed: <date>

### 1. <description>
- Reviewer: @username
- File: `path:line`
- Severity: P0/P1/P2
- Action: <what to change>
```

### Step 5: Summary

```text
Fixes queued: N
Justification replies drafted: N
Clarification replies drafted: N
Next: implement fixes, then re-run Mode 1 against the updated HEAD.
```

### Step 6: Improve the heuristic after misses

If a human reviewer finds an issue this self-review should have caught, update the relevant generic
or company-context heuristic. Keep company facts in the Step 0 context directory, not in this core
skill.
