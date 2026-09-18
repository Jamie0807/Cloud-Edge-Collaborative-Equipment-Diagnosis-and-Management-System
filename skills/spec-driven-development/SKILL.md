---
name: spec-driven-development
description: Use when defining or changing a business feature in the cloud-edge device diagnostics project before implementation begins.
---

# Spec-Driven Development

Turn an approved diagnostic-management need into traceable feature documentation before business code changes.

## Input

- A feature request, affected services, and known constraints.
- Existing approved `constitution.md`, `spec.md`, `plan.md`, and `tasks.md` when they apply.

## Output

- A feature `spec.md`, `plan.md`, and `tasks.md` that connect user stories and acceptance criteria to owned files and verification commands.
- An ADR only when the work makes a durable architecture decision.

## Project decisions to capture

- Identify whether the change belongs in `apps/web`, `apps/cloud-api`, `apps/edge-service`, `apps/terminal-simulator`, `packages/contracts`, or `packages/test-fixtures`.
- For every cross-service event or API, state how `assetId`, `terminalId`, `edgeId`, and `eventId` remain independently meaningful.
- State the terminal-to-edge-to-cloud path and any file-save, metadata-normalization, simulated-analysis, or pending-upload-cache effect.
- Define happy path, invalid input, unavailable dependency, and empty/loading/error UI behavior where applicable.

## Boundaries

- Do not turn ambiguous requirements into production code. Clarify conflicting acceptance criteria, destructive effects, architecture changes, or external-release scope before planning implementation.
- Do not substitute governance documents for an actual business feature spec, and do not expand a feature into unrelated dependency upgrades or refactoring.

## Success evidence and failures

- Tasks name their file write set, prerequisites, verification command, and acceptance criterion. The planned test set includes contract coverage for cross-service fields where relevant.
- When repository-wide quality is in scope, the task plan explicitly names `pnpm validate` as the full gate; when a repository skill changes, run `python3 /Users/jamie/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-directory>` for each changed skill directory.
- If requirements cannot identify an owner, contract, or acceptance condition, record the unresolved decision and stop before implementation. A plan without that traceability is not ready to execute.
