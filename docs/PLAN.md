# Master plan: 0 to 100%

Fifteen phases. Each is a shippable increment on its own branch, merged into `main` only with Nour's "yes". Weights add up to 100 and are proposed, confirm with Nour in Phase 1.

| # | Phase | Weight | Cumulative | Branch |
|---|---|---|---|---|
| 0 | Repo bootstrap, CI, conventions | 4 | 4 | `phase/00-bootstrap` |
| 1 | Confirm the spec with Nour | 2 | 6 | `phase/01-spec` |
| 2 | Design system | 8 | 14 | `phase/02-design-system` |
| 3 | Clickable prototype on seed data | 10 | 24 | `phase/03-prototype` |
| 4 | Server skeleton, signaling and presence | 7 | 31 | `phase/04-signaling` |
| 5 | Pairing and end-to-end crypto | 10 | 41 | `phase/05-pairing-crypto` |
| 6 | WebRTC transfer engine | 12 | 53 | `phase/06-transfer-engine` |
| 7 | Resumable transfers | 8 | 61 | `phase/07-resume` |
| 8 | Several devices and far away (TURN, relay, share links, mailbox) | 10 | 71 | `phase/08-fanout-far` |
| 9 | Clipboard, links, PWA and share target | 5 | 76 | `phase/09-clipboard-pwa` |
| 10 | Settings, server admin and CLI surface | 4 | 80 | `phase/10-admin-cli` |
| 11 | Hardening: security, fuzzing, performance | 8 | 88 | `phase/11-hardening` |
| 12 | Release pipeline (GoReleaser) | 4 | 92 | `phase/12-release` |
| 13 | Darb Budokai integration (optional) | 3 | 95 | `phase/13-budokai` |
| 14 | Docs, demo GIF, README and public launch | 5 | 100 | `phase/14-launch` |

Every phase follows the loop in `CLAUDE.md` §2 (brainstorm, spec, plan, TDD execution with ledger, whole-branch review, finish) and the definitions of done in `CLAUDE.md` §6-7. Tasks below are the starting list; the phase plan in `docs/plans/` breaks them into bite-sized steps. "Test:" lines name the failing test written first.

---

## Phase 0: Repo bootstrap, CI, conventions (4%)

**Goal:** an empty but real repo where every rule is enforced by tooling before any feature exists.

**Deliverables:** git repo with Nour as author, Go module, Vite + TS web skeleton embedded in the binary, `kinton version` works, CI green, hooks and agent settings in place, ledger started.

**Tasks (TDD order):**
1. `git init`, `git config user.name "Nour Alden Mousa"`, `git config user.email "nmcryptoinvest@gmail.com"`, `git config core.hooksPath .githooks`. Copy this planning package into the repo (`docs/`, `CLAUDE.md`, `AGENTS.md`, `README.md`).
2. `.githooks/commit-msg` that rejects `co-authored|claude|anthropic|generated with` (case-insensitive). Test: a shell test script `tools/hooks_test.sh` feeds a bad and a good message and asserts exit codes.
3. `.claude/settings.json` with `"attribution": {"commit": "", "pr": ""}` and `"includeCoAuthoredBy": false`.
4. `go mod init github.com/b14ckPanther/darb-kinton`; `go 1.23` directive plus `toolchain` line pinned to the current stable Go (check `go env GOVERSION` / go.dev/dl). `.gitignore`, `.editorconfig`, `.env.example`.
5. Test: `cmd/kinton/main_test.go` expects `kinton version` to print version and commit injected by ldflags. Implement with `flag` subcommands.
6. `internal/config`: test that defaults load from `config/kinton.example.yaml`, env `KINTON_SERVER_ADDR` overrides, and an invalid value (negative chunk size) fails validation with a clear error. Implement with koanf v2.
7. Web skeleton: `npm create vite@latest web -- --template vanilla-ts` (framework replaced in Phase 2 if Nour picks one), Vitest set up with one passing test, ESLint + Prettier.
8. `internal/server/webassets.go` with `//go:embed all:dist` (copied from `web/dist` by the build); test that `GET /` returns the embedded `index.html` with CSP header.
9. `.golangci.yml` (v2 format) enabling `govet`, `staticcheck`, `errcheck`, `gosec`, `revive`, `gocritic`, `misspell`; `Makefile` targets from `CLAUDE.md` §5.
10. `.github/workflows/ci.yml`: Go (vet, lint, `test -race`, govulncheck), web (lint, test, build), attribution grep on PR commits, emoji grep, `goreleaser check`. Uses `actions/setup-go` with `go-version-file: go.mod`.
11. `docs/PROGRESS.md` ledger first rows; README status "Phase 0 done".

**Tests that prove it:** `go test -race ./...` and `npm --prefix web test` green; hook test passes; CI green on the branch (once Nour approves creating the remote).

**Definition of done:** CLAUDE.md §7, plus: `git log` shows only Nour; `.claude/settings.json` present; `kinton version` runs from a clean checkout build.

**Skills:** `superpowers:brainstorming`, `superpowers:writing-plans`, `superpowers:executing-plans`, `superpowers:test-driven-development`, `superpowers:verification-before-completion`, `superpowers:requesting-code-review`, `superpowers:finishing-a-development-branch`, `code-review`, `run`.

---

## Phase 1: Confirm the spec with Nour (2%)

**Goal:** turn every "proposed" item into a decision.

**Deliverables:** answers to `docs/OPEN_QUESTIONS.md` recorded in `docs/DECISIONS.md` (one ADR per decision that changes design), updated `VISION.md`, `ARCHITECTURE.md`, `THREAT_MODEL.md`, `UI_DESIGN.md` and phase weights, and `docs/specs/YYYY-MM-DD-phase-01-spec.md` approved by Nour.

**Tasks:**
1. Ask the questions in `docs/OPEN_QUESTIONS.md` one at a time, open-ended ones first. Don't batch.
2. After each answer, update the affected doc and log an ADR.
3. Walk Nour through `THREAT_MODEL.md` residual risks; record which are accepted.
4. Write the Phase 1 spec summarising final scope, platforms, hosting, art-direction shortlist and phase weights. Ask for approval.

**Tests that prove it:** none (docs). Every "proposed, confirm with Nour in Phase 1" label is either removed or moved to an explicit later decision with a reason.

**Definition of done:** spec approved; `grep -rn "proposed, confirm with Nour in Phase 1" docs/` only shows items Nour deferred on purpose.

**Skills:** `superpowers:brainstorming`, `superpowers:writing-plans`, `writing-guidelines`, `superpowers:verification-before-completion`.

---

## Phase 2: Design system (8%)

**Goal:** Nour picks an art direction side by side, and the design system exists as tokens and live components.

**Deliverables:** three live comps (Observatory glass, Signal paper, Deep-water lanterns) of the Orbit screen and the Receive sheet at 390 x 844 and 1440 x 900; the chosen direction's tokens (`web/src/tokens/*.json`: colour light/dark, type scale, spacing, radii, materials, springs, durations); component gallery page (`/_gallery`, dev only): nav bar with large collapsing title, bottom tab bar, sheet with detents, inset grouped list with swipe actions, buttons with pressed scale, orb (2D SVG version), thread/progress, SAS word box, toasts; icon set chosen and wired; fonts self-hosted from Google Fonts with licences in `ASSETS.md`; framework decision (vanilla TS + Web Components, Svelte 5 or React 19) recorded as an ADR.

**Tasks (TDD order where code):**
1. Brainstorm with Nour using `UI_DESIGN.md` §6; gather references; run `audit-reference-originality` on any reference used.
2. Build the three comps (static scene + one arc animation each) and present them side by side. Record the pick.
3. Test: token compiler produces CSS custom properties and a typed TS module from JSON; fails on a missing dark-mode value or a colour pair below contrast threshold (contrast pairs listed in tokens). Implement.
4. Test (Vitest + Playwright component screenshots): each component renders in light/dark, has a visible focus ring, meets 44 pt targets, and has a reduced-motion variant. Implement components one by one.
5. Spring utility (`web/src/motion/spring.ts`): test that it settles to target within tolerance for token parameters and never uses linear easing; implement.
6. Icon pipeline: Iconify icons (Solar or Lucide) compiled to inline SVG at build time (`@iconify/utils` or `unplugin-icons`, proposed); OS logos from Simple Icons. Test: build fails if an icon name is missing.
7. UX copy pass for all components with `design:ux-copy`; copy lives in `config/copy/en.yaml`.
8. Accessibility review of the gallery with `design:accessibility-review` and axe.
9. Nour approves the design system; record in ledger.

**Tests that prove it:** token contrast test; component tests; axe zero serious/critical on `/_gallery`; emoji grep clean.

**Definition of done:** CLAUDE.md §7; Nour's approval of direction and components recorded; `ASSETS.md` lists fonts and icon set licences.

**Skills:** `frontend-design`, `impeccable:impeccable`, `design-taste-frontend`, `build-awwwards-quality-sites`, `design-first-ui-prompting`, `design:design-system`, `design:design-critique`, `design:accessibility-review`, `design:ux-copy`, `audit-reference-originality`, `writing-guidelines`, `web-design-guidelines`, `solar-duotone-bold`, `company-logos`, `animation-systems`, `threejs-choose-skills`, `threejs-web-design`, `threejs-procedural-materials`, `tailwindcss` (only if chosen), `superpowers:test-driven-development`, `superpowers:verification-before-completion`, `superpowers:requesting-code-review`.

---

## Phase 3: Clickable prototype on seed data (10%)

**Goal:** every screen in `UI_DESIGN.md` §4 works in the browser on realistic seed data, with the real orbit scene and motion, before any backend exists. Nour approves screen by screen.

**Deliverables:** `web` app with S1-S15 against a **mock transport** (`web/src/transport/mock.ts`) that plays seed scenarios from `config/seed/demo/*.yaml` (devices, an in-progress 4.2 GB transfer, a paused one, a far-away device via TURN, an inbox history, a share link); the Three.js orbit scene with arcs, threads, pause dashes and arrival pulse; the 2D SVG fallback and List view twin; PWA manifest; "Demo data" banner.

**Tasks (TDD order):**
1. Test: seed loader parses the demo YAML into typed view models and rejects unknown fields. Implement.
2. Test: transfer view-model state machine (offered, accepted, sending, paused, resuming, verifying, done, failed, declined) with table-driven transitions. Implement. (The same machine is reused for real transfers later.)
3. Orbit scene: `threejs-choose-skills` first. Orbs (lit spheres per the chosen direction), layout on an arc, breathing, hover/drag lean, drop hit-testing in screen space. Test: hit-testing pure function for drop target selection (Vitest). Implement.
4. Arc flight and thread: Bezier path utility tested for apex and length; bead + trail with `threejs-particles-trails-and-effects`; subtle bloom with `threejs-bloom` only if the direction calls for it.
5. Fallbacks: test that with WebGL unavailable the SVG scene mounts; test reduced-motion path renders a straight progress line. Implement with `threejs-compatibility-fallbacks`.
6. Screens S1-S15 in order, each with a Playwright test of its main flow (keyboard only and pointer) and an axe check, built against the mock transport.
7. Native-feel pass on WebKit at 390 x 844: safe areas, collapsing titles, tab bar, sheet detents and drag-to-dismiss, swipe actions, pressed scale.
8. Performance pass: 60 fps target on the orbit scene (Chrome performance panel, `performance-profiling`), render-on-demand when idle, DPR cap.
9. Visual validation of the scene with `threejs-visual-validation`; screenshots to Nour per screen; record each approval.

**Tests that prove it:** Vitest suite; Playwright E2E per screen on chromium and webkit; axe zero serious/critical; screenshot tests for orbit, fallback and reduced-motion.

**Definition of done:** CLAUDE.md §7; every screen approved by Nour in the ledger; no backend calls anywhere (mock transport only).

**Skills:** `frontend-design`, `impeccable:impeccable`, `design-taste-frontend`, `build-awwwards-quality-sites`, `ui-implementer`, `web-design-guidelines`, `design:design-critique`, `design:accessibility-review`, `design:ux-copy`, `design:design-handoff`, `solar-duotone-bold`, `company-logos`, `animation-systems`, `gsap`, `optimize-web-animations`, `threejs-choose-skills`, `threejs`, `threejs-web-design`, `3dviz-pro-max`, `threejs-bloom`, `threejs-particles-trails-and-effects`, `threejs-procedural-materials`, `threejs-camera-controls-and-rigs`, `threejs-exposure-color-grading`, `add-mouse-driven-orbit`, `threejs-compatibility-fallbacks`, `threejs-debugging`, `threejs-visual-validation`, `optimize-threejs-games`, `playwright-cli`, `performance-profiling`, `procedural-sfx` (optional sounds), `superpowers:test-driven-development`, `superpowers:requesting-code-review`, `run`.

---

## Phase 4: Server skeleton, signaling and presence (7%)

**Goal:** a real `kinton serve` with WebSocket signaling and live presence; the prototype's Orbit shows real devices (still unpaired demo identities until Phase 5).

**Deliverables:** `internal/server`, `internal/signal`, `internal/store` (SQLite + migrations), `/healthz`, `/readyz`, structured logs, rate limits, graceful shutdown; web `transport/ws.ts` replacing the mock for presence.

**Tasks (TDD order):**
1. Test: store migrations apply to an empty temp DB and are idempotent. Implement with `modernc.org/sqlite` + goose.
2. Test: signaling message codec round-trips every message type and rejects unknown types and oversize frames (table-driven). Implement `internal/protocol/signal.go`. Add `FuzzSignalMessage`.
3. Test: hub registers/unregisters connections and broadcasts presence to the owner group only. Implement hub with one writer goroutine per client and a bounded channel.
4. Test: a slow client whose send buffer is full is disconnected without blocking other clients (`-race`).
5. Test (httptest + `coder/websocket` client): two clients connect, see each other online, one disconnects, the other gets offline within the configured timeout. Implement ping/pong keepalive.
6. Test: server shuts down cleanly on context cancel, closing sockets with a close code. Implement.
7. Test: security headers (CSP, `Referrer-Policy`, `nosniff`) on every route. Implement middleware.
8. Test: rate limit on `/ws` upgrades per IP (`golang.org/x/time/rate`, limits from config). Implement.
9. Web: `transport/ws.ts` with reconnect + exponential backoff (values from config served at `/api/config`); Vitest against a fake socket; Orbit uses live presence.

**Tests that prove it:** Go tests above with `-race`; Playwright: two browser contexts see each other appear and disappear.

**Definition of done:** CLAUDE.md §7; `THREAT_MODEL.md` updated for the hub.

**Skills:** `superpowers:test-driven-development`, `superpowers:systematic-debugging`, `superpowers:subagent-driven-development`, `superpowers:verification-before-completion`, `superpowers:requesting-code-review`, `code-review`, `security-review`, `playwright-cli`, `run`.

---

## Phase 5: Pairing and end-to-end crypto (10%)

**Goal:** devices get real identities, pair by QR or code with SAS verification, authenticate to the hub, and can run the transfer handshake. Go and TypeScript crypto agree byte for byte.

**Deliverables:** `internal/crypto`, `web/src/crypto` (in a Web Worker), shared vectors in `testdata/vectors/`, pairing endpoints and screens S2/S3 wired, Devices screen with revoke, hub challenge-response auth, ADR for the final construction after `security-review`.

**Tasks (TDD order):**
1. Review `ARCHITECTURE.md` §4.2 and §5 with `security-review` before writing code; record the final construction as an ADR. Stop and ask Nour if the review changes the wire format.
2. Test: HKDF derivation with fixed inputs matches the vector file (Go). Implement. Same test in TS against WebCrypto `deriveBits`/`HKDF`.
3. Test: chunk seal/open with fixed key, index and AAD matches vectors; open fails on wrong index, wrong transferId, flipped bit. Implement Go and TS.
4. Test: nonce construction is unique for indices 0..2^32 sample and across directions. Implement.
5. Test: handshake transcript signing/verification (ECDSA P-256; Go `crypto/ecdsa` with ASN.1 vs WebCrypto raw r||s: convert and test both ways). Implement.
6. Test: SAS words derived from both public keys match across Go and TS; wordlist in `config/sas-words/en.txt` (original list or a properly licensed one recorded in `ASSETS.md`). Implement.
7. Test: pairing token create/consume is single-use and expires (config TTL); stored as SHA-256 hash. Implement `/api/pair`.
8. Test: QR path rejects a key that doesn't match the fingerprint in the fragment; code path requires SAS confirm from both sides. Implement web flow S2/S3.
9. Test: hub rejects connections whose challenge signature fails or whose device is revoked. Implement.
10. Web: keys created as non-extractable `CryptoKey`, stored in IndexedDB; `navigator.storage.persist()` requested; Devices screen with revoke.

**Tests that prove it:** shared vectors pass in Go and TS; `TestPairRejectsSwappedKey`, `TestSASDiffersWhenKeySwapped`, `TestHubRejectsBadSignature`, `TestRevokedDeviceCannotConnect`; Playwright pairing between chromium and webkit contexts via QR URL and via code.

**Definition of done:** CLAUDE.md §7; `security-review` findings fixed; `THREAT_MODEL.md` updated.

**Skills:** `security-review`, `superpowers:test-driven-development`, `superpowers:systematic-debugging`, `superpowers:verification-before-completion`, `superpowers:requesting-code-review`, `superpowers:receiving-code-review`, `code-review`, `design:ux-copy` (pairing and SAS copy), `playwright-cli`.

---

## Phase 6: WebRTC transfer engine (12%)

**Goal:** a real encrypted file, text or link moves from one device to another over a WebRTC DataChannel, browser to browser, CLI to browser and CLI to CLI, with backpressure and verification. The arc in the UI is driven by real progress.

**Deliverables:** `internal/protocol` frames and manifest, `internal/transfer`, `internal/peer` (pion/webrtc v4), web `transfer/` engine with OPFS writer worker, `kinton send` / `kinton receive` CLI, accept/decline flow, Inbox populated from real history.

**Tasks (TDD order):**
1. Test: frame encode/decode (header + ciphertext) round-trips and rejects truncated or oversize frames. Implement; add `FuzzDecodeFrame` and `FuzzManifest`.
2. Test: chunker yields correct offsets/lengths for sizes 0, 1, chunk-1, chunk, chunk+1 and a 10 GB virtual file (table-driven, no real file). Implement.
3. Test: segment hash and list hash computed incrementally equal a one-shot SHA-256 reference. Implement.
4. Test: sender scheduler respects backpressure (fake channel with `BufferedAmount` and low-threshold callback). Implement.
5. Test (Go, vnet): two `internal/peer` peers on a virtual LAN transfer 64 MiB of random data; receiver output hash equals input. Implement peer with `pion/webrtc/v4` `SettingEngine.SetNet(vnet)`.
6. Test: receiver waits for accept and writes nothing before it; decline closes cleanly on both sides.
7. Web: OPFS writer worker with `createSyncAccessHandle`; Vitest with a fake handle; save via `showSaveFilePicker` or download fallback.
8. Web: wire the transfer state machine from Phase 3 to the real engine; arc and thread fed by real progress events.
9. CLI: `kinton send <path> --to <device>` and `kinton receive --dir <dir>` with designed progress output (S14). Test output formatting with golden files and `NO_COLOR`.
10. Benchmark: `BenchmarkSealChunk`, `BenchmarkTransferLoopback`; record numbers in the ledger.

**Tests that prove it:** vnet integration test; Playwright: chromium sends a 200 MB generated file to webkit, hash matches; CLI-to-browser test using a headless browser context; benchmarks recorded.

**Definition of done:** CLAUDE.md §7; a 2 GB file moves phone-to-laptop on Nour's LAN (manual check recorded); `THREAT_MODEL.md` updated.

**Skills:** `superpowers:test-driven-development`, `superpowers:subagent-driven-development`, `superpowers:systematic-debugging`, `superpowers:verification-before-completion`, `superpowers:requesting-code-review`, `code-review`, `security-review`, `performance-profiling`, `playwright-cli`, `threejs-debugging`, `optimize-web-animations`, `run`.

---

## Phase 7: Resumable transfers (8%)

**Goal:** an interrupted transfer (network drop, tab reload, network switch, laptop sleep) resumes from where it stopped, verified.

**Deliverables:** persisted bitmap and resume state (IndexedDB, CLI state file), missing-range negotiation, re-handshake on resume, "Paused at N%" UI, sender file reselect flow with identity check, resume TTL cleanup.

**Tasks (TDD order):**
1. Test: bitmap set/get/persist and missing-range run-length encoding for edge cases (none missing, all missing, alternating, last chunk only). Implement Go and TS; add `FuzzRanges`.
2. Test: resume message codec. Implement.
3. Test (vnet): cut the virtual link at random points in 50 runs; after reconnect the transfer completes and the hash matches; no chunk is sent twice under the same key (`TestNoncesUniqueAcrossResume`).
4. Test: reselected file with different size, `lastModified` or first-segment hash is rejected (`TestResumeRejectsChangedFile`).
5. Test: resume state older than `transfer.resume_ttl` is cleaned up on both sides.
6. Web: persist File System Access handle in IndexedDB on Chromium; reselect sheet elsewhere; Vitest for the decision logic.
7. UI: paused thread (dashed, labelled), resuming animation; reduced-motion version.
8. Playwright: start a 500 MB transfer, reload the receiver tab at about 50%, transfer resumes and completes with matching hash; same with the sender tab (reselect flow).

**Tests that prove it:** the tests above; manual check recorded: phone switches Wi-Fi to mobile data mid-transfer and resumes (after Phase 8 adds TURN, re-run).

**Definition of done:** CLAUDE.md §7.

**Skills:** `superpowers:test-driven-development`, `superpowers:systematic-debugging`, `superpowers:verification-before-completion`, `superpowers:requesting-code-review`, `code-review`, `security-review`, `animation-systems`, `playwright-cli`, `run`.

---

## Phase 8: Several devices and far away (10%)

**Goal:** send to several devices at once; send to a paired device on another network; send to a friend with a share link; receive from a friend with a drop link; deliver to offline devices through the mailbox.

**Deliverables:** fan-out scheduler; embedded `pion/turn/v4` with time-limited credentials and private-address deny; WebSocket relay fallback; mailbox with TTL sweeper and quotas; share link and drop link flows (S9, S10); path labels on threads.

**Tasks (TDD order):**
1. Test: fan-out reads each chunk once for fast peers and per-recipient backpressure lets a slow peer lag without slowing others (fake peers). Implement.
2. Test: TURN credentials are HMAC time-limited and only issued to authenticated devices (`TestTURNDeniesUnauthenticated`). Implement `internal/turnsrv`.
3. Test: TURN refuses permissions to private, loopback and link-local peer addresses (`TestTURNDeniesPrivatePeerAddress`). Implement permission handler.
4. Test (vnet): two peers behind symmetric NATs connect through the embedded TURN and transfer correctly.
5. Test: relay pairs only the two endpoints of a signed offer, enforces bandwidth caps (`TestRelayCapsBandwidth`), carries only ciphertext (test asserts no plaintext marker crosses).
6. Test: client falls back direct, then TURN, then relay within configured timeouts (fake ICE outcomes). Implement.
7. Test: mailbox stores and serves ciphertext chunks, enforces quota and TTL, sweeper deletes expired items (`TestMailboxQuota`). Implement.
8. Test: share link key derivation from the fragment key; server never receives the fragment (`TestServerNeverReceivesFragment` inspects request lines and logs). Implement S9/S10.
9. Drop link: friend encrypts to an ephemeral public key from the fragment. Implement and Playwright-test with a fresh context that has no Darb Kinton state.
10. UI: far-away orbs beyond the horizon, path labels, "All devices" ring.

**Tests that prove it:** the tests above; Playwright: send to 3 contexts at once; share link opened in a clean context; manual check recorded: phone on mobile data receives from home laptop via the self-hosted server.

**Definition of done:** CLAUDE.md §7; `THREAT_MODEL.md` updated for TURN, relay, mailbox and links; `security-review` run on the phase diff.

**Skills:** `security-review`, `superpowers:test-driven-development`, `superpowers:subagent-driven-development`, `superpowers:systematic-debugging`, `superpowers:verification-before-completion`, `superpowers:requesting-code-review`, `code-review`, `design:ux-copy`, `threejs`, `threejs-particles-trails-and-effects`, `animation-systems`, `playwright-cli`, `run`.

---

## Phase 9: Clipboard, links, PWA and share target (5%)

**Goal:** the daily small things: send clipboard text and links in two taps, install Darb Kinton on the phone home screen, share into Darb Kinton from other apps.

**Deliverables:** Compose Text/Link tabs wired, paste shortcut on Orbit, receive sheet Copy/Open, PWA install (manifest, service worker for the app shell only, never caching payloads), Web Share Target (Android/Chromium), notifications for incoming items when the PWA is open in the background (where supported), CLI clipboard send/receive.

**Tasks (TDD order):**
1. Test: link validation allows only `http`/`https` and shows the domain; `javascript:` and `data:` are refused (Playwright XSS test). Implement.
2. Test: small-payload path sends text/link as one sealed message under the size in config. Implement.
3. Test: service worker caches only hashed app-shell assets and never intercepts `/relay`, `/api/mailbox`, `/ws`. Implement with Workbox (proposed) or a hand-written SW.
4. Test: share target POST hands files and text to Compose. Implement.
5. CLI: `kinton send --clipboard` and `kinton receive --to-clipboard` via OS tools; golden output tests; exec mocked.
6. Native-feel and accessibility re-check of the new sheets; Nour approves.

**Tests that prove it:** tests above; Playwright for paste, Copy, Open; manual install on iOS and Android recorded.

**Definition of done:** CLAUDE.md §7.

**Skills:** `superpowers:test-driven-development`, `superpowers:verification-before-completion`, `superpowers:requesting-code-review`, `code-review`, `security-review`, `design:ux-copy`, `design:accessibility-review`, `ui-implementer`, `playwright-cli`, `run`.

---

## Phase 10: Settings, server admin and CLI surface (4%)

**Goal:** owners can see and tune their server without editing files, and the CLI is pleasant to use.

**Deliverables:** S12 Settings and S13 Server admin wired (usage charts, editable limits subset, Darb Budokai adapter status placeholder), admin auth (admin token from env exchanged for a session cookie, proposed), `kinton devices`, `kinton pair` CLI, `--help` texts written with `design:ux-copy`.

**Tasks (TDD order):**
1. Test: settings API validates and persists only the allowlisted keys; values take effect without restart. Implement.
2. Test: admin endpoints reject non-owner devices and missing/invalid admin session. Implement.
3. Test: usage aggregation queries (transfers per path, relay bytes, mailbox disk) over seeded rows. Implement.
4. Admin charts following `dataviz` rules; Playwright + axe.
5. CLI golden tests for `devices`, `pair` (QR rendered in terminal with `github.com/mdp/qrterminal/v3`, proposed) and `--help`.

**Tests that prove it:** tests above; Nour approves S12, S13 and the CLI output.

**Definition of done:** CLAUDE.md §7.

**Skills:** `dataviz`, `design:ux-copy`, `design:design-critique`, `ui-implementer`, `superpowers:test-driven-development`, `superpowers:requesting-code-review`, `code-review`, `security-review`, `playwright-cli`, `run`.

---

## Phase 11: Hardening: security, fuzzing, performance (8%)

**Goal:** Darb Kinton is safe to expose on the internet and fast enough to beat "message yourself".

**Deliverables:** completed `THREAT_MODEL.md` §6 checklist; fuzz corpora in `testdata/fuzz/`; performance report in `docs/PERFORMANCE.md` with LAN and TURN throughput, CPU and memory profiles; fixes for anything found.

**Tasks:**
1. Run every fuzz target for 10 minutes; fix crashes with a regression test first.
2. `security-review` over the whole repo; fix or record accepted risks in `THREAT_MODEL.md`.
3. Header, CSP and Trusted Types tests; log-field allowlist test (`TestLogsContainNoPayloadFields`).
4. `govulncheck`, `npm audit --omit=dev`; pin and update dependencies.
5. Profile sender and receiver with `pprof` (CLI) and Chrome performance panel (browser); remove allocations in the chunk loop (`BenchmarkSealChunk` allocs/op target 0, proposed); tune chunk size and buffer thresholds via config, not code.
6. Measure throughput on real hardware (laptop-laptop wired, phone-laptop Wi-Fi, via TURN) and record honestly.
7. Soak test: 24 h server run with a synthetic client generating transfers in vnet; no goroutine or memory growth (`runtime.NumGoroutine`, heap profile diff).
8. Re-run full accessibility pass (VoiceOver, TalkBack, axe) and native-feel check.

**Tests that prove it:** all §6 checklist items ticked; soak test passes; benchmarks recorded in the ledger.

**Definition of done:** CLAUDE.md §7.

**Skills:** `security-review`, `performance-profiling`, `optimize-threejs-games`, `optimize-web-animations`, `design:accessibility-review`, `superpowers:systematic-debugging`, `superpowers:test-driven-development`, `superpowers:verification-before-completion`, `superpowers:requesting-code-review`, `code-review`, `simplify`.

---

## Phase 12: Release pipeline (GoReleaser) (4%)

**Goal:** one command (after Nour's yes) produces signed, checksummed binaries for every platform and a container image.

**Deliverables:** `.goreleaser.yaml` (v2) per `ARCHITECTURE.md` §12, `Dockerfile` on `gcr.io/distroless/static-debian12`, release workflow on `v*` tags, install instructions, `kinton version --assets` printing embedded asset hashes.

**Tasks:**
1. Test: `kinton version --assets` output matches hashes computed from `web/dist` at build time. Implement.
2. `goreleaser check` and `goreleaser release --snapshot --clean` in CI; test the snapshot binary for linux/amd64 runs `kinton version` in CI.
3. SBOM via syft, optional cosign keyless signing (Nour decides), GHCR image with multi-arch manifest.
4. Write install docs: binary, Docker, systemd unit example, reverse proxy examples (Caddy), TLS options.
5. Ask Nour before the first real tag and release.

**Tests that prove it:** snapshot release green in CI on all targets; container runs `kinton serve --demo` and answers `/healthz`.

**Definition of done:** CLAUDE.md §7; first release published only after Nour's explicit yes.

**Skills:** `superpowers:test-driven-development`, `superpowers:verification-before-completion`, `superpowers:requesting-code-review`, `code-review`, `security-review`, `run`.

---

## Phase 13: Darb Budokai integration (optional) (3%)

**Goal:** Darb Budokai shows a portal when a transfer opens, without Darb Kinton depending on Darb Budokai.

**Deliverables:** as in `INTEGRATION.md` §4.

**Tasks (TDD order):** follow `INTEGRATION.md` §4 steps 1-6. First failing tests: schema validation of examples; `TestPortalEventHasNoPayloadFields`; outbox row written in the accept transaction; HMAC signature matches Darb Budokai's algorithm against the fake ingest; retries and rejection handling.

**Tests that prove it:** contract tests and fake-ingest tests green; optional manual end-to-end with local Darb Budokai recorded.

**Definition of done:** CLAUDE.md §7; adapter off by default; Darb Kinton's full test suite passes with Darb Budokai absent.

**Skills:** `superpowers:test-driven-development`, `superpowers:verification-before-completion`, `superpowers:requesting-code-review`, `code-review`, `security-review`.

---

## Phase 14: Docs, demo GIF, README and public launch (5%)

**Goal:** a public repo that makes a recruiter want to try it, launched only with Nour's yes.

**Deliverables:** README with hero GIF of the signature moment (two devices, arc, pause, resume), honest numbers from `PERFORMANCE.md`, threat model summary and residual risks, install, architecture diagram, an "AI workflow" section describing how Nour used agent tooling and reviewed its output (no attribution lines anywhere); `docs/` cleaned; demo server (optional, paid VPS, ask first); Darb Kaioken write-up outline.

**Tasks:**
1. Record the demo GIF (screen capture of two windows plus a phone) at high quality; keep it under 8 MB.
2. Rewrite README with `writing-guidelines`; run `audit-reference-originality` on visuals.
3. Final whole-repo review with `code-review` and `security-review`.
4. Push checklist (`CLAUDE.md` §8). Ask Nour before creating/publicising the repo, then use `publish-project-to-github`.
5. Ask Nour before tagging `v1.0.0` and before deploying any public demo server.

**Tests that prove it:** full CI green on `main`; push checks print exactly Nour and 0; emoji grep clean; links in README work.

**Definition of done:** CLAUDE.md §7; Nour approved the public launch.

**Skills:** `writing-guidelines`, `audit-reference-originality`, `design:design-critique`, `code-review`, `security-review`, `superpowers:verification-before-completion`, `superpowers:finishing-a-development-branch`, `publish-project-to-github` (only after Nour approves going public).
