---
name: review-and-verify
description: Use when reviewing a change or preparing a cloud-edge diagnostics task for handoff, with evidence required before any completion claim.
---

# Review and Verify

Review the authorized diff against its feature traceability, service boundaries, and fresh validation evidence before handoff.

## Input

- The approved task or feature documents, diff, and current worktree status.
- Test, lint, format, typecheck, build, health-check, and contract-test results that were actually run.

## Output

- A review report that separates verified behavior, failed checks, unrun checks, environment limitations, and remaining risks.
- Actionable findings tied to the affected file or requirement.

## Review focus

- Confirm each edited file is within the task write set and trace it from `spec.md` through `plan.md`, `tasks.md`, implementation, and tests.
- Check service boundaries: terminal simulator reaches only the edge service, web reaches the cloud API rather than a database, and cross-service contracts retain independent `assetId`, `terminalId`, `edgeId`, and `eventId` semantics.
- Inspect for conflict markers, unexplained placeholders, temporary files, secrets, unsafe file/path handling, and unrelated edits.
- Run `git diff --check` and the relevant focused checks. Use `pnpm validate` as the full repository quality entry point when it is feasible and in scope.

## Evidence rule

- Never claim a change is complete, fixed, passing, or production-ready without fresh command output or directly observed behavior supporting that claim.
- State a check as not run when it was not run. State a failure when it failed; do not relabel it as an environmental pass.

## Failure handling

- Stop scope expansion when a finding requires an unapproved architecture or contract change. Report the exact evidence, affected boundary, and needed decision.
- Do not commit, push, open a pull request, reset, or delete changes as part of review unless separately authorized.
