# Kontablo Roadmap

**Status:** Phase 0 (Research)
**Started:** 2025-01-27
**Target Completion:** 2025-06-30 (Phase 2)

## Phase 0: Research & Validation (Weeks 1-12)

**Goal:** Peer-reviewed white paper validating ontology

### Week 1-4: Standards Inventory
- IFRS/XBRL taxonomy extraction
- Mexico (SAT) analysis
- Colombia (PUC) analysis
- Panama (DGI/SMV) analysis
- Peru (PCGE) analysis
- US GAAP overview

### Week 5-8: Comparative Analysis
- Cross-tabulation matrix
- Frequency analysis
- Mapping complexity study
- Industry extensions

### Week 9-10: Expert Validation
- Recruit 10 CPAs (5 countries)
- Semi-structured interviews
- Survey on ontology
- Case study: Real company migration

### Week 11-12: Ontology Refinement
- Core v0.1 finalization
- Validation rules
- AI training dataset

## Phase 1: Specification & Reference Models (Weeks 13-18)

**Goal:** Published white paper & Ready-to-use Market Templates

- **Default Tree Panama/México/Colombia Kontablo:**
  - Creation of "Standard Reference Trees" per market.
  - These serve as a baseline for new companies and configuration templates for commercial ERPs (Sage, QuickBooks, SAP).
  - Used as the gold standard for automated testing of the Kontablo ontology.
- Draft paper (Methodology, Results).
- Submit to Journal of Information Systems / Preprint on SSRN.

## Phase 2: Implementation & Assisted Mapping (Weeks 19-30)

**Goal:** Working API + Mapping MicroSaaS + ERP Connectors

### 2.1 Assisted Mapping Engine (MicroSaaS)
- Build a **Mapping API/MicroSaaS** for assisted account mapping.
- Integration of **LLM Agents** to minimize manual intervention during the Konbtalo onboarding process.
- Automated suggestion of UUIDs based on account names and historical patterns.

### 2.2 Core Infrastructure
- REST/gRPC API for universal account resolution.
- AI classifier for transaction tagging.
- SDK (Python, JavaScript).

### 2.3 Native Ecosystem
- **Native ERP Integrations:** Direct connectors for main market ERPs (Sage 50, QuickBooks, Odoo, SAP Business One).
- ERPNext module (Reference Implementation).
- Open-source mapping UI for human-in-the-loop validation.

---

**Track progress:** https://github.com/kontablo/kontablo-core/projects/1
