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

### 1. Phase 4: Real-Data Validation (Round 2) — Active
- [ ] Tier A1: EDGAR us-gaap crosswalk + held-out resolution benchmark (H1, H2).
- [ ] Tier A5: IMF GFS / Eurostat COFOG public-sector crosswalk (H5) — validates the drafted `public_sector_ipsas.yaml` extension.
- [ ] Tier A2: ESEF/ifrs-full sample benchmark (H1, H2).
- [ ] Tier B: UK Companies House real-subsidiary case study (H3, H4).
- Full design, pre-registered hypotheses, and falsification thresholds: [`research/real_data_validation_plan.md`](research/real_data_validation_plan.md).

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
