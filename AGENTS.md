# AGENTS.md

This repo's full agent manual is **`CLAUDE.md`**. Every agent tool (Codex, Cursor, Copilot, Gemini, Aider, others) must read and follow it. The rules below are a summary; if anything differs, `CLAUDE.md` wins.

## Non-negotiable rules

1. **No AI contributors.** "Never add "Co-Authored-By" or any other AI attribution line to commit messages, pull request descriptions, or any other text, in any project. Commit messages end with the last line of the actual description." Every commit is authored and committed as `Nour Alden Mousa <nmcryptoinvest@gmail.com>` (`git config user.name/user.email` set in the repo). Never write the word "claude" in a commit message.
2. **No hardcoded data.** Chunk sizes, TTLs, rate limits, relay caps, ICE servers, copy and design tokens live in `config/kinton.yaml` (+ `KINTON_*` env), the SQLite database or `web/src/tokens/`. Fixtures only in tests and the labelled `--demo` mode.
3. **Secrets** only in env vars or git-ignored `.env`; keep `.env.example` current. Never log keys, share-link fragments, file names or clipboard content.
4. **Original assets only.** Google Fonts OK. Log third-party assets in `ASSETS.md`.
5. **Ask Nour first** before creating/publicising the GitHub repo, pushing to `main`, merging, tagging, releasing, deploying to a paid VPS or deleting. Commit locally freely. One branch per phase (`phase/NN-name`). Small, honest, working commits.
6. **TDD.** Failing test first, watch it fail, then implement. `go test -race`, fuzz network parsers, pion `vnet` for network tests. No live third-party calls in tests or CI.
7. **Design-first UI** on seed data, Nour approves screen by screen. Responsive, keyboard accessible, `prefers-reduced-motion`, WCAG AA contrast.
8. **Native feel, no emoji.** SwiftUI-like mobile (safe areas, collapsing large titles, bottom tab bar, sheets with detents, springs, 44 pt targets). One modern SVG icon set (Solar or Lucide) or custom SVG; real logos only via Simple Icons. No emoji anywhere: UI, notifications, CLI, docs, commits.
9. **E2EE is sacred.** The server, TURN and relay only ever see ciphertext. Changes to crypto or wire format need an ADR and Nour's approval.
10. **Use the installed skills.** Check the skill list before each task, invoke every matching skill, record them in the ledger. See `CLAUDE.md` §3.
11. **Workflow:** brainstorm, written spec (`docs/specs/`), plan (`docs/plans/`), execute with a ledger (`docs/PROGRESS.md`), whole-branch review, finish.

## Before every push

```bash
git log --format='%an %ae%n%cn %ce' | sort -u          # only: Nour Alden Mousa nmcryptoinvest@gmail.com
git log --format=%B | grep -ciE 'co-authored|claude|anthropic|generated with'   # must be 0
rg -n --pcre2 '[\x{1F000}-\x{1FAFF}\x{2600}-\x{27BF}\x{FE0F}]' web/src internal/ cmd/ config/ docs/   # must print nothing
```

## Resume after a reset

Read `CLAUDE.md`, then `docs/PROGRESS.md`, then `git log --oneline -20`, then the current phase in `docs/PLAN.md`.
