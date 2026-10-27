# Darb Kinton

Send files, links and clipboard text between any of your devices (iPhone, Android, Mac, Windows, Linux) or to a friend's browser with nothing installed. Darb Kinton is a single Go binary you host yourself. Everything is end-to-end encrypted: the server only ever sees ciphertext. You can send to several devices at once, send to someone far away, and resume huge transfers that were interrupted.

**Signature moment:** your devices float as orbs. Drag a file onto one and it shoots across in an arc. In Darb Budokai, Darb Kinton is the portal between your devices.

Status: planning package. No code yet. Phase 0 starts the repo.

## Stack

| Layer | Choice | Status |
|---|---|---|
| Language | Go 1.23+ (`go 1.23` directive minimum; Phase 0 pins the current stable toolchain) | fixed by roadmap |
| Peer-to-peer | WebRTC DataChannels, `github.com/pion/webrtc/v4` | fixed by roadmap |
| Signaling | WebSockets (`github.com/coder/websocket`) | WebSockets fixed; library proposed |
| Encryption | End-to-end: P-256 ECDH + HKDF-SHA256 + AES-256-GCM per chunk | E2EE fixed; scheme proposed |
| NAT traversal | Embedded STUN/TURN (`github.com/pion/turn/v4`) + encrypted WebSocket relay fallback | proposed |
| Storage | SQLite via `modernc.org/sqlite` (pure Go, `CGO_ENABLED=0`) | proposed |
| Config | YAML + env via `github.com/knadh/koanf/v2` | proposed |
| Web client | Vite + TypeScript, Three.js orbs with 2D/list fallback, embedded with `//go:embed` | proposed |
| Release | GoReleaser v2, one binary per OS/arch | fixed by roadmap |

Everything marked "proposed" is confirmed or changed with Nour in Phase 1.

## Folder map (this package)

```
Darb Kinton/
├── README.md            this file
├── CLAUDE.md            agent operating manual (the law)
├── AGENTS.md            short pointer for other agent tools
└── docs/
    ├── VISION.md        why, goals, non-goals, anti-goals
    ├── ARCHITECTURE.md  components, data flow, storage, config, testing
    ├── THREAT_MODEL.md  assets, adversaries, STRIDE, mitigations, residual risk
    ├── UI_DESIGN.md     signature moment, screens, motion, art directions, a11y
    ├── INTEGRATION.md   kinton.portal.opened v1 for Darb Budokai (optional, later)
    ├── PLAN.md          phases 0 to 100% with tasks, tests and skills
    ├── PROGRESS.md      ledger template
    ├── DECISIONS.md     ADR log
    ├── OPEN_QUESTIONS.md questions only Nour can answer (asked in Phase 1)
    └── CONVENTIONS.md   code style, layout, tests, commits, branches, PR template
```

## How to start

Open Claude Code in this folder and say:

> start Phase 0

The agent reads `CLAUDE.md`, then `docs/PLAN.md`, and bootstraps the repo. It asks before creating the GitHub repo or pushing anything.

## How it fits the universe

Darb Kinton is "The Portal" in Darb Budokai, the RPG Nour's real life powers. When a transfer opens, Darb Kinton can emit a cosmetic `kinton.portal.opened` v1 event so Darb Budokai draws a portal ring between device regions on the world map. No file names, sizes or contents ever leave Darb Kinton. The adapter is off by default and Darb Kinton works fully without Darb Budokai. See `docs/INTEGRATION.md`.
