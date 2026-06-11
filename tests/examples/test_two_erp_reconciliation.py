"""Offline (fixtures-mode) test for the two-ERP reconciliation walkthrough.

The live ERPNext+Odoo path requires Docker and is not exercised in CI; this test
locks the deterministic fixtures path AND asserts it agrees, line for line, with
the zero-dependency self-contained example — guaranteeing the two tiers stay
consistent (they share core.engine).
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from examples.transnational_reconciliation import reconcile as self_contained_reconcile  # noqa: E402
from examples.two_erp_reconciliation.run_reconciliation import (  # noqa: E402
    INTERCOMPANY_USD,
    reconcile as two_erp_reconcile,
)


def test_two_erp_fixtures_reconciliation_balances():
    result = two_erp_reconcile("fixtures")
    assert result.is_balanced()
    assert result.balance_difference == 0.0
    assert result.eliminations_applied == 1
    assert result.escalations == []


def test_two_erp_matches_self_contained_line_for_line():
    """Same group, two delivery tiers → identical consolidated USD trial balance."""
    a = {l.kontablo_id: l.net_usd for l in self_contained_reconcile().lines}
    b = {l.kontablo_id: l.net_usd for l in two_erp_reconcile("fixtures").lines}
    assert a == b


def test_intercompany_amount_is_consistent_across_tiers():
    from examples.transnational_reconciliation import INTERCOMPANY_USD as sc_amount
    assert INTERCOMPANY_USD == sc_amount
