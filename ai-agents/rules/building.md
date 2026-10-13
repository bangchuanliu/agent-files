# Building and shipping rules

## Guardrails

- Reproduce a bug end to end, as close to the user's experience as possible, before claiming it fixed, and confirm the same path passes afterwards; if it cannot be reproduced, say so and report the fix as unverified.
- Every bug fix ships with a regression test, and new behavior ships with tests; never ask whether tests are wanted.
- Never add an agent as co-author in commit messages or PR descriptions.

## Environment

- Create git worktrees under `$WTREE_ROOT/<repo-group>/` (default `~/.worktree`), never inside the main checkout; the `wtree` skill does this.

## Preferences

- Prefer simplicity, correctness, robustness, and long-term maintainability over development cost.
- Fix lint errors, test failures, and flaky tests you encounter, even when your change did not cause them.
- When testing a user-facing product, hold the UI to a pixel-perfect bar and fix anything that clearly looks off along the way.
