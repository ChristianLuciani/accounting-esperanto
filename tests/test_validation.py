"""Unit tests for the shared monetary-input invariants (core.harness.validation).

These guarantee one definition of "valid accounting amount" across REST, gRPC,
and MCP — a non-finite amount or non-positive FX rate must raise, finite values
must pass through unchanged.
"""

import math

import pytest

from core.harness.validation import ensure_finite, ensure_positive_finite, is_finite_number


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), float("-inf")])
def test_ensure_finite_rejects_non_finite(bad):
    with pytest.raises(ValueError) as exc:
        ensure_finite(bad, "debit")
    assert "debit" in str(exc.value)


@pytest.mark.parametrize("good", [0.0, -100.0, 1234.56, 1e308])
def test_ensure_finite_accepts_finite(good):
    assert ensure_finite(good, "x") == good


@pytest.mark.parametrize("bad", [0.0, -1.0, -0.001, float("nan"), float("inf")])
def test_ensure_positive_finite_rejects(bad):
    with pytest.raises(ValueError):
        ensure_positive_finite(bad, "fx_rate")


@pytest.mark.parametrize("good", [0.001, 1.0, 18.5])
def test_ensure_positive_finite_accepts(good):
    assert ensure_positive_finite(good, "fx_rate") == good


def test_is_finite_number():
    assert is_finite_number(3) is True
    assert is_finite_number(3.5) is True
    assert is_finite_number(float("nan")) is False
    assert is_finite_number(float("inf")) is False
    assert is_finite_number(None) is False
    assert is_finite_number(True) is False  # bool is not a monetary amount
    assert is_finite_number("3") is False
