# Personal project mode

A non-code project (fitness goal, side business, learning plan, home renovation) organized so status is visible in seconds: **goals** say where you are going, the **plan** says how, the **progress log** says what actually happened. The three files change at different rates, so they stay separate.

Default location: `~/personal/projects/<kebab-name>/`. Recommend `git init` for free history.

## Layout

```
<project>/
├── README.md      why, scope, status line, links
├── GOALS.md       outcomes with metric, target, date; rarely edited
├── PLAN.md        milestones and task checklists; edited weekly
├── PROGRESS.md    dated log, newest first; append-only
├── notes/         yyyy-mm-dd__topic.md
├── resources/     reference material and links
└── archive/       superseded plans and dropped ideas, moved whole
```

## File templates

`README.md`:
```markdown
# <Project name>
**Status:** on-track | at-risk | off-track | paused | done - <one line, updated at each review>
**Why:** <one paragraph: the change this project makes>
**Scope:** <in> / **Not:** <out>
Goals: GOALS.md - Plan: PLAN.md - Progress: PROGRESS.md
```

`GOALS.md`: every goal is an outcome with a number and a date, not an activity.
```markdown
# Goals
| ID | Outcome | Metric | Baseline | Target | By | Status |
|----|---------|--------|----------|--------|----|--------|
| G1 | Run a sub-4h marathon | finish time | 4:32 | 3:59 | 2027-04-18 | on-track |
```

`PLAN.md`: milestones serve goals; tasks are checkboxes small enough to finish in one sitting.
```markdown
# Plan
## M1 - Base mileage to 50 km/week (G1) - due 2026-12-15
- [x] Pick a training plan
- [ ] Week 1-4 base block
## Next up
<the 1-3 tasks to do next; the first thing to read when resuming>
## Parking lot
<ideas not yet scheduled>
```

`PROGRESS.md`: one entry per work session or weekly review, newest first.
```markdown
# Progress
## 2026-10-09 (weekly review)
- Moved: <what changed, with metric values for affected goals>
- Learned: <surprises, decisions and why>
- Blocked: <blockers, or none>
- Next: <the task that becomes Next up>
```

## Tracking

- **Status at a glance:** README status line, then the GOALS status column, then `Next up`.
- **Progress percent per milestone:** done checkboxes / all checkboxes under it; report it when asked "where am I".
- **Weekly review:** add a PROGRESS entry, update each goal's status and metric, refresh `Next up`, re-date or cut slipping milestones.
- **Done:** set all statuses to `done`, write a final PROGRESS retrospective, move the folder whole to `~/archive/<yyyy>/`.

## Init

Ask once for: project name, why, 1-3 goals (metric, target, date), first milestone. Plan `create` rows for the layout with templates filled in; leave unknown fields as `<TBD>` instead of inventing them.

## Refactor

Survey every file. Plan moves into the layout, then `edit` rows that extract existing content into the tracking files: stated goals into GOALS, todo lists into PLAN checkboxes, dated journal entries into PROGRESS. Keep originals in `archive/` rather than merging destructively. Flag goals missing a metric or date as `<TBD>` in the plan for the user to fill.

## Where a single item goes

Meeting or thinking notes -> `notes/` with a dated name. Links, manuals, receipts -> `resources/`. A new task -> PLAN checkbox. Something that happened -> PROGRESS entry. Superseded plan -> `archive/`.
