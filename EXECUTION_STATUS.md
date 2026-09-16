# Kontablo Global Accounting Protocol: Execution Status

## 🚀 Current Milestone: Phase 4 — Post-Publication: Real-Data Validation (Round 2)

**Kontablo v0.1.0 shipped 2026-06-17; current release v0.3.0 (2026-07-20).** Zenodo concept DOI [10.5281/zenodo.20738795](https://doi.org/10.5281/zenodo.20738795) (resolves to latest version), SSRN preprint (DOI [10.2139/ssrn.6960598](https://doi.org/10.2139/ssrn.6960598), abstract 6960598), ResearchGate (publication 407549570) — see `CITATION.cff` / `.zenodo.json` for the authoritative, up-to-date record. This banner was stale until 2026-07-18 (it still said "release day pending" a month after release); **trust `CITATION.cff`/`.zenodo.json` over this file's phase banner if they ever disagree again.**

Active work: round-2 validation against real, publicly filed financial data (SEC EDGAR, ESEF/filings.xbrl.org, UK Companies House, IMF/Eurostat government finance statistics), complementing — not replacing — the synthetic 97.3% figure. Full pre-registered design: [`research/real_data_validation_plan.md`](research/real_data_validation_plan.md). This round also activates and validates the previously-drafted-but-unwired public-sector/IPSAS extension (see that plan, §2).

Última actualización: 2026-07-18

---

## ✅ Completed Milestones

### 1. Global Jurisdictional Coverage (195/195 — 100%)
- [x] **195 sovereign jurisdictions** mapped — complete global coverage.
- [x] 7,000+ account mappings across all localizations.
- [x] Mandatory charts: SYSCOHADA (17 países OHADA), PCG-France, SNC-Portugal,
      MAR-Belgium, EKR-Austria, K-GAAP-Korea, BAS-Sweden, Smerná osnova-Czech,
      SCF-Algeria, PCGM-Morocco, P(S)BO-Ukraine, OMF-Romania, and more.
- [x] Special contexts: IAS 29 hyperinflation (VE, LB, ZW, CU, SR, SY),
      Islamic finance (SA, QA, KW, BH, PK, BN, SD), distribution-only CIT
      (EE, LV, GE), no-VAT jurisdictions (HK, BN, VU, AG, KN, KI, FM, PW).
- [x] Multi-lingual names: Arabic, Chinese (Simplified + Traditional), Korean,
      Estonian, Polish, Czech, Slovak, Croatian, Bulgarian, Ukrainian, and more.
- [x] Discovery: the 3 last-added countries (EE, BW, NA) all share pure IFRS
      adoption with no mandatory chart — confirming the ontology's universal
      coverage thesis (see preprint appendix).
- [x] Preprint updated: "23 jurisdictions" → "195 sovereign jurisdictions
      (complete global coverage)" across all .tex files.

### 2. Advanced Whitepaper & Research (10-Page Preprint)
- [x] Modular LaTeX implementation for academic publishing.
- [x] Visual documentation of "Tree-to-Graph" Universal Bridge.
- [x] Detailed "Three Crises" problem statement (M2M Void, Babel, Hyperinflation).
- [x] **Co-responsibility Governance Architecture** (Section 8).
- [x] Deterministic Boundary Library (Appendix).

### 3. Agentic Economy Infrastructure
- [x] Support for **AP2 (Agent Payments Protocol)** and **A2A (Agent2Agent)**.
- [x] Implement deterministic boundary library (Cash vs Non-Current, Debit vs Credit).
- [x] Update `MappingService` to trigger `inconsistency_flag` and `inconsistency_note`.
- [x] Update `kontablo_frappe` app to store and display inconsistencies in the ERPNext UI.
- [x] Verify co-responsibility logic with `tests/test_coresponsibility.py`.
- [x] **Model Context Protocol (MCP)** integration for ledger querying.
- [x] Schema update with `agent_id`, `inconsistency_flag`, and `inconsistency_note`.

### 4. Technical Prototype & UI
- [x] High-end Glassmorphism Dashboard in React + Framer Motion.
- [x] API Service (FastAPI) for semantic mapping and consolidation.
- [x] ERPNext/Frappe native connector (`kontablo_frappe`).

---

## 🛠 Active Work & Next Steps

### 1. Phase 4: Real-Data Validation (Round 2) — executed 2026-07-30, **completed 2026-07-31**
Results, verdicts and the "what must not be claimed" list: [`research/experiments/ROUND2_RESULTS.md`](research/experiments/ROUND2_RESULTS.md).
Design and pre-registered thresholds: [`research/real_data_validation_plan.md`](research/real_data_validation_plan.md) (+ Addendum A and Addendum B, execution operationalizations).

**All five hypotheses are now scored.** No hypothesis remains outstanding.

- [x] Tier A1: EDGAR ingestion (53,255 filings, 5.44M facts) + train-only crosswalk (130 tags). Coverage 48.4% weighted holdout.
- [x] Tier A2: ESEF/ifrs-full — 100 filings, 20 countries, 2,821 concepts, parsed from xBRL-JSON (no Arelle/GPL). Coverage vs `ifrs_tag` 6.3% weighted / 2.3% unweighted; H2 clean on 1,404 extension codes.
- [x] Tier A5: IMF GFS / Eurostat COFOG ingestion + 47-entry crosswalk. Coverage 27.7%.
- [x] Tier B: UK Companies House case study (n=10). **H4 supported (100%); H3 falsified (22.7% vs 30% floor).**
- [x] **Gold standard labeling.** Four blind passes (two per experiment, tag-first vs node-first), κ 0.797/0.777 (A1, n=320) and 0.771/0.807 (A5, n=212), 34 + 21 disagreements adjudicated by a third pass.
- [x] **H1 scored: partial at 74.3% weighted**, 0.7 pp below the ≥75% support band. Failure mode is over-mapping (87 false positives vs 5 wrong-node); in-core accuracy 94.6% weighted.
- [x] **H5 scored: 82.3% weighted, clearing its ≥70% threshold — but structurally weak.** 75% of the census is COFOG codes whose correct answer is "escalate"; only 13 codes test real mapping and 12 of 19 drafted nodes get zero evidence.

**Open decisions and follow-ups (not blockers, but do not lose them).**
Work items, cost classes and spoke allocation: [`research/round2_followups.md`](research/round2_followups.md).
Note the two hazard classes recorded there — *gated* changes (touching the core node set) trip the CI claims gate and force all four citable surfaces in the same PR, and *fresh-holdout* changes must have their split reserved **before** they are built.

- [ ] **Owner decision: do NOT promote public-sector wording on H5 alone.** Plan §2 ties promotion to H5 clearing its threshold; it cleared, but on 13 mapped codes covering 7 of 19 nodes. Recommendation recorded in ROUND2_RESULTS.md: keep "drafted, not yet empirically validated" and keep the extension unwired (plan §14) until a census that exercises the stock nodes exists.
- [ ] **Ontology defects surfaced by real data** (4 internal inconsistencies + 1 non-injective field). Highest-value: `ifrs_tag` maps 30 nodes onto 27 tags, so `CashAndCashEquivalents`, `CurrentTaxLiabilitiesCurrent` and `OtherNonCurrentFinancialLiabilities` cannot resolve deterministically. Also `asset.noncurrent.investments` (label vs `ifrs_tag`), `expense.admin` (`ifrs_tag` vs the EBIT aggregation rule), `liability.noncurrent.lease` (note vs node id), `EXP_SocialBenefitsExpense` (`ipsas_ref` vs `examples`).
- [ ] **Missing core nodes named by the gold pass**: intermediate consumption / use of goods and services (the largest unmapped government expense line), non-current tax / provision / payables tiers, current lease-liability portion, contra-asset representation, OCI components, restricted cash.
- [ ] **Label-vocabulary gap**: no combined liability+equity lens, so `LiabilitiesAndStockholdersEquity` has no correct aggregate label.
- [ ] **A2 has no temporal holdout** — the committed mechanical rule selects earliest-per-country. A future round needs a rule that stratifies on period, introduced as a dated addendum rather than a silent edit.
- [ ] Follow-up from the H3 falsification: the Tier-2 rule set lacks British-English vocabulary and 6 of 30 nodes have no rule at all. **Fixing it requires a fresh holdout** — repairing and re-running against the same corpus would be tuning on the test set.

### 2. Expert Validation (still open — not yet started as of 2026-07-18)
- [ ] Conduct structured validation interviews with international CPAs.
- [ ] Peer-review adjustments based on expert feedback.

### 3. Production ERP Connectors (backlog, no committed date)
- [ ] Two-way API integration for **NetSuite** and **SAP S/4HANA**.
- [ ] Production-grade authentication (JWT) for the consolidation API.

---

## 📄 Key Repository Documents
- **Whitepaper PDF:** [kontablo_preprint_modular.pdf](docs/papers/drafts/kontablo_preprint_modular.pdf)
- **ADR 008 (Co-responsibility):** [ADR 008](docs/adr/008-co-responsibility-governance.md)
- **Node Definitions:** [ontology_definitions.md](research/ontology_definitions.md)
