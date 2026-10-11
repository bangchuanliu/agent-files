# Coding project mode

Organize a source repository by its **ecosystem's convention first**. Tools, IDEs, and new contributors already expect it; a custom layout costs everyone. Use the generic layout only where the ecosystem is silent.

## Detect the ecosystem

Read the manifests at the root: `pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`, `build.gradle`/`pom.xml`, `Gemfile`, etc. Multiple manifests in subfolders means a monorepo: apply this mode per package and keep shared tooling at the root.

| Ecosystem | Scaffold (init) | Source | Tests |
|---|---|---|---|
| Python | `uv init --package <name>` | `src/<pkg>/` | `tests/` |
| Node / TypeScript | `npm init -y` plus `tsconfig.json` | `src/` | `test/` or colocated `*.test.ts` |
| Go | `go mod init <module>` | `cmd/<app>/`, `internal/` | `*_test.go` beside code |
| Rust | `cargo new <name>` | `src/` | inline `#[cfg(test)]`, `tests/` for integration |
| JVM (Gradle) | `gradle init` | `src/main/<lang>/` | `src/test/<lang>/` |

Prefer the scaffold command over hand-made folders; it gets defaults right.

## Generic root layout

```
<repo>/
├── README.md        what it is, quickstart, how to test
├── LICENSE
├── .gitignore       ecosystem template plus local artifacts
├── .editorconfig
├── AGENTS.md        agent instructions (optional)
├── <manifest + lockfile>
├── src/             or the ecosystem's source dir
├── tests/           or the ecosystem's test location
├── docs/            design docs, ADRs as docs/adr/NNNN-title.md
├── scripts/         dev and ops scripts, executable, with usage headers
└── .github/workflows/  CI
```

Rules:
- Root holds config and entry docs only; code and data never sit loose at the root.
- Generated output (`build/`, `dist/`, `target/`, `node_modules/`, `.venv/`) is gitignored, never organized or committed.
- Names follow the language: `snake_case.py`, `kebab-case` or `camelCase` per the existing JS codebase, `PascalCase.java`. Match what the repo already uses over the general naming rule.
- Do not hand-edit generated files such as `CHANGELOG.md` produced by release tooling.

## Init

1. Ask for name, ecosystem, and whether it is a library, CLI, or service if not given.
2. Plan: the scaffold command, then `create` rows for the generic files it did not produce, `git init` if needed.
3. After applying, run the ecosystem's build and test commands once; done means both pass on the empty project.

## Refactor

1. Require a clean `git status` (or the user's OK) so every change is reviewable as a diff.
2. Run the build and tests first and record the baseline result.
3. Survey the tree against the ecosystem convention. Plan `move` rows with `git mv`, plus an `edit` row for every reference to a moved path: imports, package declarations, build config, CI paths, Dockerfiles, docs links. Find them by searching for the old path and module name.
4. After applying, rerun build and tests. Done means the result matches or beats the baseline and no search hit for an old path remains.
5. Do not commit unless asked; summarize the diff for the user.

Keep a structural refactor separate from behavior changes so the diff stays pure moves and reference updates.

## Where a single item goes

Production code -> source dir by module. Test -> the ecosystem's test location mirroring the source path. One-off script -> `scripts/`. Design note -> `docs/`. Sample or fixture data -> `tests/fixtures/`. Secrets -> never in the repo; use the approved secret store.
