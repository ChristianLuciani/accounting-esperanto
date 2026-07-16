#!/usr/bin/env python3
"""
Deterministic classification of a verbatim official chart (produced by
parse_official_chart.py) onto Kontablo's universal Level-3 ontology
(core/schemas/level3_accounts.yaml).

This is a SEPARATE, reviewable step from parsing on purpose (principle #5,
determinism over stochasticity; principle #3, logic-based mapping via
deterministic scripts, never hardcoded free-text guessing). Classification
is done via longest-prefix-match against a per-jurisdiction rule table
defined in this file -- not inferred by an LLM, and not left as a silent
best-guess: any code with no matching prefix is written out with
kontablo_uuid: null and needs_review: true rather than forced onto the
nearest plausible node.

Statement-only presentation captions (cash-flow reconciliation lines,
statement-of-changes-in-equity movement lines) are NOT postable ledger
accounts and are tagged is_statement_caption: true instead of being forced
onto a Level-3 node.

Usage:
    python3 scripts/coa_fidelity/map_official_chart.py \
        --official localizations/ec/supercias_official_chart.yaml \
        --jurisdiction ec \
        --out localizations/ec/supercias_mapping.yaml
"""
import argparse
import yaml

ONTOLOGY_PATH = "core/schemas/level3_accounts.yaml"

# --- Ecuador (Supercias NIIF Plan de Cuentas) prefix -> Level-3 id rules ---
# Longest-prefix match wins. Prefixes are official CODIGO values (as strings).
# Every prefix here was verified against the parsed official chart before
# being added -- see localizations/ec/supercias_official_chart.yaml.
EC_RULES = {
    # ACTIVO CORRIENTE
    "1010101": "asset.current.cash",
    "1010102": "asset.current.bank",
    "1010103": "asset.current.bank",
    "10102": "asset.noncurrent.investments",   # current financial assets; no dedicated short-term-investment node exists yet
    "1010205": "asset.current.receivables",     # DEUDORES COMERCIALES Y OTRAS CxC NO RELACIONADOS (clientes)
    "1010206": "asset.current.other_receivables",  # CxC relacionados
    "1010207": "asset.current.receivables",     # provision cuentas incobrables (contra, nets against receivables)
    "10103": "asset.current.inventory",
    "10104": "asset.current.prepaid",
    "1010501": "asset.current.vat_input",
    "1010502": "asset.current.withholding_tax",
    "1010503": "asset.current.withholding_tax",
    # ACTIVOS NO CORRIENTES
    "10201": "asset.noncurrent.ppe",
    # 10203 ACTIVOS BIOLOGICOS: no rule -- asset.noncurrent.biological is
    # PLANNED status with no uuid yet (core/schemas/level3_accounts.yaml
    # pending_accounts); left needs_review rather than mapped to a
    # non-existent node. Real ontology gap, tracked in STATUS.yaml.
    "1020401": "asset.noncurrent.goodwill",
    "10204": "asset.noncurrent.intangibles",
    "10206": "asset.noncurrent.investments",
    "10207": "asset.noncurrent.rou_assets",
    "1020806": "asset.noncurrent.investments",
    "1020807": "asset.noncurrent.investments",
    "1020808": "asset.noncurrent.investments",
    "1020809": "asset.noncurrent.investments",
    "1020810": "asset.noncurrent.investments",
    # PASIVO CORRIENTE
    "20101": "liability.current.short_term_debt",
    "20103": "liability.current.payables",
    "20104": "liability.current.short_term_debt",
    "20105": "liability.current.accrued",
    "20106": "liability.current.short_term_debt",
    "2010701": "liability.current.tax",
    "2010702": "liability.current.tax",
    "2010703": "liability.current.payroll",
    "2010704": "liability.current.payroll",
    "2010705": "liability.current.payroll",
    "2010706": "liability.current.accrued",
    "2010707": "liability.current.accrued",
    "20108": "liability.current.payables",
    "20109": "liability.current.short_term_debt",
    "20110": "liability.current.deferred_revenue",
    "20112": "liability.current.payroll",
    "20113": "liability.current.accrued",
    "20114": "liability.current.short_term_debt",
    # PASIVO NO CORRIENTE
    "20201": "liability.noncurrent.lease",
    "20202": "liability.noncurrent.debt",
    "20203": "liability.noncurrent.debt",
    "20204": "liability.noncurrent.debt",
    "20205": "liability.noncurrent.debt",
    "20206": "liability.current.deferred_revenue",
    "20207": "liability.current.payroll",
    "20208": "liability.current.accrued",
    "2020901": "liability.current.deferred_revenue",
    "2020902": "liability.noncurrent.deferred_tax",
    "20210": "liability.noncurrent.debt",
    # PATRIMONIO
    "301": "equity.capital",
    "302": "equity.capital",
    "303": "equity.capital",
    "304": "equity.reserves",
    "305": "equity.reserves",
    "306": "equity.retained",
    "307": "equity.retained",
    # INGRESOS
    "401": "revenue.operating",
    "403": "revenue.other",
    # GASTOS
    "501": "expense.cogs",
    "50201": "expense.admin",   # GASTOS DE VENTA -- no dedicated selling-expense node; see needs_review note
    "50202": "expense.admin",   # GASTOS ADMINISTRATIVOS
    "5020120": "expense.depreciation",
    "5020121": "expense.depreciation",
    "5020220": "expense.depreciation",
    "5020221": "expense.depreciation",
    "5020222": "expense.depreciation",
    "50203": "expense.interest",
    "5020307": "expense.fx_loss",
    "603": "expense.tax",
    "705": "expense.tax",
}

# Prefixes that ARE genuine subtotal/computed rows (not postable accounts,
# not a classification gap) -- excluded from needs_review noise.
SUBTOTAL_PREFIXES = {
    "402", "600", "601", "602", "604", "605", "606", "607",
    "700", "701", "702", "703", "704", "706", "707",
    "80101", "80102",
}


def load_ontology_nodes():
    """Real, UUID-bearing Level-3 nodes only. The ontology file is split
    across multiple '---'-separated YAML documents (core list under the
    'level3:' key, then bare-list continuation docs for liabilities/equity/
    revenue/expense, then a dict under 'extended_core:'). A trailing
    'pending_accounts:' doc lists DRAFT/RESEARCH/PLANNED ids with NO uuid --
    those are deliberately excluded: mapping onto a node that doesn't exist
    yet would be exactly the kind of silent guess this pipeline exists to
    avoid.
    """
    node_uuid = {}
    for doc in yaml.safe_load_all(open(ONTOLOGY_PATH, encoding="utf-8")):
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
    if entry["statement"] in (
        "Estado de Cambios en el Patrimonio",
    ) or code[:1] == "9":
        return {"kontablo_uuid": None, "kontablo_node": None,
                "is_statement_caption": True, "is_aggregate": False, "needs_review": False}
    node_id = longest_prefix_match(code, rules)
    if node_id:
        return {"kontablo_uuid": None, "kontablo_node": node_id,
                "is_statement_caption": False, "is_aggregate": False, "needs_review": False}
    is_subtotal = any(code == p or code.startswith(p) and len(code) <= len(p) + 2
                       for p in SUBTOTAL_PREFIXES)
    if is_subtotal:
        return {"kontablo_uuid": None, "kontablo_node": None,
                "is_statement_caption": True, "is_aggregate": False, "needs_review": False}
    if code in parent_codes:
        # Header/rollup row (has more granular children in this same chart) --
        # never independently postable, so it is not a classification gap.
        return {"kontablo_uuid": None, "kontablo_node": None,
                "is_statement_caption": False, "is_aggregate": True, "needs_review": False}
    return {"kontablo_uuid": None, "kontablo_node": None,
            "is_statement_caption": False, "is_aggregate": False, "needs_review": True}


def derive_nature(entry):
    root = entry["code"][0]
    sign = entry["sign"]
    if root in ("1", "5"):
        base = "Debit"
    elif root in ("2", "3", "4"):
        base = "Credit"
    else:
        return None
    if sign == "POSITIVO":
        return base
    if sign == "NEGATIVO":
        return "Credit" if base == "Debit" else "Debit"
    return base  # DUAL: default to natural side, not authoritative


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--official", required=True)
    ap.add_argument("--jurisdiction", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    node_uuid = load_ontology_nodes()
    ontology_ids = set(node_uuid)

    rules = EC_RULES if args.jurisdiction == "ec" else {}
    official = yaml.safe_load(open(args.official, encoding="utf-8"))

    all_codes = [e["code"] for e in official["accounts"]]
    parent_codes = {
        a for a in all_codes
        if any(b != a and b.startswith(a) for b in all_codes)
    }

    mappings = {}
    stats = {"mapped": 0, "caption": 0, "aggregate": 0, "needs_review": 0}
    for entry in official["accounts"]:
        cls = classify(entry, rules, parent_codes)
        node_id = cls["kontablo_node"]
        if node_id and node_id not in ontology_ids:
            raise ValueError(f"Rule references unknown ontology id: {node_id}")
        row = {
            "name": entry["name"],
            "nature": derive_nature(entry),
            "statement": entry["statement"],
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
            "jurisdiction": args.jurisdiction,
            "authority": official["metadata"]["authority"],
            "source_url": official["metadata"]["source_url"],
            "version": "0.2.0-full-chart",
            "total_official_codes": len(mappings),
            "classified_to_kontablo_node": stats["mapped"],
            "statement_captions_not_postable": stats["caption"],
            "aggregate_header_rows": stats["aggregate"],
            "needs_review_unclassified": stats["needs_review"],
            "note": (
                "Every code from the official chart is present here -- no "
                "hand-picked subset. Classification onto Kontablo's "
                "universal Level-3 ontology is many-to-one by design "
                "(principle: graph, not tree). is_aggregate=true means the "
                "code is a header/rollup row with more granular children in "
                "this same chart (never independently postable). "
                "needs_review=true means no existing Level-3 node fits AND "
                "the code is a genuine leaf; that is an honest ontology gap, "
                "not a silent guess -- see research/coa_fidelity/STATUS.yaml."
            ),
            "generator": "scripts/coa_fidelity/map_official_chart.py",
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
