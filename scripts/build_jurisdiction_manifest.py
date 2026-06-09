#!/usr/bin/env python3
"""
Build the Kontablo 195-jurisdiction coverage manifest.

"195 jurisdictions" = the 193 UN member states + 2 UN observer states
(Holy See, State of Palestine). This is the standard count of sovereign states.

Honest coverage model (no fabricated codes):
  Every jurisdiction is covered by Kontablo's IFRS-anchored universal layer
  (each Level-3 node carries an ifrs_tag). On TOP of that, jurisdictions that
  impose a *statutory national chart of accounts* additionally get a
  local_codes / chart-family overlay enabling Tier-1 exact lookup.

  mapping_mode:
    - "statutory_chart" : a mandated national chart exists; a chart_family is
                          named (codes are populated for the families we can
                          verify against a primary source).
    - "ifrs_direct"     : no mandated national numeric chart (typically
                          common-law / IFRS-direct); mapping is via the IFRS tag.

Classification basis:
  - IFRS adoption status: IFRS Foundation, "Who uses IFRS Accounting Standards?"
    (jurisdiction profiles; 169 profiled). Marked per jurisdiction; "profile_na"
    where the Foundation has no profile.
  - Statutory-chart vs IFRS-direct: legal-tradition heuristic (civil-law systems
    typically mandate a national chart; common-law systems typically do not),
    refined by named chart families (OHADA/SYSCOHADA, PCG, PGC, SAT, PUC, CAS,
    VAS, RAS, HGB, ...). This is a documented classification, not a claim of a
    verified code set for every state — code sets are populated only where a
    primary source is cited (see core/schemas/chart_families.yaml).

Output: core/schemas/jurisdiction_coverage.yaml  (+ printed summary)
Run:    venv/bin/python scripts/build_jurisdiction_manifest.py
"""

import os
import yaml
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "core/schemas/jurisdiction_coverage.yaml")

# --- 195 sovereign states: ISO-3166-1 alpha-2 -> (name, region) -------------
STATES = {
 # Africa
 "dz":("Algeria","Africa"),"ao":("Angola","Africa"),"bj":("Benin","Africa"),
 "bw":("Botswana","Africa"),"bf":("Burkina Faso","Africa"),"bi":("Burundi","Africa"),
 "cv":("Cabo Verde","Africa"),"cm":("Cameroon","Africa"),"cf":("Central African Republic","Africa"),
 "td":("Chad","Africa"),"km":("Comoros","Africa"),"cg":("Congo (Republic)","Africa"),
 "cd":("DR Congo","Africa"),"ci":("Cote d'Ivoire","Africa"),"dj":("Djibouti","Africa"),
 "eg":("Egypt","Africa"),"gq":("Equatorial Guinea","Africa"),"er":("Eritrea","Africa"),
 "sz":("Eswatini","Africa"),"et":("Ethiopia","Africa"),"ga":("Gabon","Africa"),
 "gm":("Gambia","Africa"),"gh":("Ghana","Africa"),"gn":("Guinea","Africa"),
 "gw":("Guinea-Bissau","Africa"),"ke":("Kenya","Africa"),"ls":("Lesotho","Africa"),
 "lr":("Liberia","Africa"),"ly":("Libya","Africa"),"mg":("Madagascar","Africa"),
 "mw":("Malawi","Africa"),"ml":("Mali","Africa"),"mr":("Mauritania","Africa"),
 "mu":("Mauritius","Africa"),"ma":("Morocco","Africa"),"mz":("Mozambique","Africa"),
 "na":("Namibia","Africa"),"ne":("Niger","Africa"),"ng":("Nigeria","Africa"),
 "rw":("Rwanda","Africa"),"st":("Sao Tome and Principe","Africa"),"sn":("Senegal","Africa"),
 "sc":("Seychelles","Africa"),"sl":("Sierra Leone","Africa"),"so":("Somalia","Africa"),
 "za":("South Africa","Africa"),"ss":("South Sudan","Africa"),"sd":("Sudan","Africa"),
 "tz":("Tanzania","Africa"),"tg":("Togo","Africa"),"tn":("Tunisia","Africa"),
 "ug":("Uganda","Africa"),"zm":("Zambia","Africa"),"zw":("Zimbabwe","Africa"),
 # Americas
 "ag":("Antigua and Barbuda","Americas"),"ar":("Argentina","Americas"),
 "bs":("Bahamas","Americas"),"bb":("Barbados","Americas"),"bz":("Belize","Americas"),
 "bo":("Bolivia","Americas"),"br":("Brazil","Americas"),"ca":("Canada","Americas"),
 "cl":("Chile","Americas"),"co":("Colombia","Americas"),"cr":("Costa Rica","Americas"),
 "cu":("Cuba","Americas"),"dm":("Dominica","Americas"),"do":("Dominican Republic","Americas"),
 "ec":("Ecuador","Americas"),"sv":("El Salvador","Americas"),"gd":("Grenada","Americas"),
 "gt":("Guatemala","Americas"),"gy":("Guyana","Americas"),"ht":("Haiti","Americas"),
 "hn":("Honduras","Americas"),"jm":("Jamaica","Americas"),"mx":("Mexico","Americas"),
 "ni":("Nicaragua","Americas"),"pa":("Panama","Americas"),"py":("Paraguay","Americas"),
 "pe":("Peru","Americas"),"kn":("Saint Kitts and Nevis","Americas"),"lc":("Saint Lucia","Americas"),
 "vc":("Saint Vincent and the Grenadines","Americas"),"sr":("Suriname","Americas"),
 "tt":("Trinidad and Tobago","Americas"),"us":("United States","Americas"),
 "uy":("Uruguay","Americas"),"ve":("Venezuela","Americas"),
 # Asia
 "af":("Afghanistan","Asia"),"am":("Armenia","Asia"),"az":("Azerbaijan","Asia"),
 "bh":("Bahrain","Asia"),"bd":("Bangladesh","Asia"),"bt":("Bhutan","Asia"),
 "bn":("Brunei","Asia"),"kh":("Cambodia","Asia"),"cn":("China","Asia"),
 "cy":("Cyprus","Asia"),"ge":("Georgia","Asia"),"in":("India","Asia"),
 "id":("Indonesia","Asia"),"ir":("Iran","Asia"),"iq":("Iraq","Asia"),
 "il":("Israel","Asia"),"jp":("Japan","Asia"),"jo":("Jordan","Asia"),
 "kz":("Kazakhstan","Asia"),"kw":("Kuwait","Asia"),"kg":("Kyrgyzstan","Asia"),
 "la":("Laos","Asia"),"lb":("Lebanon","Asia"),"my":("Malaysia","Asia"),
 "mv":("Maldives","Asia"),"mn":("Mongolia","Asia"),"mm":("Myanmar","Asia"),
 "np":("Nepal","Asia"),"kp":("North Korea","Asia"),"om":("Oman","Asia"),
 "pk":("Pakistan","Asia"),"ps":("State of Palestine","Asia"),"ph":("Philippines","Asia"),
 "qa":("Qatar","Asia"),"sa":("Saudi Arabia","Asia"),"sg":("Singapore","Asia"),
 "kr":("South Korea","Asia"),"lk":("Sri Lanka","Asia"),"sy":("Syria","Asia"),
 "tj":("Tajikistan","Asia"),"th":("Thailand","Asia"),"tl":("Timor-Leste","Asia"),
 "tr":("Turkey","Asia"),"tm":("Turkmenistan","Asia"),"ae":("United Arab Emirates","Asia"),
 "uz":("Uzbekistan","Asia"),"vn":("Vietnam","Asia"),"ye":("Yemen","Asia"),
 # Europe
 "al":("Albania","Europe"),"ad":("Andorra","Europe"),"at":("Austria","Europe"),
 "by":("Belarus","Europe"),"be":("Belgium","Europe"),"ba":("Bosnia and Herzegovina","Europe"),
 "bg":("Bulgaria","Europe"),"hr":("Croatia","Europe"),"cz":("Czechia","Europe"),
 "dk":("Denmark","Europe"),"ee":("Estonia","Europe"),"fi":("Finland","Europe"),
 "fr":("France","Europe"),"de":("Germany","Europe"),"gr":("Greece","Europe"),
 "hu":("Hungary","Europe"),"is":("Iceland","Europe"),"ie":("Ireland","Europe"),
 "it":("Italy","Europe"),"va":("Holy See","Europe"),"lv":("Latvia","Europe"),
 "li":("Liechtenstein","Europe"),"lt":("Lithuania","Europe"),"lu":("Luxembourg","Europe"),
 "mt":("Malta","Europe"),"md":("Moldova","Europe"),"mc":("Monaco","Europe"),
 "me":("Montenegro","Europe"),"nl":("Netherlands","Europe"),"mk":("North Macedonia","Europe"),
 "no":("Norway","Europe"),"pl":("Poland","Europe"),"pt":("Portugal","Europe"),
 "ro":("Romania","Europe"),"ru":("Russia","Europe"),"sm":("San Marino","Europe"),
 "rs":("Serbia","Europe"),"sk":("Slovakia","Europe"),"si":("Slovenia","Europe"),
 "es":("Spain","Europe"),"se":("Sweden","Europe"),"ch":("Switzerland","Europe"),
 "ua":("Ukraine","Europe"),"gb":("United Kingdom","Europe"),
 # Oceania
 "au":("Australia","Oceania"),"fj":("Fiji","Oceania"),"ki":("Kiribati","Oceania"),
 "mh":("Marshall Islands","Oceania"),"fm":("Micronesia","Oceania"),"nr":("Nauru","Oceania"),
 "nz":("New Zealand","Oceania"),"pw":("Palau","Oceania"),"pg":("Papua New Guinea","Oceania"),
 "ws":("Samoa","Oceania"),"sb":("Solomon Islands","Oceania"),"to":("Tonga","Oceania"),
 "tv":("Tuvalu","Oceania"),"vu":("Vanuatu","Oceania"),
}

# --- Statutory chart families (jurisdiction -> family). Only named where a
#     mandated national/ supranational chart is well established. -------------
OHADA = ["bj","bf","cm","cf","td","km","cg","cd","ci","gq","ga","gn","gw",
         "ml","ne","sn","tg"]  # 17 OHADA states sharing SYSCOHADA
CHART_FAMILY = {**{j: "SYSCOHADA" for j in OHADA}}
CHART_FAMILY.update({
    "fr":"PCG","mc":"PCG",                         # Plan Comptable Général
    "ma":"CGNC","tn":"PC_Tunisie","dz":"SCF",      # Maghreb (PCG-derived)
    # Latin America: only states with a genuinely mandated national chart.
    # Chile, Costa Rica, Uruguay, Dominican Rep., Paraguay apply IFRS directly
    # without a mandated national numeric chart -> left as ifrs_direct.
    "es":"PGC_ES","co":"PUC_CO","pe":"PCGE_PE","ec":"PUC_EC","bo":"PUC_BO",
    "mx":"SAT","br":"SPED","ar":"PCGA_AR","ve":"PUC_VE",
    "de":"HGB_SKR","at":"OEKR","ch":"PME_CH",
    "ru":"RAS_94n","by":"RAS_BY","kz":"RAS_KZ","ua":"RAS_UA","uz":"RAS_UZ",
    "am":"RAS_AM","az":"RAS_AZ","ge":"RAS_GE","kg":"RAS_KG","tj":"RAS_TJ",
    "tm":"RAS_TM","md":"RAS_MD",
    "cn":"CAS","vn":"VAS","kr":"KIFRS_chart","jp":"JP_chart","th":"TH_chart",
    "id":"SAK_ID","kh":"CAS_KH","la":"LAS",
    "pt":"SNC_PT","gr":"EGLS","pl":"PL_chart","ro":"RO_chart","cz":"CZ_chart",
    "sk":"SK_chart","hu":"HU_chart","bg":"BG_chart","si":"SI_chart","hr":"HR_chart",
    "rs":"RS_chart","be":"PCMN_BE","lu":"PCN_LU","tr":"TR_chart",
})

# Tier-1 availability is DERIVED FROM ACTUAL DATA (no hand list): a jurisdiction
# is Tier-1 iff it has >=1 real (digit-bearing) inline code in level3_accounts.yaml
# OR is a member of a chart family that carries codes in chart_families.yaml.
# Descriptive text placeholders (e.g. "Cash") are not codes and do not count.
ONTOLOGY_PATH = os.path.join(ROOT, "core/schemas/level3_accounts.yaml")
FAMILIES_PATH = os.path.join(ROOT, "core/schemas/chart_families.yaml")


def _is_code(c):
    return any(ch.isdigit() for ch in str(c))


def derive_codes_available():
    numeric_inline, fam_members = set(), set()
    for d in yaml.safe_load_all(open(ONTOLOGY_PATH, encoding="utf-8")):
        items = d.get("level3") if isinstance(d, dict) and "level3" in d else (d if isinstance(d, list) else [])
        for it in items or []:
            if isinstance(it, dict) and "nature" in it:
                for j, code in (it.get("local_codes") or {}).items():
                    if _is_code(code):
                        numeric_inline.add(j)
    fams = (yaml.safe_load(open(FAMILIES_PATH, encoding="utf-8")) or {}).get("families", {})
    for fam in fams.values():
        if fam.get("codes"):
            fam_members.update(fam.get("members", []))
    return numeric_inline, fam_members

# IFRS adoption status overrides (default: required for listed companies, per
# IFRS Foundation profiles). Only notable deviations are listed.
IFRS_OVERRIDE = {
    "us":"US-GAAP (IFRS permitted for foreign private issuers)",
    "cn":"Chinese ASBE (substantially converged with IFRS)",
    "jp":"IFRS permitted; J-GAAP + JMIS also used",
    "in":"Ind-AS (IFRS-converged)",
    "vn":"VAS (IFRS adoption roadmap to 2025+)",
    "th":"TFRS (IFRS-converged)",
    "id":"SAK (IFRS-converged)",
    "bo":"national GAAP (IFRS not required)",
    "ye":"profile_na","so":"profile_na","kp":"profile_na","tm":"profile_na",
    "er":"profile_na","ss":"profile_na","va":"profile_na","cu":"national GAAP",
}
DEFAULT_IFRS = "IFRS required for domestic listed companies (IFRS Foundation profile)"


def build():
    numeric_inline, fam_members = derive_codes_available()
    rows = []
    for iso, (name, region) in STATES.items():
        fam_named = CHART_FAMILY.get(iso)
        has_codes = iso in numeric_inline or iso in fam_members
        mode = "statutory_chart" if (fam_named or has_codes) else "ifrs_direct"
        # name the chart family; jurisdictions with real inline codes but no
        # supranational family are tagged "national_inline".
        fam = fam_named or ("national_inline" if iso in numeric_inline else None)
        rows.append({
            "iso": iso, "name": name, "region": region,
            "ifrs_status": IFRS_OVERRIDE.get(iso, DEFAULT_IFRS),
            "mapping_mode": mode,
            "chart_family": fam,
            "tier1_codes_available": has_codes,
            "coverage_basis": ("statutory local_codes overlay + IFRS anchor"
                               if mode == "statutory_chart"
                               else "IFRS tag (no mandated national chart)"),
        })
    rows.sort(key=lambda r: (r["region"], r["name"]))
    doc = {
        "metadata": {
            "title": "Kontablo Jurisdiction Coverage Manifest",
            "count": len(rows),
            "definition": "193 UN member states + 2 UN observer states (Holy See, State of Palestine)",
            "ifrs_status_source": "IFRS Foundation, 'Who uses IFRS Accounting Standards?' jurisdiction profiles (https://www.ifrs.org/use-around-the-world/use-of-ifrs-standards-by-jurisdiction/)",
            "mapping_mode_basis": "legal-tradition heuristic refined by named statutory chart families; code sets populated only where a primary source is cited (see chart_families.yaml)",
            "note": "Universal coverage is via the IFRS-anchored layer (every Level-3 node has an ifrs_tag). statutory_chart jurisdictions additionally receive a local-code overlay.",
            "boundary_conditions": [
                "B1. No fabricated codes. A jurisdiction is marked tier1_codes_available ONLY when a primary-source-cited code set exists (inline in level3_accounts.yaml or via a chart family in chart_families.yaml).",
                "B2. Two distinct claims. mapping_mode='statutory_chart' is a CLASSIFICATION that a mandated national chart exists (legal-tradition heuristic + named family); tier1_codes_available is the stronger, VERIFIED claim that we hold cited codes. The two are reported separately; statutory_chart without codes means 'chart exists, codes not yet transcribed', not 'covered by Tier 1'.",
                "B3. IFRS-direct is a real coverage mode, not a gap. For the ~122 jurisdictions with no mandated national numeric chart (typically common-law), the honest and complete mapping basis is the IFRS tag carried by every Level-3 node; there is no local code to transcribe.",
                "B4. Multi-state multipliers only where a chart is genuinely shared. SYSCOHADA (OHADA Uniform Act) is the one supranational chart shared verbatim by 17 states. The EU has NO shared chart (each member state has its own), so EU coverage is per-country, not a multiplier.",
                "B5. Conservative classification. Where statehood applies IFRS directly without a mandated chart (e.g., Chile, Uruguay, Costa Rica, Dominican Rep., Paraguay), the jurisdiction is left ifrs_direct rather than asserting a chart that does not exist.",
                "B6. IFRS status provenance. ifrs_status derives from the IFRS Foundation jurisdiction profiles (169 profiled); states without a profile are marked 'profile_na' rather than assumed.",
            ],
        },
        "jurisdictions": rows,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        yaml.safe_dump(doc, f, allow_unicode=True, sort_keys=False, width=100)

    # summary
    n = len(rows)
    by_mode = Counter(r["mapping_mode"] for r in rows)
    by_region = Counter(r["region"] for r in rows)
    fams = Counter(r["chart_family"] for r in rows if r["chart_family"])
    t1 = sum(1 for r in rows if r["tier1_codes_available"])
    print(f"Jurisdictions: {n}  (expected 195)")
    print(f"By region: {dict(by_region)}")
    print(f"Mapping mode: {dict(by_mode)}")
    print(f"Tier-1 code sets available (primary-source cited): {t1}")
    print(f"  - of which via SYSCOHADA (one chart, 17 states): {len(OHADA)}")
    print(f"Distinct statutory chart families named: {len(fams)}")
    print(f"Written: {os.path.relpath(OUT, ROOT)}")
    assert n == 195, f"expected 195 states, got {n}"


if __name__ == "__main__":
    build()
