# Kontablo examples — transnational reconciliation

**Kontablo is a graph-based, UUID-keyed universal accounting ontology.** These
examples show it doing the thing it exists to do: take two companies whose books
live in two *different* national charts of accounts, map both to one universal
UUID ontology, consolidate across currencies, eliminate the intercompany
balance, and produce a single cross-border trial balance that balances.

There are two tiers, in increasing realism. Both run the **same**
`core.engine.ConsolidationEngine` — the same deterministic `resolve()` path that
backs the validation harness, the REST API, and the gRPC server — so they
produce the identical reconciled result.

## Tier 1 — self-contained (zero dependencies)

```bash
python examples/transnational_reconciliation.py
```

Reconciles a Spanish parent (PGC) and a Mexican subsidiary (SAT) from synthetic,
balanced trial balances held in the script. No Docker, no network, no API keys.
This is the fastest way to see the pipeline end to end.

- Parent: *Ibérica Manufactura, S.A.* — Spain, PGC, EUR
- Subsidiary: *Manufactura del Norte, S.A. de C.V.* — Mexico, SAT, MXN (100% owned)
- One intercompany balance (parent receivable ↔ subsidiary payable), eliminated.

Tested by `tests/examples/test_transnational_reconciliation.py`.

## Tier 2 — two real open-source ERPs (ERPNext + Odoo)

```bash
cd examples/two_erp_reconciliation
python run_reconciliation.py                # --source fixtures (default, offline)
```

Same group, but each subsidiary's books live in a real ERP: the parent in
**ERPNext** and the subsidiary in **Odoo**, pulled through the Apache-2.0
connectors (`connectors/erpnext`, `connectors/odoo`). It runs in two modes:

- `--source fixtures` (default): reads committed trial-balance exports — fully
  deterministic, no Docker. This is what CI asserts.
- `--source live`: pulls from running ERPNext + Odoo containers (`docker compose
  up` + seeding). See `two_erp_reconciliation/README.md`.

Tested by `tests/examples/test_two_erp_reconciliation.py`, which also asserts the
Tier-2 fixtures output matches Tier-1 **line for line**.

## Honesty note (per the project's epistemic standards)

The **amounts** in every example are synthetic trial balances, balanced by
construction — they are not real-world ledger data. The **local codes** (PGC
`430`, SAT `201`, …) are real statutory codes drawn from the committed Kontablo
ontology, so the Tier-1 exact-lookup resolutions are genuine. No step calls an
LLM: every mapping is a graph lookup or a deterministic keyword rule, and every
intercompany elimination keys on explicit structured fields, never on free text.
