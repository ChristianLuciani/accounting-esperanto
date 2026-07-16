#!/usr/bin/env python3
"""
Deterministic parser for tabular "CODIGO / NOMBRE DE LA CUENTA / SIGNO"-style
official chart-of-accounts PDFs (the Ecuador Superintendencia de Companias
Plan de Cuentas layout, and any other primary source sharing the same
column shape: a numeric code, a name, and a sign/type marker per line).

This exists so that transcribing an official chart into Kontablo never goes
through hand-typing (the failure mode that produced the Ecuador draft: 13
hand-picked accounts instead of the ~700 the source actually lists). The
input is `pdftotext -layout <official.pdf>`; the output is a raw, verbatim,
source-cited YAML — no Kontablo UUID classification happens here, that is a
separate, reviewable step (see map_official_chart.py).

Usage:
    pdftotext -layout official_chart.pdf official_chart.txt
    python3 scripts/coa_fidelity/parse_official_chart.py \
        --input official_chart.txt \
        --jurisdiction ec \
        --source-url "https://appscvsmovil.supercias.gob.ec/balances/PLAN_CUENTAS.pdf" \
        --authority "Superintendencia de Companias, Valores y Seguros (Ecuador)" \
        --out localizations/ec/supercias_official_chart.yaml
"""
import argparse
import re
import sys
import yaml

SIGN_TOKENS = {"POSITIVO", "NEGATIVO", "DUAL"}
CODE_RE = re.compile(r"^(\d+)\s+(.+?)\s+(POSITIVO|NEGATIVO|DUAL)\s*$")
HEADER_RE = re.compile(r"^(Estado de .+|CÓDIGO\s)", re.IGNORECASE)


def parse_lines(lines):
    entries = []
    current_statement = None
    for raw in lines:
        line = raw.rstrip("\n")
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.lower().startswith("estado de"):
            current_statement = stripped
            continue
        if stripped.upper().startswith("CÓDIGO") or stripped.upper().startswith("CODIGO"):
            continue
        m = CODE_RE.match(stripped)
        if not m:
            continue
        code, name, sign = m.groups()
        entries.append({
            "code": code,
            "name": " ".join(name.split()),
            "sign": sign,
            "statement": current_statement,
            "depth": len(code),
        })
    return entries


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="pdftotext -layout output")
    ap.add_argument("--jurisdiction", required=True)
    ap.add_argument("--source-url", required=True)
    ap.add_argument("--authority", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        lines = f.readlines()

    entries = parse_lines(lines)
    if not entries:
        print("ERROR: no account lines parsed - check input format/regex", file=sys.stderr)
        sys.exit(1)

    codes_seen = set()
    duplicates = []
    for e in entries:
        if e["code"] in codes_seen:
            duplicates.append(e["code"])
        codes_seen.add(e["code"])

    doc = {
        "metadata": {
            "jurisdiction": args.jurisdiction,
            "authority": args.authority,
            "source_url": args.source_url,
            "extraction_command": "pdftotext -layout <official.pdf> <output.txt>",
            "parser": "scripts/coa_fidelity/parse_official_chart.py",
            "total_accounts": len(entries),
            "duplicate_codes": sorted(set(duplicates)) or None,
            "note": (
                "Verbatim transcription of the primary-source official chart. "
                "No Kontablo UUID classification here by design - that mapping "
                "is a separate, human-reviewable step so a parsing bug can "
                "never silently corrupt the semantic mapping."
            ),
        },
        "accounts": entries,
    }

    with open(args.out, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=100)

    print(f"Parsed {len(entries)} accounts ({len(codes_seen)} unique codes)")
    if duplicates:
        print(f"WARNING: {len(set(duplicates))} duplicate codes: {sorted(set(duplicates))[:10]}...")
    print(f"Written: {args.out}")


if __name__ == "__main__":
    main()
