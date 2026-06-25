# Kontablo API — three machine-consumable faces, one engine

Kontablo's data layer is **API-first**; on top of it sits an **agent-native**
layer (architectural principle #4). All faces below are thin adapters over the
*same* deterministic engine (`core.harness` + `core.engine`) — there is one
mapping/consolidation brain, never duplicated logic.

| Face | Path | Transport | Audience | Status |
|---|---|---|---|---|
| **REST** | [`api/src`](src) (`api.src.main:app`) | HTTP/JSON (FastAPI) | ERPs, banks, any HTTP client | ✅ canonical, full |
| **gRPC** | [`api/grpc`](grpc) | HTTP/2 + protobuf | low-latency / typed clients | ✅ deterministic RPCs; LLM RPCs `UNIMPLEMENTED` |
| **MCP** | [`api/mcp`](mcp) | stdio (Model Context Protocol) | LLM agents | ✅ deterministic tools; Tier-3/LLM planned |

There is also [`api/rest`](rest) — a separate **LLM-powered** mapping microSaaS
(multi-agent), distinct from the deterministic `api/src` REST service above.

An ERP/bank consumes REST or gRPC directly; an autonomous agent consumes MCP.
Neither is subordinate. See each subdirectory's README for run instructions and
the full tool/endpoint reference: [REST is self-documenting at `/docs`](src/main.py),
[gRPC](grpc/README.md), [MCP](mcp/README.md).

## Deterministic vs. LLM (the honesty line)

Account **mapping**, **ontology queries**, **consolidation** (with intercompany
elimination), and **balance validation** are deterministic — graph lookup, rules,
arithmetic — and identical across all three faces. The **only** stochastic
surface is transaction *classification* from free text (REST
`/classification/transaction`); it is LLM-backed, requires a provider key, and is
never silently invoked by the gRPC or MCP deterministic surfaces (they leave it
`UNIMPLEMENTED` / unexposed rather than faking determinism).

## Shared input-robustness contract

A malformed-but-parseable request must fail **cleanly** and never silently
corrupt an accounting result. One definition of "valid monetary amount" lives in
[`core/harness/validation.py`](../core/harness/validation.py) and backs all three
faces:

| Rule | Why | REST | gRPC | MCP |
|---|---|---|---|---|
| Amounts (debit/credit/elim) must be **finite** | a `NaN` "balances" (`abs(NaN) > tol` is `False`) and breaks JSON | `422` | `INVALID_ARGUMENT` | `ToolError` |
| Manual FX rate must be **> 0 and finite** | `0` zeroes amounts; `< 0` sign-flips them | `422` | `INVALID_ARGUMENT` | `ToolError` |
| A finite-sum **overflow** to ±inf | never emit a non-finite figure | `400` | error | `NON_FINITE_TOTAL` |
| Negative amounts | legitimate (contra entries/reversals) | ✅ allowed | ✅ | ✅ |

Notes:
- The REST service installs a `RequestValidationError` handler that scrubs
  non-finite values from the 422 body — otherwise FastAPI's input-echo would
  itself crash serialization (Starlette renders with `allow_nan=False`) and turn
  a clean 422 into an opaque 500.
- In gRPC/proto3 a `0.0` scalar is indistinguishable from "unset", so a `0`
  `fx_rate_to_target` correctly falls back to the FX provider rather than being
  rejected; a negative rate is rejected.

## Two response patterns (branch on both)

1. **Transport/contract error** — `4xx` (REST), `INVALID_ARGUMENT`/`NOT_FOUND`
   (gRPC), `ToolError` (MCP): the request was malformed. Fix and retry; the
   server stays alive.
2. **In-band domain result** — a well-formed call whose *accounting* answer is
   "no": an unresolved mapping escalates (`resolved:false` / `match_method:
   "not_found"`) rather than guessing; an unpriceable currency is a clean error.
   These are normal outcomes.

## Determinism guarantee

Every deterministic surface returns byte-identical output for identical input
(principle #5), so results are cacheable and reproducible — the same property the
CI claims-evidence gate relies on.
