# Kontablo MCP interface

`server.py` is an **MCP (Model Context Protocol) server** that exposes Kontablo's
**deterministic** accounting operations as agent-consumable tools. It is a thin
adapter over the same engine (`core.harness` + `core.engine`) that backs the REST
API and the gRPC server (`api/grpc/server.py`) — one mapping/consolidation brain,
exposed over multiple machine-consumable faces (REST = the body; gRPC + MCP =
additional faces). Every tool is deterministic: a graph lookup, a keyword rule,
or arithmetic. **No tool calls an LLM** (CLAUDE.md principle #5).

This realises the **agent-native layer** of architectural principle #4: an ERP
or bank consumes the REST/gRPC API directly; an autonomous LLM agent consumes
this MCP surface.

## Tools (each mirrors a deterministic gRPC RPC over the same engine)

| MCP tool | gRPC RPC it mirrors | What it does |
|---|---|---|
| `resolve_account` | `MappingService.MapAccount` | jurisdiction + local code/name → universal Kontablo node UUID via the three-tier resolver (Tier-1 exact code, Tier-2 multilingual keyword). Returns tier, confidence, and Co-responsibility boundary flags. Returns `resolved=false` (no guess) when neither deterministic tier matches. |
| `get_account` | `AccountService.GetAccount` | Look up an ontology node by `account_id` **or** by `uuid`. Returns label, nature, statement, and the jurisdiction local-code overlay. |
| `validate_balance_sheet` | `ValidationService.ValidateBalanceSheet` | Checks the double-entry identity Σdebits − Σcredits == 0 deterministically. |
| `consolidate_trial_balances` | `ConsolidationService.ConsolidateTrialBalances` | Consolidate subsidiary trial balances to USD with explicit (structured) intercompany elimination. Returns consolidated lines, eliminations applied, balance check, escalations, and a per-entity **FX audit trail** (`FXQuote`). |
| `list_jurisdictions` | (coverage scope) | List jurisdiction coverage from the 195-jurisdiction manifest. Filters: `region`, `mapping_mode`, `tier1_only`. Returns the headline summary (195 / 60 / 56). |

## Status (honest)

| Capability | Status |
|---|---|
| The five deterministic tools above | ✅ implemented (Tier-1/Tier-2, graph lookups, arithmetic) |
| Tier-3 semantic / LLM fallback as an MCP tool | ⛔ **not exposed** — planned |

This mirrors the same honesty bar the gRPC server uses (it returns
`UNIMPLEMENTED` for stochastic RPCs). The Tier-3 LLM fallback is deliberately
**not** exposed as an MCP tool in v1: exposing a stochastic capability as if it
were deterministic would hide the stochasticity and misrepresent a mapping's
confidence. `resolve_account` therefore returns `resolved=false` and escalates
to human review rather than guessing. If Tier-3 is added later it must return the
Deterministic Boundary Library verdict **and** the confidence — never a bare
guess. **This is not full feature parity with REST**; it is "deterministic core
implemented, Tier-3/LLM tools planned."

## Run

```bash
pip install -r requirements.txt
python -m api.mcp.server        # serves over stdio (the standard local-agent transport)
```

`KONTABLO_FX_MODE` is env-gated exactly as for REST/gRPC: `live` by default
(ECB/Frankfurter → open.er-api → pinned static fallback), `static` for an
offline/hermetic run. The pinned static table is always the deterministic
fallback.

## Example: an agent calling the server

`demo.py` launches the server as a subprocess over stdio and drives it with the
official MCP **client** — the same handshake an LLM agent runtime performs:

```bash
python -m api.mcp.demo
```

```
Kontablo MCP tools: ['resolve_account', 'get_account', 'validate_balance_sheet',
                     'consolidate_trial_balances', 'list_jurisdictions']
resolve(MX, SAT, 101, 'Caja') -> asset.current.cash
    (uuid=00000000-0000-4000-8000-000000000101, tier=tier1_exact, conf=1.0)
get_account(uuid) -> asset.current.cash: Cash and Cash Equivalents (debit)
validate_balance_sheet -> is_valid=True, diff=0.0
list_jurisdictions -> total=195, statutory_chart=60, tier1_codes_available=56
```

### Registering with an MCP client (e.g. Claude Desktop)

```json
{
  "mcpServers": {
    "kontablo": {
      "command": "python",
      "args": ["-m", "api.mcp.server"],
      "cwd": "/path/to/accounting-esperanto",
      "env": { "KONTABLO_FX_MODE": "static" }
    }
  }
}
```

Once registered, an agent discovers the five tools automatically; every tool and
every parameter is self-describing (the input JSON schema carries a description
for each field, enforced by `tests/mcp/test_mcp_server.py`). The reference below
is for humans — agents read the same information from the schema.

## Tool reference (inputs & outputs)

All amounts are plain numbers in the stated currency; all responses are JSON
objects. Codes are strings (`"101"`, not `101`).

### 1. `resolve_account`

Map a local statutory account to a universal Kontablo node.

| Param | Type | Required | Description |
|---|---|---|---|
| `jurisdiction` | string | ✅ | ISO 3166-1 alpha-2, e.g. `"mx"` (case-insensitive). |
| `local_code` | string | – | Local statutory code, e.g. `"101"`. Drives the Tier-1 exact lookup. |
| `local_name` | string | – | Local account name in any supported language. Drives the Tier-2 keyword match. |
| `nature` | string | – | `"debit"` / `"credit"` or omit. Sanity-check only. |

Provide `local_code`, `local_name`, or both.

```jsonc
// request
{ "jurisdiction": "mx", "local_code": "101", "local_name": "Caja" }
// response (resolved)
{
  "resolved": true,
  "kontablo_id": "asset.current.cash",
  "kontablo_uuid": "00000000-0000-4000-8000-000000000101",
  "label_en": "Cash and Cash Equivalents",
  "nature": "debit", "statement": "balance_sheet",
  "tier": "tier1_exact", "match_method": "exact_lookup",
  "confidence": 1.0, "cra_flags": [],
  "note": "Resolved deterministically via tier1_exact."
}
```

When nothing matches deterministically the tool **does not guess** — it returns
`resolved: false` and escalates (Tier-3/LLM is not exposed over MCP):

```jsonc
// response (escalated)
{ "resolved": false, "kontablo_id": null, "tier": "escalated",
  "match_method": "not_found", "confidence": 0.0,
  "note": "No deterministic mapping (Tier-1/Tier-2); escalate to human review ..." }
```

`tier` is `tier1_exact` (confidence 1.0), `tier2_keyword` (0.85), or `escalated`
(0.0). `cra_flags` lists any Co-responsibility boundary warnings (e.g. a
nature mismatch).

### 2. `get_account`

Look up an ontology node by id **or** UUID.

| Param | Type | Required | Description |
|---|---|---|---|
| `account_id` | string | one of | Kontablo node id, e.g. `"asset.current.cash"`. |
| `uuid` | string | one of | Kontablo node UUID (as returned by `resolve_account`). |

```jsonc
// request
{ "account_id": "asset.current.cash" }
// response
{
  "found": true,
  "kontablo_id": "asset.current.cash",
  "kontablo_uuid": "00000000-0000-4000-8000-000000000101",
  "label_en": "Cash and Cash Equivalents",
  "nature": "debit", "statement": "balance_sheet",
  "local_codes": { "mx": "101", "co": "1105", "pa": "1.1.01", "...": "..." }
}
// not found -> { "found": false, "error": "account 'nope' not found" }
```

### 3. `validate_balance_sheet`

Check the double-entry identity Σdebits − Σcredits == 0.

| Param | Type | Required | Description |
|---|---|---|---|
| `entries` | array of `{local_code?, local_name?, debit?, credit?}` | ✅ | Trial-balance rows. Amounts must be finite; negatives allowed. |

```jsonc
// request
{ "entries": [ { "local_code": "572", "debit": 100 },
               { "local_code": "100", "credit": 100 } ] }
// response
{ "is_valid": true, "total_debits": 100.0, "total_credits": 100.0,
  "balance_difference": 0.0, "errors": [] }
```

When unbalanced, `errors` carries `{"code": "UNBALANCED", ...}`; when the totals
overflow to a non-finite value, `{"code": "NON_FINITE_TOTAL", ...}` and the
numeric fields are `null` (never `inf`/`NaN`).

### 4. `consolidate_trial_balances`

Consolidate subsidiaries to USD with explicit intercompany elimination.

| Param | Type | Required | Description |
|---|---|---|---|
| `subsidiaries` | array of subsidiary | ✅ | Each: `subsidiary_id`, `jurisdiction`, `currency`, `entries[]`, optional `fx_rate_to_usd` (+ `fx_rate_as_of`, `fx_rate_note`). |
| `eliminations` | array | – | Each: `from_subsidiary`, `from_kontablo_id`, `to_subsidiary`, `to_kontablo_id`, `amount_usd`. |
| `target_currency` | string | – | `"USD"` only in v0.x. |
| `parent_company_id` | string | – | Echoed back. |

A subsidiary is priced by: a manual `fx_rate_to_usd` (> 0) if given, else the
runtime FX provider, else the pinned static table. Every conversion is recorded
in `fx_audit`.

```jsonc
// request (single subsidiary, no elimination)
{ "subsidiaries": [ { "subsidiary_id": "norte-mx", "jurisdiction": "mx",
    "currency": "MXN", "entries": [
      { "local_code": "102", "local_name": "Bancos", "debit": 1724137.93 },
      { "local_code": "201", "local_name": "Proveedores", "credit": 1724137.93 } ] } ] }
// response (abridged)
{ "ok": true, "target_currency": "USD",
  "trial_balance": [
    { "kontablo_id": "asset.current.bank", "debit": 100000.0, "credit": 0.0, "net": 100000.0 },
    { "kontablo_id": "liability.current.payables", "debit": 0.0, "credit": 100000.0, "net": -100000.0 } ],
  "eliminations_applied": 0, "balanced": true, "balance_difference": 0.0,
  "escalations": [],
  "fx_audit": [ { "subsidiary_id": "norte-mx", "currency": "MXN",
    "usd_per_unit": 0.058, "source": "static-pinned", "mode": "static",
    "as_of": null, "note": null } ],
  "warnings": [] }
```

To eliminate a parent receivable against a subsidiary payable, add
`{"from_subsidiary":"iberica-es","from_kontablo_id":"asset.current.receivables",`
`"to_subsidiary":"norte-mx","to_kontablo_id":"liability.current.payables","amount_usd":100000}`.
Lines that fail to resolve appear in `escalations`; an unsupported currency
returns `{"ok": false, "error": "..."}`.

### 5. `list_jurisdictions`

List coverage from the 195-jurisdiction manifest.

| Param | Type | Required | Description |
|---|---|---|---|
| `region` | string | – | e.g. `"Africa"`, `"Europe"` (case-insensitive). |
| `mapping_mode` | string | – | `"statutory_chart"` or `"ifrs_direct"`. |
| `tier1_only` | bool | – | Only jurisdictions with verified Tier-1 codes. |

```jsonc
// request
{ "tier1_only": true }
// response
{ "summary": { "total": 195, "statutory_chart": 60, "ifrs_direct": 135,
               "tier1_codes_available": 56 },
  "count_returned": 56,
  "jurisdictions": [ { "iso": "dz", "name": "Algeria", "region": "Africa",
                       "mapping_mode": "statutory_chart",
                       "tier1_codes_available": true, "...": "..." } ],
  "metadata": { "...": "..." } }
```

## Error model — two distinct response patterns

Agents should branch on both:

1. **Protocol error (`isError: true` / a raised `ToolError`).** The request
   violated the tool *contract*: a missing required field, a wrong type, a
   non-finite amount, or an invalid manual FX rate (`<= 0`). The message names
   the offending field. The server stays alive — fix the call and retry.
2. **In-band domain result.** The call was well-formed but the *accounting*
   answer is "no": `resolve_account` → `resolved: false` (escalate to a human;
   do not invent a UUID); `get_account` → `found: false`; `consolidate_trial_balances`
   → `ok: false` (e.g. unsupported currency) or a populated `escalations` /
   `warnings` array. These are normal outcomes, not failures.

Determinism guarantee (principle #5): the same input always yields byte-identical
output, so an agent can cache and reason about results safely.

## Robustness / input validation

For Kontablo to be a dependable interface for the agentic economy, a malformed
agent request must fail cleanly — never silently corrupt an accounting result.
The tool inputs are validated at the boundary (Pydantic + explicit checks):

- **Monetary amounts must be finite.** `NaN`/`±Infinity` debits, credits, and
  elimination amounts are rejected — a `NaN` would defeat the double-entry check
  (`abs(NaN) > tol` is `False`, so a `NaN` "balances") and is not valid JSON on
  the wire. A finite-input sum that overflows to `±inf` is reported as a
  `NON_FINITE_TOTAL` error, never emitted as a non-finite number.
- **Manual FX rates must be > 0 and finite.** A `0.0` rate would silently zero
  every converted amount; a negative rate would sign-flip them — both are
  rejected before reaching the FX audit trail.
- **`nature` must be `debit`/`credit` (or omitted).** Negative amounts are
  *allowed* (contra entries, reversals); only non-finite values are rejected.
- **Resilience.** Wrong types / missing required fields are rejected with a
  structured error (FastMCP `isError`), and the server stays alive — one bad
  request never takes the session down. Resolution is deterministic: the same
  input always yields byte-identical output (principle #5).

## Test

`tests/mcp/test_mcp_server.py` asserts (not print-only) that every tool returns
the same answers as the engine that backs REST and gRPC, **and** that the input
hardening above holds (non-finite amounts, invalid FX rates, and a malformed
call that the server survives). It runs hermetically (no live FX, no LLM key —
the session forces `KONTABLO_FX_MODE=static`) and exercises each tool both
through its pure `*_impl` function and through the real FastMCP `call_tool`
dispatch.

## License

This is **core** Kontablo (not an open-source-ERP connector), so it is covered by
the repository's **BSL 1.1** — not the Apache 2.0 used for the ERPNext/Odoo
connectors.
