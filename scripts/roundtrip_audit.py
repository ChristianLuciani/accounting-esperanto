#!/usr/bin/env python3
"""
Kontablo round-trip audit — the lossless-translation gate (ADR-016).

Proves, on the SAME synthetic dataset as the published v2 validation run
(``scripts/mass_consolidation_v2.py``), that the translation local -> universal
is lossless at the entry level:

  1. CONSERVATION — every input trial-balance row appears in the engine's
     resolved output exactly once (nothing dropped, silently or otherwise).
  2. RECONSTRUCTION — the original local trial balances are reconstructible
     byte-for-byte (code, name, side, local amount) from the lineage alone.
  3. FIBER CONSISTENCY — every consolidated line equals the sum of its fiber
     (the resolved entries that aggregated into it).
  4. LOSS LEDGER — everything the pipeline cannot translate is a TYPED record
     (ontology collisions, non-code placeholders, escalated entries, CRA
     flags), never a silent drop. ``silent_losses`` MUST be 0.

Deterministic: no LLM, no network (pinned FX only — rate overrides are passed
explicitly as manual quotes). The committed artifact regenerates byte-for-byte;
provenance timestamps are deliberately excluded from it.

Run:  venv/bin/python scripts/roundtrip_audit.py
Output (committed for reproducibility):
  research/experiments/roundtrip_audit/results.json
"""

import importlib.util
import json
import os
import sys
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from core.engine import ConsolidationEngine, LocalEntry, SubsidiaryTB  # noqa: E402
from core.harness import FX  # noqa: E402

OUT_DIR = os.path.join(ROOT, "research/experiments/roundtrip_audit")


def _load_runner():
    """Import the v2 validation runner by path so the audit uses the exact
    same synthetic dataset generation (no duplicated data definitions)."""
    path = os.path.join(ROOT, "scripts", "mass_consolidation_v2.py")
    spec = importlib.util.spec_from_file_location("mass_consolidation_v2", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _entities_to_tbs(entities):
    """Convert the runner's entity dicts into engine SubsidiaryTB inputs.

    Every row becomes a LocalEntry (amount on its natural side). Rows the
    runner treats specially (equity plugs, forced_id CRA injections) are kept
    as ordinary rows here: the audit's question is conservation and
    reconstruction, not coverage statistics.
    """
    tbs = []
    for ent in entities:
        entries = [
            LocalEntry(
                code=str(e["code"]),
                name=e["name"],
                debit=e["amt"] if e["nature"] == "debit" else 0.0,
                credit=e["amt"] if e["nature"] == "credit" else 0.0,
                nature=e["nature"],
            )
            for e in ent["data"]
        ]
        override = ent.get("rate_override")
        tbs.append(
            SubsidiaryTB(
                subsidiary_id=ent["id"],
                jurisdiction=ent["j"],
                currency=ent["ccy"],
                entries=entries,
                # Pass the runner's rate explicitly when it overrides the pinned
                # table (IAS 29 parallel rates, currencies outside the table).
                fx_rate_to_usd=override
                if override is not None or ent["ccy"] in FX
                else None,
                fx_rate_as_of="synthetic" if override is not None else None,
                fx_rate_note="runner rate_override (parallel/IAS29)"
                if override is not None
                else None,
            )
        )
    return tbs


def run_audit():
    runner = _load_runner()
    engine = ConsolidationEngine()
    entities = runner.add_equity_plug(
        runner.build_entities(engine.accounts, engine.by_code, runner.load_families()),
        engine.accounts,
    )
    tbs = _entities_to_tbs(entities)
    result = engine.consolidate(tbs)

    # ---- 1. CONSERVATION: input rows == resolved rows, per subsidiary ------
    def row_key(sub, code, name, debit, credit):
        return (sub, str(code), name, round(debit, 2), round(credit, 2))

    inputs = Counter()
    for ent, tb in zip(entities, tbs):
        for e in tb.entries:
            inputs[row_key(tb.subsidiary_id, e.code, e.name, e.debit, e.credit)] += 1
    outputs = Counter()
    for r in result.resolved:
        outputs[row_key(r.subsidiary_id, r.local_code, r.local_name,
                        r.debit_local, r.credit_local)] += 1
    missing = inputs - outputs   # rows lost by the translation
    phantom = outputs - inputs   # rows invented by the translation

    # ---- 2. RECONSTRUCTION: rebuild each local TB from lineage alone -------
    rebuilt = defaultdict(list)
    for r in result.resolved:
        rebuilt[r.subsidiary_id].append(
            (r.local_code, r.local_name, r.debit_local, r.credit_local)
        )
    reconstruction_exact = True
    for tb in tbs:
        original = sorted(
            (e.code, e.name, e.debit, e.credit) for e in tb.entries
        )
        recovered = sorted(rebuilt.get(tb.subsidiary_id, []))
        if original != recovered:
            reconstruction_exact = False

    # ---- 3. FIBER CONSISTENCY: every line == sum of its fiber --------------
    fibers = result.lineage()
    fiber_mismatches = []
    for line in result.lines:
        fiber = fibers.get(line.kontablo_id, [])
        if (
            line.source_count != len(fiber)
            or round(sum(r.debit_usd for r in fiber), 2) != line.debit_usd
            or round(sum(r.credit_usd for r in fiber), 2) != line.credit_usd
        ):
            fiber_mismatches.append(line.kontablo_id)

    # ---- 4. LOSS LEDGER: every non-translation is a typed record -----------
    provenance_complete = all(
        r.mapping is not None and r.fx is not None for r in result.resolved
    )
    loss_ledger = {
        "ontology_code_collisions": len(engine.collisions),
        "non_code_placeholders": len(engine.placeholders),
        "escalated_entries": len(result.escalations),
        "cra_flags": len(result.cra_flags),
    }

    silent_losses = (
        sum(missing.values()) + sum(phantom.values()) + len(fiber_mismatches)
        + (0 if reconstruction_exact else 1)
        + (0 if provenance_complete else 1)
    )

    summary = {
        "dataset": "identical to scripts/mass_consolidation_v2.py (imported, not duplicated)",
        "entities": len(tbs),
        "jurisdictions": len({tb.jurisdiction for tb in tbs}),
        "entries_in": sum(inputs.values()),
        "entries_resolved_out": sum(outputs.values()),
        "conservation": {
            "missing_rows": sum(missing.values()),
            "phantom_rows": sum(phantom.values()),
        },
        "reconstruction_exact": reconstruction_exact,
        "fiber_mismatches": fiber_mismatches,
        "provenance_complete": provenance_complete,
        "loss_ledger": loss_ledger,
        "silent_losses": silent_losses,
        "note": (
            "silent_losses counts information discarded WITHOUT a typed record. "
            "Escalations/collisions/placeholders/CRA flags are NOT silent losses: "
            "they are the loss ledger — explicit, typed, and countable."
        ),
    }
    return summary


def main():
    summary = run_audit()
    os.makedirs(OUT_DIR, exist_ok=True)
    out_path = os.path.join(OUT_DIR, "results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False, sort_keys=True)
        f.write("\n")

    print("Kontablo round-trip audit (ADR-016)")
    print("-" * 46)
    for k in ("entities", "jurisdictions", "entries_in", "entries_resolved_out"):
        print(f"  {k:24} {summary[k]}")
    print(f"  reconstruction_exact     {summary['reconstruction_exact']}")
    print(f"  provenance_complete      {summary['provenance_complete']}")
    print(f"  loss_ledger              {summary['loss_ledger']}")
    print(f"  SILENT LOSSES            {summary['silent_losses']}")
    print(f"Artifact: {os.path.relpath(out_path, ROOT)}")

    if summary["silent_losses"] != 0 or not summary["reconstruction_exact"]:
        print("FAIL: translation lost information without a typed record.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
