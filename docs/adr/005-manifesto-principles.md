# ADR 005: Kontablo Manifesto - Core Principles

**Status:** Accepted  
**Date:** 2025-01-27  
**Deciders:** Core team + AI Peer Review (Gemini/Claude Synthesis)

## Context

An initial proposal (Gemini) suggested a 10-principle manifesto incorporating cutting-edge concepts like:
- Triple entry accounting
- Zero-knowledge proofs
- Real-time valuation
- 8-capital measurement

While visionary, peer review identified risks:
- **Overengineering:** ZK-proofs for a COA standard adds unnecessary complexity.
- **Scope Creep:** Smart contracts mix data structure with business logic.
- **Compliance Risk:** "Triple entry" is a marketing term, not a GAAP standard.

## Decision

**Adopt 7 Core Principles** (refined from the original 10):

### ✅ Adopted (Now or Phase 1)
1. **Semantic Universality:** UUID-based truth.
2. **Graph-Based Structure:** Multi-dimensional classification.
3. **AI-Native Design:** Machine-readable metadata.

### ⏳ Adopted with Phasing (Phase 2)
4. **Causality Transparency:** REA metadata as an optional extension.
5. **Impact Readiness:** ESG metadata as an optional extension.

### 🔮 Adopted as Future Direction (Phase 3+)
6. **Immutable Auditability:** Versioned standard anchoring.
7. **Pragmatic Extensibility:** Core minimalism, infinite extensions.

### ❌ Rejected or Out of Scope
- **Triple Entry:** Renamed to "blockchain-anchored" (optional feature).
- **ZK-Proofs:** Application-layer concern, not COA standard.
- **Smart Clauses:** Business logic belongs in the ERP/Workflow, not the schema.
- **Real-Time Valuation:** ERP feature, not standard requirement.
- **8-Capital Mandate:** Prepare structure (extensible), don't mandate framework.

## Consequences

### Positive
- **Academic credibility:** REA and ESG are established research areas.
- **Implementability:** Core remains simple for Phase 0/1 delivery.
- **Future-proof:** Structure supports emerging paradigms without breaking changes.

### Negative
- **Less "hype":** Marketing shift from "Blockchain-Native" to "Standards-Based".
- **Phased delivery:** Visionary features deferred to Phase 2/3.

### Mitigation
- **Clear Roadmap:** Explicit distinction between v1.0 and v2.0 features.
- **Extension Framework:** Community can add ZK/REA layers without forking core.

## Implementation

1. Update `MANIFESTO.md` with 7 principles.
2. Defer REA/ESG schema extensions to Phase 2.
3. Focus Phase 0 research on IFRS mapping and Local Jurisdictions.

## References

- McCarthy, W. E. (1982). The REA Accounting Model
- CSRD (Corporate Sustainability Reporting Directive)
- ADR-001: Graph-Based Account Model
