#!/usr/bin/env python3
"""
Self-contained transnational reconciliation (zero external dependencies).

What this is: a runnable, fully deterministic demonstration of Kontablo
consolidating a two-jurisdiction group whose books live in two *different*
classical local charts of accounts:

  * Parent  — "Ibérica Manufactura, S.A."     Spain   (PGC, EUR)
  * Subsidiary — "Manufactura del Norte, S.A. de C.V."  Mexico  (SAT, MXN)

It pulls each local chart, maps every account to the universal Kontablo UUID
ontology via the deterministic resolve() path (Tier-1 exact local-code lookup,
Tier-2 multilingual keyword fallback), normalises both currencies to USD,
consolidates, eliminates one intercompany balance, and prints a unified
cross-border trial balance that still balances (Σdebits = Σcredits).

Honesty note: the trial balances below are SYNTHETIC (hand-constructed,
balanced by construction) — they are not real-world ledger data. The *local
codes themselves* are real PGC/SAT statutory codes drawn from the committed
Kontablo ontology, so the Tier-1 lookups are genuine. No LLM is involved; every
mapping and every elimination is a deterministic graph/rule operation.

This is the zero-dependency tier. The next tier up
(``examples/two_erp_reconciliation/``) runs the *same* engine against two real
open-source ERPs (ERPNext + Odoo) over Docker via the connectors.

Run:  python examples/transnational_reconciliation.py
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.engine import (  # noqa: E402
    ConsolidationEngine,
    IntercompanyLink,
    LocalEntry,
    SubsidiaryTB,
)

# USD value of the single intercompany balance (parent financed the subsidiary):
# the parent carries an intercompany receivable; the subsidiary an intercompany
# payable of the same USD size. On consolidation the pair is eliminated.
INTERCOMPANY_USD = 100_000.0


def build_parent_spain() -> SubsidiaryTB:
    """Ibérica Manufactura, S.A. — Spanish PGC, amounts in EUR.

    Balanced by construction: Σdebit = Σcredit = 1,670,000 EUR.
    Account 430 (Clientes) includes the intercompany receivable from Mexico.
    """
    return SubsidiaryTB(
        subsidiary_id="iberica-es",
        jurisdiction="es",
        currency="EUR",
        entries=[
            LocalEntry("572", "Bancos, c/c vista, euros", debit=200_000, nature="debit"),
            LocalEntry("430", "Clientes por ventas y prestaciones de servicios",
                       debit=300_000, nature="debit", intercompany_with="norte-mx"),
            LocalEntry("300", "Mercaderías (existencias)", debit=150_000, nature="debit"),
            LocalEntry("21", "Inmovilizado material", debit=500_000, nature="debit"),
            LocalEntry("600", "Compras de mercaderías", debit=400_000, nature="debit"),
            LocalEntry("62", "Servicios exteriores", debit=120_000, nature="debit"),
            LocalEntry("100", "Capital social", credit=600_000, nature="credit"),
            LocalEntry("129", "Resultado del ejercicio", credit=170_000, nature="credit"),
            LocalEntry("400", "Proveedores", credit=250_000, nature="credit"),
            LocalEntry("170", "Deudas a largo plazo con entidades de crédito",
                       credit=250_000, nature="credit"),
            LocalEntry("700", "Ventas de mercaderías", credit=400_000, nature="credit"),
        ],
    )


def build_subsidiary_mexico() -> SubsidiaryTB:
    """Manufactura del Norte, S.A. de C.V. — Mexican SAT chart, amounts in MXN.

    Balanced by construction: Σdebit = Σcredit = 15,200,000 MXN.
    Account 201 (Proveedores) includes the intercompany payable to Spain.
    """
    return SubsidiaryTB(
        subsidiary_id="norte-mx",
        jurisdiction="mx",
        currency="MXN",
        entries=[
            LocalEntry("101", "Caja", debit=500_000, nature="debit"),
            LocalEntry("102", "Bancos", debit=1_500_000, nature="debit"),
            LocalEntry("105", "Clientes", debit=2_000_000, nature="debit"),
            LocalEntry("151", "Inventarios", debit=1_200_000, nature="debit"),
            LocalEntry("181", "Maquinaria y equipo", debit=6_000_000, nature="debit"),
            LocalEntry("501", "Costo de ventas", debit=3_000_000, nature="debit"),
            LocalEntry("504", "Gastos de administración", debit=1_000_000, nature="debit"),
            LocalEntry("300", "Capital social", credit=4_000_000, nature="credit"),
            LocalEntry("305", "Resultados acumulados", credit=1_200_000, nature="credit"),
            LocalEntry("201", "Proveedores", credit=3_275_862, nature="credit",
                       intercompany_with="iberica-es"),
            LocalEntry("311", "Documentos por pagar a largo plazo",
                       credit=1_724_138, nature="credit"),
            LocalEntry("401", "Ventas", credit=5_000_000, nature="credit"),
        ],
    )


def intercompany_links() -> list[IntercompanyLink]:
    """The single intercompany balance to eliminate, keyed on deterministic
    (subsidiary_id, kontablo_id) — never on free text."""
    return [
        IntercompanyLink(
            from_subsidiary="iberica-es",
            from_kontablo_id="asset.current.receivables",  # PGC 430
            to_subsidiary="norte-mx",
            to_kontablo_id="liability.current.payables",   # SAT 201
            amount_usd=INTERCOMPANY_USD,
        )
    ]


def reconcile():
    """Run the full pipeline and return the ConsolidationResult (used by tests)."""
    engine = ConsolidationEngine()
    subs = [build_parent_spain(), build_subsidiary_mexico()]
    return engine.consolidate(subs, eliminations=intercompany_links())


# ---------------------------------------------------------------------------
# Presentation
# ---------------------------------------------------------------------------
def _print_local_chart(tb: SubsidiaryTB, engine: ConsolidationEngine) -> None:
    print(f"\n  {tb.subsidiary_id}  ·  {tb.jurisdiction.upper()}  ·  {tb.currency}")
    print(f"  {'code':>7}  {'local account':<46} {'→ kontablo_id':<34} tier")
    print("  " + "-" * 100)
    for e in tb.entries:
        kid, tier, _ = engine.resolve(e, tb.jurisdiction)
        print(f"  {e.code:>7}  {e.name[:46]:<46} {str(kid):<34} {tier}")


def _section(lines, statement, natures):
    return [l for l in lines if l.statement == statement and l.nature in natures]


def main() -> None:
    engine = ConsolidationEngine()
    parent = build_parent_spain()
    sub = build_subsidiary_mexico()

    print("=" * 104)
    print("KONTABLO — Transnational reconciliation (self-contained, deterministic)")
    print("  Parent:     Ibérica Manufactura, S.A.        Spain (PGC)   EUR")
    print("  Subsidiary: Manufactura del Norte, S.A. de C.V.  Mexico (SAT)  MXN  (100% owned)")
    print("=" * 104)

    print("\n[1] LOCAL CHARTS → KONTABLO UUID ONTOLOGY (deterministic resolve)")
    _print_local_chart(parent, engine)
    _print_local_chart(sub, engine)

    result = engine.consolidate([parent, sub], eliminations=intercompany_links())

    print("\n[2] FX NORMALISATION TO USD")
    print(f"  EUR→USD {engine.fx_to_usd(parent):.4f}   MXN→USD {engine.fx_to_usd(sub):.4f}")

    print("\n[3] INTERCOMPANY ELIMINATION")
    print(f"  Eliminated {result.eliminations_applied} intercompany balance "
          f"(USD {INTERCOMPANY_USD:,.0f}): "
          f"Ibérica receivable (PGC 430) ↔ Norte payable (SAT 201)")

    print("\n[4] UNIFIED CROSS-BORDER TRIAL BALANCE (USD)")
    groups = [
        ("ASSETS", "balance_sheet", {"debit"}),
        ("LIABILITIES & EQUITY", "balance_sheet", {"credit"}),
        ("REVENUE", "income_statement", {"credit"}),
        ("EXPENSES", "income_statement", {"debit"}),
    ]
    for title, stmt, natures in groups:
        rows = _section(result.lines, stmt, natures)
        if not rows:
            continue
        print(f"\n  {title}")
        for l in rows:
            amt = l.debit_usd if "debit" in natures else l.credit_usd
            print(f"    {l.kontablo_id:<34} {l.label_en[:30]:<30} {amt:>16,.2f}")

    print("\n  " + "-" * 100)
    print(f"  {'Σ DEBITS (USD)':<66} {result.total_debits:>16,.2f}")
    print(f"  {'Σ CREDITS (USD)':<66} {result.total_credits:>16,.2f}")
    print(f"  {'BALANCE DIFFERENCE (should be ~0.00)':<66} {result.balance_difference:>16,.2f}")
    status = "BALANCED ✓" if result.is_balanced() else "OUT OF BALANCE ✗"
    print(f"\n  RECONCILIATION: {status}")
    if result.escalations:
        print(f"  Escalated to human review (CRA): {len(result.escalations)} entr(ies)")
    if result.cra_flags:
        print(f"  CRA boundary flags: {len(result.cra_flags)}")
    print("=" * 104)


if __name__ == "__main__":
    main()
