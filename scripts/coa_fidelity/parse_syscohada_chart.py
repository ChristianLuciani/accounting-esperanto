#!/usr/bin/env python3
"""
Deterministic parser for the SYSCOHADA (revised) "Plan de Comptes" -- the
official chart of accounts shared by all 17 OHADA member states, as
transcribed verbatim from the Acte Uniforme relatif au Droit Comptable et a
l'Information Financiere (AUDCIF), Titre VII "Structure, contenu et
fonctionnement des comptes", Chapitre 2 "Structure du plan de comptes",
Section 3 "Liste des comptes".

This source's layout differs from Ecuador's single-line "CODE NAME SIGN"
table (parse_official_chart.py), so it gets its own parser rather than
reusing that regex, per the fidelity-sweep protocol:

  - Each account class (1-9) opens with a compact 2-digit index, then the
    SAME 2-digit codes reappear as detailed section headers with 3- and
    4-digit sub-accounts nested beneath them (indentation is not reliable;
    the code's own digit count IS the hierarchy signal: 2 digits = section,
    3 = account, 4 = sub-account).
  - Long account names wrap across two physical lines (no leading digits on
    the continuation line); footnote bodies ("(1) A l'exception des...")
    and the running page footer ("SYSCOHADA STRUCTURE, CONTENU ET
    FONCTIONNEMENT DES COMPTES <n>") are noise to be discarded, not
    continuations.
  - Unlike the Ecuador source, this table carries no explicit debit/credit
    "signe" column per line, so no per-account "nature" is fabricated here;
    nature is left to be inferred from the Kontablo node an account
    classifies onto (map_syscohada_chart.py), never guessed at parse time.

Usage:
    pdftotext -layout <AUDCIF.pdf> <audcif.txt>
    sed -n '<first>,<last>p' audcif.txt > liste_des_comptes.txt   # Section 3 only
    python3 scripts/coa_fidelity/parse_syscohada_chart.py \
        --input liste_des_comptes.txt \
        --source-url "<AUDCIF full-text URL>" \
        --authority "OHADA (Organisation pour l'Harmonisation en Afrique du Droit des Affaires)" \
        --out localizations/_syscohada/syscohada_official_chart.yaml
"""
import argparse
import re
import sys
import yaml

FOOTER_RE = re.compile(r"^SYSCOHADA STRUCTURE", re.IGNORECASE)
CLASSE_RE = re.compile(r"\bCLASSE\s*(\d)\b", re.IGNORECASE)
CODE_RE = re.compile(r"^\s*(\d{2,4})\s+(\S.*?)\s*$")
FOOTNOTE_RE = re.compile(r"^\(\s*\d")
RANGE_REF_RE = re.compile(r"^à\s+\d")  # e.g. "911 à 914 CONTREPARTIE..." -- a cross-reference note, not a coded account


def parse_lines(lines):
    entries = {}  # code -> entry dict, insertion order preserved (py3.7+)
    order = []
    current_class = None
    active_code = None       # code whose name is still eligible for continuation
    prev_line_was_content = False  # True only if the immediately preceding
                                    # non-discarded line extended `active_code`

    for raw in lines:
        line = raw.rstrip("\n")
        stripped = line.strip()

        if not stripped:
            prev_line_was_content = False
            continue
        if FOOTER_RE.match(stripped):
            # Running page footer -- discard, but do NOT break continuation
            # chains (it can appear mid-wrap between two halves of a name).
            continue
        m_classe = CLASSE_RE.search(stripped)
        if m_classe and not CODE_RE.match(stripped):
            current_class = m_classe.group(1)
            active_code = None
            prev_line_was_content = False
            continue
        if FOOTNOTE_RE.match(stripped):
            active_code = None
            prev_line_was_content = False
            continue

        m = CODE_RE.match(line)
        if m:
            code, name = m.group(1), m.group(2)
            if RANGE_REF_RE.match(name):
                # e.g. "911 à 914 CONTREPARTIE DES ENGAGEMENTS OBTENUS, 901 à
                # 904" -- the source describes these by cross-reference only
                # and never spells out 911-914/915-918 as individual lines.
                # Not a real coded entry; do not fabricate one.
                active_code = None
                prev_line_was_content = False
                continue
            if code in entries:
                # Reappears as the detailed section header after the
                # class's compact 2-digit index; keep the richer (later)
                # name if it differs, otherwise this is a no-op.
                entries[code]["name"] = name
            else:
                entries[code] = {
                    "code": code,
                    "name": name,
                    "class": current_class,
                    "depth": len(code),
                }
                order.append(code)
            active_code = code
            prev_line_was_content = True
            continue

        # Not a code line. Only treat as a wrapped continuation of the
        # active entry's name if the previous kept line was that same
        # entry (no blank line / footnote / class-header break since).
        if active_code is not None and prev_line_was_content:
            entries[active_code]["name"] = (entries[active_code]["name"] + " " + stripped).strip()
            prev_line_was_content = True
            continue

        # Otherwise: stray prose (e.g. class-title wrap text like "COMPTES
        # DE TRESORERIE" between "CLASSE 5" and the first "50 ..." line, or
        # a footnote continuation line) -- discard.
        prev_line_was_content = False

    return [entries[c] for c in order]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Section-3-only slice of pdftotext -layout output")
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

    by_class = {}
    for e in entries:
        by_class[e["class"]] = by_class.get(e["class"], 0) + 1

    doc = {
        "metadata": {
            "jurisdiction": "_syscohada",
            "chart_family": "SYSCOHADA",
            "members": ["bj", "bf", "cm", "cf", "td", "km", "cg", "ci", "cd",
                        "gq", "ga", "gn", "gw", "ml", "ne", "sn", "tg"],
            "authority": args.authority,
            "source_url": args.source_url,
            "source_instrument": (
                "Acte Uniforme relatif au Droit Comptable et a l'Information "
                "Financiere (AUDCIF), adopted 26 January 2017 (Journal "
                "Officiel OHADA, 15 February 2017), in force 1 January 2018 "
                "for individual accounts. Titre VII, Chapitre 2, Section 3 "
                "\"Liste des comptes\"."
            ),
            "extraction_command": (
                "pdftotext -layout <AUDCIF.pdf> audcif.txt && "
                "sed -n '<first>,<last>p' audcif.txt > liste_des_comptes.txt  "
                "# Titre VII / Chapitre 2 / Section 3, printed pages ~222-276"
            ),
            "parser": "scripts/coa_fidelity/parse_syscohada_chart.py",
            "total_accounts": len(entries),
            "accounts_by_class": dict(sorted(by_class.items())),
            "duplicate_codes": sorted(set(duplicates)) or None,
            "note": (
                "Verbatim transcription of the primary-source official chart "
                "shared by all 17 OHADA member states. No Kontablo UUID "
                "classification here by design -- see map_syscohada_chart.py. "
                "Unlike the Ecuador source, this table has no per-line "
                "debit/credit 'signe' column, so no 'nature' field is "
                "fabricated per entry; class 9 (comptes des engagements hors "
                "bilan et comptabilite analytique de gestion) is of "
                "'application facultative' (optional) per the source itself "
                "and is transcribed for completeness but is not part of the "
                "mandatory postable ledger."
            ),
        },
        "accounts": entries,
    }

    with open(args.out, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=100)

    print(f"Parsed {len(entries)} accounts ({len(codes_seen)} unique codes)")
    print(f"By class: {dict(sorted(by_class.items()))}")
    if duplicates:
        print(f"NOTE: {len(set(duplicates))} codes overwritten by a later (detailed) occurrence: {sorted(set(duplicates))[:10]}...")
    print(f"Written: {args.out}")


if __name__ == "__main__":
    main()
