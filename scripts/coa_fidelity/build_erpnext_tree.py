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

# Per-jurisdiction reparenting for official numbering schemes that do not
# give Equity and Income/Expense their own top-level root digit the way
# EC/MX's charts happen to -- verified against the actual source, not
# assumed (see localizations/<cc>/README.md's "ERPNext tree" section).
# Each (official_code, synthetic_root_label, root_type) entry detaches that
# code's subtree from its normal numeric parent and reparents it directly
# under a new synthetic top-level root with the given ERPNext root_type;
# multiple entries sharing the same label become siblings under one shared
# synthetic root.
#
# Brazil's Plano de Contas Referencial (RFB SPED) nests Patrimônio Líquido
# (Equity) under the same root "2" as Passivo (Liability) at 2.03, and
# bundles ALL P&L accounts (Receitas AND Despesas/Custos, for both the
# Atividade Geral and the parallel Atividade Rural sections) under a single
# root "3" ("Resultado") -- both verified against the parsed chart, neither
# assumed from EC/MX's convention (where root digits map 1:1 to Asset/
# Liability/Equity/Income/Expense). Without this, build_tree()'s plain
# leading-digit ROOT_TYPE_BY_DIGIT lookup would misrepresent Patrimônio
# Líquido as a Liability subgroup and dump every Receita/Despesa leaf under
# one undifferentiated "Equity" root (root "3"'s generic fallback).
JURISDICTION_REPARENT = {
    "br": [
        ("2.01", "Passivo", "Liability"),               # Passivo Circulante
        ("2.02", "Passivo", "Liability"),                # Passivo Não Circulante
        ("2.03", "Patrimônio Líquido", "Equity"),        # nests under root "2" in BR's own numbering
        ("3.01.01.01.01", "Receitas", "Income"),         # Receita Bruta (Atividade Geral)
        ("3.01.01.05", "Receitas", "Income"),             # Outras Receitas Operacionais (Atividade Geral)
        ("3.11.01.01.01", "Receitas", "Income"),          # Receita Bruta (Atividade Rural)
        ("3.11.01.05", "Receitas", "Income"),             # Outras Receitas Operacionais (Atividade Rural)
        ("3.01.01.01.02", "Despesas e Custos", "Expense"),  # Deduções da Receita Bruta
        ("3.01.01.03", "Despesas e Custos", "Expense"),      # Custo dos Bens e Serviços Vendidos
        ("3.01.01.07", "Despesas e Custos", "Expense"),      # Despesas Operacionais
        ("3.01.01.09", "Despesas e Custos", "Expense"),      # Outras Despesas Operacionais
        ("3.01.01.11", "Despesas e Custos", "Expense"),      # Outras Receitas/Despesas + Descontinuadas
        ("3.01.05", "Despesas e Custos", "Expense"),         # Participações
        ("3.02", "Despesas e Custos", "Expense"),            # Provisão para CSLL e IRPJ
        ("3.11.01.01.02", "Despesas e Custos", "Expense"),   # Deduções (Atividade Rural)
        ("3.11.01.03", "Despesas e Custos", "Expense"),      # Custo (Atividade Rural)
        ("3.11.01.07", "Despesas e Custos", "Expense"),      # Despesas Operacionais (Atividade Rural)
        ("3.11.01.09", "Despesas e Custos", "Expense"),      # Outras Despesas (Atividade Rural)
        ("3.11.01.11", "Despesas e Custos", "Expense"),      # Outras Receitas/Despesas Descontinuadas (Rural)
        ("3.11.05", "Despesas e Custos", "Expense"),         # Participações (Atividade Rural)
        ("3.12", "Despesas e Custos", "Expense"),            # Provisão CSLL (Atividade Rural)
    ],
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

    # Jurisdiction-specific reparenting: sever the listed codes from their
    # normal numeric parent so they surface as their own synthetic top-level
    # roots instead (see JURISDICTION_REPARENT's header comment for why).
    reparent_root_type = {}
    reparent_label_of = {}
    for code, label, root_type in JURISDICTION_REPARENT.get(jurisdiction, []):
        if code in parent_of:
            parent_of[code] = None
            reparent_root_type[code] = root_type
            reparent_label_of[code] = label

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

    def prune_empty_groups(d):
        # A header/aggregate node that lost all its children to reparenting
        # (e.g. BR's "2" PASSIVO once 2.01/2.02/2.03 are promoted to their
        # own synthetic roots, or "3"/"3.01"/"3.01.01" once every Receita/
        # Despesa leaf below them is promoted) becomes a childless is_group
        # node -- not useful in an ERPNext import. Drop these recursively,
        # bottom-up, from any level of the tree. No-op for jurisdictions
        # that don't reparent (EC/MX): nothing here has zero children unless
        # the source chart itself does.
        for key in list(d.keys()):
            v = d[key]
            if not isinstance(v, dict):
                continue
            prune_empty_groups(v)  # recurse bottom-up into v's own children first
            if v.get("is_group") and not any(
                isinstance(vv, dict) for k, vv in v.items() if k not in ("is_group", "root_type")
            ):
                del d[key]

    roots = [c for c in codes if parent_of[c] is None]
    # Group reparented roots by their synthetic label -- multiple official
    # codes (e.g. BR's 3.01.01.03 Custo + 3.01.01.07 Despesas Operacionais)
    # sharing one label become siblings under one shared synthetic root,
    # rather than each minting its own top-level tree key.
    synthetic_roots = {}
    plain_roots = []
    for r in roots:
        if r in reparent_label_of:
            synthetic_roots.setdefault(reparent_label_of[r], []).append(r)
        else:
            plain_roots.append(r)

    tree = {"Company Name": company_placeholder, "country_code": jurisdiction}
    for r in sorted(plain_roots):
        entry = postable[r]
        node = node_dict(r)
        node["root_type"] = ROOT_TYPE_BY_DIGIT.get(r[0], "Asset")
        key = unique_key(tree, entry["name"].title(), r)
        tree[key] = node
    for label, member_codes in synthetic_roots.items():
        node = {"is_group": 1, "root_type": reparent_root_type[member_codes[0]]}
        for r in sorted(member_codes):
            entry = postable[r]
            key = unique_key(node, entry["name"].title(), r)
            node[key] = node_dict(r)
        tree[label] = node

    prune_empty_groups(tree)
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
