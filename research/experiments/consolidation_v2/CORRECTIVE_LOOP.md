# Corrective Loop Record — Validation-Driven Ontology Correction

> Historical record of a closed corrective feedback loop in Kontablo's
> construction: the validation harness detected latent defects in the ontology
> it was testing, those defects were corrected against primary national
> standards, and re-validation confirmed resolution. Dated 2026-06-08.

## Why this record exists

Kontablo's design thesis is that determinism and machine-verifiability turn a
standard into a self-checking artifact. This episode is the first concrete
instance of that thesis operating on Kontablo *itself*: the consolidation
validation harness (`scripts/mass_consolidation_v2.py`), when run with trial
balances generated from the ontology's own `local_codes`, surfaced
data-quality defects in `core/schemas/level3_accounts.yaml`. We record the loop
end-to-end as part of the project's evolution and audit trail.

## 1. Detection (validation run, pre-fix)

The harness builds a reverse index `(jurisdiction, local_code) -> Kontablo node`
and flags **collisions** — a single national code mapped to two different
universal nodes, which makes Tier-1 exact lookup ambiguous. The run reported:

| Jurisdiction | Code | Collided Kontablo nodes |
|---|---|---|
| MX | `509` | `expense.interest`, `expense.fx_loss` |
| RU | `68.2` | `asset.current.vat_input`, `liability.current.vat_output` |
| VN | `311` | `liability.current.short_term_debt`, `liability.noncurrent.debt` |
| VN | `635` | `expense.interest`, `expense.fx_loss` |

The RU case is the most severe: a single code mapped across the asset/liability
boundary (debit vs credit). The CRA additionally flagged it at runtime as a
nature mismatch — the co-responsibility layer catching a latent ontology defect,
not merely a transaction error.

## 2. Root cause

- **MX `509`**: placeholder/incorrect code. The SAT *código agrupador*
  (Anexo 24) places financial expenses under group **701**, with distinct
  sub-codes for interest and FX loss.
- **RU `68.2`**: input and output VAT were both pointed at the settlement
  account. In the Russian chart (Order 94n), input VAT is a separate account
  (**19**), distinct from VAT settlements (**68-02**).
- **VN `311`**: short- and long-term borrowings were both `311`. Circular
  200/2014 uses **341** for long-term borrowings and finance-lease liabilities.
- **VN `635`**: not a typo but a genuine *granularity mismatch* — VAS account
  635 ("Chi phí tài chính") aggregates interest and FX losses under one
  statutory code, so a single code legitimately corresponds to two Kontablo
  leaves.

## 3. Correction (sources cited)

| Node | Old | New | Source |
|---|---|---|---|
| `expense.interest` (MX) | `509` | `701.04` | SAT Anexo 24 — 701.04 "Intereses a cargo" |
| `expense.fx_loss` (MX) | `509` | `701.01` | SAT Anexo 24 — 701.01 "Pérdida cambiaria" |
| `asset.current.vat_input` (RU) | `68.2` | `19` | Order 94n — account 19 "НДС по приобретенным ценностям" |
| `liability.current.vat_output` (RU) | `68.2` | `68.02` | Order 94n — account 68 sub-2 "Расчеты по НДС" |
| `liability.noncurrent.debt` (VN) | `311` | `341` | Circular 200/2014 — account 341 long-term borrowings |
| `expense.fx_loss` (VN) | `635` | *(removed)* | VAS 635 has no distinct FX-loss leaf; `635` retained only on `expense.interest` (dominant component), documented in the YAML note |

Primary sources consulted:
- SAT, *Código agrupador de cuentas* (Anexo 24, RMF):
  http://omawww.sat.gob.mx/fichas_tematicas/buzon_tributario/Documents/codigo_agrupador.pdf
- РФ, План счетов (Приказ Минфина 94н), accounts 19 and 68:
  https://www.consultant.ru/document/cons_doc_LAW_66752/
- Vietnam, Circular 200/2014/TT-BTC (accounts 341, 635):
  https://vietnamlawenglish.blogspot.com/2015/05/no-2002014tt-btc.html

## 4. Re-validation (post-fix)

Re-running the harness after the corrections:

```
ONTOLOGY DEFECTS SURFACED: 0 local-code collision(s)
```

The loop is closed. The same run was then expanded for breadth (see below).

## 5. Expanded validation (final state, 2026-06-08)

Coverage is now recorded in a 195-jurisdiction manifest
(`core/schemas/jurisdiction_coverage.yaml`) and statutory chart families
(`core/schemas/chart_families.yaml`, e.g. SYSCOHADA for the 17 OHADA states).

| Metric | Result |
|---|---|
| Sovereign states in manifest | 195 (193 UN + Holy See + Palestine) |
| — universal IFRS-anchor layer | 195 |
| — statutory-chart overlay | 67 (JP, KR, ID, TH, KH, CH reclassified to ifrs_direct: IFRS-converged, no mandated numeric chart) |
| — IFRS-direct (IFRS-tag mapping) | 128 |
| — Tier-1 code sets populated (cited) | 54 (SYSCOHADA 17 + PGC-FR/MC + PGC-ES + SNC + PCMN + LU + AT + CAS + PCGE + CGNC + SCF + RO + CZ + SK + HU + BG + UA + KZ + TN + BY + RS + HR + SI + inline) |
| Descriptive placeholders excluded from Tier-1 (B1) | 14 |
| Entities consolidated | 73 |
| Jurisdictions exercised in run | 67 |
| Local entries processed | 356 |
| Deterministic coverage (Tier 1+2) | 97.2% (Tier1 84.3% + Tier2 12.9%) |
| CRA injected-error catalog detected & quarantined | 8/8 (12 flags, 5 invariant classes) |
| Escalated to human (CRA) | 4 (all genuine coverage-boundary cases) |
| Ontology code-collisions remaining | 0 |
| Universal nodes populated | 25 / 30 |
| IAS 29 hyperinflation dual-rate cases | 4 (VE, AR, LB, TR) |
| Consolidated total assets (USD) | 14,326,038 |

## 6. Lessons / standing practice

1. **The harness is a continuous data-quality check on the standard, not only a
   mapping engine.** Collision detection is now a permanent part of the run and
   gates the deterministic index.
2. **Granularity mismatches (VN 635) are first-class, not bugs.** Where a
   national code genuinely aggregates two universal leaves, Kontablo maps the
   code to the dominant leaf and documents the aggregation rather than
   fabricating a spurious distinct code.
3. **Every code correction must cite a primary national source** (epistemic
   standard), recorded in the YAML inline comment and here.
