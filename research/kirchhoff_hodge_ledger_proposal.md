# Spin-out proposal: the ledger as a conservation network (Kirchhoff / Hodge / sheaf Laplacian)

**Status:** Draft proposal (research, not yet a claim the preprint proves)
**Owner:** Christian Luciani
**Relates to:** ADR 012 (prior-art tiers), ADR 009 (determinism), preprint
`sections/mathematical_foundations.tex`
**Date:** 2026-05-29

## One-line thesis
Double-entry's balance constraint is a *conservation law on a network*; reading the ledger
through discrete Hodge theory and the **sheaf Laplacian** turns consolidation and
reconciliation into deterministic linear algebra, with a computable, localizable obstruction
(`H¹`) where global consistency is impossible.

## Why this is worth a separate output
It is the one connection in ADR 012 that is not merely *positioning* but could yield a
**theorem plus a measurable result** on Kontablo's own data — the split criterion in ADR 012.
It also reinforces ADR 009: Hodge/harmonic projection is exact, reproducible linear algebra,
the antithesis of stochastic inference.

## Honesty up front (what is and isn't established)
- The *machinery* — conservation laws as boundary operators on cell complexes, the
  Helmholtz–Hodge decomposition of flows, the sheaf Laplacian and its cohomology
  (Hansen & Ghrist 2019; Curry 2014) — is rigorous and standard.
- Ellerman (2014) already establishes the conservation/algebraic substrate of double-entry
  (the Pacioli group; the balance equation as a "zero-account").
- A *direct published treatment* of "double-entry as a Kirchhoff/Hodge sheaf" was **not found**
  in a first search. That gap is the opportunity, but novelty MUST be verified against
  discrete-exterior-calculus, money-flow-network, and sheaf-in-finance literature before any
  novelty claim ships.
- This is **conservation/flow topology**, NOT electronic band topology. Graphene / moiré /
  Chern-number analogies are a different mathematical object and stay out (Analogy-tier at
  best, per ADR 012).

## The formal picture

### 1. The ledger as a chain complex
Model the accounting universe as a directed graph (a 1-dimensional cell complex) `K`:
accounts are 0-cells (nodes), and a posting that moves value from account `i` to account `j`
is a 1-cell (directed edge) carrying a signed amount. Let `∂₁` be the boundary operator
sending edge-flows to net node-flows. Then:

- A single double-entry posting is a 1-chain whose boundary places equal and opposite
  weight on the two accounts it touches — the debit/credit pair.
- The accounting identity `A − L − E = 0` (Ellerman's *zero-account*) is a **conservation
  constraint**: posted flows neither create nor destroy value. This is structurally
  **Kirchhoff's Current Law** (net flow balances at every node), with the trial balance
  playing the role of the global conservation check.

This is the *property / quantity* layer of accounting in Ellerman's sense (valuation-free
vectors of property rights), which is the correct substrate: conservation holds before any
price vector is applied, so the topology is independent of valuation controversies.

### 2. Hodge decomposition of ledger flows
With the combinatorial (graph) Laplacian, the discrete Helmholtz–Hodge decomposition splits
any edge-flow uniquely into three orthogonal parts:

- **Gradient (potential) flow** — explainable by a scalar potential on accounts; the part of
  ledger activity reducible to a consistent level/valuation field.
- **Harmonic / cyclic flow** — circulation that *cannot* be reduced to a potential:
  intercompany loops, round-tripping, money cycling through a closed path.
- (Curl, vanishing on a graph; nontrivial once 2-cells are added.)

Operationally: the harmonic component is a **deterministic detector of irreducible
circulation** — a candidate signal for netting opportunities and for round-trip/fraud
patterns — obtained by exact linear algebra, not inference.

### 3. The multi-jurisdiction case: a cellular sheaf
Consolidation is the real target. Model many local ledgers (subsidiaries / jurisdictions)
that must reconcile to a global view as a **cellular sheaf** over the Kontablo mapping graph:

- **Stalks** — the local ledger data at each node (a vector space of account balances).
- **Restriction maps** — the deterministic mapping rules from local statutory nodes to the
  Level-3 universal nodes. *This is exactly the "deterministic boundary" of ADR 009 given a
  linear-algebraic form.*
- **Overlaps** — shared / intercompany accounts where two locals must agree.

Then, with the sheaf Laplacian `L = δᵀδ`:

- `H⁰ = ker L₀` = **global sections = consistent consolidated reconciliations**.
- `H¹ ≠ 0` = the **obstruction**: intercompany / elimination inconsistencies that no choice of
  mapping can globally reconcile. This is the graded, localizable upgrade of the binary
  *Inconsistency Flag*.
- The **spectrum** gives quantitative diagnostics: the spectral gap (smallest nonzero
  eigenvalue) measures robustness of the reconciliation; harmonic representatives localize
  *where* the inconsistency lives (Hansen & Ghrist 2019).

## Claims to prove / measure (what makes it load-bearing)
- **C1 — Representation theorem.** The Kontablo property graph with the balance constraint and
  jurisdiction restriction maps defines a cellular sheaf whose `H⁰` is the set of valid
  consolidated ledgers and whose `H¹` classifies intercompany-elimination failures.
- **C2 — Deterministic reconciliation operator.** Harmonic projection via the sheaf-Laplacian
  pseudoinverse yields a unique, reproducible "best consistent reconciliation + residual,"
  with residual `= 0` iff the `H¹`-class is trivial. (Uniqueness + reproducibility = the
  ADR 009 win.)
- **C3 — Robustness metric.** Effective resistance / spectral gap of the sheaf Laplacian as a
  scalar robustness score for a mapping configuration.
- **C4 — Empirical.** Run on the existing `scripts/mass_consolidation_demo.py` data and the
  23-jurisdiction set; check that nonzero `H¹` coincides with known reconciliation errors.

## A minimal worked example (to build first)
Two subsidiaries `A` and `B` plus a parent `P`; one intercompany loan `A → B`. Build the
sheaf; verify that when the two locals record the loan consistently, `H¹ = 0` and the
harmonic reconciliation reproduces the textbook elimination entry; then perturb one side
(a timing or FX mismatch) and verify a nonzero `H¹` class that localizes to the
intercompany edge. This toy case is the unit test for C1–C2 before scaling to C4.

## Verification tasks before any novelty claim
- Literature sweep: "discrete exterior calculus accounting", "Hodge decomposition financial /
  payment networks", "sheaf theory finance / economics", "network analysis of double-entry".
- Confirm sign/orientation conventions for `∂₁` against the debit/credit convention so the
  KCL correspondence is exact, not loose.
- Separate the property/quantity layer (valuation-free, where conservation is clean) from the
  value layer (price vectors), per Ellerman.

## Suggested venue and shape
A short applied-math paper: the representation theorem (C1) + the deterministic reconciliation
operator (C2), with the consolidation worked example and a C4 empirical section on Kontablo
data. Venue candidates: *Journal of Applied and Computational Topology*, *Compositionality*,
or an applied-category-theory / TDA workshop. Accounting-facing framing (the deterministic
consolidation protocol) could be a companion note for an accounting-information-systems venue.

## Risks
- The analogy's rigor lives in the encoding; a sloppy node/edge/potential assignment makes the
  KCL claim merely poetic. The worked example exists to force precision.
- Novelty is unconfirmed; treat the whole proposal as Sibling/Foundation-grade *pending* the
  literature sweep above. Do not assert priority until then.
