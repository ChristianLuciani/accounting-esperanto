# Consolidation v1 — the "initial run" artifact (10 entities, 9 countries)

This directory makes the *initial run* described in the preprint's evaluation
section regenerable, per the project's claims–evidence rule ("no claim without
a command").

## What is this data?

**Synthetic trial balances, formatted as source-ERP exports. Not real company
data.** Each of the 10 fixture files in `fixtures/` is written in the
trial-balance CSV export layout of one of four ERPs — ERPNext, Zoho Books,
Odoo, SAP Business One — but no ledger here was ever exported from a live ERP
instance. The entities, names, and amounts are synthetic; the statutory
account codes are real codes from the respective national charts (SAT código
agrupador, SPED-style Brazilian hierarchy, PCG, PUC, VAS Circular 200, SOCPA
numbering).

## Regenerate

```bash
python scripts/consolidation_v1_initial_run.py
```

Deterministic, no LLM/API dependency, no API keys. The script (a) writes the
fixtures, (b) ingests them back through four format-specific parsers, (c)
resolves every line through the same deterministic pipeline as
`scripts/mass_consolidation_v2.py` (imported, not duplicated): Tier 1 exact
local-code lookup → Tier 2 multilingual keyword rules → escalation to human
review (CRA). Tier 3 (semantic AI fallback) is **not** exercised, so the run
is 100% reproducible.

## Properties asserted by the script (run fails if violated)

- Every entity's trial balance balances exactly (total debits = total
  credits, in local currency); `equity.retained` is the balancing line.
- The consolidated USD ledger satisfies Assets = Liabilities + Equity +
  (Revenue − Expenses), with escalated lines carried in an explicit suspense
  bucket so the identity is exact.

## Headline numbers (from `results.json`)

| Metric | Value |
|---|---|
| Entities / countries | 10 / 9 (MX×2, BR, FR, PA, EC, CO, VN, NG, SA) |
| Source-ERP export formats | ERPNext, Zoho Books, Odoo, SAP B1 |
| Lines ingested | 131 |
| Tier 1 exact-code | 67 (51.1%) |
| Tier 2 keyword | 56 (42.7%) |
| Escalated to human (CRA) | 8 (6.1%) |
| Deterministic coverage | 93.9% |

Per-jurisdiction pattern (see `results.json → tiers_by_jurisdiction`): Saudi
Arabia escalates 7 of 12 lines (Arabic account names outside the Tier-2
vocabulary, one ontology-carried SOCPA code), while Vietnam resolves 12 of 13
at Tier 1 because the ontology carries the VAS Circular 200 code set — the
committed evidence for the paper's discussion of where deterministic
grounding does and does not substitute for parametric knowledge.

## Files

- `fixtures/` — 10 trial-balance CSVs, one per entity, in its source-ERP layout
- `results.json` — run summary (tier distribution, per-entity balance checks, consolidated USD ledger, identity check)
- `per_entry.csv` — line-level audit trail (entity, local code/name, resolved Kontablo ID, tier, confidence, USD)
