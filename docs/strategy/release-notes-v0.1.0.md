# Kontablo v0.1.0 — Initial public release

## What's in this release

- **Ontology**: 30 universal accounts (Level 3 minimum-core), UUID-keyed, mapped across **195 sovereign jurisdictions (complete global coverage)** — ~94% routine transaction volume coverage (~99% with a 34-account extended core); reproducible via `scripts/coverage_benchmark.py`
- **API**: FastAPI reference implementation (`api/`) with account mapping, batch consolidation, and transaction classification endpoints
- **Connectors**: ERPNext/Frappe connector (`connectors/erpnext/`) — Apache 2.0 license
- **Preprint**: Full academic paper — see `docs/papers/drafts/kontablo_preprint_modular.pdf`
- **Localizations**: YAML mapping files for all 195 sovereign jurisdictions (`localizations/`) — 7,000+ account mappings
- **OpenSpec**: 6 specification documents totaling ~9,800 lines (`openspec/`)

## Jurisdictional coverage

All 195 UN-recognized sovereign states. Special contexts included:
- **IAS 29 hyperinflation**: VE, LB, ZW, CU, SR, SY
- **Islamic finance**: SA, QA, KW, BH, PK, BN, SD
- **Distribution-only CIT** (Estonian model): EE, LV, GE
- **SYSCOHADA** (OHADA mandatory chart): CI, CM, SN, CD, CG, GA, GN, ML, BF, NE, BJ, TG, BI, CF, TD
- **IFRS-pure** (no mandatory chart — core maps directly): EE, BW, NA, and ~60 others

## Known limitations

- MX SAT local code `"105"` not yet wired into YAML ontology — tracked as `xfail` in `tests/api/test_endpoints.py` with instructions
- AI semantic fallback uses `google.generativeai` (deprecated) — migration to `google.genai` pending
- Post-quantum cryptography (ML-KEM / ML-DSA per NIST FIPS 203/204) scheduled for Phase 3

## License

**Core**: Business Source License 1.1 — converts to Apache 2.0 on **2030-06-18** (the Change Date in `LICENSE`).
**ERPNext connector**: Apache 2.0.

See `LICENSE` and `LICENSING.md` for full terms.

## Citation

Preprint DOI: [10.5281/zenodo.20738796](https://doi.org/10.5281/zenodo.20738796) (Zenodo). SSRN URL pending.

```bibtex
@misc{luciani2026kontablo,
  author       = {Luciani, Christian},
  title        = {Kontablo: A Graph-Based Universal Accounting Ontology for the {M2M} Agentic Economy},
  year         = {2026},
  howpublished = {Preprint, Zenodo},
  doi          = {10.5281/zenodo.20738796},
  url          = {https://doi.org/10.5281/zenodo.20738796}
}
```
