"""Asserts on the self-contained transnational reconciliation example.

These are real assertions (not print-only), per CLAUDE.md's "tests must assert"
rule. They lock in the deterministic, balanced cross-border result and the
intercompany elimination behaviour.
"""

import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from examples.transnational_reconciliation import (  # noqa: E402
    INTERCOMPANY_USD,
    build_parent_spain,
    build_subsidiary_mexico,
    intercompany_links,
    reconcile,
)
from core.engine import ConsolidationEngine  # noqa: E402


def test_each_local_trial_balance_is_balanced_locally():
    for tb in (build_parent_spain(), build_subsidiary_mexico()):
        debits = sum(e.debit for e in tb.entries)
        credits = sum(e.credit for e in tb.entries)
        assert round(debits - credits, 2) == 0.0, f"{tb.subsidiary_id} local TB unbalanced"


def test_every_account_resolves_via_tier1_exact():
    """The synthetic charts use real PGC/SAT codes, so all should hit Tier-1."""
    engine = ConsolidationEngine()
    for tb in (build_parent_spain(), build_subsidiary_mexico()):
        for e in tb.entries:
            kid, tier, conf = engine.resolve(e, tb.jurisdiction)
            assert kid is not None, f"{tb.jurisdiction}:{e.code} did not resolve"
            assert tier == "tier1_exact"
            assert conf == 1.0


def test_consolidated_trial_balance_balances():
    result = reconcile()
    assert result.is_balanced(), f"balance diff = {result.balance_difference}"
    assert result.balance_difference == 0.0
    assert result.total_debits == result.total_credits
    assert result.total_debits > 0


def test_no_escalations_in_the_curated_demo():
    result = reconcile()
    assert result.escalations == []


def test_intercompany_elimination_is_applied():
    result = reconcile()
    assert result.eliminations_applied == 1


def test_elimination_reduces_receivables_and_payables_by_intercompany_amount():
    engine = ConsolidationEngine()
    subs = [build_parent_spain(), build_subsidiary_mexico()]

    without = engine.consolidate(subs, eliminations=[])
    with_elim = engine.consolidate(subs, eliminations=intercompany_links())

    def net(result, kid):
        return next(l.net_usd for l in result.lines if l.kontablo_id == kid)

    # Receivables (debit node): net drops by the intercompany USD amount.
    assert round(net(without, "asset.current.receivables")
                 - net(with_elim, "asset.current.receivables"), 2) == INTERCOMPANY_USD
    # Payables (credit node): net (debit-credit, i.e. negative) rises by the
    # amount because a credit was removed.
    assert round(net(with_elim, "liability.current.payables")
                 - net(without, "liability.current.payables"), 2) == INTERCOMPANY_USD

    # The group still balances both with and without elimination.
    assert without.is_balanced()
    assert with_elim.is_balanced()


def test_skipped_elimination_is_surfaced_not_silent():
    """An elimination whose leg never resolved must be flagged, not dropped."""
    from core.engine import IntercompanyLink

    engine = ConsolidationEngine()
    subs = [build_parent_spain(), build_subsidiary_mexico()]
    bogus = [IntercompanyLink("a", "asset.current.receivables", "b",
                              "nonexistent.node.id", 50_000.0)]
    result = engine.consolidate(subs, eliminations=bogus)
    assert result.eliminations_applied == 0
    assert any("elimination_skipped" in f for f in result.cra_flags)
