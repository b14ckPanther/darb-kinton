# Architecture

Fixed by the roadmap: Go 1.23+, WebRTC (pion), WebSocket signaling, end-to-end encryption, resumable chunked transfers, a single self-hosted binary released with GoReleaser, a browser client that needs nothing installed.

Everything else in this file (libraries, protocol shapes, defaults, the crypto construction) is **proposed, confirm with Nour in Phase 1**. The crypto construction is additionally reviewed with `security-review` in Phase 5 before any code depends on it. Every number below is an example default for `config/kinton.yaml`, never a constant in code.

## 1. Overview

One binary, `kinton`, does four jobs:

1. **Serves the web client** (Vite + TypeScript build, embedded with `//go:embed`).
2. **Signaling and presence** over WebSockets: which of your devices are online, SDP offer/answer and ICE candidates, transfer offers and accepts. It forwards opaque, encrypted envelopes; it never holds content keys.
3. **NAT traversal**: an embedded STUN/TURN server (`pion/turn/v4`) so devices on different networks can still connect, plus an **encrypted WebSocket relay** fallback when UDP is blocked (corporate or campus Wi-Fi).
4. **Mailbox** (optional): holds encrypted chunks for a short TTL so you can send to a device that is offline, or to a friend via a share link.

The same binary is also a **CLI peer** (`kinton send`, `kinton receive`, `kinton pair`) that uses `pion/webrtc/v4` and the same protocol as the browser. This is where most of the Go WebRTC and crypto code lives, and it makes Go-to-Go integration tests possible.

The server only ever sees: device ids, public keys, presence, encrypted envelopes, ciphertext chunks and sizes. It never sees file names, contents, clipboard text, links or keys.

## 2. Diagram

```
  Device A (browser / PWA / kinton CLI)                         Device B (browser / CLI)
  ┌───────────────────────────────┐                          ┌───────────────────────────────┐
  │ UI: orbs (Three.js) + list    │                          │ UI: receive sheet, inbox       │
  │ Keys: IndexedDB (non-extract.) │                          │ Keys: IndexedDB                │
  │ Crypto worker: ECDH/HKDF/GCM  │                          │ Crypto worker + OPFS writer    │
  │ Transfer engine (chunks,      │                          │ Bitmap of received chunks      │
  │   backpressure, resume)       │                          │   (IndexedDB)                  │
  └──────┬──────────────┬─────────┘                          └──────────┬──────────────┬──────┘
         │ WSS signaling│  WebRTC DataChannel (DTLS + E2EE chunks)      │              │
         │ (envelopes)  └───────────────────────────────────────────────┘              │
         │                     direct on LAN, or via TURN if NAT blocks                │
         ▼                                                                              ▼
  ┌───────────────────────────────────────────── kinton serve ─────────────────────────────────────┐
  │ net/http mux (Go 1.22 patterns)                                                               │
  │  GET  /                 embedded web client (CSP, SRI)                                         │
  │  GET  /ws               signaling hub (coder/websocket)  ── presence, offer/answer/ICE relay  │
  │  GET  /relay/{session}  encrypted byte relay when UDP fails (ciphertext only)                 │
  │  POST /api/pair, GET /api/devices, PUT/GET /api/mailbox/{id}/{chunk}, GET /healthz            │
  │ TURN/STUN :3478 udp/tcp (pion/turn, time-limited credentials from TURN shared secret)         │
  │ SQLite (modernc.org/sqlite): devices, pairings, transfers, mailbox index, budokai_outbox        │
  │ Mailbox blob dir: data/mailbox/<id>/<chunk>.bin (ciphertext only, TTL sweeper)                │
  │ Darb Budokai adapter (off by default): outbox -> signed CloudEvents POST                             │
  └───────────────────────────────────────────────────────────────────────────────────────────────┘
```

## 3. Components

| Package (Go) | Responsibility |
|---|---|
| `cmd/kinton` | Entry point. Subcommands `serve`, `send`, `receive`, `pair`, `devices`, `version`. Uses the standard `flag` package per subcommand (proposed; `spf13/cobra` only if subcommands grow). |
| `internal/config` | Loads `config/kinton.yaml` + `KINTON_*` env with `knadh/koanf/v2`, validates, exposes typed structs. Reload on SIGHUP for limits that are safe to change live. |
| `internal/server` | `http.Server`, routes, middleware (request id, `slog` logging, rate limit, CSP/security headers), graceful shutdown with `context`. |
| `internal/signal` | WebSocket hub. One goroutine per connection for reads, one writer goroutine with a bounded send channel; slow clients are dropped, never block the hub. Device auth by challenge signature. |
| `internal/turnsrv` | Embedded `pion/turn/v4` server; issues time-limited TURN credentials (REST-style HMAC username) to authenticated devices only. |
| `internal/relay` | WebSocket byte relay pairing two authenticated endpoints of one transfer session; per-session and global bandwidth caps from config. |
| `internal/mailbox` | Stores ciphertext chunks for offline devices and share links; TTL sweeper; quota per sender. |
| `internal/store` | SQLite access (`database/sql` + `modernc.org/sqlite`), migrations embedded with `//go:embed` and applied on start (`pressly/goose/v3`, proposed). |
| `internal/protocol` | Wire types: signaling messages (JSON), DataChannel frames (binary), manifest, versioned protocol constants. Fuzzed. |
| `internal/crypto` | Identity keys, handshake, HKDF, AES-GCM chunk seal/open, SAS words. Go stdlib `crypto/ecdh`, `crypto/ecdsa`, `crypto/aes`, `crypto/cipher`, `crypto/sha256` and `golang.org/x/crypto/hkdf`. Byte-for-byte test vectors shared with the TypeScript client. |
| `internal/peer` | CLI WebRTC peer on `pion/webrtc/v4`: DataChannel setup, backpressure via `BufferedAmountLowThreshold` + `OnBufferedAmountLow`. |
| `internal/transfer` | Transfer engine shared by CLI peer and tests: chunker, scheduler, fan-out, resume state, progress events on channels. |
| `internal/budokai` | Optional outbound adapter for `kinton.portal.opened` v1 (see `INTEGRATION.md`). |
| `web/` | Vite + TypeScript client. `src/crypto` (WebCrypto in a Web Worker), `src/transfer` (engine mirror of the Go one), `src/storage` (OPFS + IndexedDB), `src/scene` (Three.js orbs), `src/ui` (screens), `src/tokens` (design tokens JSON). Framework chosen in Phase 2 (open question: vanilla TS + Web Components vs Svelte 5 vs React 19). |

## 4. Data flow

### 4.1 Presence and signaling

1. Device opens `wss://host/ws`. Server sends a random challenge; device signs it with its ECDSA P-256 identity key; server checks the signature against the registered public key. Unknown devices get only the pairing endpoints.
2. Hub tracks online devices per owner group and pushes presence changes to the group. The UI turns these into orbs.
3. To send, A posts `offer` (to device B) with an **encrypted, signed envelope** containing the transfer handshake. The hub forwards it; it can't read it.
4. SDP offer/answer and ICE candidates flow through the hub. ICE servers given to clients: the embedded STUN/TURN with short-lived credentials (TTL in config). No public STUN servers by default (proposed; avoids leaking IPs to third parties).

### 4.2 Transfer (one recipient)

1. **Handshake.** A and B each make an ephemeral P-256 key pair. Each signs the transcript (`protocol version, transferId, both ephemeral public keys, both identity key fingerprints`) with its identity key. Each verifies the other's signature against the paired key it already trusts. Shared secret = ECDH(ephemeral A, ephemeral B). Keys = HKDF-SHA256(secret, salt = SHA-256(transcript), info = `kinton/v1/chunk/a->b` and `kinton/v1/chunk/b->a`, plus `kinton/v1/control`). Forward secrecy: ephemeral keys are discarded after the transfer.
2. **Manifest.** A sends the encrypted manifest: kind (`file|text|link`), name, size, MIME, `lastModified`, chunk size, segment size, chunk count. The receiver sees a **receive sheet** and must accept. Nothing is written before accept.
3. **Chunks.** File is read with `File.slice()` (browser) or `os.File.ReadAt` (CLI) one chunk at a time, never fully in memory. Each chunk: AES-256-GCM, nonce = 4 bytes zero || 8-byte big-endian chunk index (unique per key because keys are per transfer and per direction), AAD = `transferId || chunkIndex || chunkCount`. Frame = header (type, index, length) + ciphertext + tag.
4. **Backpressure.** Sender pauses when `bufferedAmount` exceeds the high-water mark and resumes on `bufferedamountlow` (thresholds in config).
5. **Receive.** A Web Worker decrypts and writes each chunk at its offset in an OPFS file using `FileSystemSyncAccessHandle` (works in Chromium, Firefox and Safari 16.4+). It sets the chunk's bit in a bitmap persisted in IndexedDB every N chunks (config).
6. **Integrity.** Every 4 MiB segment (config), the sender includes the segment's SHA-256 with the last chunk of the segment; the receiver hashes what it wrote and compares. The final `complete` message carries the list hash (SHA-256 over all segment hashes); the receiver checks it before showing "Received".
7. **Save.** Chromium: `showSaveFilePicker()` and stream from OPFS. Safari/Firefox: download from the OPFS `File` (disk-backed, no full copy in RAM). Text and links skip storage and appear in the receive sheet with Copy / Open actions.

### 4.3 Resume

- Transfer state survives a dropped connection, a tab reload or a network change. The receiver keeps `transferId`, manifest, bitmap and the OPFS file. Default resume TTL: 7 days (config).
- On reconnect, both sides run a **new handshake** (new ephemeral keys, new chunk key). The receiver sends `resume {transferId, missing ranges}` as run-length encoded ranges. The sender sends only missing chunks. Already-received chunks were verified when they arrived, so a new key is safe and avoids any nonce reuse.
- Sender side: the CLI reopens the path. A browser that still has the tab open keeps the `File`. **Honest limit:** after a browser reload the sender must reselect the file, unless Chromium's File System Access handle was saved in IndexedDB (then one permission click). Reselected files are checked by name, size and `lastModified`, then by recomputing the hash of the first already-sent segment; mismatch aborts with "This isn't the same file".
- Resume also works across paths: a transfer that started direct on Wi-Fi can resume over TURN or the relay after the phone switches to mobile data.

### 4.4 Several devices at once (fan-out)

Dropping a file on several orbs (or on "All my devices") creates one transfer per recipient, each with its own handshake and keys. The sender reads each chunk once and feeds it to every active transfer, with per-recipient backpressure: a slow phone doesn't slow a fast laptop (chunks for the slow one are re-read later from the `File`). Max parallel recipients in config.

### 4.5 Someone far away

- **Paired device on another network:** same flow, the connection goes direct via STUN hole punching if possible, else through the embedded TURN, else through the WebSocket relay. Content is E2EE in all three cases.
- **Friend without Darb Kinton (share link):** the sender creates a random 256-bit key K and a link `https://host/r/<linkId>#k=<base64url(K)>`. The fragment is never sent to the server (browsers don't send fragments). If the sender is still online, the friend's browser connects live (WebRTC/relay) and the handshake binds to K. If not, chunks were uploaded encrypted to the mailbox and the friend downloads them. Link TTL and max downloads in config. Optional passphrase is an open question.
- **Friend sends to you:** a "drop link" works the other way: your device publishes an ephemeral public key in the link fragment, the friend's browser encrypts to it.

### 4.6 Clipboard text and links

Small payloads (under the size in config, e.g. 64 KiB) are a single encrypted message. The receiver sees a sheet with Copy and Open. Browsers require a user gesture to write the clipboard, so "auto-copy" is not possible in the browser; the CLI peer can write the system clipboard (`golang.design/x/clipboard` is proposed but needs CGO on some platforms, so the CLI uses OS tools `pbcopy`/`wl-copy`/`xclip`/`clip.exe` via `os/exec`, proposed).

## 5. Protocol constants (not config)

Versioned in `internal/protocol/v1.go` and `web/src/protocol/v1.ts`, documented here, changed only with an ADR:
- Protocol version `1`. HKDF info labels `kinton/v1/chunk/a->b`, `kinton/v1/chunk/b->a`, `kinton/v1/control`, `kinton/v1/sas`, `kinton/v1/link`.
- Curves and algorithms: P-256 (ECDH and ECDSA), SHA-256, AES-256-GCM (12-byte nonce, 16-byte tag).
- Why P-256 and not X25519: WebCrypto X25519 is not available in every browser Darb Kinton targets (older Safari), while P-256 ECDH/ECDSA works in every modern browser and in Go's stdlib. Revisit in a later ADR.

## 6. Storage

**SQLite** via `modernc.org/sqlite` (pure Go, so `CGO_ENABLED=0` cross-compiles for every GoReleaser target). WAL mode. One file `data/kinton.db`.

| Table | Contents |
|---|---|
| `devices` | id, owner group, display name, kind (phone/laptop/desktop/browser), platform, identity public key, created_at, last_seen_at, revoked_at |
| `pairing_tokens` | token hash, created_by, expires_at, used_at |
| `transfers` | id, from_device, to_device, kind, size_bytes (ciphertext), path (direct/turn/relay/mailbox), state, started_at, finished_at. No file names. |
| `mailbox_items` | id, link_id, chunk_count, bytes, expires_at, max_downloads, downloads |
| `budokai_outbox` | id, event JSON, created_at, sent_at, attempts, last_error |
| `settings` | key, value (runtime-editable server settings from the admin screen) |

Ciphertext mailbox chunks live on disk under `data/mailbox/`, not in SQLite. Retention of `transfers` rows: 30 days (config).

Why SQLite: one binary, one file, no separate database to run for a self-hosted tool. Why not Postgres or Redis: unnecessary operational weight for one household.

Client storage: IndexedDB (keys as non-extractable `CryptoKey`, paired devices, resume state), OPFS (incoming file bodies).

## 7. Config, not code

- `config/kinton.example.yaml` documents every key; `config/kinton.yaml` is local (git-ignored if it contains host-specific values). Env overrides: `KINTON_SERVER_ADDR`, `KINTON_TRANSFER_CHUNK_SIZE`, etc. (koanf maps `KINTON_A_B` to `a.b`).
- Example keys: `server.addr` (`:8443`), `server.public_url`, `tls.mode` (`off|file|autocert`), `turn.listen` (`:3478`), `turn.budokai`, `turn.relay_port_range`, `turn.credential_ttl` (`10m`), `transfer.chunk_size` (`64KiB`, kept at or under the DataChannel `max-message-size` all target browsers accept), `transfer.segment_size` (`4MiB`), `transfer.max_file_size` (`0` = unlimited), `transfer.resume_ttl` (`168h`), `transfer.max_recipients` (`8`), `relay.max_bandwidth_per_session` (`10MiB/s`), `relay.max_sessions`, `mailbox.enabled`, `mailbox.ttl` (`24h`), `mailbox.quota_per_device` (`2GiB`), `share_link.ttl`, `share_link.max_downloads`, `pairing.token_ttl` (`5m`), `ratelimit.*`, `budokai.enabled` (`false`), `budokai.ingest_url`, `ui.copy_file` (`config/copy/en.yaml`).
- Design tokens (colours, type scale, spring constants, arc timings) in `web/src/tokens/*.json`, compiled to CSS custom properties and a TS module at build time.
- Admin screen edits a safe subset (`settings` table) live; restarts are never needed for limits.

## 8. Local development

Prerequisites: Go (version from `go.mod` toolchain line), Node 22 LTS, `golangci-lint` v2, `goreleaser` v2, `mkcert` (for local HTTPS so WebCrypto and the clipboard work on phones on the LAN).

```bash
mkcert -install && mkcert -cert-file dev/cert.pem -key-file dev/key.pem kinton.local localhost 127.0.0.1 <lan-ip>
npm --prefix web ci && npm --prefix web run dev          # Vite :5173, proxies /ws /api /relay to :8443
go run ./cmd/kinton serve --config config/kinton.dev.yaml    # TLS from dev/*.pem, TURN on :3478
go run ./cmd/kinton serve --demo                           # seed devices and history, "Demo data" banner
```

Phones on the LAN open `https://<lan-ip>:8443` after installing the mkcert root CA (iOS: Settings > General > About > Certificate Trust Settings). Proposed alternative: run behind `tailscale serve` for a real certificate (open question).

## 9. Testing strategy

| Layer | Tooling | What it proves |
|---|---|---|
| Unit (Go) | `testing`, table-driven, `go test -race` | config validation, protocol encode/decode, crypto seal/open, bitmap/range math, scheduler |
| Fuzz (Go) | native `go test -fuzz` | `FuzzDecodeFrame`, `FuzzManifest`, `FuzzSignalMessage`, `FuzzRanges` never panic and reject malformed input |
| Crypto vectors | shared JSON in `testdata/vectors/*.json` | Go and TypeScript produce identical keys, nonces, ciphertexts and SAS words for the same inputs |
| Integration (Go) | `httptest.Server`, two `internal/peer` peers over `pion/transport/v3/vnet` | signaling, NAT traversal via embedded TURN, packet loss, a mid-transfer link drop and resume, fan-out to 3 peers |
| Benchmarks | `go test -bench`, `pprof` | chunk seal/open throughput, scheduler allocations, relay copy path |
| Web unit | Vitest (+ `fake-indexeddb`) | TS crypto against vectors, chunker, resume state machine, token compile |
| E2E | Playwright with two browser contexts (chromium and webkit; firefox where OPFS sync handle allows), `@axe-core/playwright` | pair, send file/text/link, accept/decline, reload mid-transfer and resume, reduced-motion, keyboard-only send, zero serious axe violations |
| Visual | Playwright screenshots + `threejs-visual-validation` | orb scene renders, fallback 2D view renders without WebGL |
| Release | `goreleaser check`, `goreleaser release --snapshot --clean` in CI | every target builds with `CGO_ENABLED=0`, binary runs `kinton version` |

CI (GitHub Actions, proposed): `go vet`, `golangci-lint`, `go test -race`, 60 s fuzz smoke per target on PRs, `govulncheck`, web lint/test/build, Playwright E2E, GoReleaser snapshot, emoji grep, attribution grep. No job contacts a live third-party service.

## 10. Observability

`log/slog` JSON logs with request id, device id and transfer id only. `/healthz` and `/readyz`. Optional `/metrics` in Prometheus text format (proposed: `prometheus/client_golang`, off by default) with `kinton_transfers_total{path,result}`, `kinton_relay_bytes_total`, `kinton_ws_connections`. `net/http/pprof` mounted only when `debug.pprof: true` and bound to localhost.

## 11. Repository layout (created in Phase 0)

```
darb-kinton/
├── go.mod, go.sum                 module github.com/b14ckPanther/darb-kinton, go 1.23 + toolchain line
├── cmd/kinton/                      main.go, subcommands
├── internal/{config,server,signal,turnsrv,relay,mailbox,store,protocol,crypto,peer,transfer,budokai}/
├── web/                           Vite + TS client; dist/ embedded by internal/server/webassets.go
├── config/                        kinton.example.yaml, copy/en.yaml, seed/demo/*.yaml
├── testdata/vectors/              shared crypto test vectors
├── contracts/events/kinton.portal.opened/v1.schema.json (+ examples/)
├── tools/genkeys/                 local secret generation
├── dev/                           mkcert output (git-ignored)
├── .goreleaser.yaml, .golangci.yml, Makefile, Dockerfile (distroless static)
├── .github/workflows/ci.yml
├── .githooks/commit-msg
├── .env.example, ASSETS.md
└── docs/
```

## 12. Release

GoReleaser v2 (`.goreleaser.yaml`, `version: 2`):
- `before.hooks`: `npm --prefix web ci`, `npm --prefix web run build`, `go mod tidy`.
- `builds`: `CGO_ENABLED=0`, `goos: [linux, darwin, windows]`, `goarch: [amd64, arm64]`, `-trimpath`, `ldflags: -s -w -X main.version={{.Version}} -X main.commit={{.Commit}}`.
- `archives`, `checksum` (SHA-256), `sboms` (syft), optional `signs` with cosign keyless (proposed), `dockers`/`docker_manifests` to `ghcr.io/b14ckpanther/darb-kinton` (distroless static base).
- `changelog`: from commit subjects (clean by rule 1.1).
- Releases are triggered by pushing a `v*` tag, which needs Nour's "yes".
