# Kontablo spin-out roadmap

**Status:** Living document
**Relates to:** ADR 012 (theoretical positioning + split criterion)
**Date:** 2026-05-29

## Standing decision (ADR 012)
Keep the single integrative preprint now. Spin out only when a candidate's core claim is
**load-bearing on its own** — a theorem, or a measured empirical result — not a restatement of
the integrative paper. This document tracks the candidate portfolio and its readiness.

## Portfolio

### S1 — Applied-math: the translation mechanism (HIGH priority)
The import/export adjunction (Spivak) plus the sheaf-cohomological reconciliation obstruction,
with the Kontablo chart-of-accounts mapping as the worked example.
- **Load-bearing claim:** the round trip is an adjoint pair; the reconciliation obstruction is
  a cohomology class.
- **Readiness:** framing done in `sections/mathematical_foundations.tex`; needs a precise
  theorem statement and one worked example.
- **Venues:** *J. Applied & Computational Topology*, *Compositionality*, ACT/TDA workshop.

### S2 — Conservation networks: Kirchhoff / Hodge / sheaf Laplacian (HIGH priority)
The deepest and most novel-looking candidate. See the dedicated proposal:
`research/kirchhoff_hodge_ledger_proposal.md`.
- **Load-bearing claim:** representation theorem (ledger sheaf; `H⁰` = consolidations,
  `H¹` = elimination failures) + a deterministic reconciliation operator (C1–C2 there).
- **Readiness:** proposal drafted; needs the toy proof + a novelty literature sweep + an
  empirical run on `scripts/mass_consolidation_demo.py`.
- **Why now:** strongest tie to ADR 009 (exact, reproducible linear algebra) and to a
  measurable result on our own data.

### S3 — Accounting-facing note (MEDIUM priority)
Positioning vs Ellerman (Pacioli group / vector accounting) and vs the XBRL / ISO 20022
*execution gap*; the deterministic ledger-mapping protocol as the contribution.
- **Load-bearing claim:** a transaction-level (not reporting-level) deterministic mapping
  protocol, framed for accountants.
- **Venues:** accounting-information-systems venue; *Accounting Education*-adjacent.

### S4 — Graph-theory review (PARALLEL task, enabling)
A focused survey of the tree -> graph -> tree translation problem (multi-parent membership,
lossy linearization, reconciliation) across graph theory and TDA. Not a publication on its
own at first; it feeds S1 and S2 and maps the frontier. See
`research/graph_theory_review_tree_graph_translation.md`.

## Suggested sequencing
1. Finish the integrative preprint (v1.75 + the new sections) and make it public.
2. Run the S4 review in parallel — it de-risks novelty claims for S1 and S2.
3. Develop S2 (toy theorem + empirical) — likely the first true spin-out.
4. S1 as the formal companion; S3 as the accounting-facing translation of both.

## Decision log
- 2026-05-29: Portfolio seeded from ADR 012. S2 (Kirchhoff/Hodge) prioritized as the
  candidate most likely to produce a standalone theorem + measured result. No split
  committed yet; integrative preprint remains the single source.
