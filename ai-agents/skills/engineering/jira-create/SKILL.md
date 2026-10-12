---
name: jira-create
kind: leaf
description: "Use when: drafting and filing agent-optimized Jira tickets (structured fields, acceptance criteria, inferred labels, epic link) after the user approves the draft - one ticket (create Jira, Jira ticket, create ticket, document work) or a batch of related tickets under one epic. NOT for: updating, transitioning, commenting on, or searching existing tickets."
---

# Jira Create

## Objective

Draft Jira tickets with every field filled and file them only after the user approves the draft. Each ticket must be parseable by planning, development, and QA agents without human clarification, so its fields, description, and acceptance criteria are structured and specific.

Success: the user approved a draft naming project, type, summary, priority, assignee, due date, story points, component, labels, epic decision, and acceptance criteria; the ticket (or batch) exists in Jira with exactly those values; and the user has each ticket key and URL.

## Guardrails & Constraints

- MUST create nothing until the user explicitly approves the draft, because a filed ticket notifies people and is visible to the whole project. For a batch, approval of the full batch plan (every summary plus the shared fields) covers the batch.
- MUST search the target project for existing epics matching the topic and offer the top 3-5 for the user to pick, plus "None found, create new?" when nothing fits, so related work is not orphaned.
- MUST mark each field you are unsure of in the draft and offer 2-3 alternatives for it.
- MUST apply company context when your instructions provide some for this skill: it overrides the project key, components, labels, field names, and due-date rules below. Without it, the defaults below are complete.
- IF the project key is not stated and no company context supplies one, MUST ask.
- IF no Jira integration is available, MUST stop after the draft and report that it could not be filed.
- IF a create call fails or its result is unclear, MUST search for the ticket before retrying, so a retry cannot file a duplicate; IF it still cannot be confirmed, stop and report.

## Preferences

- SHOULD use these defaults when company context does not override them:
  - **Assignee:** the current requester.
  - **Labels:** topic labels only; add a baseline label only when company context names one.
  - **Due date** (from today): P0 +2 weeks, P1 +1 month, P2 +3 months, P3 none.
  - **Story points:** S(1), M(3), L(5).
  - **Type:** Story, Bug, Task, or Spike. **Priority:** P0-P3.
- SHOULD infer fields from the prompt; these hints are examples, not a closed list:

  | Keyword | Suggested fields |
  |---|---|
  | docs, documentation | Labels: `docs` |
  | pipeline, DAG, airflow | Labels: `pipeline`, Component: `data-platform` |
  | freshness, validation | Labels: `data-quality` |
  | dashboard, grafana | Labels: `dashboards` |
  | architecture, RFC | Labels: `architecture`, Type: Spike |
  | bug, broken, fix | Type: Bug, Priority: P2 or higher |
  | quick, small | Points: S(1) |
  | refactor, migration | Points: L(5) |

- SHOULD pick components from company context, else from `documentation`, `backend`, `frontend`, `data-platform`, `infrastructure`, `runbook`, `analytics`; labels from company context, else from `docs`, `runbook`, `onboarding`, `architecture`, `analytics`, `dashboards`, `data-quality`, `pipeline`, `cross-team`.
- SHOULD write the description from this default template, which agents downstream parse:

  ```
  ## Goal
  [One sentence]

  ## Content Source
  [URL to wiki/dashboard/confluence/doc]

  ## Target Location
  [Where in codebase/docs]

  ## Acceptance Criteria
  - [ ] [Specific, verifiable criterion]
  ```

- IF filing a batch, SHOULD put the tickets under one epic, keep shared fields consistent, include the source URL in every description, number the summaries (`[01/50] Add architecture overview`), and give the user a query to find them (`project = <PROJECT> AND labels = <LABEL> ORDER BY priority DESC, created ASC`).

## Output

- **Draft:** an action-oriented summary plus every field listed under Objective, the filled description, uncertain fields with their alternatives, and a closing "Does this look right?".
- **After creation:** each ticket key and URL; for a batch, the epic key and the query.

## Verification

- Before asking for approval, the draft names every field listed under Objective and every acceptance criterion is verifiable.
- After creation, each ticket read back from Jira (key, URL, fields) matches the approved draft; report any field Jira rejected or changed.
