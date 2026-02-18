# Kontablo Manifesto
**Version:** 1.0  
**Status:** Living Document  
**Last Updated:** 2025-01-27

---

## Mission

Create a universal, open-source accounting ontology that:
- Enables multi-jurisdictional consolidation
- Supports AI-native financial systems
- Prepares for emerging paradigms (ESG, real-time, multi-capital)
- Remains pragmatic and implementable TODAY

---

## Core Principles (The 7 Pillars)

### 1. **Semantic Universality** ✅ IMPLEMENTED
**Principle:** UUIDs are truth. Codes are display.

Every account concept has:
- Immutable UUID (global identifier)
- XBRL mapping (IFRS interoperability)
- Local code mappings (jurisdiction-specific)

**Why:** Enables consolidation without losing local compliance.

---

### 2. **Graph-Based Structure** ✅ IMPLEMENTED
**Principle:** Accounts exist in multiple dimensions simultaneously.

Accounts are not in a tree (single parent). They are nodes in a graph:
- Classification: Balance Sheet + Income Statement + Cash Flow
- Liquidity: Current / Non-Current
- Function: Operating / Investing / Financing

**Why:** Real-world accounting is multi-dimensional.

**See:** ADR-001

---

### 3. **AI-Native Design** ✅ IMPLEMENTED
**Principle:** Optimized for machine reasoning, readable by humans.

Every account includes:
- Synonyms (for semantic matching)
- Agent hints (vendor patterns, amount ranges)
- Confidence thresholds (when to flag for human review)

**Why:** The future of accounting is human-AI collaboration.

---

### 4. **Causality Transparency (REA Extension)** ⏳ PHASE 2
**Principle:** Every transaction links Resources, Events, and Agents.

Optional REA metadata enables:
- Supply chain traceability
- Impact measurement
- Fraud detection

**Implementation:** Schema extension (not mandatory)

**Why:** Enables next-gen analytics without breaking existing systems.

**Academic Basis:** McCarthy (1982) REA Ontology

---

### 5. **Impact Readiness (ESG Preparedness)** ⏳ PHASE 2
**Principle:** Structure supports double materiality, doesn't mandate it.

Accounts CAN include:
- Environmental impact metadata (CO2e, water, waste)
- Social impact metadata (jobs, diversity, safety)
- Governance metadata (compliance flags)

**Implementation:** Optional schema extension

**Why:** CSRD and other ESG regs are coming. Prepare structure now, mandate later.

**Standards Alignment:** GRI, SASB, TCFD, CSRD

---

### 6. **Immutable Auditability** ⏳ PHASE 3
**Principle:** Every version of the standard has a cryptographic fingerprint.

Implementation options:
- Git commit hashes (lightweight)
- Blockchain anchoring (heavyweight)
- Merkle trees (medium)

**Why:** Trust through verifiability, not authority.

**Note:** This is for the STANDARD itself, not for individual transactions (that's ERP-level).

---

### 7. **Pragmatic Extensibility** ✅ DESIGN PRINCIPLE
**Principle:** Core is minimal. Extensions are infinite.

Kontablo provides:
- **Core:** 200-300 essential accounts (Levels 1-3)
- **Extensions:** Industry-specific (Level 4-5)
- **Custom:** User-defined (Level 6+)

**Why:** Balance standardization with flexibility.

---

## What Kontablo IS

- ✅ A universal chart of accounts (ontology)
- ✅ A mapping protocol between jurisdictions
- ✅ An API specification for AI agents
- ✅ A versioned, open-source standard

## What Kontablo IS NOT

- ❌ A blockchain (but can anchor to one)
- ❌ An ERP system (but ERPs can implement it)
- ❌ A workflow engine (business logic stays in apps)
- ❌ An ESG framework (but supports them)

---

## Governance

See [CHARTER.md](governance/CHARTER.md)

**Decision Model:**
- **Core changes:** Require 2/3 maintainer vote + 30-day public comment
- **Extensions:** Community-contributed, reviewed for consistency
- **Localizations:** Country maintainers with local expertise

---

## Roadmap

**Phase 0 (2025 Q1):** Research & white paper ← WE ARE HERE  
**Phase 1 (2025 Q2):** Core v1.0 (Levels 1-3)  
**Phase 2 (2025 Q3):** Extensions (REA, ESG metadata)  
**Phase 3 (2025 Q4):** Reference implementation (API + ERP module)  

**Future:** Multi-capital accounting, real-time valuation (when standards mature)

---

## Academic Foundations

This work builds on:
- **REA Ontology** (McCarthy, 1982)
- **XBRL Taxonomy** (XBRL International, 2000+)
- **Integrated Reporting** (<IR> Framework, 2013)
- **Graph Databases** (Robinson, 2015)

---

**Status:** Living document. Open for community input via GitHub Issues.
