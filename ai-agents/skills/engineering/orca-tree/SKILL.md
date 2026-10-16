---
name: orca-tree
kind: leaf
description: "Use when: hand a task off to a new Orca-managed worktree with its own agent - create a standalone worktree named from the task, or a child worktree whose parent is the current worktree, then send the task context and start the work there (orca-tree, orca worktree, child worktree, spin off this work, continue this in another worktree). NOT for: plain git worktrees with no agent (wtree), a Herdr/WezTerm task stack (start), supervising several agents and collecting their results (Orca's orchestration skill), or removing worktrees (wtree clean)."
---

# orca-tree

## Objective

Spin a task off into a new Orca-managed worktree with an agent already working on it: create the worktree under a name derived from the task, link it to the current worktree when it is a child, and send the receiving agent a self-contained brief so it can finish without this conversation. This is a full handoff: the result stays in the new worktree and is not reported back to the caller.

Success: the new worktree exists with the intended name, base, and parent (or none), its agent's terminal shows the brief was received, and the user has the worktree path, branch, and agent terminal handle.

## Context & Tools

- `orca` CLI (Orca app running). `orca status` checks the runtime; `orca worktree current --json` gives the caller's worktree id; `orca worktree list --json` lists existing names.
- One call does the work, with the agent launched in the worktree's first terminal:
  `orca worktree create --name <slug> (--no-parent | --parent-worktree active) --agent <id> --prompt "<brief>" --json`
  Read the agent handle from `result.agentTerminalHandle`, else `result.startupTerminal.handle`. Copy the full `<repoId>::<path>` worktree id when one is needed; a bare repo id is not a worktree id.
- `orca terminal read --terminal <handle> --json` shows whether the brief landed. `orca skills get orca-cli` is the authoritative CLI guide for this Orca version; consult it when a flag or result field differs from the above.

## Guardrails & Constraints

- MUST derive the worktree name yourself as a 2-4 word kebab-case slug of the task ("scan the codebase for dead test code" -> `dead-test-scan`), because it becomes the branch and worktree name; proceed on it without asking. IF the user names the worktree, use their name.
- MUST pick the mode from the request: standalone (`--no-parent`) by default; child (`--parent-worktree active`) WHEN the user says child, sub-task, under this, or names a parent. Orca infers a parent when `--no-parent` is omitted, so always pass one of the two flags explicitly.
- IF child mode and `orca worktree current` finds no Orca-managed worktree (`selector_not_found`) but the current directory is inside a plain git worktree, MUST still link it as the parent rather than stopping: pass `--repo id:<repoId>` and `--parent-worktree worktree:<repoId>::<path>`, where `<path>` is the realpath of `git rev-parse --show-toplevel` (on macOS `/tmp` resolves to `/private/tmp`) and `<repoId>` is the Orca repo whose path is the main clone (`git rev-parse --git-common-dir`'s parent) in `orca repo list --json`. IF that repo is not registered, register it with `orca repo add --path <main clone>` and state it. IF the current directory is not in a git repo at all, stop and report, because there is no parent to link.
- MUST base the new branch on the repo's default base (omit `--base-branch`), leaving the current checkout untouched. Use `--base-branch <ref>` only when the user asks for stacked work, "branch from current", or a named ref.
- IF a worktree with the derived name already exists, MUST NOT create a duplicate or reuse it silently; ask whether to send the brief to the existing worktree or create a new one with a suffix. WHEN the user is unavailable, create `<slug>-2` and state it.
- MUST make the brief self-contained, because the receiving agent sees nothing of this conversation: goal, the facts and links it needs (labelled verified, inferred, or assumed), scope and constraints (e.g. report-only, no push, no deletes), the deliverable and where to write it, and the done criterion. MUST NOT put secrets or tokens in the brief; reference where to get them instead.
- MUST pass the brief through a temp file (`--prompt "$(cat "$brief_file")"`), because inline quoting breaks on quotes, backticks, and `$`; delete the file after the create call.
- IF `orca` is missing or `orca status` does not show the runtime reachable, MUST stop and report it rather than falling back to raw `git worktree` plus an ad hoc agent, because that loses Orca's lineage and terminal tracking; mention `wtree` for a plain worktree.
- IF the create call fails or its result is unclear, MUST check `orca worktree list --json` for the name before retrying, so a retry cannot create a second worktree or a second agent.
- MUST NOT remove, reset, or stop any worktree, terminal, or agent; teardown is the user's call (`orca worktree rm --worktree name:<slug>`).

## Preferences

- SHOULD use the agent the user names; otherwise `copilot` when it is on PATH, else `claude`.
- SHOULD tell the receiving agent to write its result to a file at the worktree root (e.g. `<slug>-report.md`) when the task produces findings, so the user or a later "collect" can read it.
- IF the user wants the result back in this session, SHOULD offer to wait for the agent's terminal to go idle and read the result file, or point to Orca's orchestration skill for supervised workers; the plain handoff does not report back.

## Output

- Worktree name, path, branch and base, mode with parent id (or none), agent and terminal handle.
- A one-line summary of the brief sent, plus how to check progress (`orca terminal read --terminal <handle>`) and remove the worktree later.

## Verification

- `orca worktree show --worktree name:<slug> --json` shows the expected `parentWorktreeId` (the caller's id for child, null for standalone) and branch; `git worktree list` lists the path.
- `orca terminal read` on the agent handle contains text from the brief. IF it does not appear within about a minute, report the handoff as not confirmed rather than re-sending, since a second send can start the work twice.
