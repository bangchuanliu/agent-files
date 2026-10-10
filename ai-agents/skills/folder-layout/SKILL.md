---
name: folder-layout
kind: leaf
description: >-
  Folder layout: init or refactor a macOS home directory, a personal project tracked by goals, plan, and progress, or a coding project, then file and name items within it. Use when: set up my Mac folders, clean Downloads or Desktop, organize files, start a personal project or goal tracker, restructure a messy project folder, scaffold or reorganize a code repo, where should this file go, or name this file.
---

# Folder Layout

Give every file one obvious home and keep the layout from rotting. Pick a **mode** by what is being organized, then an **action**: **init** (create a new layout) or **refactor** (reshape an existing one).

| Mode | Organizes | Read |
|---|---|---|
| macOS | the home directory: Downloads, Desktop, documents, screenshots, archive | [`modes/macos.md`](modes/macos.md) |
| Personal project | a non-code project tracked by goals, plan, and progress | [`modes/personal-project.md`](modes/personal-project.md) |
| Coding project | a source repository | [`modes/coding-project.md`](modes/coding-project.md) |

If the target is a single file ("where does this go?"), use the mode of its destination and skip straight to that file's placement rules. If the mode is ambiguous, ask once before planning.

## Plan, then apply

Every init or refactor runs the same four steps. Never skip the confirmation.

1. **Survey.** Read the target enough to know what each item is: name, extension, and a content peek when the name is uninformative. For refactor, account for every top-level item; group repeated patterns.
2. **Plan.** Return the plan table, then the extra sections below it. Change nothing yet.
3. **Confirm.** Ask the user to approve, edit, or reject the plan. Apply only the approved rows.
4. **Apply and verify.** Execute with the safety rules, then re-list the target and show the resulting tree.

Plan table, exact columns:

| Current | Action | New name | New location | Why |
|---------|--------|----------|--------------|-----|
| `Screenshot 2026-05-31 at 8.45.43 PM.png` | move+rename | `2026-05-31__drive-folder-structure.png` | `~/media/screenshots/` | screenshot, subject from content |
| (none) | create | `PROGRESS.md` | `~/personal/projects/marathon/` | progress log missing |
| `random.bin` | leave | - | `~/Downloads/` | cannot identify; needs the user |

Actions: `create`, `move`, `rename`, `move+rename`, `edit` (content change, such as an updated import path), `leave`. There is no delete action.

Below the table add:
- **Folders to create.**
- **Unclassified items**, each with the missing fact needed to place it.
- **Delete candidates** for the user to remove themselves: duplicates, installers, stale checkouts.
- **Side effects**: settings to change, references to update, cloud-sync churn.

Safety rules when applying:
- Never delete, overwrite, or empty trash. Use `mv -n` and `mkdir -p`; in a git repo, use `git mv`.
- Stop and report on any collision or failed command instead of improvising.
- Outside git, append every move to `~/archive/_moves/yyyy-mm-dd.tsv` (`source<TAB>destination`) so the user can reverse it.
- Done means every approved row is applied or reported failed, and the final tree is shown.

## Naming

Names identify the file without opening it and sort next to siblings. Coding projects follow their ecosystem's naming instead; see that mode.

- Point-in-time artifacts: `yyyy-mm-dd__kebab-topic__qualifier.ext`. Evergreen files drop the date.
- Lowercase kebab-case for files and folders; topic before qualifier (`oncall-runbook__api`).
- Versions live in git or file history; add `__v2` only for a real published revision.
- Spell out unclear abbreviations. Prefix pinned helpers with `_` (`_templates/`) so they sort first.

Examples:
- `Q4 sales final FINAL v2.xlsx` -> `2025-q4-sales-summary.xlsx`
- `notes.md` from a planning call -> `2026-05-20__marathon-training-planning.md`
- `design doc (copy).md` for a living design -> `search-quality-refresh-design.md`
