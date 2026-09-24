# Skill naming and category prefixes

Read this when creating, renaming, or reviewing a skill. It does not apply to normal work.

Skills live in `ai-agents/skills/` and are symlinked into `~/.copilot/skills/` and
`~/.claude/skills/`. Rename the source directory, then relink - renaming the symlink alone
does not rename the skill.

## Naming shapes

Two shapes, picked by complexity. Verb position is the signal; the category prefix is
optional and orthogonal.

| Shape | Use for | Examples |
|---|---|---|
| `<verb>-<object>` | A simple atomic skill - one action, one output, no `mode`, nothing to route between | `generate-plan`, `git-pull` |
| `<object>` | A multi-action skill with no natural family - the actions are variants of one object, so the verb moves into a `mode` argument | `gsheet` |
| `[<category>-]<object>-<verb>` | A complex skill - modes/variants, multi-step workflow, or meaningful internal routing. Add the category prefix only when it joins a family of 2 or more | `table-schema-check`, `template-general-readout`, `docs-preview` |

Where a family exists, the category prefix filters the list when you type it. Those names
read top-down, coarse to fine. A missing verb means the skill has multiple actions - check
its `mode` argument.

## Category prefixes in this repo

| Type | Contains | Pick when |
|---|---|---|
| `table-` | `null-check`, `row-count`, `duplicate-check`, `schema-check`, `freshness-check`, `distribution-check`, `traceability-check` | Anything about validating one table's data, shape, freshness, or lineage |
| `template-` | `general-readout`, `doc-data-issue-rc` | A document skeleton the agent fills in |
| _(none)_ | atomic verb-first: `generate-plan`, `git-pull`; short object: `gsheet`, `hop`, `start`, `wtree`, `yell`; complex verb-last: `jira-create`, `docs-preview`, `review-self`, `review-others`, `skill-creator`, `skill-improver` | Standalone skills with no family. Prefix-less does not mean atomic - verb position tells you which |

## Worked example: `table-schema-check`

`table-schema-check` is verb-last because it belongs to the `table-` family and performs a
specialized check. It sorts naturally with the other table checks and makes the family easy
to scan:

```text
table-distribution-check
table-duplicate-check
table-freshness-check
table-null-check
table-row-count
table-schema-check
table-traceability-check
```

A standalone name like `check-schema` would hide that relationship and should be avoided.

## Rules when adding a skill

- Pick the shape from the table above. The test is complexity, not prefix - `jira-create`
  and `docs-preview` carry no prefix and are still complex.
- One verb per skill from a closed set: `check` `count` `compare` `validate` `analyze`
  `investigate` `assign` `render` `generate` `format` `create` `review` `deploy` `monitor`
  `preview` `cleanup`. Noun forms (`-validation`, `-analysis`) are not used for new skills;
  `skill-improver` predates the rule and is kept.
- Multiple actions -> drop the verb and expose them as a `mode` argument instead.
- A prefix must partition: if it would match fewer than two skills it is the wrong prefix.
  Keep functional prefixes at 8 or fewer entries when possible; past that, split on the
  second token.
- No two skill descriptions may share an opening clause, and every description ends with
  `NOT for: <neighbour> -> use <skill>`.

## Description triggering

A skill's `description` is the only thing Copilot routes on. Any routing rule you delete
from agent rules must already be expressed in the target skill's description, or the skill
stops firing. Verify before removing a routing line.
