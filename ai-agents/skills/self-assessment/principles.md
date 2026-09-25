# Career Principles - Reference

Source-of-truth for the 11 principles used by `self-assessment` and `self-assessment-li`. Structure follows L -> E -> C. Both skills read this before scoring.

**Every bullet must follow the strict format for its principle (see below) and must close with a quantified impact.**

---

## Bullet format - strict

### Leadership bullets
> **[gap or misalignment that existed] - [what you drove, defined, or aligned, and the non-obvious decision] - [quantified impact on team or org]**

- Lead with the gap: what problem the team had before you acted (missing standard, recurring debate, unowned area, regulatory blocker).
- Middle: what you drove or defined, and what made the decision non-obvious (trade-off chosen, alternative rejected, constraint navigated).
- Close: quantified result - N teams aligned, M weeks saved, X issues prevented, Y% effort reduction.

### Execution bullets
> **[what made it technically hard or time-constrained] - [what you built, diagnosed, or validated, and the key decision] - [quantified outcome]**

- Lead with the hard part: scale, silent failure, competing constraints, tight timeline, non-obvious root cause.
- Middle: what you built or fixed, and the key technical decision (why this approach, what it prevents or enables).
- Close: quantified result - N rows, X% drift, $Y value, Z jobs eliminated, before/after counts.

### Impact quantification rule
Every bullet must close with a number. Use this hierarchy:

1. **Exact** - use the number from the artifact (rows, dollars, days, %).
2. **Inferred** - derive from evidence already in the bullet (e.g. "622M-row pipeline, 0.56% drift -> ~3.4M rows affected").
3. **Estimated** - rough order-of-magnitude is fine ("~2 weeks saved", "~80% reduction").
4. **Placeholder** - only when no evidence exists: `[quantify: <metric to fill in>]`.

Never leave impact implicit. Never write "could prevent" or "helps reduce" - name the outcome and attach a number or placeholder.

---

## Leadership (L) - the group's work

> **Leadership = direction + alignment + standards + people growth.**
> Focus on **WHAT** leadership rather than HOW.
> Leadership is not a title - it is the ability to make a group more effective than it would be without you.

### L1. Direction Setting

**What it proves:** You turned ambiguity into a coherent technical path - for the team, not just yourself.

**Bullet format:** `[ambiguity or recurring debate that existed] - [standard, decision, or architecture you defined, and the non-obvious call] - [N teams aligned / M debate cycles eliminated / X% effort saved]`

**Impact looks like:**
- Multiple teams aligned on one path instead of optimizing separately
- Ambiguity collapsed into a concrete plan others could execute
- Standard adopted across teams (review process, design pattern, metric definition)
- Recurring re-debate cycles eliminated
- Downstream consumers stopped re-asking the same question

**Look for in the artifact:**
- Drove a design or architecture decision that others now follow
- Set technical direction, culture, or best practice
- Navigated ambiguity *for the team*
- Influenced how others do their work, not just what you built yourself

**BAD -> GOOD:**

- BAD: *"I designed a new pipeline architecture."*
- GOOD: *"No standard existed for attribution window semantics - defined the canonical date-range contract and drove sign-off across data infra and product, collapsing 3 weeks of recurring debate into one executable plan; existing jobs required zero migration."*

- BAD: *"The dashboard is wrong; data infra needs to fix it."*
- GOOD: *"Reporting, billing, and experiment metrics had no agreed source of truth - defined the semantic differences and aligned product, DS, and infra on it, eliminating the weekly metric-disagreement thread."*

---

### L2. Ownership Beyond Scope

**What it proves:** You went beyond your assigned ticket - picked up unowned problems and drove outcomes the team needed.

**Bullet format:** `[unowned gap or risk that existed with no assigned owner] - [what you self-initiated and drove to completion] - [incident prevented / N teams unblocked / capability that now outlasts the project]`

**Impact looks like:**
- Gap closed before it became an incident
- Team capability gained (lineage, runbook, dashboard, validation gate) that outlasts the project
- Work shipped that wasn't on anyone's roadmap but the team needed
- Downstream consumers no longer blocked by an orphaned issue
- You became the de facto owner of a previously unowned area

**Look for in the artifact:**
- Spotted gaps proactively, no one asked
- Took responsibility for cross-project improvements
- Drove outcomes that benefited the broader team or the business, not just your immediate scope
- Followed through after launch (monitoring, post-launch improvements)

**BAD -> GOOD:**

- BAD: *"That's not my team's responsibility."*
- GOOD: *"No team owned the reconciliation between billing and reporting; self-initiated the lineage and validation contract, then handed it to the natural long-term owner - eliminating a recurring source of advertiser-facing discrepancies (~N tickets/quarter)."*

- BAD: *"The bug is in another team's code, so I'll file a ticket."*
- GOOD: *"No one had diagnosed the upstream identity drift causing recurring pipeline failures; root-caused it and submitted the fix to the identity team - eliminating the incident class instead of working around it, saving ~M hours/quarter of on-call time."*

---

### L3. Influencing Without Authority

**What it proves:** You aligned people without title or escalation.

**Bullet format:** `[who was misaligned and what was contested] - [how you reframed the trade-off or drove consensus] - [decision unblocked / re-litigation stopped / stakeholder adopted your framing]`

**Required elements - all three must be present:**
- **Counterpart**: name the team, role, or function (product, DS, legal, infra, partner team)
- **Contested point**: what reasonable people disagreed on (speed vs. rigor, scope, approach, risk tolerance)
- **Resolution**: how you reframed it or what was decided - not just "drove alignment"

**Impact looks like:**
- Stakeholder decision unblocked without escalating to a manager
- Cross-team consensus reached on a contested trade-off
- Partners adopted your framing of a problem
- Conflict converted into a concrete decision with named owners
- Re-litigation of the same disagreement stopped

**BAD -> GOOD:**

- BAD: *"Drove alignment on the attribution window decision."*
- GOOD: *"Product and data teams disagreed on whether the 90-day window change was a bug fix or a metric change - escalated with explicit risk framing before merge, separating the bug-fix scope from the behavioral change and securing product sign-off; prevented a high-impact reporting shift from shipping without business awareness."*

- BAD: *"DS rejected the modeling approach, so we're stuck."*
- GOOD: *"DS and product were deadlocked on modeling vs. attribution coverage - reframed as a coverage-vs-causality trade-off, presented both with data costs, and aligned both teams on a sequenced plan - unblocking the launch without escalation."*

---

### Strong Leadership Signals

- You made an ambiguous problem **legible** for the team.
- You changed the **quality of the decision**, not just the amount of code shipped.
- You aligned product, engineering, data, infra, and operations around a shared direction.
- You improved a **repeatable team practice**, not just one project.
- You helped someone else operate at a higher level.

---

## Execution (E) - your own work

> **Execution = decision quality + delivery quality + operational follow-through.**
> Focus on **WHY** execution rather than WHAT.

### E1. Technical Complexity & Problem Solving

**What it proves:** You solved a hard problem and made the hard part tractable.

**Bullet format:** `[what made it hard: scale, silent failure, non-obvious root cause, competing constraints] - [what you diagnosed or built, and the key architectural decision] - [correctness restored / incident class eliminated / N rows / X% improvement]`

**Impact looks like:**
- Latency/throughput improved by quantified X
- Correctness restored across affected segments (name the scale)
- System property unlocked (idempotency, ordering guarantee, recoverability)
- Recurring incident class eliminated by an architectural change
- The next blocked project became unblockable

**Look for in the artifact:**
- Ambiguous or underspecified problem framed clearly
- Cross-system or cross-team complexity navigated
- Scale, latency, or correctness constraints handled
- Key design decisions explicit - not just "I built X"

**BAD -> GOOD:**

- BAD: *"I built the ETL job for conversions."*
- GOOD: *"Conversion measurement had no event-semantic contract, causing reconciliation failures across dashboard, bidding, and billing - defined the contract, handled late arrivals, and validated all three consumers; cut reconciliation tickets by 60%."*

- BAD: *"I optimized the join."*
- GOOD: *"100× skew in user-level events was causing nightly job failures - replaced the broadcast join with sort-merge and range partitioning; cut runtime from 6h to 45min and eliminated recurring midnight pages."*

---

### E2. Planning & Timeline Management

**What it proves:** You delivered on time by sequencing well and adjusting when reality changed.

**Bullet format:** `[delivery constraint or sequencing challenge] - [how you phased, sequenced, or scoped the work, and the trade-off made] - [shipped on time / N weeks earlier / X scope deferred without losing core value]`

**Impact looks like:**
- Shipped on time despite scope or requirements change
- Dependent teams unblocked N weeks earlier than the naïve plan
- Timeline reduced by deferring non-essential work without losing core value
- Checkpoints surfaced risk before it became a delay
- Re-planning happened *before* the deadline slipped, not after

**Look for in the artifact:**
- Milestones with checkpoints, owners, and explicit decision points
- Dependencies and sequencing called out
- Trade-offs made to meet a deadline (scope, timeline, or quality dial)
- Plan adjustments when requirements evolved

**BAD -> GOOD:**

- BAD: *"We finished the migration in Q1."*
- GOOD: *"Migration had 4 dependent teams and no clean cutover point - sequenced into shadow validation, segment deltas, controlled rollout, and post-launch monitoring; deferred two non-blocking sub-features and cut 8-week scope to 5 weeks."*

- BAD: *"We delayed by two weeks because of unexpected complexity."*
- GOOD: *"Privacy-API change extended the integration spike from 1 to 3 weeks; deferred the analytics dashboard to phase 2 and shipped the critical pipeline on the original date - preserving the launch commitment to advertisers."*

---

### E3. Risk Identification & Mitigation

**What it proves:** You see production, dependency, migration, and data risks early - and reduce blast radius before launch.

**Bullet format:** `[risk identified and when - before merge, before launch, before ramp] - [mitigation designed and validated] - [incident prevented / blast radius bounded to X / rollback time reduced from Y to Z]`

**Impact looks like:**
- Incident prevented that would have caused outage, billing variance, or data loss
- Rollback path validated before launch (not improvised under pressure)
- Blast radius bounded to one segment instead of all
- Late-event / double-counting / identity drift caught before production
- Risk surfaced early to the right owner instead of escalated late

**Look for in the artifact:**
- Risks named early (tech, data, dependency, org)
- Failure modes anticipated, fallback plans defined
- Mitigation owners assigned
- Incidents or delays prevented

**BAD -> GOOD:**

- BAD: *"We shipped attribution v2 and will watch for issues."*
- GOOD: *"Before ramp, identified 5 production risks (OOM, partial writes, boundary errors, backward-compatibility breakage, performance) - each with a named mitigation; idempotent writes and parameter defaulting reduced blast radius to zero for existing jobs."*

- BAD: *"If it breaks, we'll roll back."*
- GOOD: *"Defined rollback trigger (>5% advertiser delta vs baseline), automated canary comparison, and ran the playbook once in staging - turning rollback from a fire drill into a 10-minute operation."*

---

## Craftsmanship (C) - engineering quality and leverage

> **Craftsmanship = elegant code + reuse + craft processes + reviewing + metrics-driven improvement.**

**Bullet format for C:** `[what engineering quality problem existed] - [what you built, refactored, or standardized] - [quantified leverage: N teams / M duplicate impls eliminated / X% bug rate / Y faster onboarding]`

### C1. Elegant, Simple, Maintainable Code

**What it proves:** Your code is simple, readable, and stays bend-able as requirements change.

**Impact looks like:**
- Smaller diff to make non-trivial changes
- Fewer regression bugs after the change
- Review comments shifted from "what does this do" to substantive questions
- Refactoring sustained across multiple PRs without breaking callers

**BAD -> GOOD:**

- BAD: *"I added the new feature."*
- GOOD: *"Event-tracker had 12 call sites - extracted a single abstraction, reducing touched call sites to 1 and making the next two planned features additive instead of branching."*

- BAD: *"Refactored some code."*
- GOOD: *"Three near-duplicate conversion-validation impls - consolidated into one tested module; bug-fix patch size dropped from ~150 LOC to ~30 LOC for the last two incidents."*

---

### C2. Reuse-First Mindset

**What it proves:** You design for multiple consumers - built once, leveraged by many.

**Impact looks like:**
- N teams adopted the shared component instead of building their own
- M duplicate implementations eliminated
- Bootstrap time for new features reduced by quantified X%
- One-off turned into a platform capability

**BAD -> GOOD:**

- BAD: *"Built the metric validator for my pipeline."*
- GOOD: *"Built the metric-validator as a shared utility - adopted by 3 downstream pipelines, eliminating 2 duplicate implementations and standardizing the error format across teams."*

- BAD: *"I wrote a script to backfill data."*
- GOOD: *"Generalized the backfill script into a reusable framework with idempotency and progress-reporting; used by 4 subsequent backfills without modification, reducing per-backfill setup from ~2 days to ~2 hours."*

---

### C3. Craft Processes & Mature Testing/Monitoring

**What it proves:** You set quality gates and monitoring standards that outlast the project.

**Impact looks like:**
- Test coverage gates merged into CI; regressions caught before merge
- MTTD and MTTR reduced
- Runbook used during oncall; oncall load decreased
- Quality gates explicit in CI

**BAD -> GOOD:**

- BAD: *"Added some tests."*
- GOOD: *"Added late-event and double-counting test cases - caught two pre-launch regressions in the next 4 PRs that would have caused billing variance."*

- BAD: *"Set up monitoring."*
- GOOD: *"Defined freshness, completeness, and reconciliation SLAs; built alerts tied to advertiser-facing decisions - MTTD dropped from ~hours to ~minutes."*

---

### C4. Reviewing Others' Work

**What it proves:** You multiply your impact by raising the quality of others' work.

**C4 must be from reviewing others' PRs** - evidence from your own PRs does not count. Requires: bug caught, design issue surfaced, or pattern coached in someone else's code.

**Impact looks like:**
- P0/P1 bugs caught in review before production
- Design improved before commit
- Pattern-level feedback that compounds across future PRs from the same author

**BAD -> GOOD:**

- BAD: *"Reviewed N PRs this quarter."*
- GOOD: *"Caught a recurring race-condition pattern across 3 teammates' PRs - led an RFC that eliminated the class codebase-wide; prevented an estimated 2–3 production incidents."*

- BAD: *"Gave feedback on the design doc."*
- GOOD: *"Surfaced late-event handling and identity drift as unaddressed failure modes in design review - both became explicit decisions before implementation, preventing a likely post-launch incident."*

---

### C5. Metrics-Driven Improvement

**What it proves:** You use data to drive engineering improvements, not intuition.

**Impact looks like:**
- Before/after numbers attached to every engineering change
- Metric drove a refactor that reduced cost/latency/error rate by X%
- Best-practice adoption tracked and improved across team

**BAD -> GOOD:**

- BAD: *"Improved CI."*
- GOOD: *"Profiled CI runtimes over 4 weeks - top-5 slowest tests were 90% of runtime; parallelized them, cutting median CI from 18min to 6min and saving the team ~15 hours/week."*

- BAD: *"Adopted the new linter."*
- GOOD: *"Tracked lint-warning count over 2 months as the team adopted the new linter; reduced from ~800 to ~50 warnings and gated new warnings in CI to prevent regression."*

---

## Impact & Outcomes - the measure across L, E, and C

**Every bullet must close with a quantified result.** Use this hierarchy - work down until you have a number:

| Tier | When to use | Example |
|---|---|---|
| **Exact** | Number exists in the artifact | "7,229 duplicate keys", "317,448 attributed pairs", "$1,386,906 conversion value" |
| **Inferred** | Derive from numbers already in the bullet | "622M-row pipeline at 0.56% drift -> ~3.4M affected rows" |
| **Estimated** | Order-of-magnitude is fine | "~2 weeks saved per onboarding", "~80% reduction in job executions" |
| **Placeholder** | No evidence available | `[quantify: manual QA hours saved per onboarding]` |

**Never write:**
- "could prevent" or "helps reduce" - name the outcome and attach a number
- "improved reliability" - improved by how much, for how many
- "unblocked the team" - unblocked N engineers for M weeks, or unblocked a launch by date X

**Impact categories:**
- **Business:** revenue, cost, advertiser campaigns unblocked
- **Product:** latency, accuracy, reliability, adoption
- **Engineering:** maintainability, reuse leverage, downstream teams unblocked
- **Risk reduction:** incidents prevented, blast radius bounded, rollback time
- **People:** recurring debates eliminated, decisions unblocked, onboarding time

---

## Self-Review Checkpoints

Run at end-of-week and end-of-project. Each ✓/⚠/✗ should be backed by a concrete artifact.

**Leadership:**
- L1: Did I define something others now follow - and can I name who and at what scale?
- L2: Did I pick up something no one assigned me - and what would have happened if I hadn't?
- L3: Can I name the counterpart, what was contested, and how it resolved?

**Execution:**
- E1: Did I name *why this was hard* and the key design decision, not just what I built?
- E2: Did I sequence the work, expose dependencies, and adjust when requirements moved?
- E3: Did I name risks before launch and reduce blast radius - not just "watch for issues"?

**Craftsmanship:**
- C1: Did my code stay simple and bend-able - can I show a before/after?
- C2: Did I design for reuse - name the N other consumers or future features enabled?
- C3: Did I add quality gates or monitoring that will catch failures I won't be around to see?
- C4: Did my review of someone else's work catch a real issue or shift a pattern?
- C5: Did I use a metric to drive a change - can I show the before/after number?

**Impact check:** Every bullet closes with a number (exact, inferred, estimated, or placeholder). No bullet ends with a vague outcome.

---

## Anti-patterns (catch these in your own writing)

- **Implementation framing**: naming specific classes, methods, or config keys instead of the architectural decision and its impact.
- **Capability framing**: "I am good at debugging" instead of "I cut MTTR by X% for this incident class."
- **"We shipped X"** without naming what changed for users, business, or operations.
- **Vague impact**: "improved reliability", "helped the team", "reduced complexity" - always attach a number.
- **Missing counterpart in L3**: "drove alignment" with no named counterpart, contested point, or resolution is ⚠, not ✓.
- **Own-PR evidence for C4**: evidence from your own PRs, even if about review tooling, does not count as C4.
- **Treating constraints as blockers**: privacy, deadline, or scope constraints are forcing functions for clearer trade-offs, not excuses.
- **Launching without success criteria**: shipping a pipeline or dashboard without freshness SLA, reconciliation check, and named owner is incomplete execution.
