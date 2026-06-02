# Kontablo v0.1.0 — Initial public release

## What's in this release

- **Ontology**: 30 universal accounts (Level 3 minimum-core), UUID-keyed, empirically validated across 23 jurisdictions covering 92% of routine transaction volume
- **API**: FastAPI reference implementation (`api/`) with account mapping, batch consolidation, and transaction classification endpoints
- **Connectors**: ERPNext/Frappe connector (`connectors/erpnext/`) — Apache 2.0 license
- **Preprint**: Full academic paper — see `docs/papers/drafts/kontablo_preprint_modular.pdf`
- **Localizations**: YAML mapping files for 23 jurisdictions (`localizations/`)
- **OpenSpec**: 6 specification documents totaling ~9,800 lines (`openspec/`)

## Jurisdictions validated

MX (SAT), BR (SPED), FR (PCG), VE (IAS 29 hyperinflation), SA (SOCPA), VN (VAS), NG (FRCN), AR, CO, PE, CL, GT, EC, UK, DE, JP, IN, CN, AU, ZA, IL, RU, EE

## Known limitations

- MX SAT local code `"105"` not yet wired into YAML ontology — tracked as `xfail` in `tests/api/test_endpoints.py` with instructions
- AI semantic fallback uses `google.generativeai` (deprecated) — migration to `google.genai` pending
- Post-quantum cryptography (ML-KEM / ML-DSA per NIST FIPS 203/204) scheduled for Phase 3

## License

**Core**: Business Source License 1.1 — converts to Apache 2.0 on **2030-06-01**.
**ERPNext connector**: Apache 2.0.

See `LICENSE` and `LICENSING.md` for full terms.

## Citation

Preprint DOI: *to be updated after Zenodo/SSRN deposit*

```bibtex
@misc{luciani2026kontablo,
  author       = {Luciani, Christian},
  title        = {Kontablo: A Graph-Based Universal Accounting Ontology for the {M2M} Agentic Economy},
  year         = {2026},
  howpublished = {Preprint v0.1.0},
  url          = {https://github.com/ChristianLuciani/accounting-esperanto},
  note         = {DOI to be added upon Zenodo/SSRN deposit}
}
```
