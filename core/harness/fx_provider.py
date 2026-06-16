"""Runtime foreign-exchange resolution for Kontablo.

The static ``core.harness.fx.FX`` table is a *pinned* set of synthetic rates —
deliberately frozen so the validation harness reproduces byte-identical results
(the claims-evidence gate). A real deployment, however, must price local
balances at current rates, otherwise the consolidation is fiction. This module
adds that: a small pluggable provider layer that resolves USD-per-unit rates at
runtime, with graceful degradation.

Provider chain (most authoritative first):

  1. **Frankfurter** — `https://api.frankfurter.dev` — published by the European
     Central Bank (ECB) reference rates. Authoritative primary source, but ECB
     publishes only ~30 major currencies.
  2. **open.er-api.com** (ExchangeRate-API open endpoint) — ~160 currencies,
     no key, daily updates. Covers the exotic / hyperinflation currencies (VES,
     LBP, XOF, …) that the ECB set does not.
  3. **Static pinned table** — `core.harness.fx.FX`. Offline, deterministic
     last resort; also the value the validation harness always uses.

Determinism contract: ``get_fx_provider()`` is **env-gated**. The validation
harness and the test session never touch the network (the test session forces
``KONTABLO_FX_MODE=static`` in ``conftest.py``); production runtime defaults to
``live``. Set ``KONTABLO_FX_MODE=static`` to force offline/pinned behaviour and
``KONTABLO_FX_MODE=live`` (the default) for live rates with static fallback.

Verify a rate independently, e.g.:
    curl 'https://api.frankfurter.dev/v1/latest?base=USD&symbols=EUR'
    curl 'https://open.er-api.com/v6/latest/USD'

No third-party HTTP dependency: uses the standard library ``urllib``.
"""

from __future__ import annotations

import json
import os
import threading
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

from core.harness.fx import FX as STATIC_FX


def _utcnow_iso() -> str:
    """ISO-8601 UTC timestamp (second precision) for audit records."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


@dataclass(frozen=True)
class FXQuote:
    """An auditable, attachable record of *which* rate priced a balance and
    *where it came from*. One quote is produced per currency conversion so it
    can be stamped onto the transaction / resolved entry that used it.

    Fields:
      * ``usd_per_unit`` — the rate applied (USD value of one unit of ``currency``).
      * ``source``       — provider id: ``frankfurter-ecb`` | ``open-er-api`` |
                            ``static-pinned`` | ``manual``.
      * ``mode``         — ``live`` | ``static`` | ``manual``.
      * ``as_of``        — the rate's upstream publication date/time (ECB ``date``,
                            ExchangeRate-API ``time_last_update_utc``), or the
                            operator-supplied as-of for a manual rate. ``None``
                            for the pinned static table (synthetic, undated).
      * ``retrieved_at`` — when this quote was produced / applied (UTC).
      * ``note``         — free-text rationale, used mainly for manual rates
                            (e.g. ``"contract rate, invoice 2026-03-31"``).
    """

    currency: str
    usd_per_unit: float
    source: str
    mode: str
    retrieved_at: str
    as_of: Optional[str] = None
    note: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


def manual_quote(
    currency: str,
    usd_per_unit: float,
    as_of: Optional[str] = None,
    note: Optional[str] = None,
) -> FXQuote:
    """Build an audited manual FX quote — for an asynchronous transaction priced
    at an operator-supplied rate (contract rate, invoice-date rate, agreed
    intercompany rate). ``as_of`` records the rate's effective date and ``note``
    the rationale, so a manual override is as traceable as a fetched one."""
    return FXQuote(
        currency=currency.upper(),
        usd_per_unit=float(usd_per_unit),
        source="manual",
        mode="manual",
        retrieved_at=_utcnow_iso(),
        as_of=as_of,
        note=note,
    )


# Default cache TTL: FX reference rates publish at most daily, so a multi-hour
# cache is correct and keeps a busy API from hammering the upstream endpoints.
_DEFAULT_TTL_SECONDS = 6 * 3600
_DEFAULT_TIMEOUT_SECONDS = 8.0
_USER_AGENT = "Kontablo-FX/1.0 (+https://github.com/ChristianLuciani/accounting-esperanto)"


class FXProvider:
    """Resolve the USD value of one unit of ``currency`` (ISO 4217).

    ``usd_per_unit('EUR')`` returns e.g. ``1.08`` (1 EUR = 1.08 USD). Returns
    ``None`` when the provider cannot price the currency, so a caller (or the
    chain) can fall through to the next source."""

    name = "abstract"
    mode = "static"

    def usd_per_unit(self, currency: str) -> Optional[float]:  # pragma: no cover - interface
        raise NotImplementedError

    def _as_of(self, currency: str) -> Optional[str]:
        """Upstream publication date/time of the rate, if the provider knows it."""
        return None

    def quote(self, currency: str) -> Optional[FXQuote]:
        """Resolve the rate *and* its provenance as an attachable ``FXQuote``.
        Returns ``None`` when the provider cannot price the currency."""
        rate = self.usd_per_unit(currency)
        if rate is None:
            return None
        return FXQuote(
            currency=currency.upper(),
            usd_per_unit=rate,
            source=self.name,
            mode=self.mode,
            retrieved_at=_utcnow_iso(),
            as_of=self._as_of(currency),
        )


class StaticFXProvider(FXProvider):
    """Offline provider backed by a pinned ``{CCY: usd_per_unit}`` table.

    Defaults to ``core.harness.fx.FX`` — the same values the validation harness
    uses — so a static-mode runtime reproduces the documented numbers exactly."""

    name = "static-pinned"
    mode = "static"

    def __init__(self, table: Optional[Dict[str, float]] = None):
        src = STATIC_FX if table is None else table
        self._table = {k.upper(): float(v) for k, v in src.items()}

    def usd_per_unit(self, currency: str) -> Optional[float]:
        currency = currency.upper()
        if currency == "USD":
            return 1.0  # rates are USD-denominated: USD per USD is identity
        return self._table.get(currency)


class _HTTPTableProvider(FXProvider):
    """Base class: fetch a USD-based rate table once, cache it with a TTL, and
    invert each quote (units-per-USD) to USD-per-unit.

    On any network/parse failure the cached table (possibly stale, possibly
    ``None``) is returned, so the provider degrades quietly rather than raising
    into the consolidation path."""

    url = ""
    mode = "live"

    def __init__(self, ttl_seconds: Optional[float] = None, timeout_seconds: Optional[float] = None):
        self._ttl = _DEFAULT_TTL_SECONDS if ttl_seconds is None else ttl_seconds
        self._timeout = _DEFAULT_TIMEOUT_SECONDS if timeout_seconds is None else timeout_seconds
        self._cache: Optional[Dict[str, float]] = None  # {CCY: units-per-USD}
        self._as_of_value: Optional[str] = None  # upstream publication date/time
        self._fetched_at = 0.0
        self._lock = threading.Lock()

    def _parse(self, payload: dict) -> Dict[str, float]:  # pragma: no cover - overridden
        """Return ``{CCY: units-per-USD}`` from the provider's JSON payload."""
        raise NotImplementedError

    def _parse_as_of(self, payload: dict) -> Optional[str]:
        """The rate's upstream publication date/time, if the payload carries it."""
        return None

    def _as_of(self, currency: str) -> Optional[str]:
        self._table()  # ensure a fetch has happened so _as_of_value is populated
        return self._as_of_value

    def _fresh(self) -> bool:
        return self._cache is not None and (time.time() - self._fetched_at) < self._ttl

    def _table(self) -> Optional[Dict[str, float]]:
        if self._fresh():
            return self._cache
        with self._lock:
            if self._fresh():
                return self._cache
            try:
                req = urllib.request.Request(self.url, headers={"User-Agent": _USER_AGENT})
                with urllib.request.urlopen(req, timeout=self._timeout) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
                table = self._parse(payload)
                if table:
                    self._cache = {k.upper(): float(v) for k, v in table.items() if v}
                    self._as_of_value = self._parse_as_of(payload)
                    self._fetched_at = time.time()
            except (urllib.error.URLError, ValueError, KeyError, TypeError, TimeoutError, OSError):
                # Upstream unreachable or malformed: keep whatever we last had
                # (may be a usable stale table, or None) and let the chain fall
                # through to the static provider.
                return self._cache
        return self._cache

    def usd_per_unit(self, currency: str) -> Optional[float]:
        currency = currency.upper()
        if currency == "USD":
            return 1.0
        table = self._table()
        if not table:
            return None
        units_per_usd = table.get(currency)
        if not units_per_usd:
            return None
        return 1.0 / units_per_usd


class FrankfurterProvider(_HTTPTableProvider):
    """ECB reference rates via Frankfurter (no API key)."""

    name = "frankfurter-ecb"
    url = "https://api.frankfurter.dev/v1/latest?base=USD"

    def _parse(self, payload: dict) -> Dict[str, float]:
        return payload.get("rates", {}) or {}

    def _parse_as_of(self, payload: dict) -> Optional[str]:
        return payload.get("date")  # ECB reference-rate date, e.g. "2026-06-16"


class OpenExchangeRateProvider(_HTTPTableProvider):
    """Broad-coverage rates via open.er-api.com (ExchangeRate-API, no API key)."""

    name = "open-er-api"
    url = "https://open.er-api.com/v6/latest/USD"

    def _parse(self, payload: dict) -> Dict[str, float]:
        if payload.get("result") != "success":
            return {}
        return payload.get("rates", {}) or {}

    def _parse_as_of(self, payload: dict) -> Optional[str]:
        # e.g. "Tue, 16 Jun 2026 00:02:31 +0000"
        return payload.get("time_last_update_utc")


class ChainedFXProvider(FXProvider):
    """Try each provider in order; the first non-``None`` quote wins."""

    name = "chained"

    def __init__(self, providers: List[FXProvider]):
        self.providers = list(providers)

    def usd_per_unit(self, currency: str) -> Optional[float]:
        name, rate = self.resolve(currency)
        return rate

    def resolve(self, currency: str) -> Tuple[Optional[str], Optional[float]]:
        """Like ``usd_per_unit`` but also returns the name of the provider that
        answered — useful for audit logging which source priced a balance."""
        for provider in self.providers:
            try:
                rate = provider.usd_per_unit(currency)
            except Exception:  # a misbehaving provider must not break the chain
                rate = None
            if rate is not None:
                return provider.name, rate
        return None, None

    def quote(self, currency: str) -> Optional[FXQuote]:
        """Return the full provenance quote from the first provider that can
        price ``currency`` (carrying that provider's source, mode, and as-of)."""
        for provider in self.providers:
            try:
                q = provider.quote(currency)
            except Exception:  # a misbehaving provider must not break the chain
                q = None
            if q is not None:
                return q
        return None


# ---------------------------------------------------------------------------
# Default provider selection (env-gated; default live with static fallback)
# ---------------------------------------------------------------------------
_STATIC_SINGLETON = StaticFXProvider()
_LIVE_SINGLETON: Optional[ChainedFXProvider] = None
_LIVE_LOCK = threading.Lock()


def live_fx_provider() -> ChainedFXProvider:
    """The process-wide live chain: ECB → broad coverage → static fallback.
    Cached so the HTTP tables are fetched once per TTL across the process."""
    global _LIVE_SINGLETON
    if _LIVE_SINGLETON is None:
        with _LIVE_LOCK:
            if _LIVE_SINGLETON is None:
                _LIVE_SINGLETON = ChainedFXProvider(
                    [FrankfurterProvider(), OpenExchangeRateProvider(), _STATIC_SINGLETON]
                )
    return _LIVE_SINGLETON


def static_fx_provider() -> StaticFXProvider:
    """The process-wide static/pinned provider (offline, deterministic)."""
    return _STATIC_SINGLETON


def fx_mode(default: str = "live") -> str:
    """Resolve the FX mode from ``KONTABLO_FX_MODE`` (``live`` | ``static``)."""
    mode = os.environ.get("KONTABLO_FX_MODE", "").strip().lower()
    if mode in ("static", "offline", "pinned"):
        return "static"
    if mode in ("live", "online", "real"):
        return "live"
    return default


def get_fx_provider(live: Optional[bool] = None) -> FXProvider:
    """Return the default FX provider.

    ``live=None`` (the usual case) reads ``KONTABLO_FX_MODE`` — default ``live``
    for a production runtime, while the test session and CI force ``static`` so
    they stay hermetic and reproducible. Pass ``live`` explicitly to override."""
    if live is None:
        live = fx_mode() == "live"
    return live_fx_provider() if live else _STATIC_SINGLETON


def usd_per_unit(currency: str, provider: Optional[FXProvider] = None) -> Optional[float]:
    """Convenience: USD value of one unit of ``currency`` via the given (or
    default) provider."""
    return (provider or get_fx_provider()).usd_per_unit(currency)


def convert(
    amount: float,
    from_currency: str,
    to_currency: str = "USD",
    provider: Optional[FXProvider] = None,
) -> Optional[float]:
    """Convert ``amount`` from one currency to another via USD as the pivot.

    Returns ``None`` if either leg cannot be priced (caller decides whether that
    is an error). Cross rate = (USD per ``from``) / (USD per ``to``)."""
    if from_currency.upper() == to_currency.upper():
        return amount
    provider = provider or get_fx_provider()
    src = provider.usd_per_unit(from_currency)
    dst = provider.usd_per_unit(to_currency)
    if src is None or dst is None:
        return None
    return amount * (src / dst)
