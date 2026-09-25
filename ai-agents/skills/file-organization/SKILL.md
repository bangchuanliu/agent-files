---
name: file-organization
kind: leaf
description: >-
  File organization: advise where a document, folder, screenshot, download, or messy directory belongs using a lifecycle taxonomy for work Drive and a personal laptop. Use when: file this, where should this go, organize files, clean downloads, name this doc, set up a project folder, or audit a messy directory.
---

# File Organization

Place files in the right home and keep the system from rotting. The organizing axis is **lifecycle**: unsorted, active, ongoing, reference, logistics, archived. Scope and type belong inside those lifecycle buckets.

## Operating mode: advise only

This skill is advisory. Produce exact paths and manual steps; leave every create, move, rename, or delete for the user.

Completion criteria for every answer:
- Name the exact target path and one-line reason.
- Show the relevant subtree when context makes the path ambiguous.
- List folders the user needs to create.
- For a messy directory, return the audit table in [Auditing a directory](#auditing-a-directory) and account for every item or pattern.

## Work Drive taxonomy

```
00_INBOX/        unsorted drops; triage weekly, keep near-empty
01_PROJECTS/     active work with a definition of done, bucketed by delivery period
02_AREAS/        ongoing responsibilities, no end date
03_RESOURCES/    reference consulted repeatedly but never finished
04_ADMIN/        logistics: HR, expenses, travel, access
09_ARCHIVE/      done or dead; mirrors the live tree, date-bucketed
```

### 01_PROJECTS: bucket by delivery period

Use half-year folders such as `2026-1` for Jan through Jun and `2026-2` for Jul through Dec. Bucket by when the project ships, because review and planning usually summarize shipped impact.

```
01_PROJECTS/
├── _templates/
├── 2026-1/
│   ├── _HALF-SUMMARY.gdoc
│   ├── search-quality-refresh/
│   │   ├── design/
│   │   ├── validation/
│   │   ├── prs-and-reviews/
│   │   └── meeting-notes/
│   └── project-b/
└── 2026-2/
    ├── _HALF-SUMMARY.gdoc
    └── project-c/
```

Rules:
- Bucket by the period a project ships, not when it starts.
- For a cross-period project, keep one source of truth in the earlier period and add a shortcut in the later period.
- `_HALF-SUMMARY.gdoc` captures landed impact as it happens: metric, shipped artifact, and PR or doc link.
- After review is filed, move the closed period folder to `09_ARCHIVE/projects/2026-1/`.

### 02_AREAS: ongoing, no completion date

```
02_AREAS/
├── team/         rituals, onboarding, runbooks, retros
├── org/          roadmaps, OKRs, all-hands, cross-team work
└── my-role/      journal, self-assessment, 1:1s, goals
```

`my-role/journal/` next to `my-role/self-assessment/` makes review synthesis come from captured impact instead of memory.

## Personal laptop taxonomy, rooted at home

```
~/
├── inbox/         downloads land here; triage weekly
├── personal/      personal builds and life
│   ├── projects/    active personal projects
│   ├── learning/    courses, sandboxes, scratch repos
│   └── finance/     taxes, statements
├── work/          work material on disk
│   ├── repos/       code checkouts, canonical in git
│   ├── scratch/     throwaway scripts, query drafts, one-off data
│   └── notes/       optional local mirror of Drive notes
├── reference/     local resources: templates, snippets, docs
├── media/         screenshots/, recordings, photos
└── archive/       cold storage; mirrors live tree, date-bucketed
```

Local rules:
- Keep `~/Desktop` and `~/Downloads` empty by treating `~/inbox` as the unsorted landing zone.
- Code is canonical in git. Delete unused local checkouts instead of archiving repositories.
- Keep `work/` and `personal/` split at the top so backup and sync policies can differ.

## Anti-rot rules

1. **One axis: lifecycle.** If a top-level split is by team, product, file type, or urgency, move that split under a lifecycle bucket.
2. **Inbox is temporary.** If an item cannot be classified in 5 seconds, put it in `00_INBOX/` or `~/inbox` and triage weekly.
3. **Pinned helpers use `_`.** Keep `_templates/` and `_HALF-SUMMARY.gdoc` at the top.
4. **Move things whole.** Archive a finished project or closed period as a complete folder so context stays intact.
5. **Date-bucket only in archive.** Active work is organized by lifecycle and project, not by year.

## Deciding where a single item goes

Walk lifecycle top-down and stop at the first match:

- Cannot classify in 5 seconds -> inbox.
- Active, will-be-done work project -> `01_PROJECTS / ship period / project / subfolder`.
- Active personal project -> `~/personal/projects/project/`.
- Ongoing responsibility with no end date -> `02_AREAS/`.
- Reusable reference -> `03_RESOURCES/` or `~/reference/`.
- Logistics -> `04_ADMIN/` or `~/personal/finance/`.
- Done or dead -> `09_ARCHIVE/` or `~/archive/`, date-bucketed and moved whole.

## Naming convention

Names should identify the file without opening it and sort next to siblings.

Format: `yyyy-mm-dd__kebab-topic__qualifier.ext` for point-in-time artifacts. Evergreen docs drop the date.

Rules:
- Use lowercase kebab-case.
- Put ISO date first for time-stamped artifacts.
- Put topic before qualifier: `oncall-runbook__api`, not `api__oncall-runbook`.
- Use history in git or Drive for versions. Add `__v2` only for a real published revision.
- Spell out unclear abbreviations.
- Use kebab-case folders except pinned numbered or `_` helper folders.

Examples:
- `Q4 sales final FINAL v2.xlsx` -> `2025-q4-sales-summary.xlsx`
- `Screenshot 2026-05-31 at 8.45.43 PM.png` -> `2026-05-31__drive-folder-structure.png`
- `notes.gdoc` from a planning meeting -> `2026-05-20__search-quality-planning-notes.gdoc`
- `design doc (copy).gdoc` for a living design -> `search-quality-refresh-design.gdoc`

## Auditing a directory

Read each item enough to know what it is: name, extension, and a content peek when the name is uninformative. Stay advisory; output the plan.

Use this exact table:

| Current | Suggested name | Suggested location | Why |
|---------|----------------|--------------------|-----|
| `Q4 sales final FINAL v2.xlsx` | `2025-q4-sales-summary.xlsx` | `09_ARCHIVE/projects/2025/` | shipped artifact, prior period -> archive |
| `notes.gdoc` | `2026-05-20__search-quality-planning-notes.gdoc` | `01_PROJECTS/2026-1/search-quality-refresh/meeting-notes/` | time-stamped note for an active project |
| `random.png` | open first | needs triage -> `00_INBOX/` | cannot determine contents from name |

Then add:
- Folders to create.
- Items you could not classify, routed to inbox with the missing fact needed to place them.
- Pattern notes for repeated destinations, such as `all 6 screenshots -> ~/media/screenshots, renamed yyyy-mm-dd__subject.png`.
