# Building and shipping rules

Covers writing, debugging, testing, committing, and releasing code or config.

## Guardrails

- Never claim a bug is fixed without first reproducing it end to end, as close to the user's experience as possible.
- Every bug fix ships with a regression test, and new behavior ships with tests; never ask whether tests are wanted.
- Never add an agent as co-author in commit messages or PR descriptions.

## Preferences

- Prefer simplicity, correctness, robustness, and long-term maintainability over development cost.
- Fix lint errors, test failures, and flaky tests you encounter, even when your change did not cause them.
- When testing a user-facing product, hold the UI to a pixel-perfect bar and fix anything that clearly looks off along the way.
