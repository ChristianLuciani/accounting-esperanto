# Architecture Decision Record: ADR-016
# Title: Lossless Translation — Mapping Provenance, Preserved Local Structure, Multi-Lens Graph, and the Loss Ledger
# Date: 2026-07-20
# Status: ACCEPTED (implemented; v0.3.0 line)

## Context

An audit of the implementation against the project's own claims found that the
"graph, not tree" principle (#1) and the paper's multi-dimensional λ-labeled
property graph (`sections/ontology.tex`) existed as prose, not as data:

- `core/schemas/level3_accounts.yaml` was a single-parent tree (`parent`, one
  string) with a flat `local_codes` overlay. `metadata.graph_model: true` was
  aspirational. The only multi-parent field ever defined
  (`account.schema.json` → `relations.also_rolls_up_to`) was used by **zero**
  data files and never validated.
- The 199 localization files projected each local code onto exactly one
  Kontablo UUID, discarding the local chart's own hierarchy (only an orphan
  `level` integer survived) and every analytical dimension (the
  `disaggregation_dimension: "geography"` seed in the legacy `mx_sat` demo was
  dead code).
- The engine's `ResolvedEntry` kept per-entry provenance internally, but the
  API boundary discarded it: REST consolidation aggregated by `kontablo_id`
  and dropped local code/tier/confidence; gRPC's `ConsolidationResponse`
  carried no FX audit at all; no surface could answer "which local rows made
  this consolidated figure?".

ADR-013 already accepted "controlled information loss" for tree-based ERP
imports and noted the local code "must be stored as mapping provenance" — but
no schema or code implemented that storage. The preprint's
`mathematical_foundations.tex` formalizes the universal→local return trip as
lossy by construction (the H¹ obstruction). The owner's directive (2026-07):
Kontablo is a financial-transparency protocol — **no information loss may be
silent; the system must be 100% auditable and traceable.**

## Decision

Distinguish three losses and treat each honestly:

| Loss | Nature | Resolution |
|---|---|---|
| **L1** — entry lineage dropped at the API boundary | accidental | eliminated (100%) |
| **L2** — local chart structure dropped by the mapping files | accidental | eliminated (additive schema v2) |
| **L3** — semantic coarsening (N local concepts → 1 Level-3 node) | inherent (Level-3 is deliberately coarser) | not bijectively eliminable; made **explicit, typed, and reconstructible** |

The projection cannot be a bijection, but the **system** can be lossless: store
the *morphism* (the annotated mapping plus the intact source), not just the
image. The universal view becomes a query over preserved data, never a
destructive transform. Concretely:

1. **`MappingQuote` (Phase A).** Every resolution carries provenance mirroring
   the existing `FXQuote` pattern: local code/name, jurisdiction, tier, exact
   deterministic `rule_id` (`tier1:<jur>:<code>` / `tier2:<node>:<keyword>`),
   confidence, timestamp. `ResolvedEntry` also keeps the original local-currency
   amounts (rounded USD figures are not invertible through the FX rate).
   Surfaced on every face: REST/gRPC/MCP consolidation responses expose a
   per-entry `mapping_audit` (gRPC additionally gained the previously missing
   `fx_audit`), consolidated lines expose their fiber size (`source_entries`),
   and `ConsolidationResult.lineage()` reconstructs every line from its fiber.

2. **Localization schema v2 (Phase B).** First formal JSON Schema for the
   mapping files (`core/schemas/localization_mapping.schema.json`), adding
   OPTIONAL fields: `local_parent` (the local chart's own tree edge),
   `local_hierarchy` (header/class nodes: SKR04 Kontenklassen, SPED groupings),
   `facets` (named analytical dimensions the projection flattens — geography,
   tax regime, VAT rate, contra polarity), and `aggregation_group` (declared
   N:1 fibers). Exemplars: mx (SAT Anexo 24), br (SPED), de (SKR04); the
   remaining ~196 files are an explicit incremental backlog, NOT rewritten
   wholesale.

3. **Multi-lens graph (Phase C).** Level-3 nodes carry `groupings` — parallel
   rollup lenses over the same UUIDs. The primary `ifrs` lens is composed from
   `parent` (single source of truth); the first additional lens is `cash_flow`.
   `rollup(accounts, lens)` partitions the graph under any lens;
   `node_fiber()` answers the inverse question (which local codes collapse
   into a node), enriched per jurisdiction with the v2 structure. Exposed as
   the MCP tool `get_node_fiber` and REST `GET /accounts/{id}/fiber`.
   `also_rolls_up_to` gained the referential-integrity test it never had; no
   fabricated data was added to the 3-node spec demo.

4. **The loss ledger (Phase D).** Standing invariant: *the pipeline may fail
   to translate, but it may never lose.* Every non-translation is a typed,
   countable record — ontology code collisions, non-code placeholders,
   escalated entries, CRA flags, skipped eliminations. `scripts/roundtrip_audit.py`
   proves it on the exact dataset of the published validation run: 441 entries
   in → 441 resolved out, every local trial balance reconstructed
   byte-for-byte from lineage alone, every consolidated line equal to the sum
   of its fiber, `silent_losses == 0`. CI runs it as a hard gate next to the
   claims-evidence gate.

## Constraints honored

- **All changes additive.** `resolve()` behavior is byte-identical
  (`resolve_with_rule()` wraps it); the pinned validation numbers
  (195/60/56/75/68/97.3/25/4) regenerate exactly; no citable surface changed.
- The validation harness still prices with the pinned FX table only.
- The legacy `mx_sat` list-format file remains frozen.

## Consequences

- Every consolidated figure is now reconstructible down to its source rows
  through committed, deterministic code — the repo embodies the auditability
  the paper claims, at the entry level.
- L3 remains non-bijective *by design*; the honest formulation is: the
  projection is lossy, the system is not. The paper's λ-claims vs. data gap
  (facet families F_fis/F_fun, consolidation role K) is now partially closed
  (facets, groupings) and the remainder must be reconciled in the next paper
  version (v1.10+) — tracked separately, NOT edited retroactively.
- Facet/hierarchy population across the remaining localization files is a
  long-tail data task; the schema, loaders, tests, and three exemplars define
  the pattern.
- New claims-evidence row: "0 silent losses / exact reconstruction on the
  75-entity validation dataset" ↔ `python scripts/roundtrip_audit.py` →
  `research/experiments/roundtrip_audit/results.json`.

## Verification

```bash
python -m pytest tests/ connectors/          # full suite
python scripts/mass_consolidation_v2.py      # published numbers unchanged
python scripts/roundtrip_audit.py            # silent_losses == 0, exit 0
```
