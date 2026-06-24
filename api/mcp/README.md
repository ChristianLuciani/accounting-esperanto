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

## Test

`tests/mcp/test_mcp_server.py` asserts (not print-only) that every tool returns
the same answers as the engine that backs REST and gRPC. It runs hermetically
(no live FX, no LLM key — the session forces `KONTABLO_FX_MODE=static`) and
exercises each tool both through its pure `*_impl` function and through the real
FastMCP `call_tool` dispatch.

## License

This is **core** Kontablo (not an open-source-ERP connector), so it is covered by
the repository's **BSL 1.1** — not the Apache 2.0 used for the ERPNext/Odoo
connectors.
