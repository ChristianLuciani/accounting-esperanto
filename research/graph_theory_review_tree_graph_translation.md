# Review scaffold: the tree → graph → tree translation problem

**Status:** Scaffold (structure + verified anchors + open questions). Not a finished review.
**Relates to:** ADR 012; `research/kirchhoff_hodge_ledger_proposal.md`; preprint
`sections/mathematical_foundations.tex` and `sections/related_work.tex`.
**Date:** 2026-05-29

## Central question
When two single-parent hierarchies (trees) share no common coordinate system, you cannot map
one to the other directly. Lift both into a richer structure (a multi-dimensional graph / a
pivot object), operate there, and project back to a tree. The review's question:

> **When is the round trip faithful, and what — precisely — is lost when it is not?**

## Formal problem statement (to standardize across the review)
Given source tree `T_s`, target tree `T_t`, and a universal pivot graph `G`:
the import `T_s → G` and export `G → T_t` should be characterized as functors; the loss of
the round trip and the obstruction to multi-source reconciliation should be invariants
(adjunction (co)units, cohomology classes), not anecdotes.

## Areas to cover (with verified anchors already in the bibliography)
1. **Functorial data migration / categorical databases** — import/export as adjoint functors;
   colimit as pivot. Anchor: Spivak (2012); Spivak & Kent (2012). *Verified.*
2. **Ontology / schema matching** — the same heterogeneity problem in the semantic web;
   benchmarks (OAEI). Anchor: Thiéblin et al. (2020). *Verified.*
3. **Phylogenetic reconciliation** — the literal twin: embed one tree in another, pay a cost
   in discrete events; rich complexity theory (polynomial / FPT cases). Anchor: Hasić &
   Tannier (2019) and the reconciliation literature. *Verified (concept); complexity results
   to be catalogued.*
4. **Sheaf cohomology / data fusion** — local-to-global gluing; `H¹` as obstruction; sheaf
   Laplacian for quantitative diagnostics. Anchor: Curry (2014); Hansen & Ghrist (2019);
   Robinson (2017). *Verified.*

5. **Structural alignment / optimal transport** — Gromov–Wasserstein aligns structures in
   incomparable spaces using internal distances only; implemented for graph matching. Anchor:
   Mémoli (2011); Xu et al. (2019). *Verified.* Note ADR 009 boundary: proposal generation,
   not mapping authority.
6. **Conservation on networks (Kirchhoff / Hodge)** — the bridge to the ledger-as-flow reading
   and to S2. Anchors to chase: discrete Helmholtz–Hodge decomposition; Kron's cell-complex
   network analysis; effective resistance (within Hansen & Ghrist 2019). *Partly verified;
   no direct double-entry treatment found yet — see novelty gap.*

## Known sub-questions to resolve
- **Linearization loss.** Graph-to-tree projection chooses a primary dimension and drops the
  rest. Characterize the dropped content (the non-tree part) as an invariant. Relate to
  spanning-tree / cycle-space decompositions of the graph.
- **Multi-parent membership.** Where exactly does the single-parent constraint fail, and what
  is the minimal richer structure (DAG? lattice? simplicial complex?) that restores
  expressibility without overshooting?
- **Reconciliation cost models.** Borrow the duplication/loss/transfer cost framework from
  phylogenetics; map it onto consolidation/elimination costs.

## Open / novelty gaps (verify before claiming)
- Has the tree→graph→tree round trip for charts of accounts been treated functorially before?
- Is there prior "double-entry as Kirchhoff/Hodge" or "sheaf-theoretic consolidation" work?
  (First sweep: not found. Re-check discrete-exterior-calculus and sheaf-finance literature.)

## Method
For each area: (a) state the problem in the standardized formal language above; (b) list the
load-bearing results and their complexity; (c) record what transfers to the accounting case
and what does not; (d) tag every cross-domain claim with an ADR 012 tier (Foundation /
Sibling / Analogy). Output target: a section feeding S1 and the novelty sections of S2.
