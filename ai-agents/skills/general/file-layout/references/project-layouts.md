# Project layouts

Templates are starting points, not checklists; create a file only when it is immediately useful.

## Location

| Project | Work laptop | Personal laptop |
|---|---|---|
| Personal, non-code | `~/personal/projects/<name>/` (if permitted) | `~/projects/personal/<name>/` |
| Personal, code | `~/personal/code/<name>/` (if permitted) | `~/projects/code/<name>/` |
| Company code | `~/work/repos/<name>/` | - |

## Personal project

```text
<project>/
├── README.md          # Purpose, scope, current status, next action, links
├── PLAN.md            # Milestones, completion criteria, next action
├── notes/             # Research and dated notes
├── resources/         # Supporting material
└── archive/           # Retired project artifacts
```

Start with `README.md` alone. Add `PLAN.md` for multi-step work, `GOALS.md` only for substantial measurable goals, and `PROGRESS.md` only when a dated history is needed. Each fact, such as current status, lives in exactly one file.

## Coding project

Follow the repository's and ecosystem's conventions over any generic tree:

- Scala/Spark: `build.sbt`, `src/main/scala`, `src/test/scala`
- Python: `pyproject.toml`, package directory, `tests/`
- Node/TypeScript: `package.json`, the framework's source and test layout
- Go: `go.mod`, idiomatic packages

Add `README.md`, `.gitignore`, and the manifest and lockfile. Add `docs/`, `scripts/`, `.github/workflows/`, `AGENTS.md`, or `LICENSE` only when the project needs them.
