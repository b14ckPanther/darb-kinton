# Integration with the universe

Darb Kinton is "The Portal" in Darb Budokai. Darb Kinton must work fully without Darb Budokai: the integration is an optional, later phase (Phase 13), off by default, and Darb Kinton never consumes anything from Darb Budokai.

Source of truth for the Darb Budokai side: `budokai/docs/EVENT_CONTRACTS.md` (§1 envelope, §2 ingest API, §3.4 Darb Kinton). The Darb Budokai envelope format (CloudEvents 1.0 + JSON Schema 2020-12) is itself still **proposed, confirm with Nour in Phase 1** of Darb Budokai; Darb Kinton follows whatever Darb Budokai settles on.

## 1. What Darb Kinton emits

### `kinton.portal.opened` v1

Emitted once per transfer when the receiver **accepts** (not on offer, not on decline), so the map only shows portals that really opened.

Payload (as defined by Darb Budokai, §3.4):

```json
{
  "transferId": "string",
  "fromDevice": "string",
  "toDevice": "string",
  "kind": "file|text|link",
  "openedAt": "date-time"
}
```

Schema file in this repo: `contracts/events/kinton.portal.opened/v1.schema.json` (JSON Schema 2020-12), with `additionalProperties: false`, all five fields required, `kind` an enum, `openedAt` `format: date-time`. Examples in `contracts/events/kinton.portal.opened/examples/`.

Privacy rules (enforced by `TestPortalEventHasNoPayloadFields`):
- **Never** file names, sizes, MIME types, link URLs, text, hashes or keys. Darb Budokai: "Cosmetic only (portal marker). No payload content is ever sent to Darb Budokai."
- `fromDevice` / `toDevice` are opaque Darb Kinton device ids, not names. Darb Budokai maps them to device regions; the mapping lives in Darb Budokai config.
- `transferId` is a random UUIDv7 with no meaning outside Darb Kinton.
- Share-link transfers to people outside Nour's devices are **not** emitted (proposed, confirm with Nour in Phase 1): a friend's browser is not one of Nour's devices.

Envelope (CloudEvents 1.0 structured mode, per Darb Budokai §1):

```json
{
  "specversion": "1.0",
  "id": "<UUIDv7, same as an outbox row id>",
  "source": "urn:budokai:producer:darb-kinton",
  "type": "kinton.portal.opened",
  "dataschema": "https://github.com/b14ckPanther/darb-budokai/contracts/events/kinton.portal.opened/v1.schema.json",
  "subject": "user:<budokaiuserid>",
  "time": "<openedAt with offset>",
  "datacontenttype": "application/json",
  "budokaiuserid": "<from config>",
  "budokaievidence": { "tier": "verified", "ref": "darb-kinton:transfer:<transferId>" },
  "budokaimode": "live",
  "data": { ... }
}
```

`budokaimode` is `demo` when Darb Kinton runs with `--demo`. Evidence tier `verified` because the event comes from the system that did the transfer.

Darb Budokai's effect: a cosmetic portal ring between device regions on the map. No XP (Darb Budokai `GAME_DESIGN.md` §3).

## 2. What Darb Kinton consumes

Nothing. Darb Kinton has no inbound dependency on Darb Budokai or any sibling project.

## 3. Outbound adapter (`internal/budokai`)

- Off by default: `budokai.enabled: false`. Keys: `budokai.ingest_url` (e.g. `http://localhost:8082/ingest/v1/events`), `budokai.user_id`, `budokai.producer_key_id` and `REALM_PRODUCER_SECRET` (env only, a secret), `budokai.batch_size`, `budokai.retry.max_attempts`, `budokai.retry.backoff`.
- **Outbox pattern:** when a transfer is accepted, the same SQLite transaction that marks it accepted inserts a row in `budokai_outbox`. A background goroutine (with `context` cancellation on shutdown) sends pending rows with `POST /ingest/v1/events:batch`, `Content-Type: application/cloudevents-batch+json`.
- **Signing (Darb Budokai §2):** headers `X-Budokai-Producer: <keyId>` and `X-Budokai-Signature: t=<unix>,v1=<hex HMAC-SHA256(secret, t + "." + rawBody)>`.
- **Responses:** `202` marks accepted and duplicate ids as sent; `400` rejected events are marked `rejected` with the reason and not retried; `401/403` stop the sender and surface an error in Server admin; network errors and `5xx` retry with exponential backoff (values in config).
- Idempotent by design: the CloudEvent `id` is the outbox row id, so Darb Budokai dedupes retries.
- Outbox rows older than 30 days (config) are pruned whether sent or not.

## 4. Optional integration phase (Phase 13)

1. Add the schema file and examples; contract test validates every example and every emitted event against it (`github.com/santhosh-tekuri/jsonschema/v6`, proposed).
2. Implement outbox insert in the accept transaction (TDD).
3. Implement the sender with signing; test against an `httptest` fake of Darb Budokai ingest that checks the HMAC exactly like Darb Budokai does, including the replay window.
4. Server admin shows adapter status, last error and pending count.
5. If the Darb Budokai repo exists by then: run Darb Budokai locally (`docker compose` from Darb Budokai) and do one manual end-to-end check, recorded in the ledger. CI never calls a live Darb Budokai.
6. Coordinate with Darb Budokai: confirm the schema in `budokai/contracts/events/kinton.portal.opened/v1.schema.json` matches byte for byte (Darb Budokai is the owner; Darb Kinton copies).

## 5. Darb Kaioken tie-in (later, not in this repo)

Darb Kaioken plans a Darb Kinton post where readers "send a file between two windows". Darb Kinton's demo mode plus the share-link flow make this possible without new code: the post embeds two iframes pointed at a demo server. Noted here so the share-link UX stays embeddable (no `frame-ancestors 'none'` on the demo landing route only; decided in Darb Kaioken, not now).
