# ADR 015: Core-Node Admission Policy — When the Ontology Grows and When It Must Not

**Status:** Proposed
**Date:** 2026-06-11
**Deciders:** Christian Luciani

---

## Context

Building the reproducible transaction-volume coverage benchmark
(`scripts/coverage_benchmark.py`, `research/coverage_benchmark/`) forced a
question the project had answered only implicitly: **under what criteria may the
universal account core grow, and when must it not?**

Until now Kontablo carried three structures with no written rule connecting them:

1. a **frozen minimum core** of 30 Level-3 nodes (the Pareto headline);
2. a **`pending_accounts`** block (crypto, Zakat, carbon credits, biological
   assets) — candidate nodes held back without a stated promotion test; and
3. an implicit **residual** handled by the Co-responsibility Architecture
   (ADR-008) via escalation.

The benchmark made the underlying economics explicit and measurable, and three
empirical facts now govern the decision:

- **Posting volume is steeply long-tailed (Pareto).** The 30-node minimum core
  captures ~94% of routine posting volume; **four** additional nodes (payroll
  liabilities, contract/deferred revenue, withholding-tax receivable, other
  receivables) capture most of the remainder and reach ~99%. Beyond that the
  curve is flat — the next candidates each add a fraction of a percent.
- **Marginal volume per node collapses.** The first extended node (payroll)
  captured by far the largest residual slice; subsequent nodes captured rapidly
  less. Coverage rises monotonically with breadth but with severe diminishing
  returns, so unbounded growth buys almost nothing while costing determinism.
- **Each added node is a new site of ambiguity.** Every node is a new place
  where a local account can be mis-mapped, a new deterministic boundary to
  maintain (ADR-008), and a new collision surface in the local-code index. Node
  count is not free; it is a liability that must be paid for in captured volume.

This ADR also resolves a standing tension. Two of Kontablo's stated virtues pull
in opposite directions: the **elegant, citable minimum core** (small is the whole
point) versus **coverage completeness** (more nodes cover more). Without an
explicit rule, every future contributor will re-litigate "just one more account,"
reactivating the documented anti-pattern of scope creep before publication.

## Decision

We adopt a **three-layer ontology model with an explicit, evidence-gated
admission policy.** The core does not grow by intuition or by request; it grows
only when a candidate passes every admission criterion below, and the
**coverage benchmark is the gate**.

### The three layers

| Layer | Mutability | Role | Residual handling |
|---|---|---|---|
| **Minimum core** (30 nodes) | **Frozen** — changes only at a major version (ADR-006-style version bump, blockchain-anchored hash; ADR principle #6) | The universal Pareto headline; the citable invariant of the standard | n/a |
| **Extended core** (currently 34 = 30 + 4) | **Bounded growth** via this policy; minor version | Captures high-volume, cross-jurisdictional residual that passes the gate | n/a |
| **Principled residual + jurisdictional overlays** | Open-ended, but **never forced into the core** | Idiosyncratic, local, novel, or low-volume types | **Escalation to a human (CRA, ADR-008)** or local-code overlay |

The minimum core is **immutable by default**. The extended core is the *only*
layer that grows, and it grows under the following gate.

### Admission criteria — a candidate becomes a core node only if ALL hold

A proposal to promote a transaction type to a Level-3 (extended) core node MUST
satisfy every one of these. Failing any single criterion routes the type to an
overlay or to the residual, not to the core.

1. **Material, measured volume (A1).** The candidate must capture a
   non-trivial slice of routine posting volume **as measured by a committed
   re-run of `coverage_benchmark.py`**, not by assertion. The working threshold
   is **≥ ~0.5% of total posting volume** (roughly the marginal contribution of
   the smallest of the four extended nodes already admitted). Below this, the
   determinism/maintenance cost of the node exceeds the coverage it buys.
2. **Cross-jurisdictional universality (A2).** The concept must recur across a
   broad set of jurisdictions with a **clean IFRS anchor** (`ifrs_tag`). A type
   that is real in only one jurisdiction or one chart family is a **jurisdictional
   overlay**, not a universal node (ADR-001: IFRS-anchored core, local overlays).
3. **Determinable invariants (A3).** The node must admit an unambiguous,
   binary **Deterministic Boundary Library** definition: a fixed `nature`
   (debit/credit), `statement` class, and IFRS tag, with **no collision** against
   existing nodes on re-validation (`ontology_code_collisions == 0`). If the
   classification is contested or context-dependent, it cannot be deterministic
   and therefore cannot be a core node (ADR-009, ADR-008). *This is precisely the
   test that holds crypto, Zakat, and carbon credits in `pending_accounts` — they
   currently lack a confirmed `nature`.*
4. **Non-decomposability (A4).** The type must not already be adequately
   represented by aggregation of existing nodes. If it nets cleanly into an
   existing node **without losing decision-relevant information**, do not add it.
   A new node must capture a distinction the current graph cannot express.
5. **Maturity / stability (A5).** The instrument must be established, not
   emergent or speculative. Emergent instruments (tokenised assets, CBDC
   settlement, novel Islamic-finance structures) stay in `pending_accounts` until
   their accounting treatment stabilises, because admitting them prematurely
   commits the deterministic boundary to a moving target.

### Non-growth criteria — keep in residual/overlay (do NOT add a node) when

- Volume is **sub-threshold** (the flat tail) — the dominant case after the
  extended core. *Most* candidates will fail here, by design.
- The type is **single-jurisdiction or chart-family specific** → overlay.
- It lacks a **stable IFRS anchor or has contested classification** → `pending`
  / escalation.
- It is **novel or unstable** → roadmap, not core.
- The motivation is **"approaching 100%."** Chasing total coverage is explicitly
  rejected: new instruments and rules continuously regenerate the tail, so a
  closed claim of completeness is false the moment it is made (see
  `evaluation.tex`, "Coverage Expansion and the Principled Residual"). The
  residual is a **designed feature**, not a defect to engineer away.

### Is there a hard limit on core size?

**No fixed number, but a binding economic ceiling.** There is no arbitrary cap
on node count; there is a **cost-coverage gate** (A1). Because volume is
Pareto-distributed, the gate is **self-limiting**: once the extended core is in
place, the benchmark shows almost every further candidate falling below the
volume threshold, so the policy converges on its own. The expectation is that
the extended core stabilises at a **small number of dozens of nodes**, not
hundreds. National charts run to hundreds of accounts precisely because they
encode the long tail; Kontablo deliberately does not, and pushes that tail to
overlays and escalation instead.

### Governance procedure (who decides, with what evidence)

A core-node change is a versioned, evidence-bearing event:

1. **Evidence required.** Any admission proposal MUST attach (a) a
   `coverage_benchmark.py` re-run quantifying the candidate's marginal volume
   (A1), (b) cross-jurisdictional presence with IFRS anchor (A2), and (c) the
   proposed deterministic invariant set with a zero-collision re-validation (A3).
   **No measurement, no admission.**
2. **Lifecycle.** A node moves `pending_accounts` → `extended_core` only when
   A1–A5 are all satisfied. A node enters the **minimum core** only at a major
   redefinition of the standard; the default is **never**.
3. **Versioning (ADR principle #6).** Extended-core additions are **minor**
   version bumps with a re-anchored spec hash; minimum-core changes are **major**
   bumps. The frozen-by-default rule makes the headline stable enough to cite.
4. **Claims–evidence gate.** `tests/test_coverage_claim.py` pins the published
   coverage figures and node counts (30 / 34) to the benchmark, so any core
   change that is not reflected — or any drift — fails CI.

### Relationship to the residual and the CRA (ADR-008)

Core growth and escalation are **complementary levers, governed together.** You
grow the core **only where determinism is cheap and universal** (A2 + A3);
everything else escalates to a human through the Co-responsibility Architecture.
This operationalises the harness-architecture thesis: the ontology-as-constraint
eliminates the classical hallucination class, relocating residual error to the
**boundary of semantic coverage**. This policy defines *where that boundary sits*
and *how it may move* — the core captures the deterministic, high-volume centre;
the CRA owns the instrumented, human-resolved edge. Neither absorbs the other.

## Consequences

### Positive

- **Resolves the elegance-vs-completeness tension permanently.** The minimum
  core stays small and citable; coverage completeness is met by a bounded
  extended core plus escalation — both empirically backed, neither compromised.
- **Makes "just one more account" a falsifiable claim.** A proposal either
  clears the measured volume gate or it does not. Scope creep becomes a test
  failure, not a debate.
- **Keeps the deterministic boundary maintainable.** Node count grows only when
  paid for in volume, bounding the Deterministic Boundary Library's maintenance
  surface (the negative consequence flagged in ADR-008).
- **Self-limiting and reproducible.** The Pareto structure makes the gate
  converge; the benchmark makes every decision auditable.

### Negative / risks

- **Threshold is a parameter, not a law.** The ~0.5% volume gate is calibrated
  to the current synthetic benchmark; a real-ledger corpus (the documented
  roadmap in `research/coverage_benchmark/README.md`) may shift it. The
  threshold should be re-validated, not treated as eternal.
- **Jurisdictional fairness.** A type that is high-volume in only a few
  jurisdictions (e.g. Zakat in GCC states, withholding/retención in LatAm) can
  fail A2 yet matter enormously locally. The mitigation is the **overlay layer**,
  which must be funded as a first-class path so "not core" never reads as "not
  supported."
- **Judgement remains at A4/A5.** Non-decomposability and maturity are not fully
  mechanical; they require an accounting judgement call, recorded in the
  proposal. The policy bounds and documents that judgement; it does not remove
  it.

## References

- ADR-001 — Graph, not tree (IFRS-anchored universal core + local overlays).
- ADR-006 — MX-SAT alignment (overlay precedent).
- ADR-008 — Co-responsibility Governance Architecture (escalation owns the residual).
- ADR-009 — Determinism over stochasticity (A3 derives from this).
- `research/coverage_benchmark/` — the benchmark that quantifies A1 and is the admission gate.
- `docs/papers/drafts/sections/evaluation.tex` — "Coverage Expansion and the Principled Residual."
- `core/schemas/level3_accounts.yaml` — `level3:` (minimum core), `extended_core:` (admitted), `pending_accounts:` (candidates).
