"""
Acceptance-criteria tests for sheaf_consolidation.py.

Run with:  python -m pytest research/experiments/kirchhoff_hodge_toy/ -v
or:        python research/experiments/kirchhoff_hodge_toy/test_sheaf_consolidation.py

Tests are purely deterministic — no random seeds, no mocking.
"""

import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))
from sheaf_consolidation import (
    run_scenario1,
    run_scenario2,
    build_scenario2,
    build_coboundary,
    cohomology_dims,
)

TOL = 1e-10


# ---------------------------------------------------------------------------
# Scenario 1 tests — reconciliation operator (C2)
# ---------------------------------------------------------------------------

class TestScenario1Consistent:
    def setup_method(self):
        self.r = run_scenario1()

    def test_residual_norm_is_zero(self):
        assert self.r["consistent_residual_norm"] < TOL, (
            f"Expected zero residual for consistent input; got {self.r['consistent_residual_norm']}"
        )

    def test_reconciled_equals_input(self):
        diff = np.linalg.norm(
            self.r["consistent_reconciled"] - self.r["consistent_input"]
        )
        assert diff < TOL, f"Reconciled should equal input when consistent; diff={diff}"

    def test_net_intercompany_is_zero(self):
        assert self.r["net_intercompany_consistent"] < TOL, (
            f"Net intercompany elimination should be 0; got {self.r['net_intercompany_consistent']}"
        )


class TestScenario1Mismatch:
    def setup_method(self):
        self.r = run_scenario1()

    def test_residual_norm_is_positive(self):
        assert self.r["mismatch_residual_norm"] > TOL, (
            "Residual should be nonzero for mismatched input"
        )

    def test_reconciled_is_unique_least_squares_value(self):
        # The unique least-squares consistent value for r_A=100, p_B=90 is 95.
        # P projects onto ker δ0 = span([1,1]); the projection of [100,90] is [95,95].
        expected = np.array([95.0, 95.0])
        diff = np.linalg.norm(self.r["mismatch_reconciled"] - expected)
        assert diff < 1e-8, (
            f"Expected reconciled=[95,95]; got {self.r['mismatch_reconciled']}"
        )

    def test_reconciled_is_reproducible(self):
        r2 = run_scenario1()
        diff = np.linalg.norm(
            self.r["mismatch_reconciled"] - r2["mismatch_reconciled"]
        )
        assert diff < TOL, "Result must be identical across runs (ADR 009)"

    def test_residual_localized_to_edge(self):
        # In C0 (vertex space), the residual = x - P x is the component
        # along im(δ0^T), i.e., it is the part of x that "sees" the edge.
        # We verify the coboundary of the residual is nonzero (edge-localized error).
        r = self.r
        delta = r["delta"]
        edge_error = delta @ r["mismatch_residual"]
        assert np.linalg.norm(edge_error) > TOL, (
            "Coboundary of residual should be nonzero (error localized to the edge)"
        )


# ---------------------------------------------------------------------------
# Scenario 2 tests — H1 obstruction (C1)
# ---------------------------------------------------------------------------

class TestScenario2ConsistentLoop:
    """
    holonomy=1.1 (non-trivial twist on the closing edge).
    det(δ0) = 1.1 − 1 = 0.1 ≠ 0 → full rank → H1 = 0.
    Accounting reading: the 10% twist on the closing edge (e.g. an FX conversion
    factor) resolves the cycle; there is no irreconcilable global obstruction.
    H0 = 0: the only globally-consistent section is the trivial zero (no intercompany
    positions), which is consistent with H1 = 0.
    """
    def setup_method(self):
        self.r = run_scenario2(holonomy=1.1)

    def test_dim_H1_is_zero(self):
        assert self.r["dim_H1"] == 0, (
            f"Consistent loop (holonomy=1.1): expected dim H1=0; got {self.r['dim_H1']}"
        )

    def test_dim_H0_is_zero(self):
        # With a non-trivial twist, δ0 has full rank 3; ker δ0 = {0}.
        # The only globally-consistent section is the zero section.
        assert self.r["dim_H0"] == 0, (
            f"Expected dim H0=0 (only trivial global section); got {self.r['dim_H0']}"
        )


class TestScenario2InconsistentLoop:
    """
    holonomy=1.0 (identity / trivial sheaf on triangle).
    det(δ0) = 1.0 − 1 = 0 → rank 2 → H1 = 1.
    Accounting reading: three entities recording pairwise intercompany positions
    with identity restriction maps cannot globally reconcile the circular flow —
    the accounting Penrose triangle. The harmonic representative is the uniform
    circulation [1,1,1] supported on all three edges of the cycle.
    """
    def setup_method(self):
        self.r = run_scenario2(holonomy=1.0)

    def test_dim_H1_is_one(self):
        assert self.r["dim_H1"] == 1, (
            f"Inconsistent loop: expected dim H1=1; got {self.r['dim_H1']}"
        )

    def test_harmonic_rep_is_supported_on_cycle(self):
        # The harmonic representative lives in C1 (dim=3, one per edge).
        # With holonomy≠1, all three edges participate; no component should be ~ 0.
        hrep = self.r["harmonic_reps"]
        assert hrep.shape[0] == 3, "Harmonic rep should live in C1 (3 edges)"
        assert hrep.shape[1] >= 1, "Should have at least one H1 basis vector"
        # Each edge component should be nonzero (the twist circulates around the whole loop).
        for i in range(3):
            assert abs(hrep[i, 0]) > TOL, (
                f"Harmonic rep component {i} is ~0; expected full cycle support"
            )

    def test_harmonic_rep_is_in_coker(self):
        # δ0^T h = 0 for a harmonic representative h
        delta = self.r["delta"]
        hrep = self.r["harmonic_reps"]
        residual = delta.T @ hrep
        assert np.linalg.norm(residual) < 1e-8, (
            f"Harmonic rep not in ker(δ0^T); norm={np.linalg.norm(residual)}"
        )

    def test_determinism(self):
        r2 = run_scenario2(holonomy=1.0)
        assert self.r["dim_H1"] == r2["dim_H1"], "dim H1 must be identical across runs"


# ---------------------------------------------------------------------------
# Determinism meta-test (ADR 009)
# ---------------------------------------------------------------------------

def test_scenario1_fully_deterministic():
    runs = [run_scenario1() for _ in range(3)]
    for key in ("mismatch_residual_norm", "consistent_residual_norm"):
        values = [r[key] for r in runs]
        assert max(values) - min(values) < TOL, f"Non-determinism detected in {key}"


def test_scenario2_fully_deterministic():
    # Test both variants for determinism
    for h in [1.0, 1.1]:
        runs = [run_scenario2(holonomy=h) for _ in range(3)]
        dims = [r["dim_H1"] for r in runs]
        assert len(set(dims)) == 1, f"dim H1 is non-deterministic across runs (holonomy={h})"


# ---------------------------------------------------------------------------
# Standalone runner (no pytest required)
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import traceback

    tests = [
        # S1 consistent
        (TestScenario1Consistent, "test_residual_norm_is_zero"),
        (TestScenario1Consistent, "test_reconciled_equals_input"),
        (TestScenario1Consistent, "test_net_intercompany_is_zero"),
        # S1 mismatch
        (TestScenario1Mismatch, "test_residual_norm_is_positive"),
        (TestScenario1Mismatch, "test_reconciled_is_unique_least_squares_value"),
        (TestScenario1Mismatch, "test_reconciled_is_reproducible"),
        (TestScenario1Mismatch, "test_residual_localized_to_edge"),
        # S2 consistent
        (TestScenario2ConsistentLoop, "test_dim_H1_is_zero"),
        (TestScenario2ConsistentLoop, "test_dim_H0_is_zero"),
        # S2 inconsistent
        (TestScenario2InconsistentLoop, "test_dim_H1_is_one"),
        (TestScenario2InconsistentLoop, "test_harmonic_rep_is_supported_on_cycle"),
        (TestScenario2InconsistentLoop, "test_harmonic_rep_is_in_coker"),
        (TestScenario2InconsistentLoop, "test_determinism"),
    ]
    fns = [test_scenario1_fully_deterministic, test_scenario2_fully_deterministic]

    passed = failed = 0
    for cls, method in tests:
        obj = cls()
        obj.setup_method()
        try:
            getattr(obj, method)()
            print(f"  PASS  {cls.__name__}.{method}")
            passed += 1
        except Exception:
            print(f"  FAIL  {cls.__name__}.{method}")
            traceback.print_exc()
            failed += 1

    for fn in fns:
        try:
            fn()
            print(f"  PASS  {fn.__name__}")
            passed += 1
        except Exception:
            print(f"  FAIL  {fn.__name__}")
            traceback.print_exc()
            failed += 1

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(0 if failed == 0 else 1)
