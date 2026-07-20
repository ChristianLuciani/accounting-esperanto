# Brazil (`br`) localization

**Status: verified against primary source (2026-07-18).** Superseded a `0.1.0-draft` `sped_mapping.yaml` that hand-picked 7 accounts using a fabricated numbering scheme (e.g. `4.01.01` for "Venda de Mercadorias", `5.02.01` for "Despesas com Pessoal" — neither exists in the real RFB chart), and a handful of hand-picked, illustrative `br` local codes on `core/schemas/level3_accounts.yaml` (e.g. `"1.1.1.1.01-9"` for cash) that did not correspond to any real official code either. Both are removed/corrected in this round.

## Files

| File | What it is | Regenerate with |
|---|---|---|
| `plano_referencial_official_chart.yaml` | Verbatim transcription of the official Plano de Contas Referencial (RFB SPED ECF Leiaute 12, sheets L100A + L300A, all 1,123 codes) | `python3 scripts/coa_fidelity/parse_br_plano_referencial.py --input Tabelas_ECF_Leiaute12.xlsx --source-url "http://sped.rfb.gov.br/arquivo/download/8002" --out localizations/br/plano_referencial_official_chart.yaml` |
| `plano_referencial_mapping.yaml` | Every official code classified onto a Kontablo Level-3 node (or flagged `needs_review` / `is_aggregate`) | `python3 scripts/coa_fidelity/map_official_chart.py --official localizations/br/plano_referencial_official_chart.yaml --jurisdiction br --out localizations/br/plano_referencial_mapping.yaml` |
| `default_tree_br.json` | ERPNext-importable chart-of-accounts tree, generated from the mapping | `python3 scripts/coa_fidelity/build_erpnext_tree.py --mapping localizations/br/plano_referencial_mapping.yaml --jurisdiction br --out localizations/br/default_tree_br.json` |

## Source

Receita Federal do Brasil (RFB) / SERPRO, "Plano de Contas Referencial" published as part of the SPED (Sistema Público de Escrituração Digital) **Tabelas Dinâmicas e Planos de Contas Referenciais - Leiaute 12 da ECF (Escrituração Contábil Fiscal)**, Anexo ao Ato Declaratório Executivo Cofis nº 02/2026, atualização de 28/05/2026 (subsequently updated 15/07/2026).

Download endpoint: **http://sped.rfb.gov.br/arquivo/download/8002** (the `/arquivo/show/8002` URL is an HTML landing page only — the real `.xlsx` workbook is served from `/arquivo/download/8002`). File verified via `curl` + `file`: `Tabelas_ECF_Leiaute12.xlsx: Microsoft Excel 2007+`, 1.7 MB, 79 sheets.

**Authority:** Receita Federal do Brasil (RFB)
**Document:** Tabelas Dinâmicas e Planos de Contas Referenciais - Leiaute 12 da ECF
**Published:** Ato Declaratório Executivo Cofis nº 02/2026; last dynamic-table update 28/05/2026 (page itself shows a further 15/07/2026 refresh)
**Scope:** Plano de Contas Referencial for Escrituração Contábil Fiscal (ECF register J051, "Mapeamento para o Plano de Contas Referencial") — the reference chart every Brazilian legal entity's own chart of accounts must be mapped to for federal digital bookkeeping submission.

### Profile scope (deliberate, documented — not a silent gap)

The workbook publishes the reference chart per **entity profile and tax regime**, in parallel sheet families:

- `L100A`/`L300A` — **PJ do Lucro Real - PJ em Geral** (general commercial/industrial entity under the Lucro Real regime): this round's scope, 732 + 391 = 1,123 codes.
- `L100B`/`L100C`, `L300B`/`L300C` — financial institutions and insurers (sector-specific charts, BACEN/SUSEP-aligned).
- `P100A`/`P300` — the Lucro Presumido tax regime's own reference chart.

"PJ em Geral / Lucro Real" is the standard general-commercial-entity profile, analogous to what Ecuador's Supercias NIIF chart and Mexico's SAT Código Agrupador general regime cover in their own rounds. The financial-institution/insurer and Lucro-Presumido variants are **out of scope for this round** and not silently folded in — a future round can extend `br` coverage to them if warranted.

## Coverage honesty

- 1,123 official codes transcribed verbatim (732 from L100A "Contas Patrimoniais" + 391 from L300A "Contas de Resultado"); 0 hand-picked.
- 626 classified onto an existing Kontablo Level-3 node (many-to-one by design — see `core/schemas/level3_accounts.yaml`'s "graph, not tree" principle).
- 148 are aggregate/header rows (Brazil's own `TIPO` column marks these `S` = Sintética directly — no prefix-heuristic guessing needed here, unlike EC/MX). None are excluded as pure statement-presentation captions: Brazil's Plano de Contas Referencial has no off-balance-sheet order/memorandum-account section (verified against the parsed chart — only roots `1`/`2`/`3` exist), so `statement_captions_not_postable` is `0`.
- 349 are genuine `needs_review`: leaf codes (`TIPO` = `A`, Analítica) with no existing Kontablo Level-3 node fitting them, or with a fit deliberately withheld because forcing it would distort the accounting meaning. These are honest ontology/methodology gaps, not silent guesses:

  - **123 are genuine contra-asset/contra-liability/contra-equity accounts** on the balance-sheet side (L100A): allowances (`Perdas Estimadas em Créditos de Liquidação Duvidosa`), accumulated depreciation/amortization/exhaustion (`Depreciação Acumulada`, `Amortização Acumulada`, `Exaustão Acumulada`), impairment losses (`Perdas por Redução ao Valor Recuperável`), inventory write-downs (`Perda por Ajuste ao Valor Realizável Líquido`), unearned-interest discounts (`Juros a Apropriar Decorrentes de Ajuste a Valor Presente`), treasury shares (`Ações em Tesouraria`), and accumulated losses (`Prejuízos Acumulados`). Kontablo has no dedicated contra-node yet; merging these into the gross node they offset would distort gross-vs-net presentation (same convention as the `ec`, `mx`, and `_syscohada` rounds). Brazil's source marks every one of these with a literal `(-)` name prefix — parsed into `is_contra: true` — which the classifier uses directly to route them to `needs_review` instead of requiring per-code enumeration the way `mx`'s round had to.
  - **91 are L300A (P&L) lines also carrying a `(-)` name prefix**, but this is a **different signal in L300A than in L100A** — verified against the actual account names, not assumed: in the P&L, `(-)` is Brazil's sign convention for "this line subtracts from Resultado Líquido," and marks both genuine contra-revenue (sales deductions — the entire `Deduções da Receita Bruta` section, e.g. `Vendas Canceladas e Devoluções de Vendas`, `ICMS`/`COFINS`/`PIS`/`ISS sobre Receita Bruta`) and a residual of ordinary financial/loss lines with no dedicated Kontablo node: trading losses, equity-method investment losses (`Resultados Negativos em Participações Societárias Avaliadas pelo MEP`), impairment losses, OCI-reclassification expenses, and fair-value losses on financial/biological/investment-property instruments. (The classifier does **not** treat every L300A `(-)`-prefixed line as needs_review — ordinary COGS/admin/interest/tax expense lines are `(-)`-prefixed too and are classified normally; see `scripts/coa_fidelity/map_official_chart.py`'s `BR_RULES` header comment for the full verified reasoning.)
  - **129 are L100A ontology gaps unrelated to the contra-account convention**, mostly a **missing current/noncurrent distinction**: Brazil's "Longo Prazo" (long-term) mirror of `1.01.02` (Créditos), `1.01.02.03`/`.04` (Tributos a Recuperar/Compensar), `1.01.05` (Despesas Antecipadas), `2.01.01.15`/`2.02.01.09` (Provisões), and `2.01.01.19`/`2.02.01.21` (Receitas Diferidas) only have a **current** Kontablo node (`asset.current.receivables`, `asset.current.vat_input`, `asset.current.withholding_tax`, `asset.current.prepaid`, `liability.current.accrued`, `liability.current.deferred_revenue`); forcing a long-term balance into a current node would misstate current vs. noncurrent (same principle as `mx`'s `186`/`253`/`255` gaps). Also: `1.01.10`/`1.02.01.10`/`1.02.03.04` (Ativo Biológico — `asset.noncurrent.biological` is `PLANNED` status with no UUID yet, same gap `ec`/`mx` hit); `1.01.11` (Ativo Não Circulante Mantido para Venda — IFRS 5 held-for-sale, no dedicated node); `1.02.02.03` (Propriedades para Investimento — IAS 40 investment property, distinct from both PPE and equity investments, no dedicated node); `1.02.01.05` (Ativos Fiscais Diferidos — a deferred tax **asset**; only `liability.noncurrent.deferred_tax`, a liability node, exists — same gap as `mx`'s `185`); `1.02.06` (Diferido — legacy pre-Lei 11.941/2009 Brazilian-GAAP deferred-charge concept, no clean IFRS-anchored equivalent, same kind of gap as `mx`'s `173`–`182` family); `2.01.01.11`/`.12` (Valores Mobiliários - Hedge — derivative hedge liability, no dedicated node); assorted generic "outras obrigações"/"outros créditos" catch-alls and construction-contract cost-control accounts.
  - **6 are L300A revenue-side items** in the `Outras Receitas/Despesas + Resultado de Operações Descontinuadas` section (`3.01.01.11`/`3.11.01.11`) — gains on disposal of investments/PPE and discontinued-operations income. This entire small, structurally mixed section (disposal gains AND losses, discontinued-ops income AND expense) has no single Level-3 node that fits cleanly and is left `needs_review` rather than force-split (same reasoning as `mx`'s `505`/`703` gaps).
  - Also left `needs_review` for the same "no dedicated node" reason: `3.01.05`/`3.11.05` (Participações — statutory profit-sharing expense to employees/administrators/debenture-holders, same gap as `mx`'s `607` PTU); `2.02.01.11.13` (Adiantamento para Futuro Aumento de Capital - Passivo — genuinely ambiguous equity-vs-liability presentation, an honest gray area rather than a forced call).

  Tracked in `research/coa_fidelity/STATUS.yaml`.

### Brazil's own data made two things more reliable than EC/MX's rounds

Unlike Ecuador's and Mexico's source PDFs (parsed via `pdftotext -layout` and a text-table regex), the RFB workbook carries two authoritative columns EC/MX had to infer:

1. **`TIPO`** (`S` = Sintética/header, `A` = Analítica/leaf) — used directly for `is_aggregate` detection instead of a `parent_codes`/`SUBTOTAL_PREFIXES` heuristic.
2. **`CONTA SUPERIOR`** (explicit parent code) — carried through in the transcription for reference, though the ERPNext tree builder still derives hierarchy from code-prefix containment (safe here because Brazil's dot-segmented codes don't have EC/MX's undotted-digit false-prefix risk).

Brazil's data also marks contra-accounts with a literal `(-)` name prefix (parsed into `is_contra`), which is what let `123` L100A contra-accounts be routed to `needs_review` **generically** via one classifier rule instead of `mx`'s approach of hand-enumerating every contra code.

### ERPNext tree: root-type reparenting (Brazil-specific, verified against the source)

Brazil's own numbering does **not** give Equity or Income/Expense their own top-level root digit the way EC's and MX's charts happen to:

- **Patrimônio Líquido (Equity) is `2.03`** — nested under the same root `2` as Passivo (Liability), not a sibling top-level root.
- **All P&L accounts — Receitas AND Despesas/Custos, for both the "Atividade Geral" and the parallel "Atividade Rural" sections — sit under a single root `3` ("Resultado")**, not split into separate Income/Expense roots.

Both were verified against the parsed chart, not assumed from EC/MX's convention (where a leading digit maps 1:1 to Asset/Liability/Equity/Income/Expense). `scripts/coa_fidelity/build_erpnext_tree.py` was extended with a generic, jurisdiction-keyed `JURISDICTION_REPARENT` mechanism (empty for `ec`/`mx`, populated for `br`) that detaches specific official-code subtrees from their normal numeric parent and promotes them to their own synthetic top-level root with the correct ERPNext `root_type`. The resulting `default_tree_br.json` has five top-level roots — **Ativo** (Asset, 416 leaves), **Passivo** (Liability, 169 leaves), **Patrimônio Líquido** (Equity, 46 leaves), **Receitas** (Income, 112 leaves), **Despesas e Custos** (Expense, 232 leaves) — summing to all 975 postable (non-aggregate-only) leaf accounts. Header nodes left childless by the reparenting (e.g. the original `2` PASSIVO node once `2.01`/`2.02`/`2.03` are promoted) are pruned rather than left as empty groups.

## Related

- **Kontablo Level-3 ontology:** `core/schemas/level3_accounts.yaml`
- **Sweep methodology:** `research/coa_fidelity/README.md`
- **Sweep status:** `research/coa_fidelity/STATUS.yaml`
