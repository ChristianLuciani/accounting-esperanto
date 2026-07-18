#!/usr/bin/env python3
"""
Build an ERPNext 'verified' chart-of-accounts JSON tree from the SYSCOHADA
Kontablo mapping (localizations/_syscohada/syscohada_mapping.yaml, produced
by map_syscohada_chart.py). Same purpose as build_erpnext_tree.py, but
SYSCOHADA's class digits (1-9) mix asset/liability/equity within the same
class (e.g. class 4 "comptes de tiers" holds both receivables AND payables),
unlike Ecuador's presentation-chart where each root digit was a clean
Asset/Liability/Equity/Income/Expense bucket. So root_type here is derived
from the Kontablo node id prefix an account actually classified onto
("asset."/"liability."/"equity."/"revenue."/"expense." -> ERPNext root type)
-- authoritative and per-account, not a per-class-digit guess. Aggregate/
header rows with no direct node inherit their root_type from the majority
vote of their own postable descendants.

Only postable accounts are emitted (is_statement_caption=false entries --
this excludes all of SYSCOHADA's optional class 9 and the class-1 "soldes
intermediaires de gestion" computed subtotals). Parent/child structure is
derived deterministically from code containment, exactly as in
build_erpnext_tree.py.

Usage:
    python3 scripts/coa_fidelity/build_syscohada_erpnext_tree.py \
        --mapping localizations/_syscohada/syscohada_mapping.yaml \
        --out localizations/_syscohada/default_tree_syscohada.json
"""
import argparse
import json
from collections import Counter

import yaml

NODE_PREFIX_ROOT_TYPE = {
    "asset": "Asset",
    "liability": "Liability",
    "equity": "Equity",
    "revenue": "Income",
    "expense": "Expense",
}

ACCOUNT_TYPE_BY_NODE = {
    "asset.current.cash": "Cash",
    "asset.current.bank": "Bank",
    "asset.current.receivables": "Receivable",
    "asset.current.other_receivables": "Receivable",
    "asset.current.withholding_tax": "Tax",
    "asset.current.vat_input": "Tax",
    "asset.current.inventory": "Stock",
    "asset.current.prepaid": "Prepaid Expense",
    "asset.noncurrent.ppe": "Fixed Asset",
    "asset.noncurrent.intangibles": "Fixed Asset",
    "asset.noncurrent.investments": "Investment Account",
    "liability.current.payables": "Payable",
    "liability.current.tax": "Tax",
    "liability.current.vat_output": "Tax",
    "liability.current.payroll": "Payable",
    "liability.current.accrued": "Payable",
    "liability.current.deferred_revenue": "Payable",
    "liability.current.short_term_debt": "Payable",
    "liability.noncurrent.debt": "Payable",
    "liability.noncurrent.lease": "Payable",
    "liability.noncurrent.deferred_tax": "Payable",
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
    "expense.fx_loss": "Expense Account",
}


def node_root_type(node_id):
    if not node_id:
        return None
    prefix = node_id.split(".", 1)[0]
    return NODE_PREFIX_ROOT_TYPE.get(prefix)


def build_tree(mapping, company_placeholder):
    postable = {c: v for c, v in mapping.items() if not v["is_statement_caption"]}
    codes = sorted(postable, key=len)

    def find_parent(code):
        candidates = [c for c in codes if c != code and code.startswith(c)]
        return max(candidates, key=len) if candidates else None

    parent_of = {c: find_parent(c) for c in codes}
    children = {}
    for c, p in parent_of.items():
        children.setdefault(p, []).append(c)

    def descendant_root_types(code):
        """All direct-node root types among a code's own postable descendants
        (used to color in a root_type for aggregate/needs_review groups that
        have no node of their own)."""
        found = []
        rt = node_root_type(postable[code]["kontablo_node"])
        if rt:
            found.append(rt)
        for kid in children.get(code, []):
            found.extend(descendant_root_types(kid))
        return found

    def resolve_root_type(code):
        rt = node_root_type(postable[code]["kontablo_node"])
        if rt:
            return rt
        votes = descendant_root_types(code)
        if votes:
            return Counter(votes).most_common(1)[0][0]
        # No node anywhere in this subtree (a pure needs_review leaf with no
        # mapped descendants) -- fall back to the class digit's dominant
        # side per the source's own class semantics, so the tree still
        # imports; the account itself remains flagged needs_review in the
        # mapping file, which is the source of truth for the coverage gap.
        cls = postable[code]["class"]
        return {"1": "Liability", "2": "Asset", "3": "Asset", "4": "Asset",
                "5": "Asset", "6": "Expense", "7": "Income",
                "8": "Expense"}.get(cls, "Asset")

    def unique_key(container, name, code):
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
    tree = {"Company Name": company_placeholder, "country_code": "syscohada"}
    for r in sorted(roots):
        entry = postable[r]
        node = node_dict(r)
        node["root_type"] = resolve_root_type(r)
        key = unique_key(tree, entry["name"].title(), r)
        tree[key] = node
    return tree


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mapping", required=True)
    ap.add_argument("--company-placeholder", default="Company Name")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    with open(args.mapping, encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    tree = build_tree(doc["mappings"], args.company_placeholder)

    def count_leaves(d):
        n = 0
        for k, v in d.items():
            if isinstance(v, dict):
                if v.get("is_group"):
                    n += count_leaves(v)
                elif "account_number" in v:
                    n += 1
        return n

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(tree, f, ensure_ascii=False, indent=1)
        f.write("\n")

    print(f"Written: {args.out}")
    print(f"Postable leaf accounts in tree: {sum(count_leaves(v) for k, v in tree.items() if isinstance(v, dict))}")


if __name__ == "__main__":
    main()
