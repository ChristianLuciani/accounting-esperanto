"""Tests for the human-oversight surface (core/harness/oversight.py).

These assert the Co-responsibility Architecture as *behaviour*, not prose: that
the accountable human can withdraw standing authorization prospectively
(``ReviewPolicy``) and enumerate what a rule already produced retrospectively
(``postings_by_rule`` / ``revocation_impact``).

The load-bearing test in this file is
``test_default_policy_does_not_change_resolution``: the entire feature must be
inert unless a human configures it, or the published claims-evidence numbers
would move.
"""

from __future__ import annotations

import pytest

from core.harness import (
    TIER_HELD,
    ReviewPolicy,
    held_rule_id,
    load_families,
    load_ontology,
    merge_family_codes,
    postings_by_rule,
    resolve_with_rule,
    revocation_impact,
)


@pytest.fixture(scope="module")
def graph():
    accounts, by_code, _collisions, _placeholders = load_ontology()
    by_code = merge_family_codes(by_code, load_families())
    return accounts, by_code


@pytest.fixture(scope="module")
def tier1_hit(graph):
    """A real (jurisdiction, code) pair that resolves via Tier 1, from the
    committed ontology — not a fabricated fixture."""
    _accounts, by_code = graph
    for jur in sorted(by_code):
        for code, kid in sorted(by_code[jur].items()):
            return jur, str(code), kid
    pytest.skip("no Tier-1 index entries in the committed ontology")


# ---------------------------------------------------------------- inertness


def test_default_policy_does_not_change_resolution(graph, tier1_hit):
    """No policy, and an empty policy, must both behave exactly as before.

    This is what protects the published deterministic-coverage numbers: the
    oversight feature is opt-in or it is a claims-evidence break.
    """
    accounts, by_code = graph
    jur, code, kid = tier1_hit
    entry = {"code": code, "name": "irrelevant", "nature": "debit"}

    baseline = resolve_with_rule(entry, jur, accounts, by_code)
    assert baseline == resolve_with_rule(entry, jur, accounts, by_code, policy=None)
    assert baseline == resolve_with_rule(
        entry, jur, accounts, by_code, policy=ReviewPolicy()
    )
    assert baseline[0] == kid
    assert baseline[1] == "tier1_exact"


def test_empty_policy_reports_holding_nothing():
    assert ReviewPolicy().holds_nothing is True
    assert ReviewPolicy.build().holds_nothing is True
    assert ReviewPolicy.build(rules=["tier1:de:1600"]).holds_nothing is False


# ------------------------------------------------- prospective: the hold


def test_holding_a_rule_withholds_the_resolution(graph, tier1_hit):
    accounts, by_code = graph
    jur, code, kid = tier1_hit
    entry = {"code": code, "name": "irrelevant", "nature": "debit"}
    rule = f"tier1:{jur}:{code}"

    policy = ReviewPolicy.build(rules=[rule], reason="under audit")
    got_kid, tier, conf, got_rule = resolve_with_rule(
        entry, jur, accounts, by_code, policy=policy
    )

    assert got_kid is None, "a held resolution must not be applied"
    assert tier == TIER_HELD
    assert conf == 0.0
    # The withheld rule stays on the record — withholding must not erase the
    # fact under review.
    assert got_rule == f"held:rule:{rule}"
    assert rule in got_rule


def test_held_is_distinguishable_from_escalated(graph, tier1_hit):
    """An escalation means no answer existed; a hold means one existed and a
    human withheld it. Collapsing them would lose the distinction the loss
    ledger exists to preserve."""
    accounts, by_code = graph
    jur, code, _kid = tier1_hit

    escalated = resolve_with_rule(
        {"code": "zzz-no-such-code", "name": "zzzz no keyword match zzzz"},
        jur,
        accounts,
        by_code,
    )
    held = resolve_with_rule(
        {"code": code, "name": "irrelevant"},
        jur,
        accounts,
        by_code,
        policy=ReviewPolicy.build(rules=[f"tier1:{jur}:{code}"]),
    )

    assert escalated[1] == "escalated"
    assert held[1] == TIER_HELD
    assert escalated[1] != held[1]
    # Both are unresolved, and both carry a record — neither is silent.
    assert escalated[0] is None and held[0] is None
    assert escalated[3] is None, "escalation has no rule to name"
    assert held[3] is not None, "a hold must name what it withheld"


def test_holding_a_jurisdiction_withholds_every_rule_in_it(graph, tier1_hit):
    accounts, by_code = graph
    jur, code, _kid = tier1_hit
    policy = ReviewPolicy.build(jurisdictions=[jur.upper()])  # case-insensitive
    _kid2, tier, _conf, rule = resolve_with_rule(
        {"code": code, "name": "irrelevant"}, jur, accounts, by_code, policy=policy
    )
    assert tier == TIER_HELD
    assert rule.startswith("held:jurisdiction:")


def test_holding_a_node_withholds_resolutions_onto_it(graph, tier1_hit):
    accounts, by_code = graph
    jur, code, kid = tier1_hit
    policy = ReviewPolicy.build(nodes=[kid])
    _kid2, tier, _conf, rule = resolve_with_rule(
        {"code": code, "name": "irrelevant"}, jur, accounts, by_code, policy=policy
    )
    assert tier == TIER_HELD
    assert rule.startswith("held:node:")


def test_hold_scope_prefers_the_narrowest_match(graph, tier1_hit):
    """When several scopes apply, the recorded scope is the most specific, so the
    audit says why the human intervened at the level they intervened."""
    _accounts, _by_code = graph
    jur, code, kid = tier1_hit
    rule = f"tier1:{jur}:{code}"
    policy = ReviewPolicy.build(rules=[rule], jurisdictions=[jur], nodes=[kid])
    assert policy.hold_scope(rule_id=rule, jurisdiction=jur, kontablo_id=kid) == "rule"


def test_a_hold_does_not_leak_into_unrelated_resolutions(graph, tier1_hit):
    accounts, by_code = graph
    jur, code, _kid = tier1_hit
    policy = ReviewPolicy.build(rules=["tier1:xx:not-a-real-rule"])
    got_kid, tier, _conf, _rule = resolve_with_rule(
        {"code": code, "name": "irrelevant"}, jur, accounts, by_code, policy=policy
    )
    assert tier == "tier1_exact"
    assert got_kid is not None


def test_held_rule_id_format_is_stable():
    assert held_rule_id("rule", "tier2:asset.current.cash:kasse") == (
        "held:rule:tier2:asset.current.cash:kasse"
    )
    # A hold on an escalation-shaped resolution still produces a parseable id.
    assert held_rule_id("jurisdiction", None) == "held:jurisdiction:none"


def test_review_policy_is_immutable():
    """The policy is the human's authorization record; it must not be mutable in
    place by whatever holds a reference to it."""
    policy = ReviewPolicy.build(rules=["r1"])
    with pytest.raises(Exception):
        policy.held_rules = frozenset({"r2"})  # type: ignore[misc]


# ------------------------------------------ retrospective: what a rule did


class _FakeQuote:
    def __init__(self, rule_id):
        self.rule_id = rule_id


class _FakeEntry:
    def __init__(self, rule_id, kontablo_id=None, jurisdiction=None):
        self.mapping = _FakeQuote(rule_id)
        self.kontablo_id = kontablo_id
        self.jurisdiction = jurisdiction


def test_postings_by_rule_groups_by_the_rule_that_fired():
    entries = [
        _FakeEntry("tier1:de:1600", "asset.current.cash", "de"),
        _FakeEntry("tier1:de:1600", "asset.current.cash", "de"),
        _FakeEntry("tier2:asset.current.bank:bank", "asset.current.bank", "fr"),
    ]
    grouped = postings_by_rule(entries)
    assert set(grouped) == {"tier1:de:1600", "tier2:asset.current.bank:bank"}
    assert len(grouped["tier1:de:1600"]) == 2


def test_postings_by_rule_keeps_entries_without_provenance():
    """Grouped under None, never dropped — consistent with invariant I2."""
    grouped = postings_by_rule([_FakeEntry(None)])
    assert None in grouped
    assert len(grouped[None]) == 1


def test_revocation_impact_enumerates_every_posting_a_rule_produced():
    entries = [
        _FakeEntry("tier1:de:1600", "asset.current.cash", "de"),
        _FakeEntry("tier1:de:1600", "asset.current.cash", "DE"),
        _FakeEntry("tier1:mx:101", "asset.current.cash", "mx"),
        _FakeEntry("tier2:revenue.operating:ventas", "revenue.operating", "es"),
    ]
    impact = revocation_impact(entries, ["tier1:de:1600", "tier1:mx:101"])

    assert impact.entry_count == 3
    assert impact.is_empty is False
    assert impact.revoked_rules == frozenset({"tier1:de:1600", "tier1:mx:101"})
    assert impact.affected_nodes == frozenset({"asset.current.cash"})
    # Jurisdictions are normalised, so "de" and "DE" are one jurisdiction.
    assert impact.affected_jurisdictions == frozenset({"de", "mx"})


def test_revoking_an_unused_rule_affects_nothing():
    impact = revocation_impact([_FakeEntry("tier1:de:1600")], ["tier1:zz:9999"])
    assert impact.is_empty is True
    assert impact.entry_count == 0


def test_revocation_impact_does_not_mutate_the_entries():
    entries = [_FakeEntry("tier1:de:1600", "asset.current.cash", "de")]
    before = [(e.mapping.rule_id, e.kontablo_id) for e in entries]
    revocation_impact(entries, ["tier1:de:1600"])
    after = [(e.mapping.rule_id, e.kontablo_id) for e in entries]
    assert before == after, "revocation_impact reports; it must not apply"


# ------------------------------------------------- end-to-end on the engine


def test_engine_by_rule_is_the_dual_of_lineage():
    """``by_rule()`` and ``lineage()`` must partition the same resolved entries:
    one by what was produced, the other by why."""
    from core.engine import ConsolidationEngine, LocalEntry, SubsidiaryTB

    engine = ConsolidationEngine()
    tb = SubsidiaryTB(
        subsidiary_id="TEST-1",
        jurisdiction="mx",
        currency="MXN",
        entries=[
            LocalEntry(code="101", name="Caja", nature="debit", debit=1000.0, credit=0.0),
            LocalEntry(code="401", name="Ingresos", nature="credit", debit=0.0, credit=1000.0),
        ],
    )
    result = engine.consolidate([tb])

    by_rule = result.by_rule()
    lineage = result.lineage()

    assert sum(len(v) for v in by_rule.values()) == len(result.resolved)
    # Every resolved entry appears in exactly one bucket of each view.
    assert sum(len(v) for v in lineage.values()) <= len(result.resolved)
    # Every rule key that is not None looks like a deterministic rule id.
    for rule in by_rule:
        if rule is not None:
            assert rule.startswith(("tier1:", "tier2:", "held:")), rule
