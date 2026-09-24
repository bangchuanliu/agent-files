---
name: file-organization
description: >-
  banliu's personal taxonomy for filing documents and files — both work (Google
  Drive) and personal laptop. Use whenever placing, moving, or naming a new doc,
  folder, screenshot, or download, deciding where something belongs, organizing a
  messy directory, or setting up a new project/half folder. Trigger even when the
  user doesn't say "taxonomy" — e.g. "where should this design doc go", "file this
  under the right project", "set up my H2 folder", "clean up my Downloads",
  "organize these notes". The single organizing axis is lifecycle (how alive a doc
  is), and work projects bucket by the half they SHIP for LinkedIn self-assessment.
---

# File Organization (banliu)

Place any new file/doc in the right home and keep the system from rotting. There is
**one organizing axis: lifecycle** — how alive a thing is, from unsorted → active →
ongoing → reference → dead. Don't mix in other axes (scope, type) at the top level;
mixing axes is what makes "where did I put that" happen.

## Operating mode: advise, never act

This skill is **advisory only**. Never create, move, rename, or delete files or folders
— not even when the user says "file this" or "set it up." The user keeps control of every
`mkdir` and move. Your job is to tell them precisely *where* a thing belongs and *why*,
and show the tree so they can place it themselves.

- Name the **exact target path** (full folder chain) plus a one-line reason.
- Show the relevant **subtree** so the destination is unambiguous in context.
- If folders in the path don't exist yet, **say which to create** — as an instruction,
  not an action.
- **Google Drive (work) isn't a local filesystem and these tools can't reach it** — so for
  any work/Drive item, output **manual steps** for the user (e.g. "create `2026-2/` under
  `01_PROJECTS`, then move the doc into `2026-2/<project>/design/`"). The personal laptop
  side is also advice-only; describe the `mkdir`/`mv` commands but let the user run them.

When the request is "organize this messy directory," produce a **migration plan** — a
mapping of current item → target path, with the rules applied — for the user to execute.
Don't run it.

## Work — Google Drive

```
00_INBOX/        unsorted drops; triage weekly, keep near-empty
01_PROJECTS/     active work with a definition of "done" — bucketed by SHIP half
02_AREAS/        ongoing responsibilities, no end date (team, org, my-role)
03_RESOURCES/    reference you consult but never "finish" (templates, specs, diagrams)
04_ADMIN/        logistics (hr, expenses, travel, access)
09_ARCHIVE/      done/dead; mirrors the live tree, date-bucketed
```

### 01_PROJECTS is bucketed by half — this is the load-bearing rule

The user's work is **discrete shipped projects**, and LinkedIn perf review is per-half.
So projects live in half-folders (`2026-1` = Jan–Jun, `2026-2` = Jul–Dec) to make
self-assessment synthesis trivial.

```
01_PROJECTS/
├── _templates/                 scaffold every new project from here; "_" pins it on top
├── 2026-1/
│   ├── _HALF-SUMMARY.gdoc       running brag-doc: one bullet per landed thing (metric + PR)
│   ├── attribution-pipeline-manager/
│   │   ├── design/
│   │   ├── data-validation/
│   │   ├── prs-and-reviews/
│   │   └── meeting-notes/
│   └── <project-b>/
└── 2026-2/
    ├── _HALF-SUMMARY.gdoc
    └── <project-c>/
```

Filing rules:
- **Bucket by the half a project SHIPS, not when it started** — that's the half it
  counts toward for self-assessment.
- **Cross-half project** → keep it in the earlier half, add a Drive *shortcut* (not a
  copy — one source of truth) into the later half.
- **`_HALF-SUMMARY.gdoc` is the payoff.** Every time something lands, add a bullet with
  the metric and PR link. Self-assessment becomes editing, not archaeology. Without it,
  the half-buckets are just tidier folders.
- **Archive closed halves.** Once a half's self-assessment is filed, move the whole
  `2026-1/` folder to `09_ARCHIVE/projects/2026-1/`. `01_PROJECTS` should show only the
  current half (+ one still being written up).

### 02_AREAS — ongoing, no completion date

```
02_AREAS/
├── team/         oncall (runbooks, retros), rituals (standup/sprint/retro), onboarding
├── org/          planning (roadmaps, OKRs), all-hands, cross-team
└── my-role/      journal, self-assessment (promo packet, brag doc), 1on1s, goals
```

`my-role/` is the promo engine — `journal/` next to `self-assessment/` means review
season is synthesis from captured impact, not reconstruction from memory.

## Personal — laptop, rooted at `~`

Same lifecycle axis, adapted for things Drive doesn't hold (code, downloads, media).

```
~/
├── inbox/         downloads land here; triage weekly, keep near-empty
├── personal/      personal builds & life
│   ├── projects/    active personal projects (this skill lives in projects/skills/)
│   ├── learning/    courses, sandboxes, scratch repos
│   └── finance/     taxes, statements
├── work/          LinkedIn stuff on disk
│   ├── repos/       MP checkouts, code (canonical in git — don't archive, delete)
│   ├── scratch/     throwaway scripts, query drafts, one-off data
│   └── notes/       optional local mirror of Drive work notes
├── reference/     local 03_RESOURCES-type material (templates, snippets, docs)
├── media/         screenshots/, recordings, photos
└── archive/       cold storage; mirrors live tree, date-bucketed
```

Local rules:
- **Keep `~/Desktop` and `~/Downloads` empty.** Repoint macOS screenshots to
  `~/media/screenshots` (`defaults write com.apple.screencapture location ~/media/screenshots`).
  Desktop clutter is the local unsorted-inbox.
- **Code is canonical in git, not in `archive/`.** Don't archive repos — delete local
  checkouts; the remote is the source of truth.
- **`work/` and `personal/` split at the top level** so backups and cloud sync can treat
  them differently.

## The rules that keep any of this from rotting

These matter more than the exact folder names — apply them when organizing:

1. **One axis: lifecycle.** If you're tempted to split by scope (team/org) or type
   (admin/archive) at the top, stop — that's the bug that creates filing hesitation.
   Scope/type belong as *subfolders inside* a lifecycle bucket.
2. **The inbox is sacred and temporary.** Anything you can't classify in 5 seconds goes
   to `00_INBOX`/`~/inbox`. Empty it weekly. If it stays full for a month, the taxonomy
   is wrong — fix the taxonomy, not the file.
3. **`_` prefix pins helpers to the top** (`_templates/`, `_HALF-SUMMARY.gdoc`) so
   scaffolding is one click away and never mistaken for real content.
4. **Move things whole.** Archive a finished project (or closed half) as an entire
   folder — don't cherry-pick files, you lose context. This is why per-project subfolders
   (`design/`, `meeting-notes/`) live *inside* each project, not as global folders.
5. **Date-bucket only inside ARCHIVE.** Active work is never sorted by time (no
   `01_PROJECTS/2025/`). Archives are, so old years prune wholesale.

## Deciding where a single new item goes

Walk the lifecycle axis top-down and stop at the first match:

- Can't classify in 5 seconds? → **inbox**.
- Tied to an active, will-be-done project? → **01_PROJECTS / current half / that project**
  (work) or **~/personal/projects/** (personal). Bucket work by ship half.
- An ongoing responsibility with no end date? → **02_AREAS** (team / org / my-role).
- Something you'll consult repeatedly but never "finish" (template, spec, snippet,
  diagram)? → **03_RESOURCES** or **~/reference**.
- Logistics (HR, expense, access)? → **04_ADMIN** or **~/personal/finance**.
- Done or dead? → **09_ARCHIVE** / **~/archive**, date-bucketed, moved whole.

## Naming convention

A good name tells you what a file is *without opening it* and sorts sensibly next to its
siblings. Names are the other half of findability — the right folder with a name like
`Untitled (3) final FINAL.docx` is still lost.

Format: `<yyyy-mm-dd>__<kebab-topic>__<qualifier>.<ext>` — date only when the file is a
point-in-time artifact (a meeting note, a snapshot, a readout). Evergreen docs (a living
design doc, a runbook) drop the date so they don't look stale.

Rules, and the why:
- **lowercase kebab-case** (`attribution-design`, not `Attribution Design` or
  `attribution_design`) — no spaces means no quoting in shells, no `%20` in links, and
  consistent casing means no "did I capitalize it?" guessing.
- **ISO date `yyyy-mm-dd`, leading**, for anything time-stamped — it sorts
  chronologically by plain name sort, which is the whole point of dating a file.
- **Most-significant-first.** Topic before qualifier (`oncall-runbook__espresso`, not
  `espresso__oncall-runbook`) so related files cluster when sorted.
- **No `final`, `v2`, `FINAL-FINAL`, `(1)`.** Version lives in git or Drive history, not
  the name. If you must mark a real revision, use `__v2` deliberately, never as panic.
- **Spell out cryptic abbreviations** unless they're house terms you'd recognize cold
  (`ash`, `uce`, `mp` are fine; `doc2-newcopy` is not).
- **Folders are kebab too**, except the pinned `01_`/`02_` work buckets and `_`-prefixed
  helpers, which follow their existing scheme.

Examples:
- `Q4 sales final FINAL v2.xlsx` → `2025-q4-sales-summary.xlsx`
- `Screenshot 2026-05-31 at 8.45.43 PM.png` → `2026-05-31__drive-folder-structure.png`
- `notes.gdoc` (from a planning meeting) → `2026-05-20__attribution-planning-notes.gdoc`
- `design doc (copy).gdoc` (living) → `attribution-pipeline-design.gdoc`

## Auditing a directory

When the user points at a folder of files and wants them sorted, this is the core job:
read each file enough to know what it *is* (name, extension, and a peek at contents when
the name is uninformative — don't guess from a vague name), then produce a single table.
Stay in advisory mode — output the plan, don't move or rename anything.

ALWAYS use this exact table:

| Current | Suggested name | Suggested location | Why |
|---------|----------------|--------------------|-----|
| `Q4 sales final FINAL v2.xlsx` | `2025-q4-sales-summary.xlsx` | `09_ARCHIVE/projects/2025/` | shipped artifact, prior half → archive |
| `notes.gdoc` | `2026-05-20__attribution-planning-notes.gdoc` | `01_PROJECTS/2026-1/attribution-pipeline-manager/meeting-notes/` | time-stamped note for an active H1 project |
| `random.png` | — (open it first) | needs triage → `00_INBOX/` | couldn't determine contents from name |

Then, below the table:
- List any **folders the user needs to create** for these targets (as instructions).
- Flag files you **couldn't classify** — route them to the inbox rather than guessing a
  wrong home, and say what you'd need to know to place them.
- If many files share a destination, **note the pattern** ("all 6 screenshots →
  `~/media/screenshots`, renamed `yyyy-mm-dd__<subject>`") instead of repeating rows —
  silent truncation reads as "I covered everything"; an explicit pattern note doesn't.
