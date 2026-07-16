#!/usr/bin/env python3
"""
Build/refresh research/coa_fidelity/STATUS.yaml -- the master, resumable,
per-jurisdiction chart-of-accounts fidelity tracker for all 195 jurisdictions.

Why this exists: the localizations/<cc>/ files were found to be curated
subsets (e.g. Ecuador had 13 hand-picked accounts against an official chart
of 721) rather than exhaustive transcriptions of each country's official
chart. Fixing this for every statutory-chart jurisdiction is a multi-session
effort that must survive context/quota limits -- this file is the checklist
that makes that possible: it is read and rewritten by every future session
that picks up the next jurisdiction, never re-derived from memory.

Reuses STATES / CHART_FAMILY from scripts/build_jurisdiction_manifest.py so
the 195-jurisdiction list has exactly one source of truth.

Usage:
    python3 scripts/coa_fidelity/build_status_tracker.py \
        --out research/coa_fidelity/STATUS.yaml \
        [--preserve-manual-fields]   # keep existing status/notes on rerun
"""
import argparse
import importlib.util
import os
import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MANIFEST_SCRIPT = os.path.join(ROOT, "scripts", "build_jurisdiction_manifest.py")


def load_manifest_module():
    spec = importlib.util.spec_from_file_location("build_jurisdiction_manifest", MANIFEST_SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Hand-seeded known state as of the 2026-07-16 audit that discovered the
# problem (Ecuador verified this session; nothing else touched yet).
SEED_STATUS = {
    "ec": {
        "fidelity_status": "verified",
        "official_total_codes": 721,
        "current_localization_codes": 33,  # distinct Kontablo nodes carrying an 'ec' local_code
        "source_url": "https://appscvsmovil.supercias.gob.ec/balances/PLAN_CUENTAS.pdf",
        "source_authority": "Superintendencia de Companias, Valores y Seguros (Ecuador)",
        "last_verified": "2026-07-16",
        "notes": ("Full official chart transcribed verbatim in "
                  "localizations/ec/supercias_official_chart.yaml, classified in "
                  "supercias_mapping.yaml (540 mapped / 116 captions / 23 aggregate "
                  "headers / 42 needs_review). ERPNext tree in default_tree_ec.json. "
                  "See localizations/ec/README.md."),
    },
}


def build(out_path, preserve_manual=True):
    mod = load_manifest_module()
    numeric_inline, fam_members = mod.derive_codes_available()

    existing = {}
    if preserve_manual and os.path.exists(out_path):
        prev = yaml.safe_load(open(out_path, encoding="utf-8")) or {}
        for row in prev.get("jurisdictions", []):
            existing[row["iso"]] = row

    rows = []
    for iso, (name, region) in mod.STATES.items():
        fam_named = mod.CHART_FAMILY.get(iso)
        has_codes = iso in numeric_inline or iso in fam_members
        mapping_mode = "statutory_chart" if (fam_named or has_codes) else "ifrs_direct"

        prior = existing.get(iso, {})
        seed = SEED_STATUS.get(iso, {})

        if seed:
            fidelity_status = seed["fidelity_status"]
        elif prior.get("fidelity_status") and prior["fidelity_status"] != "not_started":
            fidelity_status = prior["fidelity_status"]  # preserve manual progress from a prior session
        elif mapping_mode == "ifrs_direct":
            fidelity_status = "n/a_no_statutory_chart"
        elif fam_named or has_codes:
            fidelity_status = "partial_curated_subset"  # known state for ALL non-ec jurisdictions today
        else:
            fidelity_status = "not_started"

        row = {
            "iso": iso,
            "name": name,
            "region": region,
            "mapping_mode": mapping_mode,
            "chart_family": fam_named,
            "fidelity_status": fidelity_status,
            "official_total_codes": seed.get("official_total_codes", prior.get("official_total_codes")),
            "current_localization_codes": seed.get("current_localization_codes", prior.get("current_localization_codes")),
            "source_url": seed.get("source_url", prior.get("source_url")),
            "source_authority": seed.get("source_authority", prior.get("source_authority")),
            "last_verified": seed.get("last_verified", prior.get("last_verified")),
            "notes": seed.get("notes", prior.get("notes")),
        }
        rows.append(row)

    rows.sort(key=lambda r: (r["region"], r["name"]))

    by_status = {}
    for r in rows:
        by_status[r["fidelity_status"]] = by_status.get(r["fidelity_status"], 0) + 1

    doc = {
        "metadata": {
            "title": "Kontablo Chart-of-Accounts Fidelity Tracker",
            "purpose": (
                "Per-jurisdiction checklist so the COA-fidelity correction effort "
                "survives context/quota limits across many sessions. Every session "
                "working this effort MUST read this file first, pick the next "
                "'not_started' or 'partial_curated_subset' row, do the work, and "
                "rewrite this file (or rerun build_status_tracker.py with "
                "--preserve-manual-fields) before ending."
            ),
            "status_values": {
                "not_started": "No official-source verification attempted yet.",
                "partial_curated_subset": ("Known current state for every statutory_chart "
                                            "jurisdiction except ec: the localization file is a "
                                            "small hand-picked subset, NOT an exhaustive "
                                            "transcription of the official chart. Treat as a "
                                            "confirmed gap, not merely unstarted."),
                "source_identified": "Official primary source located and cited, not yet extracted.",
                "extracted": "Official chart transcribed verbatim (parse_official_chart.py output exists).",
                "classified": "Verbatim chart classified onto Kontablo Level-3 nodes (map_official_chart.py output exists).",
                "verified": "Extracted + classified + spot-checked + ERPNext tree built + README written.",
                "n/a_no_statutory_chart": ("ifrs_direct jurisdiction: no mandated national numeric "
                                            "chart exists to be exhaustive against. Lower priority; "
                                            "fidelity here means the IFRS-tag mapping is reasonable, "
                                            "not that a national chart is missing."),
                "blocked": "Attempted; blocked on something (see notes) -- e.g. no accessible primary source PDF.",
            },
            "counts": by_status,
            "total_jurisdictions": len(rows),
            "methodology": "research/coa_fidelity/README.md",
            "generator": "scripts/coa_fidelity/build_status_tracker.py",
        },
        "jurisdictions": rows,
    }

    with open(out_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=100)

    print(f"Wrote {len(rows)} jurisdictions to {out_path}")
    for k, v in sorted(by_status.items(), key=lambda kv: -kv[1]):
        print(f"  {k}: {v}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="research/coa_fidelity/STATUS.yaml")
    ap.add_argument("--preserve-manual-fields", action="store_true", default=True)
    args = ap.parse_args()
    build(args.out, preserve_manual=args.preserve_manual_fields)


if __name__ == "__main__":
    main()
