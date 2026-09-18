---
name: project-bootstrap
description: Use when starting or repairing the cloud-edge device diagnostics project and you need to establish runnable local prerequisites without changing business behavior.
---

# Project Bootstrap

Prepare a development environment for this repository's four-part diagnostic flow: terminal simulator → edge service → cloud API → Vue management web.

## Input

- The requested component or end-to-end path.
- Current checkout and any user-supplied environment configuration.

## Output

- A reproducible startup sequence and a clear record of services that are healthy or blocked.
- No business feature, contract, dependency, or infrastructure change unless that change is separately authorized.

## Project checks

- Keep the terminal simulator connected only to `apps/edge-service`; do not use a cloud API shortcut.
- Keep the web application in `apps/web` behind the cloud API; do not introduce direct database access.
- Preserve distinct `assetId`, `terminalId`, `edgeId`, and `eventId` values in sample requests, configuration, and health checks.
- Inspect the current worktree before starting. Treat existing uncommitted changes as another contributor's work unless their ownership is explicit.

## Verification and failure handling

- Use the repository's documented service health checks when they exist, then run `pnpm validate` when the requested bootstrap work changes repository-controlled setup.
- Report each attempted command and its observed result. If a required service, dependency, secret, or port is unavailable, stop at the failed boundary and state the exact missing prerequisite; do not replace it with fake credentials, mock production behavior, or an unapproved configuration change.

## Prohibited

- Do not add sample secrets or log credentials.
- Do not bypass the edge service, directly access a service database, or start unrelated components merely to claim an end-to-end result.
