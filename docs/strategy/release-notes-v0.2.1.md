# Kontablo v0.2.1 — Agent-native layer goes real

This is a **minor release** (backward-compatible new features) over
[v0.1.1](release-notes-v0.1.0.md). The headline: the **agent-native layer the
preprint describes is now implemented in code, not just asserted** — Kontablo
ships a real MCP server, and all three machine-consumable faces (REST, gRPC, MCP)
are hardened against malformed input behind one shared invariant.

> **Why v0.2.1 and not v0.2.0?** The identical content was first tagged as
> `v0.2.0`, but that tag was created from a stale local checkout (it pointed at a
> pre-MCP commit) and GitHub's immutable-releases feature permanently burned the
> `v0.2.0` name. `v0.2.1` is the first *valid* public release of this feature set;
> `v0.2.0` is retracted.

No headline numbers changed: still **195** sovereign jurisdictions, **60**
statutory-chart overlays (**56** exercised against primary-source-cited charts),
and the **75 entities / 68 jurisdictions / 97.3% deterministic** validation. The
claims-evidence CI gate reproduces them byte-for-byte.

## What's new since v0.1.1

### Agent-native: MCP deterministic core (the big one)
- New **MCP (Model Context Protocol) server** (`api/mcp/`, official `mcp`/FastMCP
  SDK, stdio transport) exposing five **deterministic** tools over the *same*
  `core.harness` + `core.engine` brain that backs REST and gRPC — no logic
  duplicated:
  - `resolve_account` — local statutory account → universal node UUID (Tier-1
    exact + Tier-2 multilingual keyword), with tier, confidence, and
    Co-responsibility boundary flags.
  - `get_account` — ontology node by id **or** UUID.
  - `validate_balance_sheet` — double-entry identity check.
  - `consolidate_trial_balances` — multi-subsidiary consolidation with
    intercompany elimination and a per-entity FX audit trail.
  - `list_jurisdictions` — coverage manifest (195 / 60 / 56).
- The **Tier-3 semantic/LLM fallback is deliberately not exposed** — exposing a
  stochastic capability as deterministic would misrepresent confidence;
  unresolved mappings escalate (`resolved:false`) instead of guessing, matching
  how gRPC leaves LLM RPCs `UNIMPLEMENTED`.
- Every tool and **every parameter is self-describing** in its JSON schema (what
  an agent actually reads), enforced by a test.
- Runnable demo (`python -m api.mcp.demo`) drives the server over real stdio with
  the official MCP client.

### Robustness across all three faces
- One shared definition of a valid monetary amount,
  `core/harness/validation.py` (`ensure_finite` / `ensure_positive_finite` /
  `is_finite_number`), now backs REST, gRPC, **and** MCP so they cannot disagree
  at the boundary.
- Malformed-but-parseable requests now fail **cleanly** instead of silently
  corrupting a result or crashing serialization:
  - Non-finite (NaN/±Inf) amounts rejected — a `NaN` would "balance" the
    double-entry check (`abs(NaN) > tol` is `False`) and is invalid JSON.
  - Manual FX rates must be `> 0` and finite (a `0` zeroes every amount; a
    negative sign-flips them).
  - Finite-sum overflow is surfaced as a clean error, never emitted as `inf`.
  - Rejection is face-appropriate: REST `422`/`400` (with a validation handler
    that scrubs non-finite values so the error body itself serializes), gRPC
    `INVALID_ARGUMENT`, MCP structured `ToolError` (server stays alive).
- The deterministic REST `/consolidation` now also reports
  `balanced` / `balance_difference` / totals (parity with gRPC and MCP).
- Negative amounts remain valid everywhere (contra entries, reversals).

### Documentation
- New `api/README.md` ties the three faces to one engine, the
  deterministic-vs-LLM line, the shared robustness contract, and the two response
  patterns (transport/contract error vs in-band domain "no").
- `api/mcp/README.md` full per-tool reference with verified request/response
  examples and an explicit error model.
- README now links the project website
  (https://christianluciani.github.io/accounting-esperanto/) and a long-form
  overview essay.

### Tests
- `tests/mcp/test_mcp_server.py` (deterministic tools + input-hardening +
  self-describing-schema gate), `tests/test_validation.py` (shared invariants),
  `tests/api/test_robustness.py` (REST returns 4xx, never a 500), and gRPC
  `INVALID_ARGUMENT` regressions. Full suite green; claims-evidence numbers
  unchanged.

## Not in this release (honest scope)
- **A2A and AP2 remain asserted-but-unimplemented** — MCP is the only
  agent-native face with a real deterministic core. Described as "deterministic
  tools implemented, Tier-3/LLM tools planned"; **not** full feature parity with
  REST.
- Post-quantum signatures (ML-DSA per NIST FIPS 204) on spec version hashes —
  still roadmap.
- Production NetSuite/SAP connectors — reserved for Praxia (commercial), not
  open-core.

## License
**Core**: Business Source License 1.1 — converts to Apache 2.0 on **2030-06-18**.
**ERPNext/Odoo connectors**: Apache 2.0. See `LICENSE` and `LICENSING.md`.

## Citation
Concept DOI (always resolves to the latest version):
[10.5281/zenodo.20738795](https://doi.org/10.5281/zenodo.20738795) ·
SSRN [abstract 6960598](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6960598).

## Release checklist (owner-gated — Christian)
The code/docs are ready on `main`. Because `git push` of a tag is blocked by the
repo ruleset (immutable releases), create the tag **through the Release UI**, not
the CLI:
1. GitHub → Releases → **Draft a new release**.
2. **Choose a tag** → type `v0.2.1` → "Create new tag: v0.2.1 on publish".
3. **Target:** `main` (server-side tip — guarantees the correct commit).
4. Title `Kontablo v0.2.1 — Agent-native MCP layer`; body = this file.
5. **Publish** → Zenodo auto-archives and mints a **v0.2.1 version DOI** under the
   concept DOI. Add that version DOI to `CITATION.cff` `identifiers` afterward.
6. Optional coordinated posts per the launch playbook.
