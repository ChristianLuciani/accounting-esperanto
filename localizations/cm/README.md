# Cameroon (`cm`) localization

**Status: verified against primary source (2026-07-16), via the shared
SYSCOHADA chart family.** Cameroon is one of the 17 OHADA member states bound
by the same Acte Uniforme relatif au Droit Comptable et a l'Information
Financiere (AUDCIF) -- SYSCOHADA revise, in force since 1 January 2018 --
so its chart of accounts is verified once, centrally, rather than
per-country. See **`localizations/_syscohada/README.md`** for the full
verbatim transcription (1,399 codes), the classification methodology, the
coverage-honesty breakdown, and the regeneration commands.

## What changed this round

This directory already carried a pre-fidelity-sweep `cm_mapping.yaml` (a
~20-account hand-picked draft predating this sweep, using non-canonical
UUIDs and at least one account code -- `20`, "Immobilisations incorporelles"
-- that does not exist in the revised chart). It is **left in place
unchanged**, because `logic/knowledge_base.py` reads it to register Cameroon
at all (deleting it during this round regressed
`tests/test_localization_integrity.py`'s jurisdiction-count check from 200
to 184 -- caught and reverted before commit). It is superseded in
*authority*, not removed: the shared, verified SYSCOHADA family chart below
is now the source of truth for Cameroon's chart of accounts, and
`cm_mapping.yaml`'s stale codes/UUIDs should not be trusted or extended.
Retiring it properly (migrating `logic/knowledge_base.py` and its callers
onto the new `core/harness/ontology.py` family-table path) is future work,
not this round's scope.

- `core/schemas/chart_families.yaml` (`families.SYSCOHADA`) -- the 33
  single-code-per-node representative mappings the live deterministic
  engine indexes for Cameroon (and all 16 other members) via
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

See `research/coa_fidelity/STATUS.yaml`, row `iso: cm` --
`fidelity_status: verified`, `chart_family: SYSCOHADA`.
