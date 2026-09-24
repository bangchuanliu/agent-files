---
name: jira-create
kind: leaf
description: "Create agent-optimized JIRA tickets with structured fields. Use when: create JIRA, JIRA ticket, create ticket, document work, batch tickets."
---

# JIRA Create

Create JIRA tickets with fields that enable efficient agent processing. Every ticket should be parseable by TL, dev, and QA agents without human clarification.

## Step 0 - company context

Read `~/.config/dotfiles/context/jira-create/context.md` if it exists. If it does not exist,
skip this step - its absence is normal and the generic guidance below is complete on its own.

## Process

1. **Search for existing Epics** in the configured Jira project matching the topic. Present top 3-5 for user to pick.
2. **Infer fields** from the user's prompt using the heuristics below.
3. **Apply company context** from Step 0 when present. It may override project keys, components, labels, field names, or due-date rules.
4. **Present a draft** with all fields filled in. Highlight uncertain fields with 2-3 alternatives.
5. **Wait for explicit confirmation** before creating through the available Jira integration - never create without approval.

## Draft Format

```
Draft Ticket

Summary: [action-oriented title]
Type: Story | Bug | Task | Spike
Assignee: [current requester or configured default]
Priority: P0 | P1 | P2 | P3
Due Date: [auto: P0→+2wk, P1→+1mo, P2→+3mo, P3→none]
Story Points: S(1) | M(3) | L(5)
Component: [from component list]
Labels: [baseline label if configured], [+ topic labels]
Epic Link: [from search, or "None found, create new?"]

Description:
[filled-in template]

Does this look right?
```

## Description Template

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

## Defaults

- **Assignee**: current requester unless the company context specifies a default
- **Labels**: include a baseline label only when the company context specifies one
- **Due date**: P0→+2wk, P1→+1mo, P2→+3mo, P3→none (from today)

## Inference Heuristics

| Keyword | Suggested Fields |
|---------|-----------------|
| docs, documentation | Labels: `docs` |
| pipeline, DAG, airflow | Labels: `pipeline`, Component: `data-platform` |
| freshness, validation | Labels: `data-quality` |
| dashboard, grafana | Labels: `dashboards` |
| architecture, RFC | Labels: `architecture`, Type: Spike |
| bug, broken, fix | Type: Bug, Priority: P2+ |
| quick, small | Points: S(1) |
| refactor, migration | Points: L(5) |

## Components

Generic defaults: `documentation`, `backend`, `frontend`, `data-platform`, `infrastructure`, `runbook`, `analytics`.

Use the company context component list when present.

## Labels

Generic defaults: `docs`, `runbook`, `onboarding`, `architecture`, `analytics`, `dashboards`, `data-quality`, `pipeline`, `cross-team`.

Use the company context label taxonomy when present.

## Batch Creation

For many related tickets: create one Epic, use consistent fields, include source URL in every description, number summaries (`[01/50] Add architecture overview`).

Query pattern: `project = <PROJECT> AND labels = <LABEL> ORDER BY priority DESC, created ASC`
