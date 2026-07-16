# Guinea-Bissau (`gw`) localization

**Status: verified against primary source (2026-07-16), via the shared
SYSCOHADA chart family.** Guinea-Bissau is one of the 17 OHADA member states bound
by the same Acte Uniforme relatif au Droit Comptable et a l'Information
Financiere (AUDCIF) -- SYSCOHADA revise, in force since 1 January 2018 --
so its chart of accounts is verified once, centrally, rather than
per-country. See **`localizations/_syscohada/README.md`** for the full
verbatim transcription (1,399 codes), the classification methodology, the
coverage-honesty breakdown, and the regeneration commands.

## What changed this round

Unlike its 16 sibling SYSCOHADA states, Guinea-Bissau had **no localization
file at all** before this round -- not even a stale hand-picked draft.
`localizations/gw/gw_mapping.yaml` was created this round so
`logic/knowledge_base.py` registers `GW` like every other jurisdiction; it
is populated directly and only from the verified
`core/schemas/chart_families.yaml` SYSCOHADA table below (33 entries, real
ontology UUIDs, real official codes) -- no hand-picked or fabricated data.

- `core/schemas/chart_families.yaml` (`families.SYSCOHADA`) -- the 33
  single-code-per-node representative mappings the live deterministic
  engine indexes for Guinea-Bissau (and all 16 other members) via
  `core/harness/ontology.py`'s `merge_family_codes`.
- `localizations/_syscohada/syscohada_official_chart.yaml` -- verbatim
  transcription of every official SYSCOHADA account code.
- `localizations/_syscohada/syscohada_mapping.yaml` -- every code
  classified onto a Kontablo Level-3 node, or flagged `needs_review` /
  `is_statement_caption`.
- `localizations/_syscohada/default_tree_syscohada.json` -- ERPNext-
  importable chart-of-accounts tree.

## Source

OHADA, Acte Uniforme relatif au Droit Comptable et a l'Information
Financiere (AUDCIF), adopted 26 January 2017, in force 1 January 2018.
Titre VII, Chapitre 2, Section 3 "Liste des comptes". See
`localizations/_syscohada/README.md` for the full citation, the
verification note on source provenance, and regeneration commands.

## Tracking

See `research/coa_fidelity/STATUS.yaml`, row `iso: gw` --
`fidelity_status: verified`, `chart_family: SYSCOHADA`.
