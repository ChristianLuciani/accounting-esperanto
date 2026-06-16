"""The Deterministic Boundary Library of the Kontablo harness.

``cra_validate()`` is the Co-responsibility Architecture's set of deterministic
accounting invariants (nature, liquidity, statement-class, VAT direction,
equity-vs-liability). Each check is a deterministic rule — never a model
inference — so a flagged mapping can be held for human review reproducibly.
The heuristic name-vs-target checks (3-5) apply only to *forced* (proposed)
mappings, so a correct name-derived resolution is never false-flagged.
"""

from __future__ import annotations


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
