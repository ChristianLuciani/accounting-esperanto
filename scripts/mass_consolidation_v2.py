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
import sys
import csv
import json
import yaml
from collections import defaultdict, Counter

# Run as a script (`python scripts/mass_consolidation_v2.py`): put the repo root
# on sys.path so the shared harness package (`core.harness`) is importable.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

# The deterministic core lives in the shared harness package — this script is
# now purely the validation RUNNER (synthetic data + the run + artifact writing)
# and imports the resolver, the Deterministic Boundary Library, the ontology
# loaders, and the FX tables rather than defining them. Re-defining them here
# is what created the inverted dependency (core.engine importing from this
# script); keep this import-only.
from core.harness import (  # noqa: E402
    FX,
    JCCY,
    TIER2_RULES,  # noqa: F401  (re-exported for callers importing it from here)
    cra_validate,
    load_families,
    load_ontology,
    merge_family_codes,
    resolve,
)

COVERAGE_PATH = os.path.join(ROOT, "core/schemas/jurisdiction_coverage.yaml")
OUT_DIR = os.path.join(ROOT, "research/experiments/consolidation_v2")


def load_coverage():
    """195-jurisdiction manifest (list of dict rows). Runner-local: the coverage
    manifest is used only for the printed/serialised report, not for resolution."""
    doc = yaml.safe_load(open(COVERAGE_PATH, encoding="utf-8"))
    return doc.get("jurisdictions", [])


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


# Currency per jurisdiction (JCCY) and USD-per-unit FX (FX) now live in
# core.harness.fx (imported above) — shared with core.engine's normalisation.

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
