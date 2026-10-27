# Vision

## Intent

Moving a file between your own devices should take one drag. Today it doesn't: AirDrop only works inside Apple's world, Quick Share inside Android/Windows, messaging apps recompress photos and keep copies on someone else's server, and cloud drives make you upload then download. Darb Kinton is one tool that works between **any** devices, including a friend's browser with nothing installed, and it is end-to-end encrypted so the server you host can't read what passes through it.

Roadmap line: "Darb Kinton has to beat AirDrop where AirDrop can't go."

## What it does (fixed by the roadmap)

- Send files, links and clipboard text between iPhone, Android, Mac, Windows, Linux and any modern browser.
- A friend with nothing installed can receive (and send) from a browser.
- A single Go binary you host yourself.
- End-to-end encryption.
- Send to several devices at once.
- Send to someone far away (not on your network).
- Resume huge transfers that were interrupted.

**Signature moment:** your devices float as orbs. Drag a file onto one and it shoots across in an arc. In Darb Budokai, it's the portal between your devices.

## Goals

1. **Daily use by Nour.** Phone to laptop photos, laptop to phone links and clipboard, at least once a day. If Nour goes back to messaging themself on WhatsApp, Darb Kinton failed.
2. **Fast on a LAN.** Direct WebRTC between devices on the same network. Proposed target: at least 50 MB/s between two laptops on gigabit Ethernet, at least 20 MB/s on good Wi-Fi (measured in Phase 11, numbers go in the README honestly).
3. **Never lose a big transfer.** A 10 GB file that drops at 70% resumes from 70%, verified by hash.
4. **Zero trust in the server.** The operator (Nour, or anyone else who self-hosts) can't read content, file names or clipboard text.
5. **One command to self-host.** `./kinton serve` and it runs: signaling, TURN, relay, web client, all in one binary.
6. **A portfolio piece that proves Go.** Goroutines and channels, context cancellation, WebRTC, WebSockets, real cryptography, table-driven tests, fuzzing, pprof, GoReleaser.

## Non-goals

- Not a cloud drive or sync tool. No folder sync, no versioning, no long-term storage (the optional mailbox holds encrypted items for a short TTL only).
- Not a chat app.
- No native iOS/Android apps in this project. Phones use the browser client (installable as a PWA). Native apps could be a later project.
- No accounts, no email sign-up. Devices are identified by keys.
- No multi-tenant SaaS. One self-hosted server per person or household (proposed, confirm with Nour in Phase 1).

## Anti-goals (would make it a failure even if it works)

- **The server can read anything.** If any path (relay, mailbox, share link, logs) exposes plaintext or keys to the server, Darb Kinton has failed its one promise.
- **A pretty demo that can't move a 4 GB file.** If big transfers stall, run out of memory in the browser, or restart from zero, the orbs are lipstick.
- **A file-upload form with a 3D background.** If removing the orbs leaves a generic upload page, the design failed. The orbs must be the interface: drag target, presence indicator, progress.
- **Template or toy look.** Gradient blobs, cartoon rockets, emoji, stock icons, a "Features / Pricing / Testimonials" landing page.
- **Silent transfers.** Anything arriving on a device without the receiver accepting it.
- **Setup friction.** If pairing a new phone takes more than about 15 seconds or needs typing a long code, people won't use it.

## Why this stack for the Israeli junior market

- Go appears in about a third of backend listings in Nour's market data and is the default language for fast networked services, infrastructure and security tooling (Wiz, Check Point, cloud teams).
- Nour's GitHub today is about 90% Next.js/Supabase/TypeScript. Darb Kinton proves systems skills that profile doesn't show: concurrency with goroutines and channels, context cancellation, binary protocols, NAT traversal, applied cryptography, fuzzing, profiling, and shipping a cross-compiled binary.
- Security companies in Israel care about threat models. A written threat model with tests that enforce it is rare in a junior portfolio.
- It is a tool interviewers can try live: open the link on their phone and receive a file during the interview.
