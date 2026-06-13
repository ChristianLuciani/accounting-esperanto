#!/usr/bin/env python3
"""
Kontablo initial-run consolidation artifact — v1 (10 entities, 9 countries).

This script makes the "initial run" described in the preprint's evaluation
section (Section: Mass Consolidation Simulation, opening paragraphs) fully
regenerable, per the project's claims-evidence rule ("no claim without a
command"). It does three things, all deterministic, no LLM/API dependency:

  1. GENERATE the synthetic trial-balance fixtures for 10 entities across
     9 countries (MX x2, BR, FR, PA, EC, CO, VN, NG, SA), each written in the
     trial-balance CSV export layout of one of four source ERPs:
     ERPNext, Zoho Books, Odoo, SAP Business One.
     The ledgers are SYNTHETIC. They are formatted as ERP exports; they are
     not real company data and were never exported from a live ERP instance.
     Every entity's trial balance balances exactly (total debits == total
     credits, in local currency) — equity.retained is the balancing line.

  2. INGEST the fixtures back through four format-specific parsers (one per
     ERP layout) and resolve every line through the same deterministic
     pipeline as scripts/mass_consolidation_v2.py (imported, not duplicated):
     Tier 1 exact local-code lookup -> Tier 2 multilingual keyword rules ->
     ESCALATED to human review (CRA). Tier 3 (semantic AI fallback) is NOT
     exercised: lines the deterministic tiers cannot resolve are escalated,
     exactly as in the v2 harness, so the run is 100% reproducible.

  3. CONSOLIDATE resolved lines to USD and verify the accounting identity
     Assets = Liabilities + Equity + (Revenue - Expenses) over the posted
     ledger, with escalated lines carried in an explicit suspense bucket so
     the identity is exact and auditable.

Run:  venv/bin/python scripts/consolidation_v1_initial_run.py
Outputs (committed for reproducibility):
  research/experiments/consolidation_v1/fixtures/*.csv   (10 ERP-format TBs)
  research/experiments/consolidation_v1/results.json
  research/experiments/consolidation_v1/per_entry.csv
"""

import csv
import io
import json
import os
import sys
from collections import Counter, defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import mass_consolidation_v2 as v2  # noqa: E402  (shared deterministic pipeline)

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.path.join(ROOT, "research/experiments/consolidation_v1")
FIX_DIR = os.path.join(OUT_DIR, "fixtures")

# ---------------------------------------------------------------------------
# Entity definitions: 10 entities, 9 countries, 4 source-ERP formats.
# Each row: (intended kontablo id or None, local account name, nature,
#            USD base magnitude, local statutory code or None).
# A row's code is the jurisdiction's real statutory code where the source
# chart carries one (VAS, PCG, PUC, SAT...); whether that code resolves at
# Tier 1 depends on the ontology's committed local_codes index — codes the
# ontology does not carry fall through to Tier 2 (name rules) or escalate,
# which is exactly the behavior the run measures. equity.retained amount is
# ignored as specified and recomputed as the balancing line.
# ---------------------------------------------------------------------------

ROWS_ES = [  # Spanish-language standard set (MX/PA/EC/CO share names; codes differ)
    ("asset.current.cash",          "Caja",                          "debit",  50000),
    ("asset.current.bank",          "Bancos",                        "debit",  40000),
    ("asset.current.receivables",   "Clientes",                      "debit", 120000),
    ("asset.current.inventory",     "Inventarios",                   "debit",  60000),
    ("asset.noncurrent.ppe",        "Propiedad Planta y Equipo",     "debit", 200000),
    ("liability.current.payables",  "Proveedores",                   "credit", 70000),
    ("liability.current.tax",       "Impuestos por Pagar",           "credit", 15000),
    ("liability.noncurrent.debt",   "Deuda Largo Plazo",             "credit",100000),
    ("equity.capital",              "Capital Social",                "credit", 80000),
    ("equity.retained",             "Resultados Acumulados",         "credit",      0),
    ("revenue.operating",           "Ventas",                        "credit",300000),
    ("expense.cogs",                "Costo de Ventas",               "debit", 150000),
    ("expense.admin",               "Gastos Administrativos",        "debit",  60000),
    ("expense.depreciation",        "Depreciación",                  "debit",  20000),
]

# SAT código agrupador (Anexo 24) statutory codes for the Mexican entities.
CODES_MX = {"asset.current.cash": "101", "asset.current.bank": "102",
            "asset.current.receivables": "105", "asset.current.inventory": "151",
            "asset.noncurrent.ppe": "181", "liability.current.payables": "201",
            "liability.current.tax": "2030", "liability.noncurrent.debt": "212",
            "equity.capital": "300", "equity.retained": "305",
            "revenue.operating": "401", "expense.cogs": "501",
            "expense.admin": "601", "expense.depreciation": "613"}

# Panama chart codes (ontology-carried PA set where available).
CODES_PA = {"asset.current.cash": "1.1.01", "asset.current.bank": "1.1.02",
            "asset.current.receivables": "1.1.05", "asset.current.inventory": "1.1.08",
            "asset.noncurrent.ppe": "2.1.01", "liability.current.payables": "3.1.01",
            "liability.current.tax": "3.1.04", "liability.noncurrent.debt": "4.1.01",
            "equity.capital": "5.1.01", "equity.retained": "5.2.01",
            "revenue.operating": "6.1.01", "expense.cogs": "7.1.01",
            "expense.admin": "8.1.01", "expense.depreciation": "8.2.01"}

ENTITIES = [
    # --- Mexico: two entities (10 entities across 9 countries) ---
    {"id": "MX-01", "name": "Manufactura Azteca SA de CV", "j": "mx", "ccy": "MXN",
     "erp": "erpnext",
     "rows": [(k, n, nat, usd, CODES_MX.get(k)) for k, n, nat, usd in ROWS_ES]},
    {"id": "MX-02", "name": "Distribuidora del Norte SA", "j": "mx", "ccy": "MXN",
     "erp": "zoho_books",
     "rows": [(k, n, nat, usd, CODES_MX.get(k)) for k, n, nat, usd in ROWS_ES]},
    # --- Brazil (SPED-style deep codes; ontology carries only 2 BR codes,
    #     so most lines resolve at Tier 2 on Portuguese names) ---
    {"id": "BR-01", "name": "Industria Paulista Ltda", "j": "br", "ccy": "BRL",
     "erp": "sap_b1",
     "rows": [
         ("asset.current.cash",         "Caixa",                       "debit",  50000, "1.1.1.1.01-9"),
         ("asset.current.receivables",  "Contas a Receber",            "debit", 120000, "1.1.1.2.01-0"),
         ("asset.current.inventory",    "Estoque",                     "debit",  60000, "1.1.4.1.01-5"),
         ("asset.noncurrent.ppe",       "Ativo Imobilizado",           "debit", 200000, "1.2.3.1.01-2"),
         ("liability.current.payables", "Fornecedores",                "credit", 70000, "2.1.1.1.01-4"),
         ("liability.current.tax",      "Imposto a Pagar",             "credit", 15000, "2.1.4.1.01-7"),
         ("equity.capital",             "Capital Social",              "credit", 80000, "2.3.1.1.01-1"),
         ("equity.retained",            "Lucros Acumulados",           "credit",      0, "2.3.5.1.01-8"),
         ("revenue.operating",          "Receita de Vendas",           "credit",300000, "3.1.1.1.01-3"),
         ("expense.cogs",               "Custo das Mercadorias",       "debit", 150000, "3.2.1.1.01-6"),
         ("expense.admin",              "Despesas Administrativas",    "debit",  85000, "3.3.1.1.01-9"),
     ]},
    # --- France (PCG codes carried by the ontology -> high Tier 1) ---
    {"id": "FR-01", "name": "Société Lyonnaise SARL", "j": "fr", "ccy": "EUR",
     "erp": "odoo",
     "rows": [
         ("asset.current.cash",         "Caisse",                      "debit",  50000, "512"),
         ("asset.current.inventory",    "Stocks de marchandises",      "debit",  60000, "371"),
         ("asset.noncurrent.ppe",       "Immobilisations corporelles", "debit", 200000, "211"),
         ("asset.current.vat_input",    "TVA déductible",              "debit",   8000, "445660"),
         ("liability.current.payables", "Fournisseurs",                "credit", 70000, "401"),
         ("liability.current.vat_output","TVA collectée",              "credit", 12000, "445710"),
         ("liability.current.tax",      "État, impôts",                "credit", 15000, "444"),
         ("equity.capital",             "Capital social",              "credit", 80000, "101"),
         ("equity.retained",            "Report à nouveau",            "credit",      0, "110"),
         ("revenue.operating",          "Ventes de produits",          "credit",300000, "701"),
         ("expense.cogs",               "Achats de marchandises",      "debit", 150000, "607"),
         ("expense.admin",              "Frais généraux",              "debit",  60000, "627"),
         ("expense.depreciation",       "Dotations aux amortissements","debit",  20000, "681"),
     ]},
    # --- Panama (ontology carries a PA chart -> mixed Tier 1 / Tier 2) ---
    {"id": "PA-01", "name": "Logística Istmo SA", "j": "pa", "ccy": "USD",
     "erp": "zoho_books",
     "rows": [(k, n, nat, usd, CODES_PA.get(k)) for k, n, nat, usd in ROWS_ES]},
    # --- Ecuador (no ontology code set -> pure Tier 2 on Spanish names) ---
    {"id": "EC-01", "name": "Comercial Andina Cia Ltda", "j": "ec", "ccy": "USD",
     "erp": "erpnext",
     "rows": [(k, n, nat, usd, None) for k, n, nat, usd in ROWS_ES]},
    # --- Colombia (PUC codes carried by the ontology) ---
    {"id": "CO-01", "name": "Comercializadora Bogotá SAS", "j": "co", "ccy": "COP",
     "erp": "odoo",
     "rows": [
         ("asset.current.cash",         "Caja",                        "debit",  50000, "1105"),
         ("asset.current.bank",         "Bancos",                      "debit",  40000, "1110"),
         ("asset.current.receivables",  "Clientes",                    "debit", 120000, "1305"),
         ("asset.current.inventory",    "Inventarios",                 "debit",  60000, "1430"),
         ("asset.noncurrent.ppe",       "Propiedades Planta y Equipo", "debit", 200000, "1516"),
         ("liability.current.payables", "Proveedores",                 "credit", 70000, "2205"),
         ("liability.current.tax",      "Impuestos por Pagar",         "credit", 15000, "2404"),
         ("equity.capital",             "Capital Social",              "credit", 80000, "3105"),
         ("equity.retained",            "Resultados Acumulados",       "credit",      0, "3605"),
         ("revenue.operating",          "Ingresos Operacionales",      "credit",300000, "4135"),
         ("expense.cogs",               "Costo de Ventas",             "debit", 150000, "6105"),
         ("expense.admin",              "Gastos Administrativos",      "debit",  85000, "5205"),
     ]},
    # --- Vietnam (VAS Circular 200 codes; the source chart is deeper than
    #     the ontology's committed VN code set, so some statutory lines fall
    #     through to Tier 2 or escalate — the pattern the paper discusses) ---
    {"id": "VN-01", "name": "Công ty TNHH Sông Hồng", "j": "vn", "ccy": "VND",
     "erp": "erpnext",
     "rows": [
         ("asset.current.cash",         "Tiền mặt",                    "debit",  50000, "111"),
         ("asset.current.bank",         "Tiền gửi ngân hàng",          "debit",  40000, "112"),
         ("asset.current.receivables",  "Phải thu của khách hàng",     "debit", 120000, "131"),
         ("asset.current.inventory",    "Hàng tồn kho",                "debit",  60000, "152"),
         ("asset.noncurrent.ppe",       "Tài sản cố định hữu hình",    "debit", 200000, "211"),
         (None,                         "Chi phí trả trước dài hạn",   "debit",   9000, "242"),
         ("liability.current.payables", "Phải trả cho người bán",      "credit", 70000, "331"),
         (None,                         "Thuế và các khoản phải nộp",  "credit", 15000, "333"),
         ("equity.capital",             "Vốn đầu tư của chủ sở hữu",   "credit", 80000, "411"),
         ("equity.retained",            "Lợi nhuận sau thuế chưa phân phối", "credit", 0, "421"),
         ("revenue.operating",          "Doanh thu bán hàng",          "credit",300000, "511"),
         (None,                         "Giá vốn hàng bán",            "debit", 150000, "632"),
         (None,                         "Chi phí quản lý doanh nghiệp","debit",  86000, "642"),
     ]},
    # --- Nigeria (IFRS-direct, no statutory chart -> Tier 2 on English) ---
    {"id": "NG-01", "name": "Lagos Trading Ltd", "j": "ng", "ccy": "NGN",
     "erp": "zoho_books",
     "rows": [
         ("asset.current.cash",         "Cash on Hand",                "debit",  50000, None),
         ("asset.current.bank",         "Bank Balances",               "debit",  40000, None),
         ("asset.current.receivables",  "Trade Receivables",           "debit", 120000, None),
         ("asset.current.inventory",    "Inventory",                   "debit",  60000, None),
         ("asset.noncurrent.ppe",       "Property Plant and Equipment","debit", 200000, None),
         ("liability.current.payables", "Trade Payables",              "credit", 70000, None),
         ("liability.current.tax",      "Tax Payable",                 "credit", 15000, None),
         ("liability.noncurrent.debt",  "Long-Term Debt",              "credit",100000, None),
         ("equity.capital",             "Share Capital",               "credit", 80000, None),
         ("equity.retained",            "Retained Earnings",           "credit",      0, None),
         ("revenue.operating",          "Revenue",                     "credit",300000, None),
         ("expense.cogs",               "Cost of Goods Sold",          "debit", 150000, None),
         ("expense.admin",              "Administrative Expenses",     "debit",  60000, None),
         ("expense.depreciation",       "Depreciation",                "debit",  20000, None),
     ]},
    # --- Saudi Arabia (SOCPA, Arabic names; ontology carries one SA code;
    #     several Arabic terms are outside the Tier-2 vocabulary -> the
    #     highest escalation rate in the run, as the paper discusses) ---
    {"id": "SA-01", "name": "شركة الرياض التجارية", "j": "sa", "ccy": "SAR",
     "erp": "sap_b1",
     "rows": [
         ("asset.current.cash",         "النقد في الصندوق",            "debit",  50000, "101"),
         ("asset.current.bank",         "البنك",                       "debit",  40000, "102"),
         ("asset.current.receivables",  "ذمم مدينة",                   "debit", 120000, "110"),
         (None,                         "المخزون",                     "debit",  60000, "120"),
         (None,                         "الأصول الثابتة",              "debit", 200000, "150"),
         ("liability.current.payables", "موردون",                      "credit", 70000, "201"),
         ("liability.current.zakat",    "مخصص الزكاة",                 "credit", 18000, "215"),
         ("equity.capital",             "رأس المال",                   "credit", 80000, "301"),
         ("equity.retained",            "الأرباح المبقاة",             "credit",      0, "305"),
         ("revenue.operating",          "إيرادات المبيعات",            "credit",300000, "401"),
         (None,                         "تكلفة المبيعات",              "debit", 150000, "501"),
         (None,                         "مصاريف إدارية",               "debit",  78000, "510"),
     ]},
]


def build_fixture_rows(ent):
    """Local-currency rows with the retained-earnings line as the exact
    balancing plug (total debits == total credits, to the cent)."""
    rate = v2.FX[ent["ccy"]]
    rows, debits, credits, plug_ix = [], 0.0, 0.0, None
    for i, (kid, name, nature, usd, code) in enumerate(ent["rows"]):
        amt = round(usd / rate, 2)
        rows.append({"kid": kid, "name": name, "nature": nature,
                     "code": code, "amt": amt})
        if kid == "equity.retained":
            plug_ix = i
        elif nature == "debit":
            debits += amt
        else:
            credits += amt
    plug = round(debits - credits, 2)
    assert plug >= 0, f"{ent['id']}: retained-earnings plug must be non-negative"
    rows[plug_ix]["amt"] = plug
    return rows


# ---------------------------------------------------------------------------
# ERP trial-balance export layouts (writer + parser per format). Layouts
# mirror each ERP's stock trial-balance CSV export columns.
# ---------------------------------------------------------------------------

def _w(rows, header, line):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(header)
    for r in rows:
        w.writerow(line(r))
    return buf.getvalue()


def write_erpnext(rows):  # ERPNext: "<code> - <name>" account column
    return _w(rows, ["Account", "Currency", "Debit", "Credit"],
              lambda r: [f"{r['code']} - {r['name']}" if r["code"] else r["name"],
                         "", f"{r['amt']:.2f}" if r["nature"] == "debit" else "0.00",
                         f"{r['amt']:.2f}" if r["nature"] == "credit" else "0.00"])


def write_zoho_books(rows):
    return _w(rows, ["Account", "Account Code", "Debit", "Credit"],
              lambda r: [r["name"], r["code"] or "",
                         f"{r['amt']:.2f}" if r["nature"] == "debit" else "0.00",
                         f"{r['amt']:.2f}" if r["nature"] == "credit" else "0.00"])


def write_odoo(rows):
    return _w(rows, ["Code", "Account", "Debit", "Credit", "Balance"],
              lambda r: [r["code"] or "", r["name"],
                         f"{r['amt']:.2f}" if r["nature"] == "debit" else "0.00",
                         f"{r['amt']:.2f}" if r["nature"] == "credit" else "0.00",
                         f"{r['amt'] if r['nature'] == 'debit' else -r['amt']:.2f}"])


def write_sap_b1(rows):
    return _w(rows, ["Acct No.", "Account Name", "Debit (LC)", "Credit (LC)"],
              lambda r: [r["code"] or "", r["name"],
                         f"{r['amt']:.2f}" if r["nature"] == "debit" else "0.00",
                         f"{r['amt']:.2f}" if r["nature"] == "credit" else "0.00"])


def _parse_dc(debit, credit):
    d, c = float(debit or 0), float(credit or 0)
    return ("debit", d) if d > 0 else ("credit", c)


def parse_erpnext(text):
    out = []
    for row in csv.DictReader(io.StringIO(text)):
        acct = row["Account"]
        code, _, name = acct.partition(" - ")
        if not name:               # no code prefix
            code, name = "", acct
        nature, amt = _parse_dc(row["Debit"], row["Credit"])
        out.append({"code": code or "x", "name": name, "nature": nature, "amt": amt})
    return out


def parse_zoho_books(text):
    out = []
    for row in csv.DictReader(io.StringIO(text)):
        nature, amt = _parse_dc(row["Debit"], row["Credit"])
        out.append({"code": row["Account Code"] or "x", "name": row["Account"],
                    "nature": nature, "amt": amt})
    return out


def parse_odoo(text):
    out = []
    for row in csv.DictReader(io.StringIO(text)):
        nature, amt = _parse_dc(row["Debit"], row["Credit"])
        out.append({"code": row["Code"] or "x", "name": row["Account"],
                    "nature": nature, "amt": amt})
    return out


def parse_sap_b1(text):
    out = []
    for row in csv.DictReader(io.StringIO(text)):
        nature, amt = _parse_dc(row["Debit (LC)"], row["Credit (LC)"])
        out.append({"code": row["Acct No."] or "x", "name": row["Account Name"],
                    "nature": nature, "amt": amt})
    return out


ERP_FORMATS = {
    "erpnext":    (write_erpnext, parse_erpnext),
    "zoho_books": (write_zoho_books, parse_zoho_books),
    "odoo":       (write_odoo, parse_odoo),
    "sap_b1":     (write_sap_b1, parse_sap_b1),
}


def main():
    accounts, by_code, _collisions, _placeholders = v2.load_ontology()
    by_code = v2.merge_family_codes(by_code, v2.load_families())

    os.makedirs(FIX_DIR, exist_ok=True)

    consolidated = defaultdict(float)
    suspense_usd = 0.0
    tier_counts = Counter()
    per_entry = []
    per_entity = []
    by_jurisdiction = defaultdict(lambda: Counter())

    for ent in ENTITIES:
        rows = build_fixture_rows(ent)
        writer, parser = ERP_FORMATS[ent["erp"]]

        # 1. write the fixture in the entity's source-ERP export layout
        text = writer(rows)
        fix_path = os.path.join(FIX_DIR, f"{ent['id']}_{ent['erp']}.csv")
        with open(fix_path, "w", encoding="utf-8") as f:
            f.write(text)

        # 2. ingest it back through the format-specific parser
        parsed = parser(text)
        debits = sum(r["amt"] for r in parsed if r["nature"] == "debit")
        credits = sum(r["amt"] for r in parsed if r["nature"] == "credit")
        assert round(debits - credits, 2) == 0.0, \
            f"{ent['id']}: trial balance does not balance ({debits} != {credits})"

        # 3. resolve each line through the shared deterministic pipeline
        rate = v2.FX[ent["ccy"]]
        t1 = t2 = esc = 0
        for line in parsed:
            kid, tier, conf = v2.resolve(line, ent["j"], accounts, by_code)
            tier_counts[tier] += 1
            by_jurisdiction[ent["j"]][tier] += 1
            # accumulate unrounded so the consolidated identity is exact
            # (rounding only at display); local TBs balance to the cent.
            usd = line["amt"] * rate
            if kid is None:
                esc += 1
                # escalated lines park in suspense, signed by nature, so the
                # consolidated identity stays exact and auditable
                suspense_usd += usd if line["nature"] == "debit" else -usd
            else:
                if tier == "tier1_exact":
                    t1 += 1
                else:
                    t2 += 1
                consolidated[kid] += usd if line["nature"] == "debit" else -usd
            per_entry.append({
                "entity": ent["id"], "jurisdiction": ent["j"],
                "currency": ent["ccy"], "source_erp": ent["erp"],
                "local_code": line["code"], "local_name": line["name"],
                "kontablo_id": kid or "ESCALATED", "tier": tier,
                "confidence": conf, "usd_value": round(usd, 2),
            })
        per_entity.append({
            "entity": ent["id"], "name": ent["name"], "jurisdiction": ent["j"],
            "currency": ent["ccy"], "source_erp_format": ent["erp"],
            "lines": len(parsed), "total_debits_local": round(debits, 2),
            "total_credits_local": round(credits, 2), "balanced": True,
            "tier1": t1, "tier2": t2, "escalated": esc,
        })

    # 4. consolidated accounting identity over the posted USD ledger:
    #    Assets = Liabilities + Equity + (Revenue - Expenses), with escalated
    #    lines in the suspense bucket. Debit-normal classes accumulate +,
    #    credit-normal classes accumulate - (sign flip below).
    def bucket(prefix):
        return sum(val for kid, val in consolidated.items() if kid.startswith(prefix))

    assets = bucket("asset")
    liabilities = -bucket("liability")
    equity = -bucket("equity")
    revenue = -bucket("revenue")
    expenses = bucket("expense")
    identity_gap = round(assets + suspense_pos(suspense_usd)[0]
                         - (liabilities + equity + (revenue - expenses)
                            + suspense_pos(suspense_usd)[1]), 2)

    total_entries = len(per_entry)
    det = tier_counts["tier1_exact"] + tier_counts["tier2_keyword"]
    summary = {
        "run": "initial_run_v1",
        "description": ("Synthetic trial balances, formatted as source-ERP "
                        "exports (ERPNext, Zoho Books, Odoo, SAP B1). Not "
                        "real company data. Fully regenerable: "
                        "python scripts/consolidation_v1_initial_run.py"),
        "entities": len(ENTITIES),
        "countries": sorted({e["j"] for e in ENTITIES}),
        "n_countries": len({e["j"] for e in ENTITIES}),
        "source_erp_formats": sorted({e["erp"] for e in ENTITIES}),
        "total_entries": total_entries,
        "tier_distribution": dict(tier_counts),
        "deterministic_coverage_pct": round(100 * det / total_entries, 1),
        "escalated": tier_counts["escalated"],
        "escalated_pct": round(100 * tier_counts["escalated"] / total_entries, 1),
        "tiers_by_jurisdiction": {j: dict(c) for j, c in sorted(by_jurisdiction.items())},
        "per_entity": per_entity,
        "consolidated_usd": {k: round(v, 2) for k, v in sorted(consolidated.items())},
        "suspense_usd": round(suspense_usd, 2),
        "identity": {
            "assets_usd": round(assets, 2),
            "liabilities_usd": round(liabilities, 2),
            "equity_usd": round(equity, 2),
            "revenue_usd": round(revenue, 2),
            "expenses_usd": round(expenses, 2),
            "suspense_usd": round(suspense_usd, 2),
            "gap_usd": identity_gap,
        },
    }
    assert identity_gap == 0.0, f"consolidated identity violated: gap={identity_gap}"

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR, "results.json"), "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    with open(os.path.join(OUT_DIR, "per_entry.csv"), "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(per_entry[0].keys()))
        w.writeheader()
        w.writerows(per_entry)

    print("=" * 78)
    print("KONTABLO INITIAL-RUN CONSOLIDATION  v1  (synthetic, ERP-formatted, deterministic)")
    print("=" * 78)
    print(f"Entities                  : {summary['entities']} "
          f"across {summary['n_countries']} countries {summary['countries']}")
    print(f"Source-ERP export formats : {summary['source_erp_formats']}")
    print(f"Lines ingested            : {total_entries}")
    for t, c in tier_counts.most_common():
        print(f"   {t:<16}: {c:>3}  ({100 * c / total_entries:5.1f}%)")
    print(f"Deterministic coverage    : {summary['deterministic_coverage_pct']}%  "
          f"(escalated to human/CRA: {summary['escalated']})")
    print("Per-jurisdiction tiers    :")
    for j, c in sorted(by_jurisdiction.items()):
        tot = sum(c.values())
        print(f"   {j}: tier1 {c['tier1_exact']}/{tot}, tier2 {c['tier2_keyword']}/{tot}, "
              f"escalated {c['escalated']}/{tot}")
    print(f"Identity A = L + E + (R - X) gap (USD, incl. suspense): {identity_gap}")
    print(f"Fixtures: {os.path.relpath(FIX_DIR, ROOT)}/  "
          f"results: {os.path.relpath(OUT_DIR, ROOT)}/results.json")


def suspense_pos(s):
    """Split signed suspense into (debit-side, credit-side) for the identity:
    a positive (debit-normal) suspense belongs on the asset side, a negative
    one on the L+E+(R-X) side."""
    return (s, 0.0) if s >= 0 else (0.0, -s)


if __name__ == "__main__":
    main()
