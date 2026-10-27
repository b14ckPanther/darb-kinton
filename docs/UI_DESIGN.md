# UI design

Fixed by the roadmap: devices float as orbs; drag a file onto one and it shoots across in an arc; in Darb Budokai it is the portal. Fixed by Nour's rules: UI first, "jaw-dropping", never childish or template-looking, mobile feels as native as SwiftUI, modern SVG icons only, no emoji anywhere.

Everything else here (screens, motion values, art directions, framework) is **proposed, confirm with Nour in Phase 1**, and the art direction is picked by Nour side by side in Phase 2. Every number below is an example default for the design tokens, never a constant in code.

## 1. Signature moment: the orbit

**What you see.** The home screen is a quiet field of space with your devices floating as orbs: crisp, lit spheres with a real light source, soft contact shadow and a thin rim, never blurry gradient blobs. Your current device sits low and centre, slightly larger, like the place you stand. Other online devices float above it in a loose arc, each breathing slowly (scale amplitude about 1.5%). Offline devices are dim, matte and lower, with their last-seen time. A small OS mark (Simple Icons logo) and the device name sit under each orb in clear text.

**Sending.** You drag a file from your desktop (or tap the orb on a phone and pick a file). While dragging, the orbs you can drop on lean towards the pointer and their rims brighten; the one under the pointer swells (about 1.08x) and shows its name large. You release. The file becomes a small bright bead that launches from your orb and travels a **ballistic arc** to the target (a quadratic Bezier with apex height proportional to distance, duration about 650 ms, spring settle at the end). The arc leaves a fading trail that stays as a thin **thread** connecting the two orbs for the length of the transfer. The thread fills along its length with progress. When the last chunk is verified, the target orb pulses once and the thread dissolves from sender to receiver.

**Several at once.** Drop onto "All devices" (a ring around your orb) and beads fan out in simultaneous arcs, one per device, each thread filling at its own speed.

**Far away.** A device on another network sits further out, beyond a faint horizon line. Its arc is higher and its thread shows a small path label: "Direct", "Via your server" (TURN) or "Relayed". The path is honest, never hidden.

**Resume.** If the connection drops, the thread freezes, goes dashed, and shows "Paused at 71%". When it reconnects the dashes re-join and filling continues from the same point. This makes resumability visible, which is the feature most file-sharing tools hide.

**Receiving.** On the receiver, a bead arrives from the sender's direction and stops above a sheet that slides up: sender orb, item name, size, kind. Accept or Decline. Nothing is saved until Accept.

**Darb Budokai link.** When the Darb Budokai adapter is on, Darb Budokai draws the same thread as a portal ring between device regions on its map. Same shape language, so the two apps feel related.

**Fallbacks.**
- No WebGL or `prefers-reduced-data`: a 2D SVG version of the same layout with the same interactions.
- `prefers-reduced-motion`: no float, no arc flight. The item appears at the target and the thread is a straight progress line that fills. Pulses become a brief outline change.
- Always available: a **List view** twin (toggle in the nav bar) with the same devices as native-style rows, each a drop target and a button. Screen readers and keyboard users get full function from it.

## 2. Native feel (mobile first)

Darb Kinton's browser client is used mostly on phones, installable as a PWA. It must feel like a SwiftUI app, not a website:

- **Safe areas:** `viewport-fit=cover`, padding from `env(safe-area-inset-*)`; content never under the notch or home indicator.
- **Large titles** ("Darb Kinton", "Inbox", "Devices") that collapse into a compact nav bar title on scroll.
- **Bottom tab bar** on phones: Orbit, Inbox, Devices, Settings. On wide screens it becomes a left rail.
- **Sheets** with detents (medium about 50%, large about 92%) and drag-to-dismiss with velocity; grabber visible; background dims and scales slightly.
- **Spring physics** for every motion (stiffness/damping in tokens, e.g. response 0.35 s, damping fraction 0.85). No linear easing anywhere.
- **Pressed state:** every tappable control scales to about 0.96 on press with a spring back.
- **44 pt minimum** touch targets everywhere, including orbs and list rows.
- **Materials:** translucent bars and sheets (`backdrop-filter: blur() saturate()`) with a solid fallback colour that still meets contrast.
- **Lists:** inset grouped style, separators inset from the leading edge, swipe actions (Inbox: swipe left to Delete, right to Save again; Devices: swipe left to Revoke, with confirm).
- **Haptics:** `navigator.vibrate` where supported (Android) for accept and arrival, off by default on desktop; settings toggle.
- **Native share target:** the PWA registers a Web Share Target so "Share > Darb Kinton" works from the phone's share sheet (Android/Chromium; iOS is limited, see open questions).

## 3. Icons, logos, type

- **One icon set:** Solar (via Iconify, duotone or linear, skill `solar-duotone-bold`) or Lucide, picked in Phase 2. Inline SVG, `currentColor`, one stroke weight. Custom-drawn SVG only when the set lacks a glyph, drawn to the same grid.
- **Logos:** device/OS marks (Apple, Android, Windows, Linux, Chrome, Firefox, Safari) only via Iconify Simple Icons (skill `company-logos`), monochrome.
- **No emoji, anywhere:** UI, notifications, toasts, CLI output, empty states, docs. No raster clip-art, no mixed icon styles.
- **Type:** Google Fonts only. Candidates per direction below. Numbers (sizes, percentages, speeds) use tabular figures.

## 4. Screens and surfaces

| # | Screen | Contents and states |
|---|---|---|
| S1 | **Welcome / first run** | One line on what Darb Kinton is, "This device" naming (suggested from platform), "Pair another device" and "I have a link". No marketing page. |
| S2 | **Pair: show** | QR code (encodes the pair URL with token and key fingerprint in the fragment), 6-character short code below, countdown ring for TTL, "Waiting for device". On success both screens show 6 **SAS words** and "Do these match?" (QR path auto-confirms). |
| S3 | **Pair: join** | Camera scan (BarcodeDetector where available, else `zxing-wasm` worker, proposed) or type the short code; then SAS compare; then name this device. |
| S4 | **Orbit (home)** | The signature scene (section 1). Nav bar: title, List/Orbit toggle, "+" (pick file, paste text, paste link). Drop anywhere on empty space shows "Drop on a device". Empty state (no other devices): your orb alone with "Pair a device" as an orbiting dashed ghost. |
| S5 | **Compose (sheet)** | From "+" or tapping an orb: tabs File / Text / Link, recipients as small orb chips (multi-select), Send. Clipboard paste button (asks for permission). |
| S6 | **In flight** | Threads on the orbit plus a compact transfers tray (bottom, above tab bar): per item name, recipient, speed, ETA, path label, Pause / Cancel. Paused and Resuming states. |
| S7 | **Receive (sheet)** | Sender, kind, name, size, path; Accept / Decline. For text: preview with Copy. For links: domain shown prominently, full URL as text, Open and Copy. After file completes: Save / Share / Show in Inbox. |
| S8 | **Inbox** | Inset grouped list by day: received and sent items, status (Received, Saved, Paused 71%, Failed, Expired), swipe actions. Items whose bytes are still in OPFS can be saved again until cleanup. |
| S9 | **Share link (sheet)** | Create link for someone far away: expiry and max downloads pickers (options from config), optional passphrase (if approved), Copy / Share / QR. Live or mailbox mode shown honestly. Revoke link. |
| S10 | **Link landing (friend's browser)** | No install, no account. Sender's display name, item name and size after decryption, Download. Clear "End-to-end encrypted. The server can't read this." with a "How?" sheet. Drop link variant: "Send to Nour" with a drop zone. |
| S11 | **Devices** | List of paired devices with OS logo, kind, last seen, key fingerprint (grouped hex), Rename, Revoke (destructive, confirm). This device highlighted. |
| S12 | **Settings** | Device name, notifications, haptics, sounds (if any), theme (system/light/dark), storage used and "Clear finished", Darb Budokai adapter status (read-only from server). |
| S13 | **Server admin** (owner only) | Server health, TURN/relay usage vs caps, mailbox disk use, editable limits (subset in `settings`), Darb Budokai adapter toggle and outbox status. Uses `dataviz` rules for the usage charts. |
| S14 | **CLI** (`kinton send`, `kinton receive`, `kinton serve`) | Designed terminal output: a one-line header, a progress bar with speed, ETA and path, SAS words in a box at pairing, clean errors with a next step. Respects `NO_COLOR` and non-TTY output (plain lines). No emoji. |
| S15 | **Errors and edge states** | Offline server, WebRTC failed (falls to relay automatically, says so), storage persistence denied, file too large for config, browser unsupported (lists what is missing). Each with plain copy written with `design:ux-copy`. |

## 5. Interaction and motion rules

- **Durations and springs come from tokens.** Proposed defaults: tap feedback 120 ms, sheet spring response 0.35 s / damping 0.85, arc flight 650 ms, arrival pulse 400 ms, orb breathing period 6 s.
- **Motion has meaning.** Arcs mean "sending", threads mean "in progress", dashes mean "paused", pulses mean "verified". No decorative motion beyond the slow breathing and starfield drift.
- **One hero at a time.** During a send, other orbs dim 20% so the arc reads.
- **Never block on animation.** The transfer starts at drop, not at the end of the arc.
- **Input:** drag and drop (desktop), tap orb then pick (touch), keyboard (section 7), paste (Ctrl/Cmd+V on Orbit opens Compose with the pasted item).
- **Performance budget:** orbit scene at 60 fps on a mid-range phone (e.g. Pixel 6a / iPhone 12) at device pixel ratio capped at 2; pause rendering when the tab is hidden or nothing moves; under 250 KB gzipped JS for first load excluding Three.js, which loads after first paint (proposed budget).
- **Sound (optional):** a soft, original synthesized whoosh on send and a low chime on arrival, made with `procedural-sfx`, off by default.

## 6. Art directions (pick one in Phase 2)

All three are original. None uses gradient blobs, neon cyberpunk clichés or space-cartoon rockets. Each defines orb material, background, arc, type and palette; Phase 2 builds all three as small live comps of S4 and S7 for Nour to compare side by side.

**A. Observatory glass.** Night sky over a dark slate field with a faint polar grid like an astrolabe. Orbs are polished glass spheres with a single warm key light and a cool rim; inside each, a tiny suspended filament glows when the device is online. Arcs are thin gold lines with a bright bead. Type: "Instrument Sans" for UI, "Instrument Serif" for large titles. Palette: ink `#0E1116`, slate `#1B2130`, brass `#C9A86A`, frost `#E8EEF5`. Light mode: pale parchment sky with ink orbs.

**B. Signal paper.** A technical-drawing world: off-white paper with a fine dot grid, orbs drawn as shaded graphite spheres with hatch shadows, rendered in Three.js with a custom toon/hatching shader. Arcs are dashed ballistic trajectories with tick marks every 10% and tiny annotations ("71% - 18.2 MB/s - direct"). Type: "IBM Plex Sans" + "IBM Plex Mono" for numbers. Palette: paper `#F4F1EA`, graphite `#2B2B2B`, signal red `#D2452B`, blueprint `#2F5D8A`. Dark mode inverts to blueprint.

**C. Deep-water lanterns.** Devices are lanterns suspended in dark water: orbs with subsurface glow, gentle caustic light on a seabed plane far below. Sending releases a light that rises and falls in an arc like a thrown ember; threads are thin bioluminescent filaments. Type: "Manrope" UI, "Fraunces" titles. Palette: abyss `#071318`, kelp `#0F2A2E`, lantern `#F2C46D`, foam `#D7EEF0`. Light mode is a shallow lagoon with darker lanterns.

## 7. Accessibility requirements

- **WCAG 2.2 AA:** text contrast 4.5:1 (3:1 large text and UI components) on every material, including over the 3D scene (labels sit on a solid or high-opacity plate).
- **Keyboard:** full operation without a pointer. On Orbit, Tab moves through orbs in a stable order (a DOM list twin of the scene); Enter opens Compose for that device; Space on a focused file item then arrow keys to choose a target orb and Enter to send ("keyboard drag"). Escape closes sheets. Visible focus ring that meets 3:1.
- **Screen readers:** every orb is a button with name, kind, status ("Nour's iPhone, phone, online"); transfers announce start, pause, resume and completion via a polite live region; the 3D canvas is `aria-hidden` with the list twin carrying semantics.
- **Reduced motion:** as in section 1. Also stops breathing and starfield drift.
- **Touch:** 44 pt targets; sheets dismissible by button as well as drag; no gesture-only actions (swipe actions also available from a row's context menu).
- **Text scaling:** layout holds at 200% zoom and with large system text (rem-based type scale).
- **Colour is never the only signal:** paused threads are dashed and labelled, not just a different colour.
- **Tested** with axe in Playwright (zero serious/critical), VoiceOver on iOS Safari and TalkBack on Android Chrome before Phase 3 approval and again at launch.
