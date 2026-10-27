# Decisions (ADR log)

Short ADRs, newest last. Status: `accepted` (fixed by roadmap or Nour's rules), `proposed` (agent's suggestion, confirm with Nour in Phase 1), `superseded by ADR-NNN`. Each later decision gets a new entry; never edit an accepted one in place.

Format: context, decision, consequences.

---

## ADR-001: Go 1.23+ for the server and CLI
- **Status:** accepted (roadmap)
- **Context:** Darb Kinton's purpose in the portfolio is to prove Go. Go 1.22 added method/path patterns to `net/http`; 1.23 is the roadmap floor.
- **Decision:** `go 1.23` minimum in `go.mod`, with a `toolchain` line pinned in Phase 0 to the current stable release.
- **Consequences:** stdlib routing, `log/slog`, `crypto/ecdh` available without extra deps.

## ADR-002: WebRTC via pion
- **Status:** accepted (roadmap)
- **Decision:** `github.com/pion/webrtc/v4` for the CLI peer and Go tests; browsers use native WebRTC. `pion/transport/v3/vnet` for network tests.
- **Consequences:** Go-to-Go and Go-to-browser transfers share one protocol.

## ADR-003: WebSocket signaling
- **Status:** accepted (roadmap); library `github.com/coder/websocket` proposed
- **Decision:** signaling, presence and relay fallback over WebSockets on the same server.
- **Consequences:** one port for HTTP and signaling; `coder/websocket` is context-aware and maintained (successor of `nhooyr.io/websocket`).

## ADR-004: End-to-end encryption, server sees ciphertext only
- **Status:** accepted (roadmap); construction proposed (ARCHITECTURE.md §4.2, §5), reviewed with `security-review` in Phase 5
- **Decision:** P-256 ECDH with ephemeral keys per transfer, ECDSA P-256 identity keys, HKDF-SHA256, AES-256-GCM per chunk with index-derived nonces and AAD binding.
- **Consequences:** works with WebCrypto in every modern browser and Go stdlib; forward secrecy per transfer; residual risk of server-served JS documented (THREAT_MODEL.md R1).

## ADR-005: Single self-hosted binary, GoReleaser releases
- **Status:** accepted (roadmap)
- **Decision:** one `kinton` binary embeds the web client (`//go:embed`), signaling, TURN, relay and mailbox. GoReleaser v2 builds linux/darwin/windows for amd64/arm64 with `CGO_ENABLED=0`.
- **Consequences:** Node is a build-time dependency only; every dependency must be pure Go (drives ADR-008).

## ADR-006: Browser client needs nothing installed
- **Status:** accepted (roadmap)
- **Decision:** the full experience works in a browser; PWA install is optional. A friend can receive via a share link with no account.
- **Consequences:** browser limits shape the design (OPFS for big files, user gesture for clipboard, reselect after reload).

## ADR-007: Resumable chunked transfers
- **Status:** accepted (roadmap); mechanism proposed (ARCHITECTURE.md §4.3)
- **Decision:** receiver-side bitmap, missing-range negotiation, fresh handshake per resume.
- **Consequences:** no nonce reuse; resume works across network paths.

## ADR-008: SQLite via modernc.org/sqlite
- **Status:** proposed
- **Decision:** pure-Go SQLite for devices, pairings, transfer metadata, mailbox index and Darb Budokai outbox.
- **Consequences:** cross-compiles without CGO; one data file to back up.

## ADR-009: Embedded TURN plus WebSocket relay fallback
- **Status:** proposed
- **Decision:** `pion/turn/v4` inside the binary with HMAC time-limited credentials; encrypted WebSocket relay when UDP is blocked; no public STUN servers by default.
- **Consequences:** works across NATs without third parties; relay bandwidth costs land on Nour's VPS (capped in config).

## ADR-010: Config, not code
- **Status:** accepted (Nour's rule)
- **Decision:** all limits, TTLs, timings, copy and design tokens in `config/` (koanf v2, YAML + `KINTON_*` env), the SQLite `settings` table, or `web/src/tokens/`.
- **Consequences:** reviews reject literals; crypto constants live in a versioned protocol file.

## ADR-011: UI first
- **Status:** accepted (Nour's rule)
- **Decision:** Phase 2 design system and Phase 3 prototype on seed data, approved screen by screen, before backend phases.
- **Consequences:** the transfer state machine is designed in Phase 3 and reused by the real engine.

## ADR-012: Native feel, one SVG icon set, no emoji
- **Status:** accepted (Nour's rule)
- **Decision:** SwiftUI-like mobile patterns, Solar or Lucide icons (picked in Phase 2), Simple Icons for real logos, no emoji anywhere; enforced by the emoji grep in the definition of done.
- **Consequences:** custom sheet, tab bar and list components in the design system.

## ADR-013: No AI attribution, Nour is the only author
- **Status:** accepted (Nour's rule)
- **Decision:** git config as Nour, commit-msg hook, agent settings attribution off, push checks.
- **Consequences:** GoReleaser changelogs are clean because commit subjects are.

## ADR-014: Darb Budokai integration is optional and outbound only
- **Status:** accepted (brief); details proposed (INTEGRATION.md)
- **Decision:** cosmetic `kinton.portal.opened` v1 via an outbox and signed CloudEvents; off by default; Darb Kinton never depends on Darb Budokai.
- **Consequences:** Darb Kinton ships and launches without Darb Budokai.

## ADR-015: Web client stack
- **Status:** proposed (framework decided in Phase 2)
- **Decision:** Vite + TypeScript, Three.js for the orbit scene with a 2D SVG fallback. Framework candidates: vanilla TS + Web Components, Svelte 5, React 19.
- **Consequences:** whichever wins, the transfer engine and crypto stay framework-free modules in `web/src/transfer` and `web/src/crypto`.

## ADR-016: Testing without live services
- **Status:** accepted (Nour's rule)
- **Decision:** vnet for networks, httptest for HTTP, fake ingest for Darb Budokai, two-context Playwright for browsers. CI never contacts public STUN, ACME, Darb Budokai or GitHub APIs beyond checkout.
- **Consequences:** network tests are deterministic and fast.
