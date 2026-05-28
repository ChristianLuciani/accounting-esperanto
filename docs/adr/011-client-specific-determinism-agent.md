# ADR 011: Client-Specific Determinism Agent

**Status:** Proposed
**Date:** 2026-05-28
**Deciders:** Christian Luciani

---

## Context

ADR-009 establishes "determinism over stochasticity wherever movable" as a standing
architectural driver at the **system-wide** level. The Kontablo ontology enforces a shared,
universal Deterministic Boundary Library that applies uniformly across all deployments.
The iterative loop defined in ADR-009 explicitly anticipates future rounds of migration from
stochastic inference to deterministic logic as the system matures.

As Kontablo moves toward production deployments, a distinct pattern becomes observable:
individual clients accumulate idiosyncratic recurring transactions that could benefit from
client-specific deterministic rules derived from their own operational history. A client in the
agricultural sector, for instance, develops recurring IAS 41 biological-asset entry patterns
that consistently resolve via Tier 3 (semantic AI fallback), despite their structural regularity
making them strong Tier 1 (exact lookup) candidates — but only within that client's
ontological context. A multinational with a specific inter-company structure develops
consolidation patterns that recur thousands of times per month but are treated as fresh
inference calls each time.

These cases are not failures of the shared ontology; they are opportunities to extend the
ADR-009 principle to a **per-client layer**, operating locally on client infrastructure and
without modifying the universal Deterministic Boundary Library.

This ADR is also motivated by the preprint section "The Kontablo Agent: Harness
Architecture and the Locus of Error," which characterizes the harness as the primary
reliability mechanism and identifies coverage-boundary errors as the residual error
population after ontology-as-constraint is applied. A Client-Specific Determinism Agent
directly addresses one sub-class of coverage-boundary errors: transactions that are
structurally unambiguous for a given client but not yet encoded in the shared library.

**Phase scope:** This is explicitly a **Phase 3+ proposal**. It is documented here to:
(a) capture design intent while architecture is being established, and
(b) prevent premature implementation during Phase 2.5 that would violate CLAUDE.md's
scope constraints. Nothing in this ADR authorizes any Phase 2.5 implementation.

---

## Decision

**Propose** (not Accept) the following architecture for a Client-Specific Determinism Agent.

An optional agent component, deployable on **client-controlled infrastructure**
(on-premises or client-controlled cloud), that operates as an extension to the harness for
that specific deployment:

### Component behavior

1. **Observe.** The agent monitors the client's Tier 3 resolution history, identifying
   recurring patterns — account categories, vendor classifications, transaction type
   sequences — that consistently resolve to the same Kontablo Level 3 node with
   high confidence over a configurable observation window.

2. **Propose.** When a pattern meets a recurrence threshold (to be defined empirically
   in Phase 3), the agent generates a candidate rule expressed in the same grammar
   as the existing Deterministic Boundary Library. This rule, if accepted, would migrate
   that pattern from Tier 3 inference to Tier 1 exact lookup or Tier 2 rule-based
   matching within the client's deployment context. Proposals are human-readable and
   carry: the pattern matched, the proposed rule predicate, the observation window,
   the recurrence count, and a sample of the transactions that triggered the proposal.

3. **Require co-signature.** No client-specific rule becomes active without explicit
   written approval from the client's designated accountant or compliance officer.
   This is a hard constraint, not a configurable option. The co-signature requirement
   is the same governance principle as ADR-008 (CRA) applied to rule creation rather
   than transaction classification. Bulk approval of multiple rules in a single action is
   prohibited by design — each rule requires individual review.

4. **Operate locally.** The agent processes only the client's own transaction data on
   their own infrastructure. Client transaction data is not transmitted to Praxia,
   not aggregated across clients, and not used to update the shared Deterministic
   Boundary Library without explicit separate authorization.

### Scope boundaries

- Client-specific rules **extend** the shared Deterministic Boundary Library locally;
  they do not **override** or **replace** universal rules. A client-specific rule that
  contradicts a universal boundary predicate is rejected at rule-creation time.
- The agent has no write access to the shared ontology graph. Its output is a local
  rule file that the client's harness consults after the shared library.
- This component is architecturally distinct from the system-wide observability signals
  defined in ADR-009 (inference-call ratio, token-cost tracking, residual-error locus).
  Those signals are system-level; this agent is per-client.

---

## Consequences

### Positive

- Extends ADR-009's determinism principle to the client-operational layer, reducing
  per-client Tier 3 inference calls as client-specific rule libraries mature.
- Reduces recurring token cost and latency for clients with stable, high-volume
  transaction patterns — directly serving the energy/resource-efficiency consequence
  articulated in ADR-009.
- Strengthens client retention: the accumulated rule library represents operational
  knowledge encoded in a portable artifact. This is a legitimate switching-cost moat
  that is not dependent on license restrictions.
- Architecturally consistent with the existing three-tier pipeline: proposed rules slot
  into Tier 1/2, requiring no new resolution pathway.

### Risk 1 — Data Sovereignty and Privacy

The agent necessarily processes sensitive financial transaction data. Even with local
deployment, the following must be specified before implementation:

- What transaction data is retained by the agent between observation cycles, and
  for how long.
- Whether rule proposals expose transaction-specific details (vendor names, amounts).
  A rule expressed as "vendor 'Proveedor ABC' → `expense.cogs`" leaks a vendor
  relationship. Rules should be expressed in structural terms (account type patterns,
  nature predicates) rather than entity-specific identifiers wherever possible.
- How the rule library itself is access-controlled and backed up.
- What data flows, if any, exist between the client deployment and Praxia's
  infrastructure for support or update purposes.

A privacy threat model is required before implementation. This ADR does not satisfy
that requirement.

### Risk 2 — Human Validation Integrity

The co-signature requirement is the safety guarantee of this component. If the approval
workflow is poorly designed — a dismissible modal, an easy-to-skip review step, or any
path that enables approving a rule without reading it — the component degrades into the
"rubber-stamping" pattern that ADR-008 was designed to prevent. The irony would be
significant: a rule that was proposed to reduce AI inference calls, approved without human
understanding, potentially encoding a pattern that was itself a Tier 3 error.

Mitigation requirements (to be designed in Phase 3):
- The approval interface must display: the rule predicate in human-readable form,
  the observation period, the recurrence count, and at least three sample transactions
  that triggered the proposal.
- The approver must confirm understanding of the rule's scope and potential
  classification impact before activation.
- Activation must generate an immutable audit record consistent with ADR-008's
  persistence requirements.

### Risk 3 — Scope Creep into Phase 2.5

The existence of this ADR, the fact that it is referenced in the preprint, and its
conceptual elegance all create pressure to begin implementation before publication.
This must not happen. The correct trigger for implementation is:

1. At least one production client deployment is live and generating observed Tier 3 history.
2. Recurring Tier 3 patterns have been empirically documented in that deployment,
   with volume sufficient to justify implementation cost.
3. Phase 3 capacity has been formally allocated.
4. The privacy threat model (Risk 1) has been completed and approved.
5. The approval interface design (Risk 2) has been specified and reviewed.

None of these conditions are met as of Phase 2.5. This ADR's Phase 2.5 value is
documentation only.

---

## References

- **ADR-008** (`008_co_responsibility_governance.md`) — the co-responsibility principle
  governs the mandatory human co-signature requirement for rule activation, and the
  audit persistence requirements for the activation record.
- **ADR-009** (`009-determinism-over-stochasticity.md`) — this ADR extends ADR-009's
  iterative "migrate from inference to deterministic logic" loop to the per-client layer.
  The iterative loop in ADR-009 explicitly anticipates this kind of extension.
- **`CLAUDE.md`** — architectural principle #5 (determinism over stochasticity);
  anti-pattern: do not chase Phase 3 work before publication.
- **Preprint section "The Kontablo Agent: Harness Architecture and the Locus of Error"**
  — establishes the harness concept and identifies coverage-boundary errors as the
  residual this agent addresses. Cites this ADR as a future per-client extension of the
  harness principle.
