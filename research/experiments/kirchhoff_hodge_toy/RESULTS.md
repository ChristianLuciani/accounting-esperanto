# Toy validation results — cellular-sheaf consolidation (C1/C2)

**Branch:** `experiment/sheaf-consolidation-toy`
**Date:** 2026-05-30
**Status:** All 15 acceptance-criteria tests pass. This is a mechanics validation, NOT a proof of the general theorem.

---

## Scope and epistemic posture

This experiment validates the *mechanics* of claims C1 and C2 from
`research/kirchhoff_hodge_ledger_proposal.md` on two small, hand-crafted scenarios.
It does not prove the general representation theorem (C1) nor the uniqueness of the
reconciliation operator in the general case (C2). Those require a full mathematical
treatment and prior-art verification (see "Prior art and open questions" below).

**What is being tested:** that the coboundary δ0, the Moore–Penrose reconciliation
projector P = I − δ0⁺δ0, and the cohomology dimensions H0/H1 behave as the sheaf
theory predicts on concrete numerical inputs.

---

## Implementation

| File | Role |
|---|---|
| `sheaf_consolidation.py` | Sheaf builder; δ0, L0; H0/H1 dims; reconciliation operator. Pure functions, no randomness. |
| `test_sheaf_consolidation.py` | 15 acceptance-criteria assertions (standalone runner + pytest-compatible). |
| `RESULTS.md` | This file. |

**Dependencies:** numpy only (tested with numpy 2.4.1, Python 3.11).
**Determinism:** all arithmetic is IEEE 754 double-precision with a fixed SVD-based rank
tolerance of 1e-10. No random seeds needed; output is bit-identical across runs (ADR 009).

---

## Scenario 1 — intercompany loan, 2 entities (validates C2)

**Setup:** two vertices v_A (A's intercompany receivable), v_B (B's recorded payable);
one edge e_AB with identity restriction maps. Global consistency ≡ receivable = payable.

**Coboundary:**
```
δ0 = [[-1.  1.]]        (1×2 matrix; (δ0 x)_AB = x_B − x_A)
dim H0 = 1,  dim H1 = 0  (acyclic graph → no H1 obstruction, as expected)
```

### 1a — Consistent input (r_A = 100, p_B = 100)

```
reconciled   = [100. 100.]
residual     = [  0.   0.]
‖residual‖  = 0.00e+00
net intercompany elimination = 0
```

**Interpretation:** input is already in ker δ0; P is the identity on this point; the
elimination entry is zero (no adjustment needed). ✓

### 1b — Mismatched input (r_A = 100, p_B = 90 — FX/timing gap of 10)

```
reconciled   = [95. 95.]
residual     = [ 5. −5.]
‖residual‖  = 7.071 (= 10/√2, the L2 norm of a ±5 correction)
```

**Interpretation:** the projector P finds the unique least-squares consistent value
(95 = midpoint, by symmetry of the identity restriction maps). The residual [5, −5] is
the correction applied to each entity. It is nonzero and localized to the e_AB edge
(δ0 applied to the residual gives the full mismatch; δ0 applied to the reconciled
output gives zero). The 10-unit gap is irreducible — no choice of global section can
make both entities simultaneously record their original values. ✓

**Note on H1:** a single-edge (acyclic) sheaf has H1 = 0 by construction. Scenario 1
tests the *reconciliation operator* (C2), not the cohomological obstruction (C1).

---

## Scenario 2 — intercompany loop, 3 entities (validates C1)

**Setup:** triangle v_A, v_B, v_C; edges AB, BC, CA; stalks R each. The closing edge
CA carries a scalar holonomy twist h on the head (v_A) restriction map.

**Key algebraic fact:** det(δ0) = h − 1.
- h = 1.0: det = 0, rank = 2, **H1 = 1** (the cycle is irreconcilable)
- h ≠ 1.0: det ≠ 0, rank = 3, **H1 = 0** (the twist resolves the cycle)

### 2a — Inconsistent loop (holonomy = 1.0, identity restriction maps)

```
dim H0 = 1,  dim H1 = 1
harmonic representative (H1 basis in C1):
  [0.577, 0.577, 0.577]   (= [1,1,1]/√3, uniform circulation)
```

**Interpretation:** with identity restriction maps on all three edges, the trivial sheaf
on a triangle always has H1 = 1. The harmonic representative [1,1,1] (uniform
circulation) is supported on all three edges of the cycle — it is the sheaf-theoretic
signature of the *accounting Penrose triangle*: three entities can each record pairwise
intercompany positions that look locally consistent, yet the global loop cannot be
closed without introducing an irreducible circulation. This is the direct analog of a
currency-triangle arbitrage that cannot be arbitraged away because no global potential
exists. The H1 class localizes the inconsistency to the cycle. ✓

The single global section (H0 = 1) is the constant section x_A = x_B = x_C — all
entities agree on a single value. Any deviation from this creates the H1 obstruction.

### 2b — Consistent loop (holonomy = 1.1, non-trivial twist on closing edge)

```
dim H0 = 0,  dim H1 = 0
```

**Interpretation:** the 10% twist on the closing edge CA (e.g. an FX conversion rate
between the currencies of entity C and entity A) makes δ0 invertible. H1 = 0: no
irreconcilable obstruction exists. H0 = 0: the only globally-consistent section is the
trivial zero section (no intercompany positions). This is not a degeneracy — it reflects
that with a non-trivial holonomy, the sheaf has no non-zero global sections, so the
only perfectly reconciled state is "nothing to reconcile."

**Note on accounting semantics of the holonomy:** this result is initially
counterintuitive. One might expect that "identity restriction maps = consistent" and
"twist = inconsistent." The sheaf-cohomological truth is the opposite: the *trivial*
sheaf on a cyclic graph *inherits the topology of the cycle* (H1 = 1); a *non-trivial*
restriction map can kill the cohomology by making the cycle algebraically contractible.
The accounting analog is that pairwise-agreeing books do not imply global reconcilability
when the underlying graph has cycles — a known failure mode in multi-entity consolidation. ✓

---

## Test results summary

```
PASS  TestScenario1Consistent.test_residual_norm_is_zero
PASS  TestScenario1Consistent.test_reconciled_equals_input
PASS  TestScenario1Consistent.test_net_intercompany_is_zero
PASS  TestScenario1Mismatch.test_residual_norm_is_positive
PASS  TestScenario1Mismatch.test_reconciled_is_unique_least_squares_value
PASS  TestScenario1Mismatch.test_reconciled_is_reproducible
PASS  TestScenario1Mismatch.test_residual_localized_to_edge
PASS  TestScenario2ConsistentLoop.test_dim_H1_is_zero
PASS  TestScenario2ConsistentLoop.test_dim_H0_is_zero
PASS  TestScenario2InconsistentLoop.test_dim_H1_is_one
PASS  TestScenario2InconsistentLoop.test_harmonic_rep_is_supported_on_cycle
PASS  TestScenario2InconsistentLoop.test_harmonic_rep_is_in_coker
PASS  TestScenario2InconsistentLoop.test_determinism
PASS  test_scenario1_fully_deterministic
PASS  test_scenario2_fully_deterministic

15 passed, 0 failed
```

---

## Prior art and open questions

### What this experiment does NOT establish

1. **Novelty.** The Hodge decomposition of flows on graphs is applied prior method.
   Direct citations that must be read before any priority claim:
   - **Jiang et al. (2011)** — "Statistical ranking and combinatorial Hodge theory,"
     *Math. Program.* 127(1):203–244. The foundational reference for Hodge decomposition
     on directed graphs.
   - **Fujiwara et al. (2021)** — applies Hodge decomposition to economic/financial flow
     networks. Must be read to assess overlap with the consolidation application.
   - **Menéndez-Winschel (2025)** and **Nester (2020)** — cited in ADR 012 as requiring
     verification before any priority claim on the sheaf-accounting connection.
   - **Hansen & Ghrist (2019)** — "Toward a spectral theory of cellular sheaves,"
     *J. Appl. Comput. Topol.* 3:315–358. The sheaf Laplacian framework used here.
   - **Ellerman (2014)** — establishes the conservation/algebraic substrate of
     double-entry (the Pacioli group). The zeroth layer this work builds on.

2. **The general representation theorem (C1).** This experiment shows the mechanics work
   on a 2- and 3-vertex toy. It does not prove that Kontablo's full property graph with
   all 23 jurisdiction mappings defines a cellular sheaf whose H0 is exactly the set of
   valid consolidated ledgers. That requires: (a) a precise sheaf structure on the actual
   Kontablo graph, (b) a proof that the restriction maps are the jurisdiction mapping
   rules, and (c) verification that boundary conditions (e.g. non-linear FX adjustments,
   hyperinflationary restatements) remain within the linear sheaf framework.

3. **Uniqueness in the general case (C2).** The pseudoinverse is unique, so the
   reconciliation operator is unique given a fixed δ0. But the choice of sheaf structure
   (which restriction maps to use) is not unique, and different choices yield different
   reconciled outputs. The toy fixes this by construction.

### Sign/orientation convention note

The coboundary convention used here — `(δ0 x)_e = F_{head◁e} x_head − F_{tail◁e} x_tail` —
is standard but requires consistent edge orientation throughout. In the Kontablo property
graph, edges are directed by the mapping relation (local → universal node). Verify that
this orientation is globally consistent before scaling up.

### What would make C1/C2 load-bearing

Per `kirchhoff_hodge_ledger_proposal.md`: run the sheaf construction on the actual
`scripts/mass_consolidation_demo.py` data and verify that nonzero H1 coincides with
known reconciliation errors. That is the empirical test (C4) that would give C1/C2
accounting content beyond mechanics.
