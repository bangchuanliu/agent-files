---
name: file-layout
kind: leaf
description: "Use when: deciding where a file belongs, starting a personal or coding project folder, tidying Downloads or Desktop, or archiving inactive material on a work or personal Mac. NOT for: restructuring code inside a repository, or deleting files."
---

# File Layout

## Objective

Give every file one obvious, predictable home on a work or personal Mac, classified by **ownership** (company or personal), then **purpose**, then **lifecycle** (inbox, active, reference, archive). Success: each placed item sits where its profile says, nothing was lost or silently replaced, and only the structure the task needed was created.

## Context & Tools

- Every branch needs the machine **profile**, `work` or `personal`. Load the matching layout:
  - work: [`references/work-macos.md`](references/work-macos.md)
  - personal: [`references/personal-macos.md`](references/personal-macos.md)
- WHEN creating or reshaping a project folder, also load [`references/project-layouts.md`](references/project-layouts.md).

## Guardrails & Constraints

- MUST take the profile from the user; IF they have not given it and the answer changes where items go, ask. Hostname and folder contents are not evidence of the profile.
- MUST keep company and personal material apart, follow the employer's policy on managed devices, and keep company data and code in company locations and accounts. Separate folders are not a security boundary.
- MUST get the user's approval of a preview before any delete, overwrite, bulk move, archive, or reorganization, and apply only the approved scope. Moves are no-clobber (`mv -n`, `git mv` inside a repo); on a conflict, stop and report both paths.
- MUST leave system-managed folders, app-managed libraries (Photos, Music, game libraries), Git internals, and the standard macOS folders (Documents, Pictures, Movies, Music) where they are. Report a problem with them instead.
- IF an item involves a symlink, hidden file, cloud-synced location, permission change, or external volume, check the effect of the change (broken links, sync churn, lost access) before making it.
- MUST keep one canonical copy of each item and preserve existing names, metadata, and repository conventions unless the user approves a change.

## Preferences

- SHOULD reuse existing folders and keep the tree shallow; create a folder only when an item is about to go in it.
- SHOULD check whether an item belongs to an existing project first; notes, screenshots, and documents for a project go inside that project, ahead of any general location in the profile.
- Lifecycle:
  - **Inbox:** Downloads and Desktop hold items only until their purpose is known.
  - **Active:** move an item to its project, work, personal, or learning location once its purpose is known.
  - **Reference:** reusable material shared across projects goes in the profile's reference location, not copied into each project.
  - **Archive:** inactive material goes to `archive/`, optionally under a year folder, with approval and within any retention rules. Archive rather than delete.

  An item may skip stages; choose the least disruptive move.

## Output

- The paths created or changed, and any conflicts, decisions, or items still waiting on approval.

## Verification

- Every reported path exists at its destination, and each moved item is gone from its source, shown by listing both.
- IF the operation could touch unrelated files, show that they are unchanged.
- Report every incomplete operation, conflict, and unverified item.
