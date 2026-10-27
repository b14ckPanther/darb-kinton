# Progress ledger

The single place that says where Darb Kinton stands. Update it after **every** task (one row) and at the end of every phase. After a context reset, read this file and `git log --oneline -20` first; if they disagree, `git log` is the truth and this file gets fixed.

## Current state

- **Phase:** not started (next: Phase 0, bootstrap)
- **Branch:** none (repo not created yet)
- **Last task:** none
- **Blockers:** none
- **Overall:** 0%

## Phases

| # | Phase | Weight | Status | Branch | Commit range | Approved by Nour |
|---|---|---|---|---|---|---|
| 0 | Repo bootstrap, CI, conventions | 4 | todo | `phase/00-bootstrap` | | |
| 1 | Confirm the spec | 2 | todo | `phase/01-spec` | | |
| 2 | Design system | 8 | todo | `phase/02-design-system` | | |
| 3 | Clickable prototype on seed data | 10 | todo | `phase/03-prototype` | | |
| 4 | Signaling and presence | 7 | todo | `phase/04-signaling` | | |
| 5 | Pairing and E2E crypto | 10 | todo | `phase/05-pairing-crypto` | | |
| 6 | WebRTC transfer engine | 12 | todo | `phase/06-transfer-engine` | | |
| 7 | Resumable transfers | 8 | todo | `phase/07-resume` | | |
| 8 | Several devices and far away | 10 | todo | `phase/08-fanout-far` | | |
| 9 | Clipboard, links, PWA | 5 | todo | `phase/09-clipboard-pwa` | | |
| 10 | Settings, admin, CLI | 4 | todo | `phase/10-admin-cli` | | |
| 11 | Hardening | 8 | todo | `phase/11-hardening` | | |
| 12 | Release pipeline | 4 | todo | `phase/12-release` | | |
| 13 | Darb Budokai integration (optional) | 3 | todo | `phase/13-budokai` | | |
| 14 | Docs, demo, launch | 5 | todo | `phase/14-launch` | | |

Status values: `todo`, `in progress`, `review`, `done`, `skipped (reason)`.

## Task log

One row per task. "Tests" is the command run and its result (e.g. `go test -race ./... ok (142 tests)`). "Skills" names every skill invoked for the task.

| Date | Phase | Task | Status | Commits | Tests | Skills | Notes |
|---|---|---|---|---|---|---|---|
| | | | | | | | |

## Screen approvals (Phases 2-3 and any UI change)

| Date | Screen / component | Viewports checked | Nour's verdict | Follow-ups |
|---|---|---|---|---|
| | | | | |

## Rulings (decisions the agent made without Nour)

Pick the cheapest reversible option. If the cost if wrong is high (crypto, wire format, threat model, public actions), stop and ask instead.

| Date | Phase | Ruling | Why | Cost if wrong | Status (proposed / confirmed / reversed) |
|---|---|---|---|---|---|
| | | | | | |

## Measurements

| Date | What | Setup | Result | Commit |
|---|---|---|---|---|
| | | | | |
