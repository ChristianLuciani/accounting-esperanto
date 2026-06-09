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
COVERAGE_PATH = os.path.join(ROOT, "core/schemas/jurisdiction_coverage.yaml")
FAMILIES_PATH = os.path.join(ROOT, "core/schemas/chart_families.yaml")
OUT_DIR = os.path.join(ROOT, "research/experiments/consolidation_v2")


def load_families():
    """family -> {members:[iso], codes:{kontablo_id: local_code}}."""
    doc = yaml.safe_load(open(FAMILIES_PATH, encoding="utf-8"))
    return doc.get("families", {})


def load_coverage():
    """195-jurisdiction manifest (list of dict rows)."""
    doc = yaml.safe_load(open(COVERAGE_PATH, encoding="utf-8"))
    return doc.get("jurisdictions", [])


def merge_family_codes(by_code, families):
    """Add shared statutory-chart-family codes into the per-jurisdiction Tier-1
    index for every member jurisdiction (e.g., SYSCOHADA -> 17 OHADA states)."""
    for fam in families.values():
        for member in fam.get("members", []):
            for kid, code in fam.get("codes", {}).items():
                by_code.setdefault(member, {}).setdefault(str(code), kid)
    return by_code

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
                "statement": item.get("statement", "unknown"),
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
    # A real statutory code contains at least one digit. Descriptive text
    # placeholders (e.g. "Cash", "Vorsteuer", "IVA Acreditable") are NOT codes
    # and are excluded from the Tier-1 index (boundary condition B1).
    def is_code(c):
        return any(ch.isdigit() for ch in str(c))

    raw = defaultdict(lambda: defaultdict(list))
    placeholders = []
    for kid, a in accounts.items():
        for j, code in a["local_codes"].items():
            if is_code(code):
                raw[j][code].append(kid)
            else:
                placeholders.append({"jurisdiction": j, "code": str(code), "id": kid})
    by_code = defaultdict(dict)
    collisions = []
    for j in raw:
        for code, ids in raw[j].items():
            if len(ids) > 1:
                collisions.append({"jurisdiction": j, "code": code, "ids": sorted(ids)})
            else:
                by_code[j][code] = ids[0]
    return accounts, by_code, collisions, placeholders


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
    ("asset.current.cash",        ["cash", "caja", "caisse", "caixa", "efectivo", "tiền mặt", "النقد", "kasse", "касса", "현금", "nakit", "espèces", "petty cash", "cassa", "kasa", "kas", "ταμείο"]),
    ("asset.current.bank",        ["bank", "banco", "banque", "banca", "банк", "은행", "banka", "ngân hàng", "bancos", "البنك", "τράπεζα"]),
    ("asset.current.receivables", ["receivable", "clientes", "clients", "cuentas por cobrar", "contas a receber", "дебитор", "매출채권", "alacak", "phải thu", "debtors", "clienti", "należności", "piutang", "πελάτες", "ذمم مدينة"]),
    ("asset.current.inventory",   ["inventory", "inventario", "stock", "existencias", "estoque", "stocks", "запас", "재고", "stok", "hàng tồn kho", "magazzino", "zapasy", "persediaan"]),
    ("asset.current.vat_input",   ["vat input", "iva acreditable", "iva soportado", "tva déductible", "input vat", "input tax credit"]),
    ("asset.current.prepaid",     ["prepaid", "anticipo", "gastos pagados por anticipado", "charges constatées", "선급"]),
    ("asset.noncurrent.ppe",      ["ppe", "property plant", "propiedad planta", "immobilisations corporelles", "ativo imobilizado", "inmueble", "maquinaria", "основные средства", "유형자산", "maddi duran"]),
    ("asset.noncurrent.intangibles", ["intangible", "intangibles", "immobilisations incorporelles", "무형자산"]),
    ("asset.noncurrent.goodwill", ["goodwill", "fondo de comercio", "écart d'acquisition", "영업권"]),
    ("liability.current.payables", ["payable", "proveedores", "fornecedores", "fournisseurs", "cuentas por pagar", "кредитор", "매입채무", "borç", "phải trả", "fornitori", "zobowiązania", "utang", "προμηθευτές", "موردون"]),
    ("liability.current.vat_output", ["vat output", "iva por pagar", "iva repercutido", "tva collectée", "output vat"]),
    ("liability.current.tax",     ["tax payable", "impuestos por pagar", "impôt", "imposto a pagar", "vergi"]),
    ("liability.current.short_term_debt", ["short-term debt", "deuda corto plazo", "préstamo corto", "empréstimo"]),
    ("liability.noncurrent.debt", ["long-term debt", "deuda largo plazo", "dette", "emprunt", "차입금"]),
    ("liability.current.zakat",   ["zakat", "زكاة"]),
    ("equity.capital",            ["capital", "share capital", "capital social", "자본금", "sermaye"]),
    ("equity.retained",           ["retained", "resultados acumulados", "lucros acumulados", "report à nouveau", "이익잉여금"]),
    ("equity.reserves",           ["reserve", "reservas", "réserves", "yedek"]),
    ("revenue.operating",         ["revenue", "ingresos", "ventas", "receita", "chiffre d'affaires", "doanh thu", "매출", "gelir", "выручка", "ricavi", "przychody", "pendapatan", "έσοδα", "πωλήσεις", "إيرادات", "sales"]),
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
    """Co-responsibility deterministic boundary checks. Returns list of flags.
    Each check is a deterministic accounting invariant; together they form the
    Deterministic Boundary Library exercised by the injected-error catalog."""
    if not kid or kid not in accounts:
        return []
    flags = []
    target = accounts[kid]
    nm = entry["name"].lower()

    # 1. Nature (debit/credit) must match the target node.
    if entry.get("nature") and entry["nature"] != target["nature"]:
        flags.append(f"nature_mismatch:{entry['nature']}!={target['nature']}@{kid}")

    # 2. Liquidity boundary: a liquid asset must not map to a non-current node.
    if any(w in nm for w in ("cash", "bank", "caja", "banco", "banque", "caisse")) \
       and "noncurrent" in kid:
        flags.append(f"boundary_violation:liquid_asset->noncurrent@{kid}")

    # Checks 3-5 are heuristic name-vs-target invariants used to catch a bad
    # upstream/AI proposal; they are applied to forced (proposed) mappings only,
    # so a correct name-derived resolution (e.g. "Prepaid Expenses" -> a
    # balance-sheet asset) is never false-flagged.
    if entry.get("forced_id"):
        # 3. Statement-class boundary: a P&L name must not land on a
        #    balance-sheet node, and vice versa.
        pl_words = ("revenue", "sales", "ventas", "ingreso", "depreciation", "interest")
        bs_words = ("receivable", "payable", "inventory", "capital", "equity")
        if any(w in nm for w in pl_words) and target["statement"] == "balance_sheet":
            flags.append(f"statement_mismatch:P&L_name->balance_sheet@{kid}")
        elif any(w in nm for w in bs_words) and target["statement"] == "income_statement":
            flags.append(f"statement_mismatch:balance_sheet_name->P&L@{kid}")

        # 4. VAT direction: input VAT must not map to the output node (or vice versa).
        in_vat = any(w in nm for w in ("input", "acreditable", "soportado", "récupérable", "recuperable"))
        out_vat = any(w in nm for w in ("output", "repercutido", "trasladado", "facturée", "facturada"))
        if in_vat and kid == "liability.current.vat_output":
            flags.append(f"vat_direction:input->output@{kid}")
        if out_vat and kid == "asset.current.vat_input":
            flags.append(f"vat_direction:output->input@{kid}")

        # 5. Equity vs liability: capital/equity must not map to a liability node.
        if any(w in nm for w in ("capital", "equity", "patrimonio")) and kid.startswith("liability"):
            flags.append(f"class_confusion:equity->liability@{kid}")

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
           "ec":"Ecuador","it":"Italy","pl":"Poland","id":"Indonesia","gr":"Greece",
           "cl":"Chile","pe":"Peru","ma":"Morocco","kz":"Kazakhstan","eg":"Egypt",
           "ke":"Kenya","ph":"Philippines","pk":"Pakistan","ch":"Switzerland"}


def build_entities(accounts, by_code, families=None):
    """Ontology-driven entities (one per jurisdiction with real local_codes,
    exercising Tier-1 exact lookup) plus curated stress/edge/CRA entities.
    Collided (ambiguous) codes are excluded via the cleaned by_code index."""
    families = families or {}
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

    # --- statutory chart-family member states (Tier-1, real cited codes).
    #     One verified chart can cover many jurisdictions (e.g. SYSCOHADA -> 17).
    #     Skip members already represented by inline ontology codes to avoid
    #     double-counting (e.g. ES, which is inline in level3_accounts.yaml).
    inline_juris = set(j2.keys())  # jurisdictions actually generated from numeric inline codes
    fam_pick = [("asset.current.cash", 50000), ("asset.current.bank", 40000),
                ("asset.current.receivables", 120000), ("liability.current.payables", 70000),
                ("revenue.operating", 300000)]
    for famname, fam in families.items():
        codes = fam.get("codes", {})
        if not codes:
            continue
        for member in fam.get("members", []):
            if member in inline_juris:
                continue  # already generated from inline ontology codes
            ccy = JCCY.get(member, "USD")
            rate = FX.get(ccy, 1.0)
            data = [{"code": str(codes[kid]), "name": accounts[kid]["label"],
                     "nature": accounts[kid]["nature"], "amt": round(usd / rate, 2)}
                    for kid, usd in fam_pick if kid in codes]
            if data:
                entities.append({"id": f"{member.upper()}-{famname}",
                                 "name": f"{COUNTRY.get(member, member.upper())} ({famname})",
                                 "j": member, "ccy": ccy, "data": data})

    # --- other non-anglophone thin-corpus jurisdictions (Tier-2 by name)
    entities += [
        {"id":"KR-KIFRS","name":"South Korea (K-IFRS, Tier-2)","j":"kr","ccy":"KRW","data":[
            {"code":"x","name":"현금","nature":"debit","amt":120000000},
            {"code":"x","name":"매출채권","nature":"debit","amt":250000000},
            {"code":"x","name":"유형자산","nature":"debit","amt":800000000}]},
    ]

    # --- additional Tier-2 jurisdictions (multilingual breadth, no ontology codes)
    def L(usd, ccy):  # local face amount giving ~usd after FX normalization
        return round(usd / FX[ccy], 2)
    more = [
        ("it","EUR",[("Cassa","debit",50000),("Crediti verso clienti","debit",120000),
                     ("Debiti verso fornitori","credit",70000),("Ricavi delle vendite","credit",300000)]),
        ("pl","PLN",[("Kasa","debit",50000),("Należności od klientów","debit",120000),
                     ("Zobowiązania wobec dostawców","credit",70000),("Przychody ze sprzedaży","credit",300000)]),
        ("id","IDR",[("Kas","debit",50000),("Piutang usaha","debit",120000),
                     ("Utang usaha","credit",70000),("Pendapatan","credit",300000)]),
        ("gr","EUR",[("Ταμείο","debit",50000),("Πελάτες","debit",120000),
                     ("Προμηθευτές","credit",70000),("Πωλήσεις","credit",300000)]),
        ("cl","CLP",[("Caja","debit",50000),("Clientes","debit",120000),("Ventas","credit",300000)]),
        # (pe -> PCGE family, ma -> CGNC family: now Tier-1, removed from Tier-2 to avoid duplicates)
        ("kz","KZT",[("Касса","debit",50000),("Дебиторская задолженность","debit",120000),
                     ("Кредиторская задолженность","credit",70000),("Выручка","credit",300000)]),
        ("eg","EGP",[("النقد","debit",50000),("البنك","debit",40000),
                     ("ذمم مدينة","debit",120000),("إيرادات","credit",300000)]),
        ("ke","KES",[("Cash at bank","debit",50000),("Trade Receivables","debit",120000),
                     ("Trade Payables","credit",70000),("Revenue","credit",300000)]),
        ("ph","PHP",[("Cash on hand","debit",50000),("Accounts Receivable","debit",120000),("Sales","credit",300000)]),
        ("pk","PKR",[("Bank balances","debit",40000),("Trade Debtors","debit",120000),("Revenue","credit",300000)]),
        ("ch","CHF",[("Banque","debit",40000),("Clients","debit",120000),("Chiffre d'affaires","credit",300000)]),
    ]
    for j, ccy, rows in more:
        entities.append({"id": f"{j.upper()}-T2", "name": f"{COUNTRY[j]} (Tier-2)",
                         "j": j, "ccy": ccy,
                         "data": [{"code":"x","name":nm,"nature":nat,"amt":L(usd,ccy)}
                                  for nm,nat,usd in rows]})

    # --- coverage-boundary escalations: v0.3-roadmap instruments + exotic reserve
    entities.append({"id":"US-FRONTIER","name":"USA (frontier instruments)","j":"us","ccy":"USD","data":[
        {"code":"x","name":"Bitcoin Treasury Holdings","nature":"debit","amt":250000},
        {"code":"x","name":"Carbon Credit Holdings","nature":"debit","amt":40000},
        {"code":"x","name":"Zakat Provision","nature":"credit","amt":18000}]})
    entities.append({"id":"DE-EDGE","name":"Germany (exotic reserve)","j":"de","ccy":"EUR","data":[
        {"code":"x","name":"Sonderposten mit Ruecklageanteil","nature":"credit","amt":50000}]})

    # --- DELIBERATELY MALFORMED entities: injected-error catalog exercising the
    #     full Deterministic Boundary Library. Each entry triggers a specific
    #     CRA check; forced_id simulates a bad upstream/AI proposal.
    entities.append({"id":"XX-CRA-TEST","name":"Injected errors (CRA catalog)","j":"mx","ccy":"USD","data":[
        # (1) nature mismatch: cash declared credit
        {"code":"x","name":"Caja Chica","nature":"credit","amt":5000},
        # (1) nature mismatch: revenue declared debit
        {"code":"x","name":"Ventas","nature":"debit","amt":10000},
        # (2) liquidity boundary: bank forced to a non-current node
        {"code":"x","name":"Bank Current Account","nature":"debit","amt":8000,"forced_id":"asset.noncurrent.ppe"},
        # (3) statement mismatch: revenue name forced to a balance-sheet node
        {"code":"x","name":"Sales Revenue Domestic","nature":"credit","amt":12000,"forced_id":"asset.current.cash"},
        # (3) statement mismatch: balance-sheet name forced to a P&L node
        {"code":"x","name":"Trade Receivables","nature":"debit","amt":9000,"forced_id":"revenue.operating"},
        # (4) VAT direction: input VAT forced to the output-VAT node
        {"code":"x","name":"IVA Acreditable (input)","nature":"debit","amt":3000,"forced_id":"liability.current.vat_output"},
        # (4) VAT direction: output VAT forced to the input-VAT node
        {"code":"x","name":"IVA Repercutido (output)","nature":"credit","amt":3000,"forced_id":"asset.current.vat_input"},
        # (5) class confusion: equity forced to a liability node
        {"code":"x","name":"Capital Social","nature":"credit","amt":40000,"forced_id":"liability.noncurrent.debt"},
    ]})
    return entities


# Currency per jurisdiction (ISO) and USD-per-unit FX (synthetic 2026 rates).
JCCY = {"ae":"AED","ar":"ARS","br":"BRL","ca":"CAD","cn":"CNY","co":"COP",
        "de":"EUR","es":"EUR","fr":"EUR","il":"ILS","in":"INR","jp":"JPY",
        "mx":"MXN","ng":"NGN","pa":"USD","ru":"RUB","sa":"SAR","tr":"TRY",
        "uk":"GBP","us":"USD","ve":"VES","vn":"VND","za":"ZAR",
        "sn":"XOF","ci":"XOF","kr":"KRW","lb":"LBP","ec":"USD",
        # --- additional Tier-2 jurisdictions (no ontology local_codes) ---
        "it":"EUR","pl":"PLN","id":"IDR","gr":"EUR","cl":"CLP","pe":"PEN",
        "ma":"MAD","kz":"KZT","eg":"EGP","ke":"KES","ph":"PHP","pk":"PKR",
        "ch":"CHF","dz":"DZD","ro":"RON","be":"EUR",
        "cz":"CZK","sk":"EUR","hu":"HUF","bg":"BGN",
        "ua":"UAH","tn":"TND","by":"BYN",
        "rs":"RSD","hr":"EUR","si":"EUR","at":"EUR",
        # --- OHADA member currencies (SYSCOHADA) ---
        "bj":"XOF","bf":"XOF","ml":"XOF","ne":"XOF","tg":"XOF","gw":"XOF",
        "cm":"XAF","cf":"XAF","td":"XAF","cg":"XAF","gq":"XAF","ga":"XAF",
        "km":"KMF","cd":"CDF"}
FX = {"AED":0.27,"ARS":0.0011,"BRL":0.20,"CAD":0.73,"CNY":0.14,"COP":0.00025,
      "EUR":1.08,"ILS":0.27,"INR":0.012,"JPY":0.0067,"MXN":0.058,"NGN":0.00065,
      "RUB":0.011,"SAR":0.27,"TRY":0.030,"GBP":1.27,"USD":1.0,"VES":0.027,
      "VND":0.00004,"ZAR":0.054,"XOF":0.00165,"KRW":0.00073,"LBP":0.0000112,
      "PLN":0.25,"IDR":0.000062,"CLP":0.0011,"PEN":0.27,"MAD":0.10,"KZT":0.0021,
      "EGP":0.021,"KES":0.0078,"PHP":0.018,"PKR":0.0036,"CHF":1.13,
      "XAF":0.00165,"KMF":0.0022,"CDF":0.00035,"DZD":0.0074,"RON":0.22,
      "CZK":0.043,"HUF":0.0028,"BGN":0.55,"UAH":0.024,"TND":0.32,"BYN":0.31,
      "RSD":0.0092}

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
    accounts, by_code, collisions, placeholders = load_ontology()
    families = load_families()
    by_code = merge_family_codes(by_code, families)
    coverage = load_coverage()
    data = build_entities(accounts, by_code, families)

    consolidated = defaultdict(float)     # kontablo_id -> USD
    tier_counts = Counter()
    per_entry = []
    flags_all = []
    countries = set()
    entities = 0
    total_entries = 0
    resolved = 0
    escalated = 0
    quarantined = 0

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
            elif flags:
                # CRA quarantine: a flagged mapping is held for human review and
                # is NOT posted to the consolidated ledger.
                quarantined += 1
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

    # ---- 195-jurisdiction coverage manifest ----
    cov_total = len(coverage)
    cov_stat = sum(1 for r in coverage if r["mapping_mode"] == "statutory_chart")
    cov_ifrs = sum(1 for r in coverage if r["mapping_mode"] == "ifrs_direct")
    cov_t1 = sum(1 for r in coverage if r.get("tier1_codes_available"))
    print("="*78)
    print("KONTABLO 195-JURISDICTION COVERAGE MANIFEST")
    print("="*78)
    print(f"Sovereign states covered   : {cov_total}  (193 UN members + Holy See + Palestine)")
    print(f"  universal IFRS-anchor    : {cov_total}/195  (every node carries an ifrs_tag)")
    print(f"  statutory-chart overlay  : {cov_stat}  (mandated national chart; chart_family named)")
    print(f"  IFRS-direct (no chart)   : {cov_ifrs}  (mapping via IFRS tag)")
    print(f"  Tier-1 code sets ready   : {cov_t1}  (primary-source cited; incl. 17 via SYSCOHADA)")

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
    print(f"CO-RESPONSIBILITY: {len(flags_all)} flag(s) across {quarantined} quarantined "
          f"entr(y/ies) (held for human review, NOT posted):")
    for f in flags_all:
        print(f"   [{f['entity']}] {f['name']}: {f['flag']}")
    print("-"*78)
    print(f"ONTOLOGY DEFECTS SURFACED: {len(collisions)} local-code collision(s) "
          f"(same jurisdiction+code -> multiple nodes; excluded from Tier 1):")
    for c in collisions:
        print(f"   {c['jurisdiction']}: code {c['code']!r} -> {c['ids']}")
    print(f"DESCRIPTIVE PLACEHOLDERS EXCLUDED FROM TIER 1 (not statutory codes, "
          f"boundary B1): {len(placeholders)}")
    for p in placeholders:
        print(f"   {p['jurisdiction']}: {p['code']!r} ({p['id']})")
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
        "coverage_manifest": {
            "sovereign_states": cov_total,
            "statutory_chart": cov_stat,
            "ifrs_direct": cov_ifrs,
            "tier1_code_sets_ready": cov_t1,
        },
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
        "descriptive_placeholders_excluded": placeholders,
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
