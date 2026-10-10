# macOS mode

Organize a Mac home directory by **lifecycle**: unsorted, active, reference, archived. Type and topic live inside those buckets, never at the top.

## Target layout

```
~/
├── Downloads/     inbox: every unsorted drop lands here; triage weekly to near-empty
├── Desktop/       kept empty; nothing lives here
├── personal/
│   ├── projects/    active personal projects (see personal-project mode)
│   ├── code/        personal repos (see coding-project mode)
│   ├── learning/    courses, sandboxes
│   └── admin/       taxes, statements, health, home, travel
├── work/
│   ├── repos/       work checkouts; canonical in git
│   └── scratch/     throwaway scripts, query drafts, one-off data
├── reference/     reused material: templates, manuals, snippets
├── media/
│   └── screenshots/ macOS screenshot target
└── archive/       done or dead; date-bucketed (archive/2026/...), moved whole
```

Rules:
- `~/Downloads` is the inbox because every app already saves there; do not add a second inbox.
- Keep `personal/` and `work/` split at the top so backup, sync, and retention can differ.
- Code is canonical in git. Stale checkouts are delete candidates, not archive items.
- Date-bucket only inside `archive/`.

## Leave alone

Never move or restructure these; list a problem as a side effect instead:
- `~/Library`, `~/Applications`, and every dotfile or dot-folder (`~/.ssh`, `~/.config`, tool caches, worktree roots).
- App-managed libraries: `Photos Library.photoslibrary`, `~/Music`, `~/Movies` app bundles.
- Cloud-provider mounts under `~/Library/CloudStorage`; moving into or out of them triggers sync.
- `~/Documents` when "Desktop & Documents Folders" iCloud sync is on (check before planning). Otherwise its contents migrate into the layout and the folder stays for apps that default to it.

## Init

1. Survey `ls -la ~` and note which target folders already exist and whether iCloud Desktop & Documents sync is on.
2. Plan `create` rows for missing folders only.
3. Side effects to propose (each needs approval):
   - Screenshot target: `defaults write com.apple.screencapture location ~/media/screenshots && killall SystemUIServer`.
   - Finder sidebar favorites for `personal`, `work`, `reference`: manual, list the steps.

## Refactor

Survey `~/Downloads`, `~/Desktop`, `~/Documents`, and any non-layout top-level folder in `~`. Place each item with the decision walk below; group patterns (`all 14 .dmg installers -> delete candidates`).

## Where a single item goes

Stop at the first match:
1. Cannot classify in 5 seconds -> stay in `~/Downloads`.
2. Installer, duplicate, or reproducible download -> delete candidate.
3. Belongs to an active personal project -> `~/personal/projects/<project>/`.
4. Code -> `~/personal/code/` or `~/work/repos/`.
5. Throwaway work material -> `~/work/scratch/`.
6. Personal logistics -> `~/personal/admin/<topic>/`.
7. Reused reference -> `~/reference/`.
8. Screenshot or recording -> `~/media/screenshots/` (or a project folder if it belongs to one).
9. Done or dead -> `~/archive/<yyyy>/`, moved whole.
