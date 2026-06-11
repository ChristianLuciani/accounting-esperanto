"""Fast unit assertions for the transnational reconciliation example.

These mirror the assertions the Dockerized two-ERP harness (``e2e/runner.py``)
makes against trial balances pulled from real ERPNext + Odoo instances. Keeping
them here means the consolidation/elimination invariants are guarded on every
fast CI run, with no Docker dependency. The e2e harness reuses the exact same
``reconcile`` / ``assert_reconciled`` code path on real-ERP data.
"""

from examples.transnational_reconciliation import (
    INTERCOMPANY_CODES,
    assert_reconciled,
    build_scenario,
    reconcile,
)


def test_each_entity_balances_locally():
    """Both statutory trial balances must balance in their own currency."""
    for entity in build_scenario():
        total = sum(line.signed for line in entity.lines)
        assert abs(total) < 0.01, f"{entity.entity_id} unbalanced: {total}"


def test_consolidated_trial_balance_balances():
    result = reconcile(build_scenario())
    assert result.balances_pre
    assert result.total_debit_pre == result.total_credit_pre == 300_000.00


def test_intercompany_nets_to_zero():
    result = reconcile(build_scenario())
    assert result.intercompany_receivable == 30_000.00
    assert result.intercompany_payable == 30_000.00
    assert result.intercompany_nets_to_zero


def test_post_elimination_still_balances():
    result = reconcile(build_scenario())
    assert result.balances_post
    assert result.total_debit_post == result.total_credit_post == 270_000.00
    # Elimination removed exactly the intra-group pair from both sides.
    assert result.total_debit_pre - result.total_debit_post == 30_000.00
    assert result.total_credit_pre - result.total_credit_post == 30_000.00


def test_intercompany_codes_are_field_based():
    """Intercompany lines are keyed on (jurisdiction, code) — not free text."""
    assert ("es", "4330") in INTERCOMPANY_CODES
    assert ("mx", "216") in INTERCOMPANY_CODES


def test_full_assertion_bundle():
    """The exact bundle e2e/runner.py invokes on real-ERP data."""
    assert_reconciled(reconcile(build_scenario()))


def test_expected_consolidated_nodes():
    """Resolution lands on the expected universal nodes (deterministic path)."""
    result = reconcile(build_scenario())
    assert set(result.nodes_post) == {
        "asset.current.cash",
        "asset.current.bank",
        "asset.current.receivables",
        "asset.current.inventory",
        "liability.current.payables",
        "equity.capital",
        "revenue.operating",
    }
