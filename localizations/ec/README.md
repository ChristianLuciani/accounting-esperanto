# Ecuador (`ec`) localization

**Status: verified against primary source (2026-07-16).** Superseded a
`0.1.0-draft` that hand-picked 13 accounts out of the official chart's 721.

## Files

| File | What it is | Regenerate with |
|---|---|---|
| `supercias_official_chart.yaml` | Verbatim transcription of the official Supercias "Plan de Cuentas" (all 4 mandated NIIF statements) | `pdftotext -layout <PDF> chart.txt && python3 scripts/coa_fidelity/parse_official_chart.py --input chart.txt --jurisdiction ec --source-url "https://appscvsmovil.supercias.gob.ec/balances/PLAN_CUENTAS.pdf" --authority "Superintendencia de Companias, Valores y Seguros (Ecuador)" --out localizations/ec/supercias_official_chart.yaml` |
| `supercias_mapping.yaml` | Every official code classified onto a Kontablo Level-3 node (or flagged `needs_review` / `is_statement_caption`) | `python3 scripts/coa_fidelity/map_official_chart.py --official localizations/ec/supercias_official_chart.yaml --jurisdiction ec --out localizations/ec/supercias_mapping.yaml` |
| `default_tree_ec.json` | ERPNext-importable chart-of-accounts tree, generated from the mapping | `python3 scripts/coa_fidelity/build_erpnext_tree.py --mapping localizations/ec/supercias_mapping.yaml --jurisdiction ec --out localizations/ec/default_tree_ec.json` |

## Source

Superintendencia de Companias, Valores y Seguros (Ecuador), "Plan de Cuentas"
(NIIF presentation chart: Estado de Situacion Financiera, Estado de Resultado
Integral, Estado de Flujos de Efectivo, Estado de Cambios en el Patrimonio).
https://appscvsmovil.supercias.gob.ec/balances/PLAN_CUENTAS.pdf

## Coverage honesty

- 721 official codes transcribed verbatim; 0 hand-picked.
- 540 classified onto an existing Kontablo Level-3 node (many-to-one is by
  design — see `core/schemas/level3_accounts.yaml`'s "graph, not tree"
  principle).
- 116 are statement-presentation captions (cash-flow reconciliation lines,
  equity-changes movement lines) — not postable ledger accounts, correctly
  excluded from the ERPNext tree.
- 23 are aggregate/header rows (have more granular children in this same
  chart) — not independently postable.
- 42 are genuine `needs_review`: leaf accounts with no existing Kontablo
  Level-3 node fitting them (e.g. IAS 41 biological assets — the ontology's
  `asset.noncurrent.biological` node is still `PLANNED` status with no UUID;
  long-term related-party receivables; investment property). These are
  honest ontology gaps, not silent guesses. Tracked in
  `research/coa_fidelity/STATUS.yaml`.
- `liability.current.vat_output` deliberately has **no** `ec` local_code:
  this presentation-level chart has no distinct output-VAT leaf (IVA payable
  folds into `2010701`, a broader tax-authority bucket). Claiming a code
  here would overstate precision the source doesn't have.
