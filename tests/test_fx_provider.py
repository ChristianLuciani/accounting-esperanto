"""Tests for the runtime FX provider (core.harness.fx_provider).

The deterministic tests (static table, chain fallback, cross-rate math, env
gating, inversion) never touch the network. The single live test is an
integration test, opt-in via ``KONTABLO_FX_LIVE_TEST=1`` so the default suite
(and CI) stays hermetic — a network outage or rate drift never reports the
deterministic core as broken (per the project's epistemic standard for
integration tests)."""

import os

import pytest

from core.harness.fx import FX
from core.harness.fx_provider import (
    ChainedFXProvider,
    FrankfurterProvider,
    StaticFXProvider,
    _HTTPTableProvider,
    convert,
    fx_mode,
    get_fx_provider,
    usd_per_unit,
)


# --- StaticFXProvider: pinned, deterministic --------------------------------
def test_static_provider_matches_pinned_table():
    p = StaticFXProvider()
    assert p.usd_per_unit("EUR") == FX["EUR"]
    assert p.usd_per_unit("eur") == FX["EUR"]  # case-insensitive
    assert p.usd_per_unit("USD") == 1.0
    assert p.usd_per_unit("ZZZ") is None  # unknown currency -> None, not a guess


def test_static_provider_custom_table():
    p = StaticFXProvider({"EUR": 2.0})
    assert p.usd_per_unit("EUR") == 2.0
    assert p.usd_per_unit("GBP") is None


# --- ChainedFXProvider: first non-None wins, fallback, audit ----------------
class _Fixed(StaticFXProvider):
    def __init__(self, name, table):
        super().__init__(table)
        self.name = name


def test_chain_falls_through_to_next_provider():
    empty = _Fixed("empty", {})
    backup = _Fixed("backup", {"VES": 0.027})
    chain = ChainedFXProvider([empty, backup])
    assert chain.usd_per_unit("VES") == 0.027
    name, rate = chain.resolve("VES")
    assert (name, rate) == ("backup", 0.027)


def test_chain_returns_none_when_no_provider_can_price():
    chain = ChainedFXProvider([_Fixed("a", {}), _Fixed("b", {})])
    assert chain.usd_per_unit("XOF") is None
    assert chain.resolve("XOF") == (None, None)


def test_chain_skips_a_raising_provider():
    class _Boom(StaticFXProvider):
        name = "boom"

        def usd_per_unit(self, currency):
            raise RuntimeError("upstream exploded")

    chain = ChainedFXProvider([_Boom(), _Fixed("ok", {"EUR": 1.08})])
    assert chain.usd_per_unit("EUR") == 1.08


# --- convert(): cross rate via USD pivot ------------------------------------
def test_convert_same_currency_is_identity():
    assert convert(100.0, "USD", "USD") == 100.0
    assert convert(100.0, "eur", "EUR") == 100.0


def test_convert_cross_rate_via_usd():
    p = StaticFXProvider({"EUR": 1.08, "GBP": 1.27})
    # 100 EUR -> USD = 108; -> GBP = 108 / 1.27
    assert convert(100.0, "EUR", "USD", provider=p) == pytest.approx(108.0)
    assert convert(100.0, "EUR", "GBP", provider=p) == pytest.approx(108.0 / 1.27)


def test_convert_unpriceable_returns_none():
    p = StaticFXProvider({"EUR": 1.08})
    assert convert(100.0, "EUR", "ZZZ", provider=p) is None


# --- HTTP provider inversion math (no network: stub the cached table) -------
def test_http_provider_inverts_units_per_usd():
    p = FrankfurterProvider()
    # Pretend the upstream returned: 1 USD = 0.86 EUR, 1 USD = 160 JPY.
    p._cache = {"EUR": 0.86, "JPY": 160.0}
    p._fetched_at = float("inf")  # never expire during the test
    assert p.usd_per_unit("EUR") == pytest.approx(1.0 / 0.86)
    assert p.usd_per_unit("JPY") == pytest.approx(1.0 / 160.0)
    assert p.usd_per_unit("USD") == 1.0


def test_http_provider_returns_none_without_a_table():
    class _Offline(_HTTPTableProvider):
        url = "http://0.0.0.0:1/never"

        def _parse(self, payload):
            return {}

    # Force a fetch that fails fast; cache stays None -> None (no static guess).
    p = _Offline(timeout_seconds=0.001)
    assert p.usd_per_unit("EUR") is None


# --- env gating -------------------------------------------------------------
def test_static_mode_selects_static_provider(monkeypatch):
    monkeypatch.setenv("KONTABLO_FX_MODE", "static")
    assert fx_mode() == "static"
    assert isinstance(get_fx_provider(), StaticFXProvider)
    # conftest forces static, so usd_per_unit is deterministic in the suite.
    assert usd_per_unit("EUR") == FX["EUR"]


def test_live_mode_selects_chain(monkeypatch):
    monkeypatch.setenv("KONTABLO_FX_MODE", "live")
    assert fx_mode() == "live"
    assert isinstance(get_fx_provider(), ChainedFXProvider)


def test_explicit_override_beats_env(monkeypatch):
    monkeypatch.setenv("KONTABLO_FX_MODE", "live")
    assert isinstance(get_fx_provider(live=False), StaticFXProvider)


# --- live integration (opt-in: KONTABLO_FX_LIVE_TEST=1) ---------------------
@pytest.mark.skipif(
    not os.environ.get("KONTABLO_FX_LIVE_TEST"),
    reason="FX live integration test: set KONTABLO_FX_LIVE_TEST=1 to run (hits the network)",
)
def test_live_frankfurter_returns_plausible_eur_rate():
    rate = FrankfurterProvider().usd_per_unit("EUR")
    assert rate is not None
    # A sanity band, not an exact assertion (rates move): 1 EUR is ~0.7–1.6 USD.
    assert 0.7 < rate < 1.6
