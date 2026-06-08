#!/usr/bin/env python3
"""
Kontablo mass-consolidation validation harness — v2 (expanded, deterministic).

Goal: an exhaustive, fully reproducible validation of the Kontablo mapping +
consolidation pipeline WITHOUT any LLM/API dependency. Tier 3 (semantic AI
fallback) is intentionally NOT exercised here; instead, transactions that the
deterministic tiers cannot resolve are counted as ESCALATED (routed to human
review by the Co-responsibility Architecture). This makes the run 100%
reproducible and lets us measure deterministic coverage honestly.

Pipeline per local account entry:
  Tier 1  exact local-code lookup against the real Level-3 ontology YAML
          (core/schemas/level3_accounts.yaml -> local_codes[jurisdiction]).
  Tier 2  deterministic multilingual keyword/regex rules on the account name.
  Escalate if neither tier resolves (residual -> human via CRA).

Then the Co-responsibility Architecture validates every resolved mapping:
  - nature mismatch (debit/credit) vs the target node;
  - deterministic boundary violation (liquid asset mapped to a non-current node).
Deliberately malformed entries are injected to demonstrate the CRA catching
upstream/AI mis-proposals (field "forced_id").

FX: balances are normalized to USD. Hyperinflation entities carry an official
and a parallel rate to exercise IAS 29 dual-rate divergence.

Run:  venv/bin/python scripts/mass_consolidation_v2.py
Outputs (committed for reproducibility):
  research/experiments/consolidation_v2/results.json
  research/experiments/consolidation_v2/per_entry.csv
"""

import os
import re
import csv
import json
import yaml
from collections import defaultdict, Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ONTOLOGY_PATH = os.path.join(ROOT, "core/schemas/level3_accounts.yaml")
OUT_DIR = os.path.join(ROOT, "research/experiments/consolidation_v2")

# ---------------------------------------------------------------------------
# Load the real Level-3 ontology
# ---------------------------------------------------------------------------
def load_ontology():
    # The YAML is multi-section: the ASSETS section is a dict with key "level3";
    # LIABILITIES/EQUITY/INCOME/roadmap sections are bare YAML lists (no key).
    # Collect account dicts from BOTH shapes; an account is any item carrying
    # both "id" and "nature" (this excludes aggregation/validation rule blocks).
    docs = list(yaml.safe_load_all(open(ONTOLOGY_PATH, encoding="utf-8")))
    accounts = {}

    def ingest(item):
        if isinstance(item, dict) and "id" in item and "nature" in item:
            accounts[item["id"]] = {
                "uuid": item.get("uuid"),
                "label": item.get("label_en", item["id"]),
                "nature": item.get("nature", "unknown"),
                "local_codes": {k: str(v) for k, v in (item.get("local_codes") or {}).items()},
            }

    for d in docs:
        if isinstance(d, dict) and "level3" in d:
            for a in d["level3"]:
                ingest(a)
        elif isinstance(d, list):
            for a in d:
                ingest(a)
    # reverse index: jurisdiction -> {local_code -> kontablo_id}
    by_code = defaultdict(dict)
    for kid, a in accounts.items():
        for j, code in a["local_codes"].items():
            by_code[j][code] = kid
    return accounts, by_code


# ---------------------------------------------------------------------------
# Tier 2 deterministic multilingual keyword rules (auditable, no AI)
# Each rule: (kontablo_id, [substrings in lowercased local name])
# Languages: en, es, pt, fr, vi, ar, de, ru, ko, tr.
# ---------------------------------------------------------------------------
TIER2_RULES = [
    ("asset.current.crypto",      ["crypto", "bitcoin", "digital asset", "criptomoneda", "token"]),
    ("asset.current.carbon_credits", ["carbon credit", "crédito de carbono", "crédit carbone", "emission allowance"]),
    ("asset.noncurrent.biological", ["biological", "activo biológico", "actif biologique", "livestock", "ganado"]),
    ("liability.current.zakat",   ["zakat", "زكاة"]),
    ("asset.current.cash",        ["cash", "caja", "caisse", "caixa", "efectivo", "tiền mặt", "النقد", "kasse", "касса", "현금", "nakit", "espèces", "petty cash"]),
    ("asset.current.bank",        ["bank", "banco", "banque", "banca", "банк", "은행", "banka", "ngân hàng", "bancos"]),
    ("asset.current.receivables", ["receivable", "clientes", "clients", "cuentas por cobrar", "contas a receber", "дебитор", "매출채권", "alacak", "phải thu", "debtors"]),
    ("asset.current.inventory",   ["inventory", "inventario", "stock", "existencias", "estoque", "stocks", "запас", "재고", "stok", "hàng tồn kho"]),
    ("asset.current.vat_input",   ["vat input", "iva acreditable", "iva soportado", "tva déductible", "input vat", "input tax credit"]),
    ("asset.current.prepaid",     ["prepaid", "anticipo", "gastos pagados por anticipado", "charges constatées", "선급"]),
    ("asset.noncurrent.ppe",      ["ppe", "property plant", "propiedad planta", "immobilisations corporelles", "ativo imobilizado", "inmueble", "maquinaria", "основные средства", "유형자산", "maddi duran"]),
    ("asset.noncurrent.intangibles", ["intangible", "intangibles", "immobilisations incorporelles", "무형자산"]),
    ("asset.noncurrent.goodwill", ["goodwill", "fondo de comercio", "écart d'acquisition", "영업권"]),
    ("liability.current.payables", ["payable", "proveedores", "fornecedores", "fournisseurs", "cuentas por pagar", "кредитор", "매입채무", "borç", "phải trả"]),
    ("liability.current.vat_output", ["vat output", "iva por pagar", "iva repercutido", "tva collectée", "output vat"]),
    ("liability.current.tax",     ["tax payable", "impuestos por pagar", "impôt", "imposto a pagar", "vergi"]),
    ("liability.current.short_term_debt", ["short-term debt", "deuda corto plazo", "préstamo corto", "empréstimo"]),
    ("liability.noncurrent.debt", ["long-term debt", "deuda largo plazo", "dette", "emprunt", "차입금"]),
    ("liability.current.zakat",   ["zakat", "زكاة"]),
    ("equity.capital",            ["capital", "share capital", "capital social", "자본금", "sermaye"]),
    ("equity.retained",           ["retained", "resultados acumulados", "lucros acumulados", "report à nouveau", "이익잉여금"]),
    ("equity.reserves",           ["reserve", "reservas", "réserves", "yedek"]),
    ("revenue.operating",         ["revenue", "ingresos", "ventas", "receita", "chiffre d'affaires", "doanh thu", "매출", "gelir", "выручка"]),
    ("revenue.other",             ["other income", "otros ingresos", "produits divers"]),
    ("expense.cogs",              ["cogs", "cost of goods", "costo de ventas", "custo", "coût des ventes", "매출원가"]),
    ("expense.admin",             ["administrative", "gastos administrativos", "frais généraux", "despesas administrativas", "판관비"]),
    ("expense.depreciation",      ["depreciation", "depreciación", "amortissement", "depreciação", "감가상각"]),
    ("expense.interest",          ["interest expense", "gastos financieros", "charges d'intérêts", "이자비용"]),
    ("expense.fx_loss",           ["fx loss", "pérdida cambiaria", "perte de change", "diferencia en cambio", "환차손"]),
]


def resolve(entry, jurisdiction, accounts, by_code):
    """Return (kontablo_id, tier, confidence)."""
    code = str(entry["code"])
    # Tier 1: exact local-code lookup
    if code in by_code.get(jurisdiction, {}):
        return by_code[jurisdiction][code], "tier1_exact", 1.0
    # Tier 2: multilingual keyword rules
    name = entry["name"].lower()
    for kid, keys in TIER2_RULES:
        if any(k in name for k in keys):
            if kid in accounts:
                return kid, "tier2_keyword", 0.85
    # Escalate (residual -> CRA human review). Tier 3 AI not run here.
    return None, "escalated", 0.0


def cra_validate(entry, kid, accounts):
    """Co-responsibility deterministic boundary checks. Returns list of flags."""
    if not kid or kid not in accounts:
        return []
    flags = []
    target = accounts[kid]
    if entry.get("nature") and entry["nature"] != target["nature"]:
        flags.append(f"nature_mismatch:{entry['nature']}!={target['nature']}@{kid}")
    nm = entry["name"].lower()
    if ("cash" in nm or "bank" in nm or "caja" in nm or "banco" in nm) and "noncurrent" in kid:
        flags.append(f"boundary_violation:liquid_asset->noncurrent@{kid}")
    return flags


# ---------------------------------------------------------------------------
# Synthetic dataset: 20 entities across 17 jurisdictions, multi-account-type,
# hyperinflation dual-rate cases, francophone/Korean non-anglophone, and
# 3 deliberately malformed entries to exercise the CRA.
# ---------------------------------------------------------------------------
def dataset():
    return [
        # --- original 10 (continuity), broadened with more account types ---
        {"id":"MX-ENT-001","name":"Kontablo Mexico","j":"mx","ccy":"MXN","data":[
            {"code":"101","name":"Caja","nature":"debit","amt":50000},
            {"code":"105","name":"Clientes","nature":"debit","amt":120000},
            {"code":"201","name":"Proveedores","nature":"credit","amt":70000},
            {"code":"401","name":"Ventas","nature":"credit","amt":300000}]},
        {"id":"BR-ENT-002","name":"Kontablo Brazil","j":"br","ccy":"BRL","data":[
            {"code":"1.1.1.1.01-9","name":"Caixa Geral","nature":"debit","amt":30000},
            {"code":"x","name":"Clientes","nature":"debit","amt":80000},
            {"code":"x","name":"Estoque de Mercadorias","nature":"debit","amt":60000},
            {"code":"x","name":"Fornecedores","nature":"credit","amt":40000}]},
        {"id":"FR-ENT-003","name":"Kontablo France","j":"fr","ccy":"EUR","data":[
            {"code":"512","name":"Banque","nature":"debit","amt":25000},
            {"code":"411","name":"Clients","nature":"debit","amt":85000},
            {"code":"607","name":"Coût des ventes","nature":"debit","amt":55000},
            {"code":"706","name":"Chiffre d'affaires","nature":"credit","amt":210000}]},
        {"id":"PA-ENT-004","name":"Kontablo Panama","j":"pa","ccy":"USD","data":[
            {"code":"1.1.01","name":"Caja Fuerte","nature":"debit","amt":40000}]},
        {"id":"EC-ENT-005","name":"Kontablo Ecuador","j":"ec","ccy":"USD","data":[
            {"code":"x","name":"Caja Principal","nature":"debit","amt":12000},
            {"code":"x","name":"Inventario de Mercaderias","nature":"debit","amt":33000}]},
        {"id":"VE-ENT-006-OFF","name":"Venezuela (Official rate)","j":"ve","ccy":"VES","hyperinflation":True,"data":[
            {"code":"x","name":"Caja en Bolivares","nature":"debit","amt":1000000}]},
        {"id":"VE-ENT-007-PAR","name":"Venezuela (Parallel rate)","j":"ve","ccy":"VES","rate_override":0.013,"hyperinflation":True,"data":[
            {"code":"x","name":"Caja en Bolivares","nature":"debit","amt":1000000}]},
        {"id":"VN-ENT-008","name":"Kontablo Vietnam","j":"vn","ccy":"VND","data":[
            {"code":"111","name":"Tiền mặt","nature":"debit","amt":300000000},
            {"code":"x","name":"Phải thu khách hàng","nature":"debit","amt":500000000}]},
        {"id":"NG-ENT-009","name":"Kontablo Nigeria","j":"ng","ccy":"NGN","data":[
            {"code":"x","name":"Cash and Bank Balances","nature":"debit","amt":1500000}]},
        {"id":"SA-ENT-010","name":"Saudi Arabia (Zakat)","j":"sa","ccy":"SAR","data":[
            {"code":"101","name":"النقد","nature":"debit","amt":50000},
            {"code":"x","name":"Zakat Provision","nature":"credit","amt":18000}]},
        # --- expanded hyperinflation IAS 29 stress cases ---
        {"id":"AR-ENT-011-OFF","name":"Argentina (Official)","j":"ar","ccy":"ARS","hyperinflation":True,"data":[
            {"code":"1100","name":"Caja y Bancos","nature":"debit","amt":9000000}]},
        {"id":"AR-ENT-012-PAR","name":"Argentina (Blue/Parallel)","j":"ar","ccy":"ARS","rate_override":0.0008,"hyperinflation":True,"data":[
            {"code":"1100","name":"Caja y Bancos","nature":"debit","amt":9000000}]},
        {"id":"TR-ENT-013","name":"Turkey (IAS 29)","j":"tr","ccy":"TRY","hyperinflation":True,"data":[
            {"code":"x","name":"Nakit ve Nakit Benzerleri","nature":"debit","amt":2000000},
            {"code":"x","name":"Ticari Alacaklar","nature":"debit","amt":3500000}]},
        {"id":"LB-ENT-014","name":"Lebanon (IAS 29)","j":"lb","ccy":"LBP","rate_override":0.000011,"hyperinflation":True,"data":[
            {"code":"x","name":"Cash on hand","nature":"debit","amt":1500000000}]},
        # --- non-anglophone thin-corpus (Tier 2 by name; no local_codes) ---
        {"id":"SN-ENT-015","name":"Senegal (SYSCOHADA)","j":"sn","ccy":"XOF","data":[
            {"code":"x","name":"Banque","nature":"debit","amt":18000000},
            {"code":"x","name":"Clients","nature":"debit","amt":25000000},
            {"code":"x","name":"Fournisseurs","nature":"credit","amt":15000000}]},
        {"id":"CI-ENT-016","name":"Côte d'Ivoire (SYSCOHADA)","j":"ci","ccy":"XOF","data":[
            {"code":"x","name":"Caisse","nature":"debit","amt":7000000}]},
        {"id":"KR-ENT-017","name":"South Korea (K-IFRS)","j":"kr","ccy":"KRW","data":[
            {"code":"x","name":"현금","nature":"debit","amt":120000000},
            {"code":"x","name":"매출채권","nature":"debit","amt":250000000},
            {"code":"x","name":"유형자산","nature":"debit","amt":800000000}]},
        # --- agentic-economy / novel instruments (coverage tail) ---
        {"id":"US-ENT-018","name":"USA (digital assets)","j":"us","ccy":"USD","data":[
            {"code":"x","name":"Bitcoin Treasury Holdings","nature":"debit","amt":250000},
            {"code":"x","name":"Carbon Credit Holdings","nature":"debit","amt":40000},
            {"code":"x","name":"Operating Revenue","nature":"credit","amt":900000}]},
        # --- entity with a genuinely unmapped exotic account (escalation) ---
        {"id":"DE-ENT-019","name":"Germany (edge case)","j":"de","ccy":"EUR","data":[
            {"code":"x","name":"Sonderposten mit Ruecklageanteil","nature":"credit","amt":50000},  # special tax-driven reserve, no clean IFRS node -> escalate
            {"code":"x","name":"Kasse","nature":"debit","amt":20000}]},
        # --- DELIBERATELY MALFORMED entity to exercise the CRA ---
        {"id":"XX-ENT-020-BAD","name":"Injected errors (CRA test)","j":"mx","ccy":"USD","data":[
            {"code":"x","name":"Caja Chica","nature":"credit","amt":5000},                 # cash declared credit -> nature_mismatch
            {"code":"x","name":"Bank Current Account","nature":"debit","amt":8000,"forced_id":"asset.noncurrent.ppe"},  # liquid->noncurrent boundary violation
            {"code":"x","name":"Ventas","nature":"debit","amt":10000}]},                   # revenue declared debit -> nature_mismatch
    ]


FX = {"MXN":0.058,"BRL":0.20,"EUR":1.08,"USD":1.0,"VES":0.027,"VND":0.00004,
      "NGN":0.00065,"SAR":0.27,"ARS":0.0011,"TRY":0.030,"LBP":0.0000112,
      "XOF":0.00165,"KRW":0.00073}


def main():
    accounts, by_code = load_ontology()
    data = dataset()

    consolidated = defaultdict(float)     # kontablo_id -> USD
    tier_counts = Counter()
    per_entry = []
    flags_all = []
    countries = set()
    entities = 0
    total_entries = 0
    resolved = 0
    escalated = 0

    for ent in data:
        entities += 1
        countries.add(ent["j"])
        rate = ent.get("rate_override", FX.get(ent["ccy"], 1.0))
        for e in ent["data"]:
            total_entries += 1
            forced = e.get("forced_id")
            if forced:
                kid, tier, conf = forced, "forced_upstream", 0.5
            else:
                kid, tier, conf = resolve(e, ent["j"], accounts, by_code)
            tier_counts[tier] += 1
            flags = cra_validate(e, kid, accounts)
            if flags:
                conf = min(conf, 0.3)
                for f in flags:
                    flags_all.append({"entity": ent["id"], "name": e["name"], "flag": f})
            if kid is None:
                escalated += 1
            else:
                resolved += 1
                consolidated[kid] += e["amt"] * rate
            per_entry.append({
                "entity": ent["id"], "jurisdiction": ent["j"], "currency": ent["ccy"],
                "local_code": e["code"], "local_name": e["name"],
                "kontablo_id": kid or "ESCALATED", "tier": tier,
                "confidence": conf, "usd_value": round(e["amt"] * rate, 2),
                "cra_flags": ";".join(flags) if flags else "",
            })

    # ---- report ----
    print("="*78)
    print("KONTABLO MASS-CONSOLIDATION VALIDATION  v2  (deterministic, reproducible)")
    print("="*78)
    print(f"Entities consolidated      : {entities}")
    print(f"Jurisdictions (countries)  : {len(countries)}  -> {sorted(countries)}")
    print(f"Hyperinflation IAS-29 cases: {sorted({e['j'] for e in data if e.get('hyperinflation')})}")
    print(f"Total local account entries: {total_entries}")
    print(f"Distinct Kontablo nodes hit : {len([k for k in consolidated])}")
    print("-"*78)
    print("TIER DISTRIBUTION (deterministic resolution):")
    for t, c in tier_counts.most_common():
        print(f"   {t:<18}: {c:>3}  ({100*c/total_entries:5.1f}%)")
    det_cov = 100*(tier_counts['tier1_exact']+tier_counts['tier2_keyword'])/total_entries
    print(f"   deterministic coverage : {det_cov:5.1f}%  (Tier1+Tier2)")
    print(f"   escalated to human (CRA): {escalated}  ({100*escalated/total_entries:.1f}%)")
    print("-"*78)
    print(f"CO-RESPONSIBILITY: {len(flags_all)} inconsistency flag(s) raised:")
    for f in flags_all:
        print(f"   [{f['entity']}] {f['name']}: {f['flag']}")
    print("-"*78)
    print("CONSOLIDATED BALANCE SHEET (USD, multi-jurisdiction, FX-normalized):")
    print(f"   {'Kontablo ID':<32} {'Label':<28} {'USD':>16}")
    total_assets = 0.0
    for kid in sorted(consolidated):
        a = accounts.get(kid, {"label":"?"})
        v = consolidated[kid]
        if kid.startswith("asset"):
            total_assets += v
        print(f"   {kid:<32} {a['label'][:28]:<28} {v:>16,.2f}")
    print("-"*78)
    print(f"   {'TOTAL ASSETS (USD)':<61} {total_assets:>16,.2f}")
    print("="*78)

    # ---- persist artifacts ----
    os.makedirs(OUT_DIR, exist_ok=True)
    summary = {
        "entities": entities,
        "countries": sorted(countries),
        "n_countries": len(countries),
        "hyperinflation_cases": sorted({e['j'] for e in data if e.get('hyperinflation')}),
        "total_entries": total_entries,
        "distinct_nodes_hit": len(consolidated),
        "tier_distribution": dict(tier_counts),
        "deterministic_coverage_pct": round(det_cov, 1),
        "escalated": escalated,
        "escalated_pct": round(100*escalated/total_entries, 1),
        "cra_flags": flags_all,
        "consolidated_usd": {k: round(v, 2) for k, v in sorted(consolidated.items())},
        "total_assets_usd": round(total_assets, 2),
    }
    with open(os.path.join(OUT_DIR, "results.json"), "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    with open(os.path.join(OUT_DIR, "per_entry.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(per_entry[0].keys()))
        w.writeheader()
        w.writerows(per_entry)
    print(f"Artifacts written to {os.path.relpath(OUT_DIR, ROOT)}/ (results.json, per_entry.csv)")


if __name__ == "__main__":
    main()
