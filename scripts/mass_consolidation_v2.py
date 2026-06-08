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
    # reverse index: jurisdiction -> {local_code -> kontablo_id}, detecting
    # collisions (same jurisdiction+code mapped to >1 Kontablo node = a latent
    # ontology data-quality defect). Collided codes are EXCLUDED from the
    # deterministic index so they are not silently mis-resolved.
    raw = defaultdict(lambda: defaultdict(list))
    for kid, a in accounts.items():
        for j, code in a["local_codes"].items():
            raw[j][code].append(kid)
    by_code = defaultdict(dict)
    collisions = []
    for j in raw:
        for code, ids in raw[j].items():
            if len(ids) > 1:
                collisions.append({"jurisdiction": j, "code": code, "ids": sorted(ids)})
            else:
                by_code[j][code] = ids[0]
    return accounts, by_code, collisions


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
COUNTRY = {"ae":"UAE","ar":"Argentina","br":"Brazil","ca":"Canada","cn":"China",
           "co":"Colombia","de":"Germany","es":"Spain","fr":"France","il":"Israel",
           "in":"India","jp":"Japan","mx":"Mexico","ng":"Nigeria","pa":"Panama",
           "ru":"Russia","sa":"Saudi Arabia","tr":"Turkey","uk":"United Kingdom",
           "us":"USA","ve":"Venezuela","vn":"Vietnam","za":"South Africa",
           "sn":"Senegal","ci":"Cote d'Ivoire","kr":"South Korea","lb":"Lebanon",
           "ec":"Ecuador"}


def build_entities(accounts, by_code):
    """Ontology-driven entities (one per jurisdiction with real local_codes,
    exercising Tier-1 exact lookup) plus curated stress/edge/CRA entities.
    Collided (ambiguous) codes are excluded via the cleaned by_code index."""
    # jurisdiction -> [(account_id, local_code)] (unambiguous codes only)
    j2 = defaultdict(list)
    for aid, a in accounts.items():
        for j, code in a["local_codes"].items():
            if by_code.get(j, {}).get(code) == aid:   # skip collided codes
                j2[j].append((aid, code))

    entities = []
    n = 0
    for j in sorted(j2):
        n += 1
        ccy = JCCY.get(j, "USD")
        rate = FX.get(ccy, 1.0)
        data = []
        for aid, code in sorted(j2[j]):
            amt = round(base_for(aid) / rate, 2)  # local face ~ comparable USD
            data.append({"code": code, "name": accounts[aid]["label"],
                         "nature": accounts[aid]["nature"], "amt": amt})
        entities.append({"id": f"{j.upper()}-{n:02d}",
                         "name": f"{COUNTRY.get(j, j.upper())} (ontology-coded)",
                         "j": j, "ccy": ccy, "data": data})

    # --- IAS 29 hyperinflation: parallel-rate duplicates (dual-rate divergence)
    for j, override in [("ve", 0.013), ("ar", 0.0008), ("tr", 0.012)]:
        ccy = JCCY[j]
        cash_code = next((c for aid, c in j2.get(j, []) if aid == "asset.current.cash"), "x")
        entities.append({"id": f"{j.upper()}-PARALLEL", "j": j, "ccy": ccy,
                         "name": f"{COUNTRY[j]} (parallel/IAS29 rate)",
                         "rate_override": override, "hyperinflation": True,
                         "data": [{"code": cash_code, "name": accounts["asset.current.cash"]["label"],
                                   "nature": "debit", "amt": round(50000 / FX[ccy], 2)}]})
    # mark official-rate hyperinflation entities too (for reporting)
    for e in entities:
        if e["j"] in ("ve", "ar", "tr"):
            e["hyperinflation"] = True

    # --- Lebanon: hyperinflation, NOT in ontology codes -> Tier-2 by name
    entities.append({"id":"LB-TIER2","name":"Lebanon (IAS29, Tier-2)","j":"lb","ccy":"LBP",
        "rate_override":0.000011,"hyperinflation":True,
        "data":[{"code":"x","name":"Cash on hand","nature":"debit","amt":1500000000}]})

    # --- non-anglophone thin-corpus jurisdictions without local_codes (Tier-2)
    entities += [
        {"id":"SN-SYSCOHADA","name":"Senegal (SYSCOHADA, Tier-2)","j":"sn","ccy":"XOF","data":[
            {"code":"x","name":"Banque","nature":"debit","amt":18000000},
            {"code":"x","name":"Clients","nature":"debit","amt":25000000},
            {"code":"x","name":"Fournisseurs","nature":"credit","amt":15000000}]},
        {"id":"CI-SYSCOHADA","name":"Cote d'Ivoire (SYSCOHADA, Tier-2)","j":"ci","ccy":"XOF","data":[
            {"code":"x","name":"Caisse","nature":"debit","amt":7000000}]},
        {"id":"KR-KIFRS","name":"South Korea (K-IFRS, Tier-2)","j":"kr","ccy":"KRW","data":[
            {"code":"x","name":"현금","nature":"debit","amt":120000000},
            {"code":"x","name":"매출채권","nature":"debit","amt":250000000},
            {"code":"x","name":"유형자산","nature":"debit","amt":800000000}]},
    ]

    # --- coverage-boundary escalations: v0.3-roadmap instruments + exotic reserve
    entities.append({"id":"US-FRONTIER","name":"USA (frontier instruments)","j":"us","ccy":"USD","data":[
        {"code":"x","name":"Bitcoin Treasury Holdings","nature":"debit","amt":250000},
        {"code":"x","name":"Carbon Credit Holdings","nature":"debit","amt":40000},
        {"code":"x","name":"Zakat Provision","nature":"credit","amt":18000}]})
    entities.append({"id":"DE-EDGE","name":"Germany (exotic reserve)","j":"de","ccy":"EUR","data":[
        {"code":"x","name":"Sonderposten mit Ruecklageanteil","nature":"credit","amt":50000}]})

    # --- DELIBERATELY MALFORMED entity to exercise the CRA
    entities.append({"id":"XX-CRA-TEST","name":"Injected errors (CRA test)","j":"mx","ccy":"USD","data":[
        {"code":"x","name":"Caja Chica","nature":"credit","amt":5000},
        {"code":"x","name":"Bank Current Account","nature":"debit","amt":8000,"forced_id":"asset.noncurrent.ppe"},
        {"code":"x","name":"Ventas","nature":"debit","amt":10000}]})
    return entities


# Currency per jurisdiction (ISO) and USD-per-unit FX (synthetic 2026 rates).
JCCY = {"ae":"AED","ar":"ARS","br":"BRL","ca":"CAD","cn":"CNY","co":"COP",
        "de":"EUR","es":"EUR","fr":"EUR","il":"ILS","in":"INR","jp":"JPY",
        "mx":"MXN","ng":"NGN","pa":"USD","ru":"RUB","sa":"SAR","tr":"TRY",
        "uk":"GBP","us":"USD","ve":"VES","vn":"VND","za":"ZAR",
        "sn":"XOF","ci":"XOF","kr":"KRW","lb":"LBP","ec":"USD"}
FX = {"AED":0.27,"ARS":0.0011,"BRL":0.20,"CAD":0.73,"CNY":0.14,"COP":0.00025,
      "EUR":1.08,"ILS":0.27,"INR":0.012,"JPY":0.0067,"MXN":0.058,"NGN":0.00065,
      "RUB":0.011,"SAR":0.27,"TRY":0.030,"GBP":1.27,"USD":1.0,"VES":0.027,
      "VND":0.00004,"ZAR":0.054,"XOF":0.00165,"KRW":0.00073,"LBP":0.0000112}

# Representative USD face value per account class (local amounts are derived as
# base/FX so each coded account contributes a comparable USD magnitude).
BASE_USD = {
    "asset.current.cash":50000, "asset.current.bank":40000,
    "asset.current.receivables":120000, "asset.current.inventory":60000,
    "asset.current.vat_input":8000, "asset.current.prepaid":5000,
    "asset.noncurrent.ppe":200000, "liability":40000, "equity":80000,
    "revenue":300000, "expense":90000,
}
def base_for(aid):
    if aid in BASE_USD: return BASE_USD[aid]
    for pref in ("asset.noncurrent","liability","equity","revenue","expense"):
        if aid.startswith(pref): return BASE_USD.get(pref, 30000)
    return 30000


def main():
    accounts, by_code, collisions = load_ontology()
    data = build_entities(accounts, by_code)

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
    print(f"CO-RESPONSIBILITY: {len(flags_all)} inconsistency flag(s) raised on injected errors:")
    for f in flags_all:
        print(f"   [{f['entity']}] {f['name']}: {f['flag']}")
    print("-"*78)
    print(f"ONTOLOGY DEFECTS SURFACED: {len(collisions)} local-code collision(s) "
          f"(same jurisdiction+code -> multiple nodes; excluded from Tier 1):")
    for c in collisions:
        print(f"   {c['jurisdiction']}: code {c['code']!r} -> {c['ids']}")
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
        "ontology_code_collisions": collisions,
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
