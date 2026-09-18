---
name: tdd-quality-gates
description: Use when implementing or changing observable behavior in the cloud-edge device diagnostics project and you need test-first evidence plus repository quality gates.
---

# TDD Quality Gates

Use a failing test to express the accepted behavior, implement the smallest change that makes it pass, then run the relevant project gates.

## Input

- An approved feature task with acceptance criteria.
- The target package and its existing test convention.

## Output

- Tests that demonstrate the requested behavior and command output showing the tested scope.
- A final gate record distinguishing passed, failed, and not-run checks.

## Test selection

- Use Vitest and Vue Testing Library for `apps/web`; use Playwright for critical management-path flows.
- Use JUnit 5 for `apps/cloud-api` and pytest for `apps/edge-service` or `apps/terminal-simulator`.
- Add schema or contract tests in `packages/contracts` whenever a cross-service payload changes; preserve independent `assetId`, `terminalId`, `edgeId`, and `eventId` semantics.
- Cover success, invalid input, exceptions, and relevant empty, loading, or error states.

## Required sequence

1. Add or update the focused test so it fails for the missing behavior (RED).
2. Make the minimal implementation pass (GREEN), then refactor only while the test remains green.
3. Run the focused test and the applicable repository checks. Run `pnpm validate` for the full quality gate when the workspace is ready for full validation.

## Prohibited and failure handling

- Do not replace behavioral tests with a manual demo, weaken assertions to make a test pass, or report a gate as passed without its command output.
- If an environment constraint prevents a check, preserve the failure or skip evidence, state why it could not run, and identify the remaining risk instead of declaring completion.
