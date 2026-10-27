# Open questions (asked in Phase 1)

Only Nour can answer these. The agent asks them **one at a time**, open-ended ones first, records each answer in `DECISIONS.md` and updates the affected doc before asking the next. Don't batch them.

## Open-ended (ask first)

1. **Daily use.** Walk me through the last few times you moved something between devices. What was it (photos, PDFs, links, code snippets), which devices, and what was annoying? Which of these should Darb Kinton make effortless first?
2. **Who besides you.** Who else should be able to use your Darb Kinton server: only your devices, your family's, friends you send links to? Should a friend ever be able to send to you without a link from you?
3. **The orb feeling.** When you picture the orbs and the arc, what does it feel like: calm and precise, playful, cinematic, mysterious? Any apps, films or objects whose feel you want (not copy)?
4. **Far away.** When you send to someone far away, do you expect them to receive while you're both online, or should it wait for them (mailbox), and for how long?
5. **What would make you stop using it?** Anything that would make you go back to WhatsApp-to-self.

## Scope and platforms

6. Phones use the browser/PWA in this project (no native iOS/Android app). OK, or do you want a native app as a later separate project?
7. Should the CLI peer (`kinton send`, `kinton receive`) be a first-class feature or a developer/test tool only?
8. Is sending whole folders needed in v1 (zipped on the fly), or files only?
9. Max file size you care about (for testing and copy): 10 GB? 50 GB? Unlimited?

## Hosting and cost

10. Where will your Darb Kinton server run: a home machine, a VPS (about $4-6/month, e.g. Hetzner CX22), or only your laptop on the LAN? Do you already have a domain for it (e.g. a `beam.zangeel.dev` subdomain)?
11. HTTPS on the LAN is needed for WebCrypto and the clipboard on phones. Prefer: built-in Let's Encrypt (`tls.mode: autocert`, needs a public domain), a reverse proxy (Caddy), mkcert for the LAN, or Tailscale (`tailscale serve`)?
12. Should there be a public demo server for recruiters at launch (costs money, needs abuse limits), or only the GIF plus self-host instructions?

## Security and privacy

13. Accept the residual risks in `THREAT_MODEL.md` §5 (especially R1: the server serves the JS)? Should the README state them plainly (proposed: yes)?
14. Share links: add an optional passphrase on top of the fragment key?
15. Should share-link transfers to friends emit the Darb Budokai portal event, or only transfers between your own devices (proposed: only your own)?
16. Sign releases with cosign (keyless via GitHub OIDC)?

## Design

17. Art direction: Observatory glass, Signal paper or Deep-water lanterns (`UI_DESIGN.md` §6)? Or a mix? Shown side by side as live comps in Phase 2.
18. Icon set: Solar (duotone) or Lucide?
19. Web framework for the client: vanilla TypeScript + Web Components (smallest, most "from scratch"), Svelte 5, or React 19 (matches more job listings, closer to your current stack)?
20. Sounds on send and arrive (original, synthesized, off by default): yes or no?
21. Light mode, dark mode, or both from day one?

## Plan

22. Phase weights and order in `PLAN.md`: any phase you want earlier (e.g. clipboard and links before resumable transfers)?
23. Is the Darb Budokai integration phase in or out for v1?
