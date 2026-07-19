# Mexico (`mx`) localization

**Status: verified against primary source (2026-07-16, corrected 2026-07-18 after review).** Superseded a `0.1.0-draft` hand-picked subset (14 codes) with a complete official chart transcription.

## Files

| File | What it is | Regenerate with |
|---|---|---|
| `sat_official_chart.yaml` | Verbatim transcription of the official SAT Código Agrupador (Anexo 24 RMF 2026, all 1,079 codes) | `pdftotext -layout <PDF> chart.txt && python3 scripts/coa_fidelity/parse_sat_codigo_agrupador.py --input chart.txt --source-url "<PDF URL>" --out localizations/mx/sat_official_chart.yaml` |
| `sat_mapping.yaml` | Every official code classified onto a Kontablo Level-3 node (or flagged `needs_review` / `is_statement_caption` / `is_aggregate`) | `python3 scripts/coa_fidelity/map_official_chart.py --official localizations/mx/sat_official_chart.yaml --jurisdiction mx --out localizations/mx/sat_mapping.yaml` |
| `default_tree_mx.json` | ERPNext-importable chart-of-accounts tree, generated from the mapping | `python3 scripts/coa_fidelity/build_erpnext_tree.py --mapping localizations/mx/sat_mapping.yaml --jurisdiction mx --out localizations/mx/default_tree_mx.json` |

## Source

Servicio de Administración Tributaria (SAT, Mexico), "Anexo 24 de la Resolución Miscelánea Fiscal para 2026" (Código Agrupador de Cuentas).
Published 13 January 2026 in the Official Gazette (*Diario Oficial de la Federación*).
https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/documentos2026/rmf/anexos/Anexo_24_RMF2026-13012026.pdf

**Authority:** Servicio de Administración Tributaria (SAT)
**Document:** Anexo 24 of Resolución Miscelánea Fiscal para 2026
**Published:** 13 January 2026 (DOF)
**Scope:** Código Agrupador (grouping codes) for electronic accounting submissions in Mexico

## Coverage honesty

- 1,079 official codes transcribed verbatim; 0 hand-picked.
- 818 classified onto an existing Kontablo Level-3 node (many-to-one by design — see `core/schemas/level3_accounts.yaml`'s "graph, not tree" principle).
- 52 are statement/order-account captions — the entire 800–899 "Cuentas de orden" block (UFIN, CUFIN, CUFINRE, CUCA, inflation adjustments, tax-loss carryforwards, consigned merchandise, import VAT/IEPS credit facilities). These are genuinely off-balance-sheet memorandum accounts, never postable ledger accounts, and are correctly excluded from the ERPNext tree.
- 48 are aggregate/header rows (have more granular children in the same chart, or bundle heterogeneous content that does not share one Level-3 node) — not independently postable.
- 161 are genuine `needs_review`: leaf codes with no existing Kontablo Level-3 node fitting them, or with a fit deliberately withheld because forcing it would distort the accounting meaning. These are honest ontology/methodology gaps, not silent guesses:
  - **Contra-accounts** (allowances, obsolescence/impairment reserves, accumulated depreciation/amortization, sales/purchase returns): e.g. `108` Estimación de cuentas incobrables, `116` Estimación de inventarios obsoletos, `171`/`172`/`183`/`189` accumulated depreciation/amortization/impairment, `402` and `503` (sales/purchase returns). Kontablo has no dedicated contra-asset/contra-revenue/contra-expense node yet; merging these into the gross node they offset would distort gross-vs-net presentation (same convention as the `ec` and `_syscohada` rounds).
  - **Mexican cash-flow-basis VAT nuances**: `119` Impuestos acreditables por pagar (VAT/IEPS invoiced but not yet paid, so not yet creditable under LIVA's cash-flow rule — a different concept from the genuinely creditable `118` Impuestos acreditables pagados) and `209` Impuestos trasladados no cobrados (output tax charged but not yet collected, so not yet owed to the tax authority).
  - **Legacy Mexican-GAAP deferred-charge concepts** with no clean IFRS-anchored equivalent: Gastos diferidos, Gastos pre-operativos, Gastos de organización, Gastos de instalación (codes `173`–`182` family).
  - **Missing current/noncurrent distinction in the ontology**: `185` Impuestos diferidos (deferred tax ASSET — only a deferred-tax *liability* node exists), `186` Cuentas y documentos por cobrar a largo plazo (long-term receivables — only a *current* receivables node exists), `253` Cobros anticipados a largo plazo (long-term deferred revenue — only a *current* deferred-revenue node exists), `255` Pasivos por beneficios a los empleados a largo plazo. Forcing these into the current/liability-side node that happens to share a name would misstate current vs. noncurrent.
  - **No dedicated node**: `606` Facilidades administrativas fiscales, `607` Participación de los trabajadores en las utilidades (PTU expense), `608`/`609` Participación en resultados de subsidiarias/asociadas, `612` Gastos no deducibles para CUFIN, `703` Otros gastos (losses on PP&E/share disposal), `505` Costo de activo fijo, `184` Depósitos en garantía, `191`/`218`/`256`/`260` generic "other" buckets, `204`/`254` generic financial-instrument liabilities, `217` Pagos realizados por cuenta de terceros, `213.06` Derechos por pagar, `252.15`/`252.16` long-term dividends payable, `158` Activos biológicos (`asset.noncurrent.biological` is `PLANNED` with no UUID yet, same gap `ec` hit).

  Tracked in `research/coa_fidelity/STATUS.yaml`.

### Corrections applied 2026-07-18 (post-review)

An initial pass force-mapped several codes onto the nearest plausible node rather than verifying against the actual parsed chart, and reused code-meaning assumptions from the stale `0.1.0-draft` (whose numbering does not match the current SAT chart). A review caught and corrected:

- Contra-asset accounts (`108`, `116`, and the nested exception `109.21`) were merged into the gross asset node instead of `needs_review`.
- `119` (not-yet-creditable tax) was force-mapped into `asset.current.vat_input` alongside the genuinely-creditable `118`.
- Systemic liability mis-mapping in the `201`–`218` range: e.g. `211` (a payroll/social-security provision) had been mapped to `liability.current.tax`; `203`/`206` (deferred revenue — "cobrado por anticipado" / customer advances) had been mapped to `liability.current.accrued`.
- `303` (Reserva legal) and `304` (Resultado de ejercicios anteriores) had `equity.reserves`/`equity.retained` swapped.
- `701` (Gastos financieros, an expense) and `703` (Otros gastos, an expense) were mapped to `revenue.other` — backwards.
- The `nature` field was `null` for the entire 600/700/800 series because the classification script's nature heuristic was written for a different jurisdiction's numbering scheme; and even after fixing that, SAT's own 700 series is not nature-uniform (`701`/`703` are Debit-nature expense codes, `702`/`704` are Credit-nature income codes despite sharing the same leading digit) — `parse_sat_codigo_agrupador.py`'s `determine_nature()` now distinguishes them explicitly.
- The 800–899 Cuentas de orden block was not being recognized as non-postable (the caption-detection logic only knew EC's "9" order-account prefix) — `classify()` is now jurisdiction-aware (`ORDER_ACCOUNT_PREFIX = {"ec": "9", "mx": "8"}`).
- A dead `SUBTOTAL_PREFIXES_MX` constant existed but was never wired into the classifier; deleted. The EC-specific `SUBTOTAL_PREFIXES` heuristic was scoped to `jurisdiction == "ec"` so it can no longer leak into MX's classification (it was silently mislabeling MX leaves like `606`/`607`/`701`/`703` as statement captions instead of the correct `needs_review`/`is_aggregate`).

Full detail in `scripts/coa_fidelity/map_official_chart.py`'s `MX_RULES` comments, which cite the verified source name for every mapping decision.

### Dataset notes

The SAT Código Agrupador (Anexo 24) is not a GAAP chart of accounts; it is a tax-compliance grouping code system. Every Mexican entity must map its internal chart to these SAT codes for electronic accounting (*Contabilidad Electrónica*) submission. The codes reflect Mexico's tax administration categories, not IFRS dimensions. Verified top-level structure (per the actual parsed chart, not assumed):

- Codes 100–191: **Activo** (Assets)
- Codes 200–260: **Pasivo** (Liabilities)
- Codes 300–306: **Capital contable** (Equity)
- Codes 400–403: **Ingresos** (Revenue)
- Codes 500–505: **Costos** (Cost of Sales)
- Codes 600–614: **Gastos** (Operating Expenses)
- Codes 700–704: **Resultado integral de financiamiento y otros** (Financial result and other income/expense — a **mixed** section: 701 and 703 are expense codes, 702 and 704 are income codes, despite sharing the "7" leading digit)
- Codes 800–899: **Cuentas de orden** (Order/Memorandum accounts — off-balance-sheet, non-postable)

There is no 900–999 range in the actual chart.

The classification onto Kontablo Level-3 follows this hierarchy without forcing a GAAP-aligned structure; many "needs_review" entries are SAT artifacts (cash-flow-basis VAT timing, legacy Mexican-GAAP deferred charges, current/noncurrent splits the ontology doesn't yet support) that do not map cleanly to an IFRS-anchored universal ontology, not parsing failures.

### ERPNext tree

The generated `default_tree_mx.json` contains 898 postable leaf accounts (the non-aggregate, non-caption rows). This tree may be imported into ERPNext for Mexican entities. Note: the tree preserves the SAT code hierarchy; local companies often add sub-accounts under these nodes for internal reporting.

## Related

- **Kontablo Level-3 ontology:** `core/schemas/level3_accounts.yaml`
- **Sweep methodology:** `research/coa_fidelity/README.md`
- **Sweep status:** `research/coa_fidelity/STATUS.yaml`
