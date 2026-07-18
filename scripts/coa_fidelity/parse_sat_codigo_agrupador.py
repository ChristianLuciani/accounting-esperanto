#!/usr/bin/env python3
"""
Deterministic parser for SAT's (Mexico) "código agrupador" table, as
published in Anexo 24 of the Resolución Miscelánea Fiscal. The source is a
"Nivel / Código agrupador / Nombre de la cuenta y/o subcuenta" three-column
table inside the Anexo 24 PDF -- structurally different from Ecuador's
"CODIGO / NOMBRE DE LA CUENTA / SIGNO" layout (parse_official_chart.py), so
it gets its own parser rather than being forced through that one.

This exists so that transcribing the official chart into Kontablo never goes
through hand-typing -- the same failure mode that originally produced only
14 hand-picked MX accounts against SAT's real chart of 1,079 codes. The
input is `pdftotext -layout <Anexo_24.pdf>`; the output is a raw, verbatim,
source-cited YAML -- no Kontablo UUID classification happens here, that is a
separate, reviewable step (see map_official_chart.py).

Usage:
    pdftotext -layout Anexo_24_RMF2026-13012026.pdf sat_anexo24.txt
    python3 scripts/coa_fidelity/parse_sat_codigo_agrupador.py \
        --input sat_anexo24.txt \
        --source-url "https://www.sat.gob.mx/minisitio/NormatividadRMFyRGCE/documentos2026/rmf/anexos/Anexo_24_RMF2026-13012026.pdf" \
        --out localizations/mx/sat_official_chart.yaml
"""
import argparse
import re
import sys

import yaml


def parse_sat_chart(lines):
    """Parse the "Nivel / Código agrupador / Nombre de la cuenta" table."""
    accounts = []

    in_table = False
    start = 0
    for i, line in enumerate(lines):
        if "Nivel" in line and "Código" in line and "Nombre" in line:
            in_table = True
            start = i + 1
            break
    if not in_table:
        print("Could not find table start (Nivel/Código/Nombre header)", file=sys.stderr)
        return []

    for line in lines[start:]:
        if "DIARIO OFICIAL" in line or line.strip().startswith("Martes"):
            continue
        if not line.strip():
            continue

        # "Nivel   Código agrupador   Nombre de la cuenta y/o subcuenta"
        # Nivel column is blank for bare section headers (e.g. "100.01").
        match = re.match(r"^(\s*)(\d+)?(\s+)([0-9.]+)(\s+)(.+?)(\s*)$", line)
        if not match:
            continue

        groups = match.groups()
        nivel_str = groups[1]
        codigo = groups[3].strip()
        nombre = groups[5].strip()

        if not codigo or not nombre:
            continue
        if codigo == "agrupador" or "Nombre de la cuenta" in nombre:
            continue

        nivel = int(nivel_str) if nivel_str and nivel_str.strip() else 0

        accounts.append({"code": codigo, "name": nombre, "nivel": nivel})

    return accounts


def determine_nature(code):
    """Determine Debit/Credit nature from SAT's código agrupador structure.

    Uses precise numeric ranges rather than a single leading digit. This
    matters because SAT's "7" root (700 Resultado integral de
    financiamiento) is NOT nature-uniform the way "1" (Activo) or "2"
    (Pasivo) are: it bundles both expense codes (701 Gastos financieros,
    703 Otros gastos) and income codes (702 Productos financieros, 704
    Otros productos) under the same root digit. A blunt "root 7 = Credit"
    rule silently mislabels 701/703 as Credit when they are genuinely
    Debit-nature expense accounts -- verified against the actual account
    names in the parsed chart, not assumed from the digit alone.
    """
    base = code.split(".")[0]
    try:
        num = float(base)
    except ValueError:
        return "Debit"

    if 100 <= num < 200:
        return "Debit"    # Activo
    if 200 <= num < 300:
        return "Credit"   # Pasivo
    if 300 <= num < 400:
        return "Credit"   # Capital contable
    if 400 <= num < 500:
        return "Credit"   # Ingresos (402 contra-revenue keeps the root's nature, same convention SAT uses for its own contra-asset/contra-expense codes)
    if 500 <= num < 600:
        return "Debit"    # Costos
    if 600 <= num < 700:
        return "Debit"    # Gastos
    if num == 700:
        return "Debit"    # Resultado integral de financiamiento (section header, non-postable)
    if num == 701:
        return "Debit"    # Gastos financieros (expense)
    if num == 702:
        return "Credit"   # Productos financieros (income)
    if num == 703:
        return "Debit"    # Otros gastos (expense)
    if num == 704:
        return "Credit"   # Otros productos (income)
    if 800 <= num < 900:
        return "Debit"    # Cuentas de orden (order/memorandum accounts, non-postable)
    return "Debit"


def to_yaml_doc(accounts, source_url):
    lines = []
    lines.append("metadata:")
    lines.append("  jurisdiction: mx")
    lines.append("  authority: SAT (Servicio de Administración Tributaria)")
    lines.append(f"  source_url: {source_url}")
    lines.append('  extraction_date: "2026-01-13"')
    lines.append("  parser: scripts/coa_fidelity/parse_sat_codigo_agrupador.py")
    lines.append(f"  total_accounts: {len(accounts)}")
    lines.append(
        "  note: Verbatim transcription of SAT Código Agrupador from Anexo 24 "
        "RMF 2026. SAT Anexo 24 does not assign codes to specific financial "
        "statements; statement field is set to \"Catálogo de Cuentas\" for "
        "all codes."
    )
    lines.append("")
    lines.append("accounts:")
    for acc in accounts:
        code = acc["code"]
        nature = determine_nature(code)
        lines.append(f"- code: '{code}'")
        lines.append(f"  name: {acc['name']}")
        lines.append(f"  nature: {nature}")
        lines.append("  sign: POSITIVO")
        lines.append("  statement: Catálogo de Cuentas")
        lines.append(f"  depth: {acc['nivel']}")
    return "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--source-url", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    with open(args.input, encoding="utf-8") as f:
        lines = f.readlines()

    accounts = parse_sat_chart(lines)
    doc_text = to_yaml_doc(accounts, args.source_url)

    # Round-trip through yaml.safe_load as a structural sanity check before
    # writing -- a malformed emit here would silently corrupt every
    # downstream classification step.
    yaml.safe_load(doc_text)

    with open(args.out, "w", encoding="utf-8") as f:
        f.write(doc_text)

    print(f"Parsed {len(accounts)} accounts")
    print(f"Written: {args.out}")


if __name__ == "__main__":
    main()
