"""
Kontablo deterministic consolidation engine (reusable core).

This module is the single deterministic ``resolve()`` + consolidate path shared
by:
  * the gRPC servicer (``api/grpc/server.py``),
  * the self-contained reconciliation example
    (``examples/transnational_reconciliation.py``), and
  * the real two-ERP walkthrough (``examples/two_erp_reconciliation/``).

It deliberately *imports* the resolution logic from the shared harness package
(``core.harness``) instead of re-implementing it, so that every surface uses the
exact same Tier-1 (local-code) and Tier-2 (multilingual keyword) rules that
produce the published 97.3% deterministic coverage number. Re-implementing the
rules here would let them drift out of sync with the harness behind the
claims-evidence gate — the documented failure mode this repo guards against.

Nothing in this module calls an LLM. Every decision is a graph lookup, a
deterministic keyword rule, or arithmetic. Intercompany eliminations key on
explicit structured fields (``IntercompanyLink``), never on free text — per
CLAUDE.md architectural principle #5 (determinism over stochasticity).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from core.harness import (
    cra_validate,
    load_families,
    load_ontology,
    merge_family_codes,
    resolve as harness_resolve,
)
from core.harness import FX as _HARNESS_FX
from core.harness import JCCY as _HARNESS_JCCY

# Re-export the canonical FX table so every surface normalises to USD identically.
FX: Dict[str, float] = dict(_HARNESS_FX)
JCCY: Dict[str, str] = dict(_HARNESS_JCCY)


@dataclass
class LocalEntry:
    """One row of a local trial balance, as pulled from an ERP."""

    code: str
    name: str
    debit: float = 0.0
    credit: float = 0.0
    nature: Optional[str] = None  # "debit" | "credit" | None
    # Optional explicit intercompany tag (deterministic, never inferred from text).
    intercompany_with: Optional[str] = None  # counterparty subsidiary_id


@dataclass
class SubsidiaryTB:
    """A subsidiary's trial balance in its local currency."""

    subsidiary_id: str
    jurisdiction: str  # ISO 3166-1 alpha-2, lowercase
    currency: str
    entries: List[LocalEntry] = field(default_factory=list)
    fx_rate_to_usd: Optional[float] = None  # overrides the FX table when set


@dataclass
class IntercompanyLink:
    """An explicit intercompany pair to eliminate on consolidation.

    Both legs are matched by (subsidiary_id, kontablo_id). The engine removes the
    USD amount from each leg's net balance — keeping the consolidated trial
    balance in balance because it drops one debit and one equal credit.
    """

    from_subsidiary: str
    from_kontablo_id: str
    to_subsidiary: str
    to_kontablo_id: str
    amount_usd: float


@dataclass
class ResolvedEntry:
    subsidiary_id: str
    jurisdiction: str
    local_code: str
    local_name: str
    kontablo_id: Optional[str]
    tier: str
    confidence: float
    debit_usd: float
    credit_usd: float
    cra_flags: List[str] = field(default_factory=list)


@dataclass
class ConsolidatedLine:
    kontablo_id: str
    label_en: str
    nature: str
    statement: str
    debit_usd: float
    credit_usd: float

    @property
    def net_usd(self) -> float:
        return round(self.debit_usd - self.credit_usd, 2)


@dataclass
class ConsolidationResult:
    target_currency: str
    lines: List[ConsolidatedLine]
    resolved: List[ResolvedEntry]
    eliminations_applied: int
    escalations: List[ResolvedEntry]
    cra_flags: List[str]

    @property
    def total_debits(self) -> float:
        return round(sum(l.debit_usd for l in self.lines), 2)

    @property
    def total_credits(self) -> float:
        return round(sum(l.credit_usd for l in self.lines), 2)

    @property
    def balance_difference(self) -> float:
        """Σdebits − Σcredits. A balanced trial balance yields ~0.0."""
        return round(self.total_debits - self.total_credits, 2)

    def is_balanced(self, tolerance: float = 0.05) -> bool:
        return abs(self.balance_difference) <= tolerance


class ConsolidationEngine:
    """Loads the real Level-3 ontology once and drives deterministic
    resolution + cross-border consolidation with intercompany elimination."""

    def __init__(self):
        # accounts: kontablo_id -> {uuid,label,nature,statement,local_codes}
        # by_code:  jurisdiction -> {local_code -> kontablo_id}
        self.accounts, self.by_code, self.collisions, self.placeholders = load_ontology()
        families = load_families()
        self.by_code = merge_family_codes(self.by_code, families)

    # -- resolution ---------------------------------------------------------
    def resolve(self, entry: LocalEntry, jurisdiction: str) -> Tuple[Optional[str], str, float]:
        """Return (kontablo_id, tier, confidence) using the harness resolver."""
        return harness_resolve(
            {"code": entry.code, "name": entry.name, "nature": entry.nature},
            jurisdiction.lower(),
            self.accounts,
            self.by_code,
        )

    def fx_to_usd(self, tb: SubsidiaryTB) -> float:
        if tb.fx_rate_to_usd is not None:
            return tb.fx_rate_to_usd
        ccy = tb.currency.upper()
        if ccy not in FX:
            # A silent 1.0 fallback would consolidate mislabeled amounts;
            # an unknown currency must be an explicit caller error.
            raise ValueError(
                f"no FX rate for currency {ccy!r} (subsidiary "
                f"{tb.subsidiary_id}); pass fx_rate_to_usd explicitly."
            )
        return FX[ccy]

    # -- consolidation ------------------------------------------------------
    def consolidate(
        self,
        subsidiaries: List[SubsidiaryTB],
        eliminations: Optional[List[IntercompanyLink]] = None,
        target_currency: str = "USD",
    ) -> ConsolidationResult:
        # v0.x consolidates in USD only. Refuse anything else explicitly
        # rather than silently labelling USD figures with another currency.
        if target_currency.upper() != "USD":
            raise ValueError(
                f"target_currency={target_currency!r} is not supported: "
                "v0.x consolidates in USD only (multi-target FX is roadmap)."
            )
        eliminations = eliminations or []
        # kontablo_id -> {"debit": x, "credit": y}
        agg: Dict[str, Dict[str, float]] = {}
        resolved: List[ResolvedEntry] = []
        escalations: List[ResolvedEntry] = []
        cra_flags: List[str] = []

        for tb in subsidiaries:
            rate = self.fx_to_usd(tb)
            for e in tb.entries:
                kid, tier, conf = self.resolve(e, tb.jurisdiction)
                debit_usd = round(e.debit * rate, 2)
                credit_usd = round(e.credit * rate, 2)
                flags = cra_validate(
                    {"code": e.code, "name": e.name, "nature": e.nature},
                    kid,
                    self.accounts,
                )
                rec = ResolvedEntry(
                    subsidiary_id=tb.subsidiary_id,
                    jurisdiction=tb.jurisdiction,
                    local_code=e.code,
                    local_name=e.name,
                    kontablo_id=kid,
                    tier=tier,
                    confidence=conf,
                    debit_usd=debit_usd,
                    credit_usd=credit_usd,
                    cra_flags=flags,
                )
                resolved.append(rec)
                if flags:
                    cra_flags.extend(f"{tb.subsidiary_id}:{f}" for f in flags)
                if kid is None:
                    escalations.append(rec)
                    continue
                slot = agg.setdefault(kid, {"debit": 0.0, "credit": 0.0})
                slot["debit"] += debit_usd
                slot["credit"] += credit_usd

        # -- intercompany elimination (deterministic, structured) ----------
        applied = 0
        for link in eliminations:
            f = agg.get(link.from_kontablo_id)
            t = agg.get(link.to_kontablo_id)
            if f is None or t is None:
                # Cannot eliminate a leg that did not resolve; surface honestly.
                cra_flags.append(
                    f"elimination_skipped:{link.from_subsidiary}->{link.to_subsidiary}"
                    f":missing_leg({link.from_kontablo_id}|{link.to_kontablo_id})"
                )
                continue
            amt = round(link.amount_usd, 2)
            from_node = self.accounts[link.from_kontablo_id]
            to_node = self.accounts[link.to_kontablo_id]
            # Remove the amount from the side it sits on for each leg, so the
            # books stay balanced (one debit and one credit of equal size drop).
            self._unbook(f, from_node["nature"], amt)
            self._unbook(t, to_node["nature"], amt)
            applied += 1

        lines: List[ConsolidatedLine] = []
        for kid, v in sorted(agg.items()):
            node = self.accounts[kid]
            lines.append(
                ConsolidatedLine(
                    kontablo_id=kid,
                    label_en=node["label"],
                    nature=node["nature"],
                    statement=node["statement"],
                    debit_usd=round(v["debit"], 2),
                    credit_usd=round(v["credit"], 2),
                )
            )

        return ConsolidationResult(
            target_currency=target_currency,
            lines=lines,
            resolved=resolved,
            eliminations_applied=applied,
            escalations=escalations,
            cra_flags=cra_flags,
        )

    @staticmethod
    def _unbook(slot: Dict[str, float], nature: str, amount: float) -> None:
        """Remove ``amount`` from the natural side of a node's running balance."""
        if nature == "debit":
            slot["debit"] = round(slot["debit"] - amount, 2)
        else:
            slot["credit"] = round(slot["credit"] - amount, 2)
