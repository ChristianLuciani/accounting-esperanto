"""The ontology is a DAG, not a tree (ADR-016, principle #1): every core node
carries multiple simultaneous rollup lenses (``groupings``), ``rollup()``
partitions the graph under any lens, and ``node_fiber()`` answers the inverse
question — which local codes collapse into a node — across the Tier-1 index
and the v2 localization structure. Deterministic; no LLM, no network."""

from core.harness import (
    load_families,
    load_ontology,
    merge_family_codes,
    node_fiber,
    rollup,
)

CF_VALUES = {"cash_and_equivalents", "operating", "investing", "financing"}


def _graph():
    accounts, by_code, _collisions, _placeholders = load_ontology()
    by_code = merge_family_codes(by_code, load_families())
    return accounts, by_code


def test_every_core_node_carries_both_lenses():
    accounts, _ = _graph()
    assert len(accounts) == 30
    for kid, node in accounts.items():
        groupings = node["groupings"]
        # Primary IFRS lens is composed from parent — single source of truth.
        assert groupings["ifrs"], f"{kid} lost its ifrs lens"
        assert groupings["cash_flow"] in CF_VALUES, (
            f"{kid} has no valid cash_flow lens: {groupings.get('cash_flow')!r}"
        )


def test_rollup_is_a_partition_under_any_lens():
    accounts, _ = _graph()
    for lens in ("ifrs", "cash_flow"):
        buckets = rollup(accounts, lens)
        # No silent loss: every node lands in exactly one bucket.
        members = [kid for ids in buckets.values() for kid in ids]
        assert sorted(members) == sorted(accounts)
        assert None not in buckets, f"nodes missing the {lens} lens: {buckets.get(None)}"
    # The two lenses genuinely differ (multi-parent, not a relabeled tree):
    # e.g. short-term debt sits with current liabilities under IFRS but with
    # long-term debt under the financing lens.
    ifrs = rollup(accounts, "ifrs")
    cf = rollup(accounts, "cash_flow")
    assert "liability.current.short_term_debt" in ifrs["liability.current"]
    assert "liability.current.short_term_debt" in cf["financing"]
    assert "liability.noncurrent.debt" in cf["financing"]
    assert "liability.current.payables" in cf["operating"]


def test_unknown_lens_groups_all_under_none():
    accounts, _ = _graph()
    buckets = rollup(accounts, "no_such_lens")
    assert set(buckets) == {None}
    assert sorted(buckets[None]) == sorted(accounts)


def test_node_fiber_tier1_view_spans_jurisdictions():
    accounts, by_code = _graph()
    fiber = node_fiber(accounts, by_code, "asset.current.cash")
    assert fiber["kontablo_id"] == "asset.current.cash"
    assert fiber["total_codes"] > 20  # local_codes overlay + chart families
    # Every member of the unfiltered view comes from the Tier-1 index.
    for members in fiber["jurisdictions"].values():
        for m in members:
            assert m["source"] == "tier1_index"


def test_node_fiber_jurisdiction_enrichment_carries_v2_structure():
    accounts, by_code = _graph()
    fiber = node_fiber(accounts, by_code, "asset.current.cash", jurisdiction="de")
    assert set(fiber["jurisdictions"]) == {"de"}
    members = {m["code"]: m for m in fiber["jurisdictions"]["de"]}
    # SKR04 Kasse from the localization file, with its local tree edge.
    assert members["1600"]["source"] == "localization"
    assert members["1600"]["name"] == "Kasse"
    assert members["1600"]["local_parent"] == "1"
    # And the facet axis survives on VAT output.
    vat = node_fiber(accounts, by_code, "liability.current.vat_output", jurisdiction="mx")
    mx = {m["code"]: m for m in vat["jurisdictions"].get("mx", [])}
    assert mx["208"]["facets"]["tax"] == "output_transferred"


def test_node_fiber_unknown_node_is_none():
    accounts, by_code = _graph()
    assert node_fiber(accounts, by_code, "does.not.exist") is None


def test_mcp_get_node_fiber_tool():
    from api.mcp.server import build_engine, get_node_fiber_impl

    engine = build_engine()
    out = get_node_fiber_impl(engine, kontablo_id="asset.current.cash", jurisdiction="de")
    assert out["found"] is True
    assert out["total_codes"] >= 2
    missing = get_node_fiber_impl(engine, kontablo_id="does.not.exist")
    assert missing["found"] is False
    by_uuid = get_node_fiber_impl(
        engine, uuid="00000000-0000-4000-8000-000000000101"
    )
    assert by_uuid["found"] is True
    assert by_uuid["kontablo_id"] == "asset.current.cash"


def test_rest_fiber_endpoint():
    from fastapi.testclient import TestClient

    from api.src.main import app

    client = TestClient(app, raise_server_exceptions=False)
    r = client.get("/accounts/asset.current.cash/fiber", params={"jurisdiction": "de"})
    assert r.status_code == 200
    body = r.json()
    codes = {m["code"] for m in body["jurisdictions"]["de"]}
    assert "1600" in codes
    assert client.get("/accounts/does.not.exist/fiber").status_code == 404
