#!/usr/bin/env python3
"""Transnational reconciliation example — Spanish parent + Mexican subsidiary.

Self-contained, deterministic, no Docker and no live ERP required. This is the
canonical scenario the production-grade two-ERP end-to-end harness (``e2e/``)
mirrors: a Spanish parent on the PGC chart reporting in EUR, a Mexican
subsidiary on the SAT (Anexo 24) chart reporting in MXN, an intra-group
receivable/payable pair of equal economic value, consolidated to a single
presentation currency (EUR) with the intercompany position eliminated.

Why this file exists
--------------------
It is the *single source of truth* for the consolidation + elimination logic
and for the trial-balance fixtures. Three consumers import from here so they can
never silently diverge:

  * ``tests/test_example_reconciliation.py`` — fast unit assertions (no Docker).
  * ``e2e/runner.py`` — the Dockerized harness, which feeds trial balances
    pulled from two *real* ERPs (ERPNext + Odoo) through the very same
    :func:`reconcile` path.
  * this module's ``__main__`` — a runnable demo.

Determinism (CLAUDE.md principle #5)
------------------------------------
Account → Kontablo-node resolution reuses :func:`scripts.mass_consolidation_v2.resolve`
verbatim — the exact deterministic Tier-1 (local-code) + Tier-2 (multilingual
keyword) path the published validation harness uses. No LLM is involved.
Intercompany lines are identified by an explicit ``(jurisdiction, local_code)``
allowlist — a deterministic field, never by parsing free text.

FX honesty
----------
The MXN→EUR rate here is a *fixed synthetic rate* (0.05) chosen so the example
is reproducible and the intra-group pair nets exactly. It is not a market rate.
The e2e harness uses the same fixed rate so the two stay consistent.
"""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# Make the repo root importable when run directly (python examples/...).
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from scripts.mass_consolidation_v2 import load_ontology, resolve  # noqa: E402

# --------------------------------------------------------------------------- #
# Presentation currency + FX. Fixed synthetic rates (NOT market data).
# --------------------------------------------------------------------------- #
PRESENTATION_CURRENCY = "EUR"
FX_TO_PRESENTATION: Dict[str, float] = {
    "EUR": 1.0,
    "MXN": 0.05,  # synthetic, fixed; documented in module docstring + e2e README
}

# Intercompany lines: explicit (jurisdiction, local_code) allowlist. Deterministic
# field-based identification — never substring-matching of names/justifications.
INTERCOMPANY_CODES: set = {
    ("es", "4330"),  # parent: intra-group receivable from the Mexican subsidiary
    ("mx", "216"),   # subsidiary: intra-group payable to the Spanish parent
}

EPSILON = 0.01  # currency rounding tolerance (cents of the presentation currency)


# --------------------------------------------------------------------------- #
# Data model
# --------------------------------------------------------------------------- #
@dataclass
class Line:
    """One trial-balance line, carrying its natural-side balance."""

    local_code: str
    local_name: str
    nature: str          # "debit" | "credit"
    amount: float        # positive, expressed on the account's natural side

    @property
    def signed(self) -> float:
        """Debit positive, credit negative — a balanced sheet sums to zero."""
        return self.amount if self.nature == "debit" else -self.amount


@dataclass
class Entity:
    entity_id: str
    name: str
    jurisdiction: str    # ISO 3166-1 alpha-2 (es, mx)
    currency: str
    source: str          # "fixture" | "erpnext" | "odoo" — honesty label
    lines: List[Line] = field(default_factory=list)


@dataclass
class ConsolidatedNode:
    kontablo_id: str
    label: str
    debit: float = 0.0
    credit: float = 0.0

    @property
    def net(self) -> float:
        return self.debit - self.credit


@dataclass
class ReconciliationResult:
    presentation_currency: str
    nodes_pre: Dict[str, ConsolidatedNode]
    nodes_post: Dict[str, ConsolidatedNode]
    intercompany_receivable: float
    intercompany_payable: float
    total_debit_pre: float
    total_credit_pre: float
    total_debit_post: float
    total_credit_post: float

    @property
    def balances_pre(self) -> bool:
        return abs(self.total_debit_pre - self.total_credit_pre) < EPSILON

    @property
    def balances_post(self) -> bool:
        return abs(self.total_debit_post - self.total_credit_post) < EPSILON

    @property
    def intercompany_nets_to_zero(self) -> bool:
        return abs(self.intercompany_receivable - self.intercompany_payable) < EPSILON


# --------------------------------------------------------------------------- #
# Scenario fixtures (used by the self-contained example + as the expected shape
# the e2e provisioning posts into the two real ERPs).
# --------------------------------------------------------------------------- #
def build_scenario() -> List[Entity]:
    """The two-entity transnational group. Each trial balance balances locally."""
    parent = Entity(
        entity_id="ES-PARENT",
        name="Iberia Holding S.A. (Spain, PGC)",
        jurisdiction="es",
        currency="EUR",
        source="fixture",
        lines=[
            Line("572", "Bancos", "debit", 100_000),
            Line("430", "Clientes", "debit", 50_000),
            Line("4330", "Clientes empresas del grupo", "debit", 30_000),  # intercompany
            Line("300", "Existencias comerciales", "debit", 40_000),
            Line("400", "Proveedores", "credit", 30_000),
            Line("100", "Capital social", "credit", 120_000),
            Line("700", "Ventas de mercaderias", "credit", 70_000),
        ],
    )
    subsidiary = Entity(
        entity_id="MX-SUB",
        name="Azteca Servicios S.A. de C.V. (Mexico, SAT)",
        jurisdiction="mx",
        currency="MXN",
        source="fixture",
        lines=[
            Line("102", "Bancos", "debit", 800_000),
            Line("105", "Clientes", "debit", 500_000),
            Line("107", "Almacen (Inventario)", "debit", 300_000),
            Line("201", "Proveedores", "credit", 200_000),
            Line("216", "Cuentas por pagar a partes relacionadas", "credit", 600_000),  # intercompany
            Line("300", "Capital social", "credit", 400_000),
            Line("401", "Ventas y/o servicios gravados", "credit", 400_000),
        ],
    )
    return [parent, subsidiary]


# --------------------------------------------------------------------------- #
# Core reconciliation logic (the only copy; everything imports this)
# --------------------------------------------------------------------------- #
def fx_rate(currency: str) -> float:
    if currency not in FX_TO_PRESENTATION:
        raise KeyError(
            f"No fixed FX rate for {currency!r}; add it to FX_TO_PRESENTATION."
        )
    return FX_TO_PRESENTATION[currency]


def assert_local_balance(entity: Entity) -> None:
    """A trial balance that does not balance locally is a provisioning bug."""
    total = sum(line.signed for line in entity.lines)
    if abs(total) >= EPSILON:
        raise AssertionError(
            f"{entity.entity_id} trial balance does not balance locally: "
            f"net {total:.2f} {entity.currency}"
        )


def reconcile(
    entities: List[Entity],
    accounts: Optional[dict] = None,
    by_code: Optional[dict] = None,
) -> ReconciliationResult:
    """Consolidate → convert → eliminate intercompany → report.

    Resolution uses :func:`scripts.mass_consolidation_v2.resolve` so this path is
    identical to the published deterministic validation harness.
    """
    if accounts is None or by_code is None:
        accounts, by_code, *_ = load_ontology()

    nodes_pre: Dict[str, ConsolidatedNode] = {}
    nodes_post: Dict[str, ConsolidatedNode] = {}
    ic_receivable = 0.0
    ic_payable = 0.0

    def node_for(container: Dict[str, ConsolidatedNode], kid: str) -> ConsolidatedNode:
        if kid not in container:
            label = accounts.get(kid, {}).get("label", kid)
            container[kid] = ConsolidatedNode(kontablo_id=kid, label=label)
        return container[kid]

    for entity in entities:
        assert_local_balance(entity)
        rate = fx_rate(entity.currency)
        for line in entity.lines:
            kid, _tier, _conf = resolve(
                {"code": line.local_code, "name": line.local_name, "nature": line.nature},
                entity.jurisdiction,
                accounts,
                by_code,
            )
            if kid is None:
                raise AssertionError(
                    f"{entity.entity_id} line {line.local_code} '{line.local_name}' "
                    f"did not resolve deterministically (escalated)."
                )
            value = round(line.amount * rate, 2)
            is_ic = (entity.jurisdiction, line.local_code) in INTERCOMPANY_CODES

            # Pre-elimination consolidated trial balance (everything posted).
            pre = node_for(nodes_pre, kid)
            if line.nature == "debit":
                pre.debit += value
            else:
                pre.credit += value

            if is_ic:
                if line.nature == "debit":
                    ic_receivable += value
                else:
                    ic_payable += value
                # Post-elimination: intercompany lines are removed.
                continue

            post = node_for(nodes_post, kid)
            if line.nature == "debit":
                post.debit += value
            else:
                post.credit += value

    total_debit_pre = round(sum(n.debit for n in nodes_pre.values()), 2)
    total_credit_pre = round(sum(n.credit for n in nodes_pre.values()), 2)
    total_debit_post = round(sum(n.debit for n in nodes_post.values()), 2)
    total_credit_post = round(sum(n.credit for n in nodes_post.values()), 2)

    return ReconciliationResult(
        presentation_currency=PRESENTATION_CURRENCY,
        nodes_pre=nodes_pre,
        nodes_post=nodes_post,
        intercompany_receivable=round(ic_receivable, 2),
        intercompany_payable=round(ic_payable, 2),
        total_debit_pre=total_debit_pre,
        total_credit_pre=total_credit_pre,
        total_debit_post=total_debit_post,
        total_credit_post=total_credit_post,
    )


def format_report(result: ReconciliationResult) -> str:
    cur = result.presentation_currency
    out = []
    out.append("=" * 72)
    out.append("KONTABLO TRANSNATIONAL RECONCILIATION — ES parent + MX subsidiary")
    out.append("=" * 72)
    out.append(f"Presentation currency: {cur}")
    out.append("")
    out.append(f"CONSOLIDATED TRIAL BALANCE (pre-elimination, {cur}):")
    out.append(f"   {'Kontablo node':<34}{'debit':>14}{'credit':>14}")
    for kid in sorted(result.nodes_pre):
        n = result.nodes_pre[kid]
        out.append(f"   {kid:<34}{n.debit:>14,.2f}{n.credit:>14,.2f}")
    out.append("   " + "-" * 62)
    out.append(
        f"   {'TOTAL':<34}{result.total_debit_pre:>14,.2f}{result.total_credit_pre:>14,.2f}"
    )
    out.append("")
    out.append("INTERCOMPANY ELIMINATION:")
    out.append(f"   intra-group receivable (ES 4330): {result.intercompany_receivable:>14,.2f} {cur}")
    out.append(f"   intra-group payable    (MX 216) : {result.intercompany_payable:>14,.2f} {cur}")
    out.append(
        f"   net after elimination           : "
        f"{result.intercompany_receivable - result.intercompany_payable:>14,.2f} {cur}"
    )
    out.append("")
    out.append(f"CONSOLIDATED TRIAL BALANCE (post-elimination, {cur}):")
    out.append(f"   {'Kontablo node':<34}{'debit':>14}{'credit':>14}")
    for kid in sorted(result.nodes_post):
        n = result.nodes_post[kid]
        out.append(f"   {kid:<34}{n.debit:>14,.2f}{n.credit:>14,.2f}")
    out.append("   " + "-" * 62)
    out.append(
        f"   {'TOTAL':<34}{result.total_debit_post:>14,.2f}{result.total_credit_post:>14,.2f}"
    )
    out.append("")
    out.append(f"   balances pre-elimination : {result.balances_pre}")
    out.append(f"   balances post-elimination: {result.balances_post}")
    out.append(f"   intercompany nets to zero: {result.intercompany_nets_to_zero}")
    out.append("=" * 72)
    return "\n".join(out)


def assert_reconciled(result: ReconciliationResult) -> None:
    """The three load-bearing invariants. Shared by example, test, and e2e."""
    assert result.balances_pre, (
        f"consolidated TB (pre) does not balance: "
        f"D {result.total_debit_pre} != C {result.total_credit_pre}"
    )
    assert result.intercompany_nets_to_zero, (
        f"intercompany does not net to zero: receivable "
        f"{result.intercompany_receivable} != payable {result.intercompany_payable}"
    )
    assert result.balances_post, (
        f"consolidated TB (post-elimination) does not balance: "
        f"D {result.total_debit_post} != C {result.total_credit_post}"
    )


def main() -> int:
    entities = build_scenario()
    result = reconcile(entities)
    print(format_report(result))
    assert_reconciled(result)
    print("\n✅ Reconciliation invariants hold.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
