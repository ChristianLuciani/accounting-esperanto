"""Shared input-validation invariants for monetary values.

Single source of truth for "what is a valid accounting amount", used by every
Kontablo surface (REST, gRPC, MCP) so they cannot disagree at the boundary.

Why these are not optional in an accounting system:
  * A non-finite amount (NaN / ±Infinity) silently defeats the double-entry
    check — ``abs(NaN) > tol`` is ``False``, so a NaN "balances" — and is not
    valid JSON, so it later crashes response serialization with an unhandled
    500 instead of a clean rejection.
  * A non-positive FX rate corrupts every converted figure: ``0`` zeroes them,
    a negative rate sign-flips them, while still being stamped into the FX audit
    trail as if legitimate.

Each helper raises ``ValueError`` (the framework-neutral signal). Callers adapt:
Pydantic turns it into a 422, gRPC into ``INVALID_ARGUMENT``, FastMCP into a
structured tool error.
"""

from __future__ import annotations

import math
from typing import Optional


def ensure_finite(value: float, field: str = "value") -> float:
    """Return ``value`` if finite; otherwise raise ``ValueError``."""
    if not math.isfinite(value):
        raise ValueError(
            f"{field} must be a finite number (got {value!r}); "
            "NaN/Infinity are not valid accounting amounts."
        )
    return value


def ensure_positive_finite(value: float, field: str = "value") -> float:
    """Return ``value`` if it is finite and strictly > 0; else raise ``ValueError``.

    For FX rates: a currency's value in another currency is always positive."""
    ensure_finite(value, field)
    if value <= 0:
        raise ValueError(
            f"{field} must be > 0 (got {value!r}); a currency's value cannot be "
            "zero or negative."
        )
    return value


def is_finite_number(value: Optional[float]) -> bool:
    """True only for a finite ``int``/``float`` (not None, not NaN/Inf)."""
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)
