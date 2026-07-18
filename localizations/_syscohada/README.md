# SYSCOHADA (shared statutory chart) localization

**Status: verified against primary source (2026-07-16).** Superseded a
`chart_families.yaml`-only curated table of ~20 concepts. This directory
holds the **single shared source of truth** for all 17 OHADA member states
(`bj`, `bf`, `cm`, `cf`, `td`, `km`, `cg`, `ci`, `cd`, `gq`, `ga`, `gn`, `gw`,
`ml`, `ne`, `sn`, `tg`) — SYSCOHADA is one statutory chart mandated
identically across all of them by the OHADA treaty, so it is verified once
here rather than 17 times. Each member's `localizations/<cc>/README.md`
points back to this directory instead of duplicating the chart.

## Why centralized here, not per-country

Unlike Ecuador (one country, one chart), SYSCOHADA is inherently a
**shared** chart: the OHADA Acte Uniforme is the single legal instrument
that binds all 17 states, and `core/schemas/chart_families.yaml` already
modeled it this way (`families.SYSCOHADA.codes`, expanded to every member
via `core/harness/ontology.py`'s `merge_family_codes`). Structuring the
verbatim/classified chart as 17 near-identical copies under
`localizations/<cc>/` would (a) contradict the "one source of truth" the
family table already establishes, and (b) create 17 places for the same
future drift to hide. Centralizing under `localizations/_syscohada/`
keeps the fidelity work aligned with the family-table architecture that
was already in place, documented here per the sweep protocol's
"use your judgment on the cleanest structure" allowance.

## Files

| File | What it is | Regenerate with |
|---|---|---|
| `syscohada_official_chart.yaml` | Verbatim transcription of every account code in the official "Liste des comptes" | `pdftotext -layout <AUDCIF.pdf> audcif.txt && sed -n '<first>,<last>p' audcif.txt > liste_des_comptes.txt && python3 scripts/coa_fidelity/parse_syscohada_chart.py --input liste_des_comptes.txt --source-url "<AUDCIF full-text URL>" --authority "OHADA" --out localizations/_syscohada/syscohada_official_chart.yaml` |
| `syscohada_mapping.yaml` | Every official code classified onto a Kontablo Level-3 node (or flagged `needs_review` / `is_statement_caption`) | `python3 scripts/coa_fidelity/map_syscohada_chart.py --official localizations/_syscohada/syscohada_official_chart.yaml --out localizations/_syscohada/syscohada_mapping.yaml` |
| `default_tree_syscohada.json` | ERPNext-importable chart-of-accounts tree, generated from the mapping | `python3 scripts/coa_fidelity/build_syscohada_erpnext_tree.py --mapping localizations/_syscohada/syscohada_mapping.yaml --out localizations/_syscohada/default_tree_syscohada.json` |

`core/schemas/chart_families.yaml`'s `families.SYSCOHADA.codes` table (33 of
the 34 available Level-3 nodes, one representative code each) is what the
live deterministic engine actually indexes for all 17 members
(`core/harness/ontology.py`'s `merge_family_codes`) — it was cross-checked
against, and refined from, the exhaustive transcription in this directory
during this round (see "Corrections to the family table" below).

## Source

OHADA (Organisation pour l'Harmonisation en Afrique du Droit des Affaires),
**Acte Uniforme relatif au Droit Comptable et à l'Information Financière
(AUDCIF)**, adopted 26 January 2017, published in the Journal Officiel OHADA
15 February 2017, in force 1 January 2018 for individual accounts (1 January
2019 for consolidated/combined accounts and IFRS financial statements).
Titre VII "Structure, contenu et fonctionnement des comptes", Chapitre 2
"Structure du plan de comptes", Section 3 "Liste des comptes" (printed pages
~222–276 of the consolidated Acte-Uniforme-plus-Système-Comptable text).

- Instrument overview / adoption metadata: https://www.ohada.org/en/uniform-act-relating-to-accounting-law-and-financial-information-audcif/
- Full-text verbatim extraction source used for this transcription:
  https://www.msg-innov.online/gallery/ACTE%20UNIFORME%20SYSCOHADA%20REVISE.pdf

**Verification note (epistemic honesty per this project's standards):**
OHADA's own site (`ohada.org`) links its digital library (`biblio.ohada.org`)
for the full legal text, which gates behind a catalog/registration flow
rather than serving a direct PDF. The transcription was performed against
the third-party-hosted full-text mirror cited above. Its authenticity was
corroborated internally, not merely assumed: its table of contents,
chapter/section numbering, and page pagination match the AUDCIF's publicly
documented structure exactly, and — decisively — its account numbering
carries the **révisé** (2018+) terminology (e.g. class-1 account `17` is
"DETTES DE LOCATION ACQUISITION", the post-2018 IFRS 16-aligned label) and
*not* the pre-2018 SYSCOHADA/SYSCOA label ("DETTES DE CRÉDIT-BAIL ET
CONTRATS ASSIMILÉS", confirmed against an older, superseded copy of the
chart consulted during research). If Christian or a reviewer can obtain the
text directly from `biblio.ohada.org` or a national OHADA-member gazette,
a cross-diff against this file is welcome and would strengthen the citation
further.

## Coverage honesty

- **1,399** official codes transcribed verbatim across all 9 classes
  (class 9 — "comptes des engagements hors bilan et de la comptabilité
  analytique de gestion" — is, per the source itself, "d'application
  facultative" i.e. optional; it is transcribed for completeness but is not
  part of the mandatory postable ledger).
- **949** classified onto an existing Kontablo Level-3 node (many-to-one is
  by design — see `core/schemas/level3_accounts.yaml`'s "graph, not tree"
  principle).
- **55** are `is_statement_caption: true` — SYSCOHADA class 9 (49 codes,
  optional/off-balance-sheet, not real postable financial-position or
  -performance accounts) plus the class-1 "soldes intermédiaires de
  gestion" (6 codes: marge commerciale, valeur ajoutée, EBE, résultat
  d'exploitation, résultat financier, résultat des activités ordinaires) —
  computed presentation subtotals, not independently posted accounts.
- **79** are `is_aggregate: true` — header/rollup rows that have more
  granular children in this same chart, never independently postable.
- **316** are genuine `needs_review`: leaf accounts with no existing
  Kontablo Level-3 node fitting them. Honest ontology gaps, not silent
  guesses. The two largest, systematic categories:
  - **Contra-asset / contra-liability accumulated-depreciation and
    provision/impairment accounts** (classes `18`/`19`/`28`/`29`/`39`/`49`/
    `59`/`69`/`79`, and most of HAO class `8`): the 34-node Level-3 core has
    no dedicated "accumulated depreciation" or "provision for risks and
    charges" node yet — the same category of gap Ecuador's own README
    implicitly carries (EC's presentation-level chart nets these away
    entirely rather than exposing them as separate lines).
  - **Biological assets** (`asset.noncurrent.biological` would be needed —
    codes `246`, `249`, `313`, `345`, `363`, `373` and their sub-accounts):
    identical IAS 41 gap already documented in `localizations/ec/README.md`.
  - Smaller genuine gaps: government investment grants (class `14`),
    regulated/statutory reserves (class `15`, all of it, including `151`
    "amortissements dérogatoires" — an IFRS/IAS-12 lens reads this as a
    deferred-tax liability, but SYSCOHADA presents it as an equity-side item
    locally, so it is left `needs_review` rather than force-mapped; see
    Greptile's PR #79 review), inter-entity/
    branch liaison accounts (class `18`), international-body and
    joint-venture settlement accounts (classes `45`/`46`/`47` in part),
    financial derivatives and precious-metals treasury instruments (class
    `54`), self-constructed-asset capitalization and inventory-change
    adjustments (classes `72`/`73`), and statutory employee profit-sharing
    (class `87`) — none of these map cleanly onto any of the 34 available
    Level-3 nodes.
- `liability.current.tax`'s family-table code was corrected this round from
  `44` (the whole "État et collectivités publiques" class, which also
  contains `445` input-VAT — an **asset** — under the same 2-digit prefix)
  to `442` ("État, autres impôts et taxes"), a genuine leaf that is
  unambiguously a tax liability. This was a real precision defect in the
  pre-existing curated table, not a stylistic change.

## Members

`localizations/bj/`, `localizations/bf/`, `localizations/cm/`,
`localizations/cf/`, `localizations/td/`, `localizations/km/`,
`localizations/cg/`, `localizations/ci/`, `localizations/cd/`,
`localizations/gq/`, `localizations/ga/`, `localizations/gn/`,
`localizations/gw/`, `localizations/ml/`, `localizations/ne/`,
`localizations/sn/`, `localizations/tg/` each carry a short `README.md`
pointing back to this directory — see `research/coa_fidelity/STATUS.yaml`
for per-jurisdiction tracking rows (all 17 updated together this round,
since they share one verification event).
