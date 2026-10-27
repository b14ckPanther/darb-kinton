# Threat model

Darb Kinton's one promise: **only the sender and the chosen receivers can read what is sent.** This file says what we protect, from whom, how, and what we can't protect. It is a living document: any phase that changes the attack surface updates it in the same branch, and Phase 11 (hardening) re-reviews it with `security-review`.

The model and every mitigation below are **proposed, confirm with Nour in Phase 1**, and the crypto parts are reviewed again in Phase 5 before code depends on them. Method: assets, trust boundaries, adversaries, STRIDE per component, then residual risk.

## 1. Assets

| Asset | Why it matters |
|---|---|
| A1 File contents, clipboard text, links | The payload. Must stay confidential and unmodified. |
| A2 Metadata: file names, MIME types | Can reveal as much as contents ("divorce_papers.pdf"). Encrypted inside the manifest. |
| A3 Device identity private keys | Whoever holds one can impersonate the device and receive future transfers. |
| A4 Per-transfer chunk keys, share-link keys | Decrypt one transfer. |
| A5 Pairing tokens, SAS words | Let an attacker pair a rogue device. |
| A6 Server availability and bandwidth (TURN, relay, mailbox) | Abuse costs Nour money and can take the server down. |
| A7 Traffic metadata: who sends to whom, when, how much | Visible to the server by design; minimised and retained briefly. |
| A8 The served web client (JS) | If it is malicious, every browser-side promise is void. |
| A9 Receiver's device | A received file could be malicious. |

## 2. Trust boundaries

```
 [Device A] ══E2EE══ [Device B]          trusted endpoints (after pairing + verification)
     │  ╲                 ╱  │
     │   ╲ ciphertext only ╱ │
     ▼    ▼               ▼  ▼
 [kinton server: signaling, TURN, relay, mailbox, static JS]   honest-but-curious at best; may be compromised
     │
 [network: Wi-Fi, ISP, corporate proxy]                      hostile
```

The server is **not trusted for confidentiality or integrity of payloads**. It is trusted for availability and, unavoidably for browser users, for serving the correct JavaScript (see R1).

## 3. Adversaries

| Id | Adversary | Capabilities |
|---|---|---|
| T1 | Passive network observer | Sees packets on Wi-Fi/ISP. |
| T2 | Active network attacker | MITM, packet injection, DNS spoofing, blocking UDP. |
| T3 | Curious or compromised server operator | Reads the database, logs, mailbox, relay traffic; can alter signaling messages; can change the served JS. |
| T4 | Malicious TURN/relay path | Same as T3 for the bytes it carries. |
| T5 | Stolen or lost device | Has a paired device with its keys in IndexedDB. |
| T6 | Someone who gets a share link | Link forwarded, posted, or seen in browser history. |
| T7 | Malicious peer | A paired device or link recipient sending crafted frames or malicious files. |
| T8 | Internet abuser | Unauthenticated, scans the server, tries to use TURN/relay/mailbox as free infrastructure or to exhaust it. |
| T9 | XSS / supply-chain attacker | Injects script via a crafted file name, link or a compromised npm/Go dependency. |

## 4. STRIDE by component

| Component | Threat (STRIDE) | Mitigation | Test that proves it |
|---|---|---|---|
| Pairing | **S**: rogue device pairs as you (T2, T3 swapping keys) | QR path: QR fragment carries a fingerprint of A's identity key; B rejects a different key. Code path: both screens show 6 SAS words from HKDF over both public keys; user confirms they match. Tokens single-use, 5 min TTL (config), stored hashed. | `TestPairRejectsSwappedKey`, `TestSASDiffersWhenKeySwapped`, E2E pairing with a malicious hub fake |
| Signaling hub | **S**: impersonate a device | Challenge-response signature with identity key on every WS connect. | `TestHubRejectsBadSignature` |
| Signaling hub | **T**: alter offers, SDP, ICE | Transfer handshake transcript is signed by both identity keys; SDP DTLS fingerprints are included in the signed transcript so a swapped DTLS endpoint fails. Payload confidentiality never relies on DTLS alone. | `TestHandshakeFailsOnTamperedTranscript`, vnet MITM test |
| Transfer | **I**: read contents (T1-T4) | AES-256-GCM per chunk with keys from ephemeral ECDH; server and TURN see ciphertext only. Manifest (names, MIME) encrypted. | Integration test asserts relay/mailbox bytes never contain plaintext markers; crypto vectors |
| Transfer | **T**: modify, reorder, drop or splice chunks (T3, T4, T7) | GCM tag per chunk, AAD binds transferId, index and chunk count; segment SHA-256; final list hash. | `TestOpenRejectsWrongIndexAAD`, `TestResumeRejectsChangedFile`, fuzz targets |
| Transfer | **I**: nonce reuse breaks GCM | Nonce = chunk index under a key unique to this transfer, direction and session; resume always re-handshakes. | `TestNoncesUniqueAcrossResume` (property test over random drop points) |
| Transfer | **R**: "I never sent that" | Out of scope: Darb Kinton is not a non-repudiation system. Local history only. | n/a |
| Receive | **E**: file auto-runs, overwrites, or lands without consent (T7) | Explicit accept for every incoming item; save via the browser's download/save picker only; names sanitised; no auto-open; size shown before accept. | E2E `incoming transfer waits for accept`; `TestSanitizeName` table |
| Web client | **E/T**: XSS via file name, link or text (T9) | Render untrusted strings with `textContent` only; links shown as text with an explicit Open that uses `rel=noopener noreferrer` and allows only `http(s)` schemes; strict CSP (`default-src 'self'; script-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'`); Trusted Types where supported. | Playwright test with a `<img onerror>` file name and a `javascript:` link |
| Web client | **T**: served JS altered (T3, T8) | See R1. Integrity of embedded assets: hashes printed by `kinton version --assets` and published in release notes. | Release CI compares embedded asset hashes with the `web/dist` build |
| Keys at rest | **I**: stolen device reveals keys (T5) | Identity keys are non-extractable `CryptoKey` in IndexedDB (can't be exported by script, still usable by anyone holding the unlocked device). Any device can revoke another from Devices; revoked keys are rejected by the hub and by peers on next presence sync. | `TestRevokedDeviceCannotConnect`, E2E revoke |
| Share links | **I**: link leaks (T6) | Key only in URL fragment (never in server logs or `Referer`, `Referrer-Policy: no-referrer`); TTL and max downloads (config); sender can revoke; optional passphrase (open question). | `TestServerNeverReceivesFragment` (asserts logs and request lines), E2E expired link |
| TURN / relay / mailbox | **D**: bandwidth or disk exhaustion; open relay abuse (T8) | TURN credentials only for authenticated devices, time-limited HMAC usernames; relay sessions only between endpoints of a signed offer; per-session and global bandwidth caps; mailbox quota per device and TTL sweeper; rate limits on `/ws`, `/api/pair`, `/r/`. TURN refuses to relay to private/loopback ranges (`pion/turn` permission handler) so it can't be used to reach Nour's LAN. | `TestTURNDeniesUnauthenticated`, `TestTURNDeniesPrivatePeerAddress`, `TestRelayCapsBandwidth`, `TestMailboxQuota` |
| Server | **I**: metadata collection (A7) | No file names in DB or logs; transfer rows keep sizes and paths for 30 days (config); `slog` fields allowlisted; no third-party STUN by default. | `TestLogsContainNoPayloadFields` (log capture), review checklist |
| Dependencies | **T**: supply chain (T9) | `go.sum` and `package-lock.json` committed; `govulncheck` and `npm audit --omit=dev` in CI; Dependabot (proposed); minimal npm runtime deps. | CI jobs |
| Darb Budokai adapter | **I**: leak to Darb Budokai | Only the cosmetic event (device ids mapped to Darb Budokai ids, kind, time). Never names, sizes or content. Off by default. | `TestPortalEventHasNoPayloadFields` against the JSON Schema |

## 5. Residual risks (accepted, stated honestly in the README)

- **R1 Server-delivered JavaScript.** For browser users the server sends the code that does the encryption. A compromised server (T3) could serve JS that exfiltrates keys. This is the fundamental limit of every web E2EE tool. Mitigations reduce but don't remove it: self-hosting (you are the operator), strict CSP, assets embedded in a signed and checksummed release binary, published asset hashes, a reproducible web build (proposed), installable PWA so code changes are visible as updates, and the CLI peer for users who want no served code at all.
- **R2 Metadata visible to the server.** Who is online, who sends to whom, when, and approximate sizes (ciphertext length). Padding sizes is out of scope for v1.
- **R3 Unlocked stolen device.** Non-extractable keys stop export, not use. Revocation from another device is the answer.
- **R4 SAS skipped.** If a user doesn't compare the SAS words on the code path, a malicious server can pair itself in the middle. The QR path avoids this; the UI makes the QR path the default.
- **R5 Malicious files.** Darb Kinton delivers bytes faithfully; it does not scan for malware. Receivers accept explicitly and the OS handles opening.
- **R6 Browser storage eviction.** OPFS and IndexedDB can be evicted under storage pressure, losing resume state. The client calls `navigator.storage.persist()` and tells the user when it is not granted.
- **R7 No independent audit.** The protocol is reviewed internally (`security-review`) only. The README says so.

## 6. Security tests checklist (owned by Phase 11)

- [ ] All tests named in §4 exist and pass in CI.
- [ ] Fuzz targets run 10 minutes each without findings; corpus committed under `testdata/fuzz/`.
- [ ] Go/TS crypto vectors match byte for byte.
- [ ] `govulncheck ./...` clean; `npm audit --omit=dev` no high/critical.
- [ ] Response headers checked by a test: CSP, `Referrer-Policy: no-referrer`, `X-Content-Type-Options: nosniff`, `Permissions-Policy`, HSTS when TLS is on.
- [ ] Manual review of every log call for payload fields.
- [ ] `security-review` run over the whole repo; findings fixed or recorded as accepted risks here.
