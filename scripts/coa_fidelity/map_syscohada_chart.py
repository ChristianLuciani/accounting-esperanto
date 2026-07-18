#!/usr/bin/env python3
"""
Deterministic classification of the verbatim SYSCOHADA official chart
(produced by parse_syscohada_chart.py) onto Kontablo's universal Level-3
ontology (core/schemas/level3_accounts.yaml) -- the same longest-prefix-match
approach as map_official_chart.py (principle #5: determinism over
stochasticity; principle #3: logic-based mapping via deterministic scripts).
A separate script rather than extending map_official_chart.py because the
source schema differs (a "class" digit instead of a "statement" string, no
per-line debit/credit "signe" field to derive nature from -- see
parse_syscohada_chart.py's docstring).

Any code with no matching rule is written out with kontablo_uuid: null and
needs_review: true -- never a forced guess. SYSCOHADA class 9 (comptes des
engagements hors bilan et comptabilite analytique de gestion) is, per the
source itself, "d'application facultative" (optional) and is not part of
the mandatory double-entry ledger (off-balance-sheet memoranda + internal
management-accounting accounts) -- it is tagged is_statement_caption: true
across the board, mirroring how parse_official_chart.py/map_official_chart.py
already treats Ecuador's own class-9 codes as non-postable.

Usage:
    python3 scripts/coa_fidelity/map_syscohada_chart.py \
        --official localizations/_syscohada/syscohada_official_chart.yaml \
        --out localizations/_syscohada/syscohada_mapping.yaml
"""
import argparse
import yaml

ONTOLOGY_PATH = "core/schemas/level3_accounts.yaml"

# --- SYSCOHADA (AUDCIF revise, "Liste des comptes") prefix -> Level-3 id ---
# Longest-prefix match wins. Every prefix here was verified against
# localizations/_syscohada/syscohada_official_chart.yaml before being added.
# Rules are deliberately given at the shortest prefix that stays semantically
# clean; a longer, more specific prefix below overrides its own parent
# whenever the sub-account's nature genuinely differs (e.g. "409" is a
# debit-side supplier prepayment carved out of the credit-side "40"
# fournisseurs bucket).
SYSCOHADA_RULES = {
    # ───────── CLASSE 1 : COMPTES DE RESSOURCES DURABLES ─────────
    "10": "equity.capital",             # CAPITAL (101-105, 109)
    "106": "equity.reserves",           # ÉCARTS DE RÉÉVALUATION -- a revaluation reserve, not paid-in capital
    "11": "equity.reserves",            # RÉSERVES
    "12": "equity.retained",            # REPORT A NOUVEAU
    "130": "equity.retained",           # RÉSULTAT EN INSTANCE D'AFFECTATION
    "131": "equity.retained",           # RÉSULTAT NET : BÉNÉFICE
    # 132-137 (MC, VA, EBE, RE, RF, RAO) are computed "soldes intermediaires
    # de gestion" -- presentation subtotals, not postable accounts -- see
    # classify() SIG_CAPTION_PREFIXES below.
    "138": "equity.retained",           # RÉSULTAT HORS ACTIVITÉS ORDINAIRES (parent code; real children 1381-1384 inherit via is_aggregate)
    "139": "equity.retained",           # RÉSULTAT NET : PERTE
    # 14 SUBVENTIONS D'INVESTISSEMENT: no deferred-income/grant node exists -- needs_review.
    # 151 AMORTISSEMENTS DÉROGATOIRES: an IFRS/IAS-12 lens reads this as a deferred-tax
    # liability (excess tax depreciation = taxable temporary difference), but SYSCOHADA
    # presents all of class 15 "provisions réglementées" as equity-side ("capitaux propres
    # et ressources assimilées"), not as a liability -- it does not behave as one locally.
    # Left as needs_review rather than forced into liability.noncurrent.deferred_tax, same
    # honesty standard as the IAS 41 biological-asset gap (Greptile PR #79 review).
    # 151-158 (all of class 15, regulated reserves/funds): no matching node -- needs_review.
    "16": "liability.noncurrent.debt",  # EMPRUNTS ET DETTES ASSIMILÉES (161-168)
    "17": "liability.noncurrent.lease", # DETTES DE LOCATION ACQUISITION (172-178)
    # 18 (participations/liaison inter-entites) and 19 (provisions pour
    # risques et charges): no matching node -- needs_review (genuine gaps;
    # no "liability.noncurrent.provisions" or intercompany-liaison node
    # exists in the 34-node core).

    # ───────── CLASSE 2 : COMPTES D'ACTIF IMMOBILISE ─────────
    "21": "asset.noncurrent.intangibles",   # 211-219
    "22": "asset.noncurrent.ppe",           # TERRAINS
    "23": "asset.noncurrent.ppe",           # BÂTIMENTS...
    "24": "asset.noncurrent.ppe",           # MATÉRIEL, MOBILIER...
    "246": "needs_review",                  # ACTIFS BIOLOGIQUES -- same IAS 41 gap noted in localizations/ec
    "247": "asset.noncurrent.ppe",          # AGENCEMENTS... ET ACTIFS BIOLOGIQUES -- predominantly equipment fittings
    "249": "needs_review",                  # MATÉRIELS ET ACTIFS BIOLOGIQUES EN COURS -- mixed WIP incl. biological, ambiguous
    "251": "asset.noncurrent.intangibles",  # AVANCES SUR IMMOBILISATIONS INCORPORELLES
    "252": "asset.noncurrent.ppe",          # AVANCES SUR IMMOBILISATIONS CORPORELLES
    "26": "asset.noncurrent.investments",   # TITRES DE PARTICIPATION (261-268)
    "27": "asset.noncurrent.investments",   # PRÊTS ET CRÉANCES / AUTRES IMMOBILISATIONS FINANCIÈRES (271-278)
    # 28 (amortissements -- accumulated depreciation) and 29 (depreciations
    # des immobilisations -- impairment): contra-asset accounts with no
    # dedicated Level-3 node -- needs_review (consistent gap; see README).

    # ───────── CLASSE 3 : COMPTES DE STOCKS ─────────
    "31": "asset.current.inventory",
    "313": "needs_review",              # ACTIFS BIOLOGIQUES (marchandises)
    "32": "asset.current.inventory",
    "33": "asset.current.inventory",
    "34": "asset.current.inventory",
    "345": "needs_review",              # ACTIFS BIOLOGIQUES EN COURS
    "35": "asset.current.inventory",    # SERVICES EN COURS (WIP services)
    "36": "asset.current.inventory",
    "363": "needs_review",              # ACTIFS BIOLOGIQUES
    "37": "asset.current.inventory",
    "373": "needs_review",              # ACTIFS BIOLOGIQUES
    "38": "asset.current.inventory",    # STOCKS EN COURS DE ROUTE...
    # 39 (dépréciations des stocks -- inventory allowance): contra-asset,
    # no node -- needs_review (same gap as 28/29).

    # ───────── CLASSE 4 : COMPTES DE TIERS ─────────
    "401": "liability.current.payables",
    "402": "liability.current.payables",
    "404": "liability.current.payables",
    "408": "liability.current.payables",
    "409": "asset.current.prepaid",         # FOURNISSEURS DÉBITEURS -- advances paid to suppliers, debit-side
    "41": "asset.current.receivables",      # CLIENTS ET COMPTES RATTACHÉS (411-418)
    "419": "liability.current.deferred_revenue",  # CLIENTS CRÉDITEURS -- advances received from customers
    "422": "liability.current.payroll",
    "423": "liability.current.payroll",     # oppositions/saisies-arrêts -- still a payroll-related withholding payable
    "424": "liability.current.payroll",
    "426": "liability.current.payroll",
    "428": "liability.current.accrued",     # PERSONNEL, CHARGES À PAYER ET PRODUITS À RECEVOIR
    # 421 (avances/acomptes au personnel, a receivable), 425 (représentants
    # du personnel) and 427 (personnel, dépôts) have no clean node --
    # needs_review.
    "43": "liability.current.payroll",       # ORGANISMES SOCIAUX (431-438)
    "441": "liability.current.tax",
    "442": "liability.current.tax",
    "443": "liability.current.vat_output",
    "444": "liability.current.vat_output",   # ÉTAT, T.V.A. DUE OU CRÉDIT DE T.V.A. (net VAT payable position)
    "445": "asset.current.vat_input",
    "446": "liability.current.tax",
    "447": "asset.current.withholding_tax",
    "448": "liability.current.accrued",
    # 449 (créances et dettes diverses -- État) too generic/bidirectional -- needs_review.
    # 45 (organismes internationaux): no matching node -- needs_review.
    "462": "asset.current.other_receivables",  # ASSOCIÉS, COMPTES COURANTS
    "465": "liability.current.payables",       # ASSOCIÉS, DIVIDENDES À PAYER
    "466": "asset.current.other_receivables",  # GROUPE, COMPTES COURANTS
    # 461, 463, 467 (capital calls / joint-operation settlements): no
    # matching node -- needs_review.
    "476": "asset.current.prepaid",            # CHARGES CONSTATÉES D'AVANCE
    "477": "liability.current.deferred_revenue",  # PRODUITS CONSTATÉS D'AVANCE
    # 471-475, 478, 479 (sundry debtors/creditors, FX translation
    # adjustments, the one-off SYSCOHADA-revision transition account): no
    # matching node -- needs_review.
    "481": "liability.current.payables",   # FOURNISSEURS D'INVESTISSEMENTS -- still a trade payable, just for capex
    "482": "liability.current.payables",
    "485": "asset.current.other_receivables",  # CRÉANCES SUR CESSIONS D'IMMOBILISATIONS
    # 484, 488 (autres dettes/créances H.A.O.): too generic -- needs_review.
    # 49 (dépréciations et provisions tiers): contra accounts, no node --
    # needs_review (same gap as 28/29/39/59).

    # ───────── CLASSE 5 : COMPTES DE TRESORERIE ─────────
    "50": "asset.noncurrent.investments",  # TITRES DE PLACEMENT -- no short-term-investment node exists yet (same workaround as localizations/ec)
    "51": "asset.current.cash",            # VALEURS À ENCAISSER -- items in the course of collection, treated as cash-equivalent
    "52": "asset.current.bank",
    "53": "asset.current.bank",            # ÉTABLISSEMENTS FINANCIERS ET ASSIMILÉS (Trésor, CCP, SGI -- bank-like)
    # 54 (instruments de trésorerie -- derivatives/precious metals): no node -- needs_review.
    "55": "asset.current.cash",            # INSTRUMENTS DE MONNAIE ELECTRONIQUE
    "56": "liability.current.short_term_debt",  # BANQUES, CRÉDITS DE TRÉSORERIE ET D'ESCOMPTE -- overdraft/short-term credit, a liability
    "57": "asset.current.cash",            # CAISSE
    "58": "asset.current.cash",            # RÉGIES D'AVANCES, VIREMENTS INTERNES
    # 59 (dépréciations et provisions court terme): contra, no node -- needs_review.

    # ───────── CLASSE 6 : COMPTES DE CHARGES DES ACTIVITES ORDINAIRES ─────────
    "60": "expense.cogs",
    "61": "expense.admin",       # TRANSPORTS
    "62": "expense.admin",       # SERVICES EXTÉRIEURS
    "63": "expense.admin",       # AUTRES SERVICES EXTÉRIEURS
    "64": "expense.tax",         # IMPÔTS ET TAXES (641, 645-648)
    "65": "expense.admin",       # AUTRES CHARGES
    "656": "expense.fx_loss",    # PERTE DE CHANGE SUR CRÉANCES ET DETTES COMMERCIALES
    "66": "expense.admin",       # CHARGES DE PERSONNEL -- no dedicated payroll-expense node exists (same gap as localizations/ec)
    "671": "expense.interest",
    "672": "expense.interest",   # INTÉRÊTS DANS LOYERS DE LOCATION ACQUISITION
    "673": "expense.interest",
    "674": "expense.interest",
    "675": "expense.interest",
    "676": "expense.fx_loss",    # PERTES DE CHANGE FINANCIÈRES
    # 677-679 (pertes sur titres de placement / risques financiers /
    # provisions financières): no matching node -- needs_review.
    "68": "expense.depreciation",  # DOTATIONS AUX AMORTISSEMENTS D'EXPLOITATION
    # 69 (dotations aux provisions et dépréciations): a provision/impairment
    # charge, distinct from depreciation -- no matching node -- needs_review
    # (consistent with the 28/29/39/49/59/79 provision-contra gap).

    # ───────── CLASSE 7 : COMPTES DE PRODUITS DES ACTIVITES ORDINAIRES ─────────
    "70": "revenue.operating",   # VENTES (701-707)
    "71": "revenue.other",       # SUBVENTIONS D'EXPLOITATION
    # 72 (production immobilisée) and 73 (variations de stocks de produits):
    # capitalization/inventory-change adjustments, distinct concepts with no
    # matching node -- needs_review.
    "75": "revenue.other",       # AUTRES PRODUITS
    "77": "revenue.other",       # REVENUS FINANCIERS -- no dedicated finance-income node exists (same gap as localizations/ec)
    # 78 (transferts de charges) and 79 (reprises de provisions/
    # dépréciations/subventions): contra-expense / provision-reversal
    # concepts, no matching node -- needs_review.

    # ───────── CLASSE 8 : COMPTES DES AUTRES CHARGES ET DES AUTRES PRODUITS ─────────
    # 81-88 (HAO -- hors activités ordinaires -- and profit-sharing /
    # equalization subsidies): extraordinary/non-recurring items and
    # employee-profit-sharing concepts with no matching Level-3 node --
    # needs_review across the board (a genuine, honestly-flagged gap; HAO
    # by definition sits outside the core 30-account universal model).
    "89": "expense.tax",         # IMPÔTS SUR LE RÉSULTAT (891, 892, 895, 899)
}

# 2-digit "soldes intermediaires de gestion" (computed performance
# subtotals) -- not postable accounts, same treatment as EC's cash-flow /
# equity-changes statement captions.
SIG_CAPTION_CODES = {"132", "133", "134", "135", "136", "137"}


def load_ontology_nodes():
    """Real, UUID-bearing Level-3 nodes only (see map_official_chart.py for
    the full rationale -- pending_accounts with no uuid are excluded)."""
    node_uuid = {}
    with open(ONTOLOGY_PATH, encoding="utf-8") as fh:
        for doc in yaml.safe_load_all(fh):
            items = None
            if isinstance(doc, list):
                items = doc
            elif isinstance(doc, dict) and "level3" in doc:
                items = doc["level3"]
            elif isinstance(doc, dict) and "extended_core" in doc:
                items = doc["extended_core"]
            for it in items or []:
                if isinstance(it, dict) and it.get("uuid"):
                    node_uuid[it["id"]] = it["uuid"]
    return node_uuid


def longest_prefix_match(code, rules):
    best = None
    for prefix, node_id in rules.items():
        if code.startswith(prefix) and (best is None or len(prefix) > len(best[0])):
            best = (prefix, node_id)
    return best[1] if best else None


def classify(entry, rules, parent_codes):
    code = entry["code"]
    # SYSCOHADA class 9 (engagements hors bilan + comptabilite analytique de
    # gestion) is "d'application facultative" per the source itself and is
    # not part of the mandatory double-entry financial-position/performance
    # ledger -- mirrors how parse/map_official_chart.py treats EC's own
    # class-9 codes.
    if entry["class"] == "9":
        return {"kontablo_node": None, "is_statement_caption": True, "is_aggregate": False, "needs_review": False}
    if code in SIG_CAPTION_CODES:
        return {"kontablo_node": None, "is_statement_caption": True, "is_aggregate": False, "needs_review": False}

    node_id = longest_prefix_match(code, rules)
    if node_id == "needs_review":
        # An explicit rule that documents "no fitting node" (vs. simply
        # absent from the table). Takes precedence over the aggregate/
        # parent-code check below, exactly like a real node match does --
        # otherwise a deliberately-flagged gap that happens to have 4-digit
        # children (e.g. "246 ACTIFS BIOLOGIQUES") would silently demote to
        # is_aggregate=true and the gap would stop being visible.
        return {"kontablo_node": None, "is_statement_caption": False, "is_aggregate": False, "needs_review": True}
    if node_id:
        return {"kontablo_node": node_id, "is_statement_caption": False, "is_aggregate": False, "needs_review": False}
    if code in parent_codes:
        # Header/rollup row (has more granular children in this same
        # chart) -- never independently postable, not a classification gap.
        return {"kontablo_node": None, "is_statement_caption": False, "is_aggregate": True, "needs_review": False}
    return {"kontablo_node": None, "is_statement_caption": False, "is_aggregate": False, "needs_review": True}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--official", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    node_uuid = load_ontology_nodes()
    ontology_ids = set(node_uuid)
    for node_id in set(SYSCOHADA_RULES.values()):
        if node_id != "needs_review" and node_id not in ontology_ids:
            raise ValueError(f"Rule references unknown ontology id: {node_id}")

    with open(args.official, encoding="utf-8") as fh:
        official = yaml.safe_load(fh)
    all_codes = [e["code"] for e in official["accounts"]]
    parent_codes = {
        a for a in all_codes
        if any(b != a and b.startswith(a) for b in all_codes)
    }

    mappings = {}
    stats = {"mapped": 0, "caption": 0, "aggregate": 0, "needs_review": 0}
    for entry in official["accounts"]:
        cls = classify(entry, SYSCOHADA_RULES, parent_codes)
        node_id = cls["kontablo_node"]
        row = {
            "name": entry["name"],
            "class": entry["class"],
            "kontablo_node": node_id,
            "kontablo_uuid": node_uuid.get(node_id),
            "is_statement_caption": cls["is_statement_caption"],
            "is_aggregate": cls["is_aggregate"],
            "needs_review": cls["needs_review"],
        }
        mappings[entry["code"]] = row
        if cls["is_statement_caption"]:
            stats["caption"] += 1
        elif cls["is_aggregate"]:
            stats["aggregate"] += 1
        elif node_id:
            stats["mapped"] += 1
        else:
            stats["needs_review"] += 1

    doc = {
        "metadata": {
            "jurisdiction": "_syscohada",
            "chart_family": "SYSCOHADA",
            "authority": official["metadata"]["authority"],
            "source_url": official["metadata"]["source_url"],
            "version": "0.1.0-full-chart",
            "total_official_codes": len(mappings),
            "classified_to_kontablo_node": stats["mapped"],
            "statement_captions_not_postable": stats["caption"],
            "aggregate_header_rows": stats["aggregate"],
            "needs_review_unclassified": stats["needs_review"],
            "note": (
                "Every code from the official SYSCOHADA chart is present here "
                "-- no hand-picked subset. Classification onto Kontablo's "
                "universal Level-3 ontology is many-to-one by design "
                "(principle: graph, not tree). is_aggregate=true means the "
                "code is a header/rollup row with more granular children in "
                "this same chart (never independently postable). "
                "is_statement_caption=true covers class-9 off-balance-sheet/"
                "management-accounting memoranda (optional per the source) "
                "and the class-1 'soldes intermediaires de gestion' computed "
                "subtotals (132-137). needs_review=true means no existing "
                "Level-3 node fits AND the code is a genuine leaf; the "
                "single largest honest gap is contra-asset/contra-liability "
                "accumulated-depreciation and provision accounts (classes "
                "18/19/28/29/39/49/59/69/79 and most of HAO class 8), for "
                "which the 34-node Level-3 core has no dedicated node yet -- "
                "see research/coa_fidelity/STATUS.yaml."
            ),
            "generator": "scripts/coa_fidelity/map_syscohada_chart.py",
        },
        "mappings": mappings,
    }
    with open(args.out, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=100)

    print(f"Total codes: {len(mappings)}")
    print(f"Mapped to a Level-3 node: {stats['mapped']}")
    print(f"Statement captions (not postable): {stats['caption']}")
    print(f"Aggregate/header rows (not postable): {stats['aggregate']}")
    print(f"Needs review (no fitting node): {stats['needs_review']}")
    print(f"Written: {args.out}")


if __name__ == "__main__":
    main()
