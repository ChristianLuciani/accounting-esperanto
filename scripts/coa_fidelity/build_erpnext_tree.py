#!/usr/bin/env python3
"""
Build an ERPNext 'verified' chart-of-accounts JSON tree from a Kontablo
localization mapping (localizations/<cc>/<x>_mapping.yaml, produced by
map_official_chart.py). This is the Kontablo -> ERPNext direction requested
alongside the official-source -> Kontablo direction (parse/map scripts).

Only postable accounts are emitted (is_statement_caption=false entries from
the mapping). Parent/child structure is derived deterministically from code
containment (each account's parent is the longest other code in the set that
is a proper prefix of it) -- not hardcoded, not guessed.

Usage:
    python3 scripts/coa_fidelity/build_erpnext_tree.py \
        --mapping localizations/ec/supercias_mapping.yaml \
        --jurisdiction ec \
        --company-placeholder "Company Name" \
        --out localizations/ec/default_tree_ec.json
"""
import argparse
import json
import yaml

ROOT_TYPE_BY_DIGIT = {
    "1": "Asset",
    "2": "Liability",
    "3": "Equity",
    "4": "Income",
    "5": "Expense",
    "6": "Expense",  # 603: continuing-operations income tax expense (subtotal siblings excluded as captions)
    "7": "Expense",  # 705: discontinued-operations income tax expense (same reasoning)
    "8": "Equity",  # Other Comprehensive Income rolls up into equity reserves
}

# ERPNext account_type heuristic from the Kontablo node the code was classified to.
ACCOUNT_TYPE_BY_NODE = {
    "asset.current.cash": "Cash",
    "asset.current.bank": "Bank",
    "asset.current.receivables": "Receivable",
    "asset.current.vat_input": "Tax",
    "asset.current.inventory": "Stock",
    "asset.noncurrent.ppe": "Fixed Asset",
    "asset.noncurrent.intangibles": "Fixed Asset",
    "asset.noncurrent.goodwill": "Fixed Asset",
    "liability.current.payables": "Payable",
    "liability.current.tax": "Tax",
    "liability.current.short_term_debt": "Payable",
    "liability.noncurrent.debt": "Payable",
    "equity.capital": "Equity",
    "equity.retained": "Equity",
    "equity.reserves": "Equity",
    "revenue.operating": "Income Account",
    "revenue.other": "Income Account",
    "expense.cogs": "Cost of Goods Sold",
    "expense.admin": "Expense Account",
    "expense.depreciation": "Depreciation",
    "expense.interest": "Expense Account",
    "expense.tax": "Tax",
}


def build_tree(mapping, jurisdiction, company_placeholder):
    postable = {c: v for c, v in mapping.items() if not v["is_statement_caption"]}
    codes = sorted(postable, key=len)

    def find_parent(code):
        candidates = [c for c in codes if c != code and code.startswith(c)]
        return max(candidates, key=len) if candidates else None

    parent_of = {c: find_parent(c) for c in codes}
    children = {}
    for c, p in parent_of.items():
        children.setdefault(p, []).append(c)

    def unique_key(container, name, code):
        # Sibling names collide occasionally (e.g. codes 603 and 705 are both
        # "IMPUESTO A LA RENTA CAUSADO" -- continuing vs discontinued ops).
        # Disambiguate with the official code rather than silently clobbering
        # one entry, which a naive dict-key assignment would do.
        if name not in container:
            return name
        return f"{name} ({code})"

    def node_dict(code):
        entry = postable[code]
        kids = sorted(children.get(code, []))
        d = {}
        if entry["is_aggregate"] or kids:
            d["is_group"] = 1
        else:
            d["account_number"] = code
            node_id = entry["kontablo_node"]
            if node_id in ACCOUNT_TYPE_BY_NODE:
                d["account_type"] = ACCOUNT_TYPE_BY_NODE[node_id]
        for kid in kids:
            key = unique_key(d, postable[kid]["name"].title(), kid)
            d[key] = node_dict(kid)
        return d

    roots = [c for c in codes if parent_of[c] is None]
    tree = {"Company Name": company_placeholder, "country_code": jurisdiction}
    for r in sorted(roots):
        entry = postable[r]
        node = node_dict(r)
        node["root_type"] = ROOT_TYPE_BY_DIGIT.get(r[0], "Asset")
        key = unique_key(tree, entry["name"].title(), r)
        tree[key] = node
    return tree


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapping", required=True)
    ap.add_argument("--jurisdiction", required=True)
    ap.add_argument("--company-placeholder", default="Company Name")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    doc = yaml.safe_load(open(args.mapping, encoding="utf-8"))
    tree = build_tree(doc["mappings"], args.jurisdiction, args.company_placeholder)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=1)
        f.write("\n")

    def count_leaves(d):
        n = 0
        for k, v in d.items():
            if isinstance(v, dict):
                if v.get("is_group"):
                    n += count_leaves(v)
                elif "account_number" in v:
                    n += 1
        return n

    print(f"Written: {args.out}")
    print(f"Postable leaf accounts in tree: {sum(count_leaves(v) for k, v in tree.items() if isinstance(v, dict))}")


if __name__ == "__main__":
    main()
