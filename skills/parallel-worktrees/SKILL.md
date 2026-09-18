---
name: parallel-worktrees
description: Use when two or more independent cloud-edge diagnostics tasks can proceed concurrently and require isolated write sets and worktrees.
---

# Parallel Worktrees

Split only genuinely independent work across isolated worktrees, with one reviewer responsible for integration.

## Input

- Two or more candidate tasks, each with expected files, dependencies, and verification commands.
- The base repository state and the location of existing worktrees.

## Output

- A task-to-worktree assignment with explicit, non-overlapping write sets.
- Per-agent results listing changed files, commands run, observed results, untested areas, and risks for the integrator.

## Partitioning rules

- Assign different files to every concurrent agent. A shared file, shared contract, shared fixture, shared quality workflow, or shared governance document is a dependency, not parallel work.
- Do not parallelize changes that jointly define a cross-service payload until its `assetId`, `terminalId`, `edgeId`, and `eventId` contract has a single owner or an approved sequencing plan.
- Keep implementation, Specs Kit documents, quality tooling, and CI changes isolated when they can be independent; otherwise sequence them.
- Inspect each worktree's status before writing and preserve unexplained changes.

## Prohibited

- Do not share an unreviewed write set, edit another agent's worktree, or merge/commit/push on another agent's behalf.
- Do not use multiple agents merely to split a single tightly coupled feature.

## Success evidence and failures

- Before dispatch, show that all write sets are disjoint and list their required verification.
- Include `pnpm validate` in the assigned verification when repository-wide quality is in scope; if a task changes a repository skill, run `python3 /Users/jamie/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-directory>` once for each changed skill directory and return the result.
- If overlap is discovered, pause the affected tasks, choose one owner or serialize the change, and report the conflict. Integration may proceed only after reviewing each returned diff and its actual validation evidence.
