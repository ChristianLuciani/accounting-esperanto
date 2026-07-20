"""Mapping provenance for the Kontablo harness.

``MappingQuote`` is the account-resolution analogue of ``FXQuote``
(``core.harness.fx_provider``): every resolution of a local statutory account to
a universal Kontablo node produces an attachable, auditable record of *how* the
decision was made — which deterministic tier answered, which exact rule fired,
and with what confidence. This is the lossless-translation guarantee at the
entry level (ADR-016): the local code and name are never discarded by the
translation, and the decision path is reconstructible without re-running the
resolver.

Nothing here calls an LLM. ``rule_id`` values are stable, deterministic
identifiers:

  * ``tier1:<jurisdiction>:<local_code>``  — exact Tier-1 index hit
  * ``tier2:<kontablo_id>:<keyword>``      — the Tier-2 keyword that matched
  * ``None``                               — escalated (no deterministic rule)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from core.harness.fx_provider import _utcnow_iso


@dataclass(frozen=True)
class MappingQuote:
    """Provenance of one local-account -> Kontablo-node resolution.

    Mirrors the ``FXQuote`` audit pattern: attach it to the resolved entry so
    the consolidated statement carries a per-entry mapping audit trail.
    """

    local_code: str
    local_name: str
    jurisdiction: str
    kontablo_id: Optional[str]  # None = escalated (explicit, never silent)
    kontablo_uuid: Optional[str]
    tier: str  # "tier1_exact" | "tier2_keyword" | "escalated"
    confidence: float
    rule_id: Optional[str]  # deterministic rule identifier (see module docstring)
    resolved_at: str  # ISO-8601 UTC timestamp of this resolution

    @property
    def resolved(self) -> bool:
        return self.kontablo_id is not None


def mapping_quote(
    *,
    local_code: str,
    local_name: str,
    jurisdiction: str,
    kontablo_id: Optional[str],
    kontablo_uuid: Optional[str],
    tier: str,
    confidence: float,
    rule_id: Optional[str],
) -> MappingQuote:
    """Build a :class:`MappingQuote` stamped with the current UTC time."""
    return MappingQuote(
        local_code=str(local_code),
        local_name=local_name,
        jurisdiction=jurisdiction,
        kontablo_id=kontablo_id,
        kontablo_uuid=kontablo_uuid,
        tier=tier,
        confidence=confidence,
        rule_id=rule_id,
        resolved_at=_utcnow_iso(),
    )
