# Conventions

## Go code style

- `gofmt` and `goimports` on save; `golangci-lint run` (v2 config) must be clean.
- Module `github.com/b14ckPanther/darb-kinton`. Everything not meant for import lives under `internal/`.
- Package names short, lower case, no underscores (`signal`, `transfer`, not `signalling_hub`).
- Every blocking or long-running function takes `ctx context.Context` as its first argument and returns when it is cancelled. Every goroutine has an owner that waits for it (`errgroup.Group` from `golang.org/x/sync/errgroup` or a `sync.WaitGroup`).
- Channels: the sender closes; buffered channels have a size from config or a named reason in a comment.
- Errors: wrap with `fmt.Errorf("open mailbox item %s: %w", id, err)`; sentinel errors as `var ErrX = errors.New(...)`; check with `errors.Is/As`. No `panic` outside `main` and impossible states.
- Logging: `log/slog` with structured fields from an allowlist (`request_id`, `device_id`, `transfer_id`, `path`, `bytes`, `duration`). Never names, links, text, keys or fragments.
- No package-level mutable state except registered metrics. No `init()` with side effects.
- Limits and timings come from `config.Config`, passed in; never literals (CLAUDE.md §1.2).

## TypeScript code style

- TypeScript `strict: true`, ESLint (typescript-eslint recommended + strict), Prettier.
- Crypto and transfer code are framework-free modules (`web/src/crypto`, `web/src/transfer`, `web/src/storage`), runnable in a Web Worker.
- Untrusted strings rendered with `textContent` or framework text bindings only; no `innerHTML`.
- Design tokens imported from the generated `tokens.ts` / CSS variables; no raw colours, durations or spring values in components.
- Icons only from the chosen set via the icon pipeline; logos only from Simple Icons. No emoji in any string.

## Project layout

See `ARCHITECTURE.md` §11. Summary:

```
cmd/kinton/            entry point and subcommands
internal/<pkg>/      server, signal, turnsrv, relay, mailbox, store, protocol, crypto, peer, transfer, budokai, config
web/src/             crypto/ transfer/ storage/ transport/ scene/ ui/ motion/ tokens/ protocol/
config/              kinton.example.yaml, copy/en.yaml, seed/demo/, sas-words/
contracts/events/    kinton.portal.opened/v1.schema.json + examples/
testdata/            vectors/, fuzz/
docs/                specs/, plans/ and the planning docs
```

## Testing conventions

- **TDD always:** failing test first, watch it fail for the right reason, then implement.
- Go: table-driven tests with `t.Run(tc.name, ...)`; `t.Parallel()` where safe; helpers call `t.Helper()`. Test names say the behaviour: `TestRelayCapsBandwidth`, `TestOpenRejectsWrongIndexAAD`.
- Always run with `-race`. Integration tests that use vnet or httptest live next to the code with the `_test.go` suffix; slow ones are guarded by `testing.Short()`.
- Fuzz targets named `FuzzXxx`, seed corpus in `testdata/fuzz/FuzzXxx/`.
- Golden files for CLI output in `testdata/golden/`, updated with `go test ./cmd/kinton -update`.
- Crypto: shared vectors in `testdata/vectors/*.json` consumed by both Go and Vitest.
- Web: Vitest for units (`*.test.ts` next to the code), Playwright for E2E (`web/e2e/*.spec.ts`), two browser contexts for any transfer test, `@axe-core/playwright` on every screen.
- No sleeps for synchronisation: use channels, `eventually` helpers with a deadline, or Playwright auto-waiting.
- No live third-party services in any test or CI job.

## Commit style

- Imperative, plain English, first line under 72 characters, optional body explaining why.
  - Good: `Reject chunks whose AAD index does not match`
  - Good: `Add failing test for relay bandwidth cap` (only when the next commit makes it pass)
  - Bad: `fix stuff`, `feat(relay): ...` (no prefixes needed), anything with an emoji.
- **No AI attribution of any kind.** No `Co-Authored-By`, no "Generated with", no tool names. Never the word "claude" in a message (the hook rejects it).
- Authored and committed as `Nour Alden Mousa <nmcryptoinvest@gmail.com>` only.
- One logical change per commit; every commit builds and passes tests.

## Branch naming

- One branch per phase: `phase/NN-short-name` (e.g. `phase/07-resume`), from `main`.
- Optional short-lived task branches off the phase branch: `phase/07-resume--bitmap`, merged back into the phase branch locally.
- `main` only changes through a merge Nour approved.

## Pull request template

Saved as `.github/pull_request_template.md` in Phase 0:

```markdown
## What

<one paragraph: what this phase/branch delivers>

## Why

<link to the phase in docs/PLAN.md and the spec in docs/specs/>

## How it was tested

- [ ] `go test -race ./...`
- [ ] `npm --prefix web test` and Playwright E2E
- [ ] axe: zero serious/critical violations
- [ ] Manual checks (list devices and browsers)

## Screens

<screenshots or GIF for any UI change, light and dark, phone and desktop>

## Checklist

- [ ] No hardcoded limits, timings or copy
- [ ] No secrets, keys, file names or clipboard content in logs
- [ ] THREAT_MODEL.md updated if the attack surface changed
- [ ] Emoji check prints nothing
- [ ] Ledger updated in docs/PROGRESS.md
- [ ] Push checks: only Nour as author/committer, attribution grep returns 0
```

The template contains no attribution line and PR descriptions never add one.
