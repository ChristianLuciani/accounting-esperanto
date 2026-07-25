# DR4 — Financial Ontologies/Standards for Machines, and the Precise Gap

> Research pass for Spoke 1 (`agentic-provenance`), feeding `TASKS.md` T1 (Related
> Work) and `references.bib`. All sources below were retrieved this session via
> `WebSearch`/`WebFetch`. Epistemic rule applied throughout: nothing is cited
> that was not actually fetched or returned in a tool result with a working
> URL; every unconfirmed field is marked `TODO`; secondary sources are labeled
> and never substituted for a primary claim.

---

## (a) Executive summary

Four standard families were compared against Kontablo's claimed properties
(UUID-canonical, graph not tree, per-entry provenance, byte-for-byte
reconstruction, 195-jurisdiction chart mapping, zero silent loss). The
headline finding is **not** that Kontablo is the only standard operating at
transaction/journal-entry granularity — **XBRL GL and OECD SAF-T/AICPA ADS
already reach entry-level granularity**, which is a genuine, fair complication
to any Related Work claim that leads with "granularity" alone. What none of
the seven standards/specs reviewed combine is: (1) entry-level granularity,
**(2)** a live, agent-callable, pre-transaction query/constraint interface,
**(3)** a single canonical ontology spanning many sovereign jurisdictions'
charts of accounts (as opposed to one taxonomy per jurisdiction, or one SAF-T
dialect per country), and **(4)** an explicit, typed, zero-silent-loss
provenance guarantee. FIBO and XBRL/ESEF/IFRS-Taxonomy sit *above* the entry
level (instrument/contract/entity semantics, or period-end reporting facts).
ISO 20022 standardizes the *message that moves value between institutions*,
not how either side's ledger books or reconstructs it. XBRL GL, AICPA ADS,
and OECD SAF-T reach the entry level but are static, post-hoc, single-
jurisdiction (or per-jurisdiction-dialect) batch-export formats with no
agent-native query surface. Each standard is, in its own lane, stronger than
Kontablo — most importantly XBRL/ESEF's binding legal mandate and ISO 20022's
network effects, both of which Kontablo entirely lacks.

## (b) Comparison table

| Standard | Semantics encoded | Granularity | Agent-native / per-entry provenance? | Cross-jurisdiction CoA mapping? | Maturity / adoption |
|---|---|---|---|---|---|
| **FIBO** (EDM Council / OMG) | OWL/RDF ontology of financial instruments, contracts, legal entities, business processes, market data — what things *are* and how they relate | Instrument / entity / contract level. **Not** transaction or journal-entry level | No. No posting primitives, no lineage/provenance model. OMG's own 2011 FDTF working note flags the FIBO↔double-entry-bookkeeping reconciliation as explicitly unfinished (see §e sourcing) | No native chart-of-accounts mapping; third-party downstream ontologies (e.g., bank call-report mappings) are built *on* FIBO by others, not shipped in FIBO itself | Mature OMG-formal-standard (FND v1.2, Dec 2017); large bank/vendor consortium; quarterly releases; open GitHub dev since 2020; **voluntary**, no regulatory mandate |
| **XBRL / iXBRL** (XBRL International) | Tagged financial-reporting facts: concepts + contexts + units → facts, inside taxonomies | Period-end / financial-statement-line-item level ("profit FY2025 = $10m"). **Not** transaction/journal-entry level | No. Tags a *finished* report; no concept of an individual agent posting a transaction, no per-entry lineage to source postings | No general cross-jurisdiction mapping mechanism — each regulator publishes its *own* taxonomy (US-GAAP via SEC, IFRS via IFRS Foundation, etc.); taxonomies are jurisdiction-specific vocabularies, not a Rosetta Stone across them | Very high. Legally mandated (SEC since 2009 for US filers; ESMA/ESEF since FY2020 for EU regulated-market issuers). XBRL's central strength |
| **ESEF / IFRS Taxonomy** (ESMA / IFRS Foundation) | IFRS-Taxonomy-based iXBRL tagging of *already-IFRS-consolidated* statements, embedded in xHTML annual reports | Financial-statement/reporting level; block-tagging for notes, granular tagging for primary statements. **Not** journal-entry level | No | No — standardizes tagging of statements already prepared under IFRS; does **not** map diverse local/non-IFRS charts into IFRS (that reconciliation happens upstream, outside the taxonomy) | Legally mandated across EU/EEA regulated-market issuers since FY2020 (Reg. (EU) 2019/815); IFRS Taxonomy referenced by many national regulators beyond the EU |
| **ISO 20022** | Metamodel + business-process/data-element dictionary for financial *messages* exchanged between institutions (payments, securities, FX, trade, cards) | Message/instruction level — closer to "transaction" than XBRL, but it is the format of the *instruction moving value*, not an internal ledger/CoA model | No native provenance/lineage model of the loss-ledger kind; standardizes what a payment message *contains*, not how either side's ledger books or reconstructs it | None — jurisdiction-agnostic *by design* at the messaging layer (one global schema), but silent on how either side classifies the amount into a local statutory chart | Extremely high network effects: SWIFT, FedNow, TARGET2 and most modern RTGS/real-time rails are migrating to or built on it; de facto global payment-messaging standard |
| **XBRL GL** (Global Ledger, XBRL International) | Generic XML/XBRL container for GL detail — journal entries, payables, receivables, inventory, payroll, purchasing, banking; "bridge from transactional standards to reporting standards" | **Transaction/journal-entry level** — the finest granularity of any standard reviewed, comparable to Kontablo's own claim | No. A static export/interchange container (its own working group called it "an alphabet without an agreed language"); no live constraint-checking, no agent-callable API, no forced accounting for untranslatable items | No — a flexible *container* that can hold any jurisdiction's chart, but supplies no ontology reconciling one jurisdiction's chart to another's | Low real-world uptake relative to core XBRL. Last confirmed formal Recommendation: 2015-03-25 (modular: COR/BUS/MUC/USK/TAF/SRCD). A 2016-12-01 draft toward a "2017" framework reads, by its own URL-encoded status, as a Public Working Draft — **not confirmed finalized to Recommendation** (flagged unverified below). Concrete adoption examples are narrow (e.g., Turkey's e-defter mandate) |
| **AICPA Audit Data Standards** | Voluntary US audit-data model: Base Standard (master/reference data) + General Ledger Standard (chart of accounts, source listings, trial balance, `GL_Detail` journal-entry lines) + subledger standards (Order-to-Cash, Procure-to-Pay, Inventory, Fixed Asset) | **Transaction/journal-entry level** (`GL_Detail` carries JE ID, account, debit/credit — line granularity) | No. Designed as a periodic *extract* an auditee hands an auditor (pipe-delimited flat files or XBRL GL), not a live pre-transaction query surface, and not a lineage-tracking system | No — US-centric; no statutory cross-jurisdiction mapping semantics | Real practitioner adoption in US audit-analytics tooling; voluntary, not legally mandated. Base + GL + O2C published July 2015; Inventory ~2017; Fixed Asset ~2017 |
| **OECD SAF-T** | National-tax-authority-facing export: chart of accounts, GL entries, customer/supplier master data, invoices/orders/payments/adjustments (v1.0, 2005); extended to inventory and fixed assets (v2.0, 2010, XSD schema) | **Transaction/journal-entry and invoice-line level** — again comparable to Kontablo's own granularity claim | No — a periodic batch file submitted to a tax authority/auditor, not a live pre-transaction constraint/query surface; no typed loss-ledger for untranslatable items | **Explicitly not solved at the OECD level.** OECD's own guidance states XML representation is "entirely a matter for revenue bodies," so each adopting country ships its *own* dialect (Portugal SAF-T PT, Poland JPK, Romania D406, Norway SAF-T Financial, France's non-conformant FEC variant) — N incompatible national variants, not one cross-jurisdiction ontology. Arguably the clearest real-world evidence of the exact gap Kontablo targets | Mandatory in a growing list of countries (Portugal 2008, Austria 2009, Luxembourg 2013, Lithuania 2019, Norway 2020/updated 2025, Romania phased 2022–2025, Denmark 2022, others) — real regulatory teeth, but fragmented by design |

## (b2) Source verification log

Format: Author/Org · Title · Year · URL · type · what it supports · how to
re-verify. **VERIFIED** = fetched/returned directly this session with usable
content. **PARTIAL** = fetch returned only limited/JS-blocked content;
corroborated via a second source. **SECONDARY** = not a standards body; used
only for color/adoption framing, never for a technical-scope claim.

| # | Source | Type | Supports | How to verify |
|---|---|---|---|---|
| 1 | EDM Council · *FIBO spec index* · n.d. (accessed 2026) · <https://spec.edmcouncil.org/fibo/> | Primary (standards body) | FIBO overview, governance (EDMC + OMG), OWL/W3C basis | Load URL; page states mission/governance directly |
| 2 | EDM Council · *GitHub: edmcouncil/fibo README* · accessed 2026 · <https://github.com/edmcouncil/fibo> | Primary (maintainer repo) | **VERIFIED.** Full module list (FND/BE/FBC/SEC/DER/LOAN/IND/CAE/BP/MD); confirms no GL/bookkeeping module | Load URL; README enumerates domains in a table |
| 3 | Object Management Group · *About the FIBO Foundations Specification v1.2* · Dec 2017 · <https://www.omg.org/spec/EDMC-FIBO/FND/About-FND/> | Primary (SDO) | **VERIFIED.** Formal version 1.2, formal adoption Dec 2017, copyright 2014–2017 OMG | Load URL directly |
| 4 | Object Management Group · *FIBO Foundations v1.2 PDF* · Dec 2017 · <https://www.omg.org/spec/EDMC-FIBO/FND/1.2/PDF> | Primary (SDO) | Formal spec document (referenced, not independently re-fetched this pass — URL came from OMG's own site search) | Resolve URL directly; cross-check against source #3 (same version/date) |
| 5 | Mike Bennett · "The financial industry business ontology: Best practice for big data" · *Journal of Banking Regulation* 14, pp. 255–268 · 2013 · DOI [10.1057/jbr.2013.13](https://doi.org/10.1057/jbr.2013.13) · <https://link.springer.com/article/10.1057/jbr.2013.13> | Peer-reviewed | Only peer-reviewed academic anchor for FIBO found this pass; history + theoretical grounding | Resolve DOI via Springer; issue number within vol. 14 not confirmed (`TODO`) |
| 6 | OMG Financial Domain Task Force · "Notes — Transaction and Accounting Semantics Overview" · 2011-11-28 · <https://www.omgwiki.org/OMG-FDTF/lib/exe/fetch.php?media=20111128_txn_semantics_notes.doc> | Primary but **informal working note**, not an adopted standard | **VERIFIED (fetched).** Substantiates the FIBO gap claim from inside FIBO's own standards body: notes the REA/double-entry "duality" is under-specified in FIBO's "Side" concept, and states "FIBO has the building blocks for such a reconciliation ... but there is work to be done" | Load .doc URL; treat as a 2011 informal note — flag its age (15 yrs old as of 2026) every time it is cited in-text; do not present as FIBO's current official position |
| 7 | XBRL International · "Extensible Business Reporting Language (XBRL) 2.1" · REC-2003-12-31, errata corrected through 2013-02-20 · <https://www.xbrl.org/specification/xbrl-2.1/rec-2003-12-31/xbrl-2.1-rec-2003-12-31+corrected-errata-2013-02-20.html> | Primary (SDO) | Core XBRL spec: facts/concepts/taxonomies/instance documents; reporting-level scope confirmed | Load URL; recommendation header states date/status |
| 8 | XBRL International · "Inline XBRL Part 1: Specification 1.1" · REC-2013-11-18 · <https://www.xbrl.org/specification/inlinexbrl-part1/rec-2013-11-18/inlinexbrl-part1-rec-2013-11-18.html> | Primary (SDO) | iXBRL basis for ESEF | Load URL |
| 9 | IFRS Foundation · "IFRS Accounting Taxonomy 2025 Published, Incorporating IFRS 18 and IFRS 19 Disclosures" · 2025 · <https://www.xbrl.org/news/ifrs-accounting-taxonomy-2025-published-incorporating-ifrs-18-and-ifrs-19-disclosures/> | Primary (announcement via SDO channel) | Current taxonomy edition name/content | Load URL; also cross-check <https://www.ifrs.org/issued-standards/ifrs-taxonomy/> (**PARTIAL** fetch — confirmed annual Q1 cadence and reporting-level scope, but page did not show the exact 2025 release date in the fetched excerpt — `TODO` pin exact date) |
| 10 | European Commission · Commission Delegated Regulation (EU) 2019/815 of 17 Dec 2018 (ESEF RTS, under Transparency Directive 2004/109/EC) · <https://eur-lex.europa.eu/eli/reg_del/2019/815/2023-01-19/eng> | Primary (legal instrument) | ESEF's legal basis, mandatory since FY2020; maintained/updated by ESMA (amended by (EU) 2019/2100 and subsequent annual taxonomy updates) | Load EUR-Lex URL (consolidated text, in-force version dated) |
| 11 | ISO · "ISO 20022-1:2026 — Financial services — Universal financial industry message scheme — Part 1: Metamodel," Edition 3, published April 2026, 154 pp., ISO/TC 68/SC 9 · <https://www.iso.org/standard/20022-1> | Primary (SDO) | **PARTIAL** — direct WebFetch of iso.org timed out/403'd repeatedly this session (likely bot-blocking); title/edition/date/page-count drawn from the ISO catalogue's own search-indexed metadata, corroborated independently by ISO/TC68 committee page and iso20022.org | Retry direct browser load of URL, or `ISO catalogue → 20022-1:2026`; TC68/SC9 catalogue at <https://www.iso.org/committee/6534831/x/catalogue/> |
| 12 | ISO 20022 Registration Authority · "The Registration Authority" · <https://www.iso20022.org/registration-authority> | Primary (RA page) | Confirms SWIFT S.C. operates RA services on behalf of ISO; governs the Financial Repository/data dictionary | Load URL directly |
| 13 | XBRL International, XBRL GL Working Group · "XBRL Global Ledger Taxonomy Framework 2015" · REC-2015-03-25 · <http://www.xbrl.org/int/gl/2015-03-25/gl-framework-REC-2015-03-25.html> | Primary (SDO) | **VERIFIED (fetched).** Confirms Recommendation status, date, modular structure (COR/BUS/MUC/USK/TAF/SRCD), entry-level granularity | Load URL directly |
| 14 | XBRL International · spec index entries for "XBRL Global Ledger Taxonomy Framework 2017" (PWD, 2016-12-01) · <http://www.xbrl.org/int/gl/2016-12-01/gl-framework-2017-PWD-2016-12-01.html> | Primary (SDO), **status UNVERIFIED past PWD** | Basis for flagging "2017 update possibly never finalized" in the table | Load URL and check for a later REC-dated successor; not done this pass — **do this before citing "2015 is the last Recommendation" as a hard claim in the paper** |
| 15 | Wikipedia · "XBRL GL" · accessed 2026 · <https://en.wikipedia.org/wiki/XBRL_GL> | **SECONDARY** | Adoption-status color only (Turkey e-defter; "expensive projects, sparse volume use" self-critique quoted from the working group) | Do not cite for technical scope — use #13 for that |
| 16 | AICPA Assurance Services Executive Committee · "General Ledger Standard (Audit Data Standards)" · published July 2015 (`auditdatastandards.gl.july2015.pdf`) · <https://www.aicpa-cima.com/resources/download/general-ledger-standard-audit-data-standards> | Primary (SDO-adjacent professional body) | **PARTIAL** fetch (page metadata only: title + July 2015 date + filename); GL_Detail/chart-of-accounts/trial-balance content confirmed via WebSearch snippet of the same AICPA family of pages | Download PDF directly from URL for full field-level content |
| 17 | Journal of Accountancy · news brief on Inventory Subledger Standard exposure/release · 2016–2017 · <https://www.journalofaccountancy.com/news/2016/may/audit-data-standards-proposed-201614459/> | **SECONDARY** (trade press) | Dating the Inventory (~2017) and Fixed Asset (~Dec 2017) subledger modules | Cross-check against AICPA's own download pages for each subledger standard |
| 18 | OECD Committee on Fiscal Affairs / Forum on Tax Administration · "Guidance for the Standard Audit File – Tax, Version 2.0" · April 2010 · <https://web-archive-storage.oecd.org/aemint-web-archive-prod/web-archive/cc/ccd3b76ffdaf3c1f3e185a390dba41be2876b0e826925278bbb3e62ad37442bf.pdf> | Primary (IGO) | **PARTIAL** — PDF fetched but returned mostly binary/encoded content; v2.0/April 2010 date and scope (chart of accounts → GL → inventory/fixed assets) corroborated via multiple independent secondary sources (Wikipedia, VATupdate, UNECE presentation) converging on the same date and scope | Re-fetch PDF with a dedicated PDF-text extraction pass (this session's generic WebFetch could not reliably parse it — saved locally at the path noted in the tool result, not committed to the repo) |
| 19 | Wikipedia · "SAF-T" · accessed 2026 · <https://en.wikipedia.org/wiki/SAF-T> | **SECONDARY** | Version-history cross-check (v1.0 May 2005, v2.0 April 2010) and country-adoption timeline | Do not cite alone for primary claims — corroborated against #18 and #20 |
| 20 | UNECE conference deck (OECD-authored) · "Standard Audit File – Taxation (SAF-T) / Standard Audit File – Payroll (SAF-P)" · 2019 · <https://unece.org/fileadmin/DAM/cefact/cf_forums/2019_Geneva/Conf_AccountAudit/PPT_1_3_OECD_SAF.pdf> | Primary (OECD-authored, third-party-hosted) | Corroborates v1.0/v2.0 dates and scope | Load URL |

**Practitioner/consultant sources found but deliberately NOT cited as
authoritative** (flagged so T1 doesn't accidentally promote them):
`finregont.com` / `bankontology.com` (Jurgen Ziemer) on FIBO↔XBRL
integration ("FinRegOnt imports FIBO … imports XBRL") — useful as
illustrative color that bridging FIBO and XBRL requires bespoke third-party
ontology work, but these are individual consultants' sites, not standards
bodies or peer review. If T1 wants this point, attribute it as "practitioner
commentary" explicitly, or drop it.

## (c) BibTeX

```bibtex
% =====================================================================
% DR4 — Financial ontologies/standards for machines (research/dr4_*.md)
% Real metadata only; TODO marks fields not independently confirmed this
% pass. Cross-reference research/dr4_financial_ontologies.md source log
% (entries #1-20) before using any entry below.
% =====================================================================

@online{fibo_edmcouncil,
  author       = {{EDM Council}},
  title        = {{Financial Industry Business Ontology (FIBO)}},
  organization = {EDM Council},
  url          = {https://spec.edmcouncil.org/fibo/},
  urldate      = {2026-07-24},
  note         = {Ontology specification index; OWL/RDF; co-published with OMG}
}

@techreport{fibo_omg_fnd_v12,
  author      = {{Object Management Group}},
  title       = {{Financial Industry Business Ontology (FIBO): Foundations}},
  institution = {Object Management Group},
  year        = {2017},
  type        = {Formal specification},
  note        = {Version 1.2, formally adopted December 2017. TODO: confirm
                 exact OMG formal document number (e.g. formal/YYYY-MM-DD);
                 not located this pass},
  url         = {https://www.omg.org/spec/EDMC-FIBO/FND/1.2/PDF},
  urldate     = {2026-07-24}
}

@article{bennett2013fibo,
  author  = {Bennett, Mike},
  title   = {{The financial industry business ontology: Best practice for big data}},
  journal = {Journal of Banking Regulation},
  year    = {2013},
  volume  = {14},
  number  = {TODO},
  pages   = {255--268},
  doi     = {10.1057/jbr.2013.13},
  url     = {https://link.springer.com/article/10.1057/jbr.2013.13}
}

@techreport{omg_fdtf_txn_semantics_2011,
  author      = {{OMG Financial Domain Task Force}},
  title       = {{Notes -- Transaction and Accounting Semantics Overview}},
  institution = {Object Management Group, Financial Domain Task Force},
  year        = {2011},
  type        = {Informal working note},
  note        = {2011-11-28; NOT a formally adopted OMG standard -- cited only
                 to show FIBO's own standards body identified the
                 FIBO-to-double-entry-bookkeeping reconciliation as unfinished
                 ("FIBO has the building blocks for such a reconciliation ...
                 but there is work to be done"). State its 2011/informal
                 status explicitly wherever cited in-text.},
  url         = {https://www.omgwiki.org/OMG-FDTF/lib/exe/fetch.php?media=20111128_txn_semantics_notes.doc},
  urldate     = {2026-07-24}
}

@techreport{xbrl21_spec,
  author      = {{XBRL International}},
  title       = {{Extensible Business Reporting Language (XBRL) 2.1}},
  institution = {XBRL International Inc.},
  year        = {2003},
  note        = {Recommendation 2003-12-31, with corrected errata through
                 2013-02-20},
  url         = {https://www.xbrl.org/specification/xbrl-2.1/rec-2003-12-31/xbrl-2.1-rec-2003-12-31+corrected-errata-2013-02-20.html},
  urldate     = {2026-07-24}
}

@techreport{ixbrl11_spec,
  author      = {{XBRL International}},
  title       = {{Inline XBRL Part 1: Specification 1.1}},
  institution = {XBRL International Inc.},
  year        = {2013},
  note        = {Recommendation 2013-11-18},
  url         = {https://www.xbrl.org/specification/inlinexbrl-part1/rec-2013-11-18/inlinexbrl-part1-rec-2013-11-18.html},
  urldate     = {2026-07-24}
}

@online{ifrs_taxonomy_2025,
  author       = {{IFRS Foundation}},
  title        = {{IFRS Accounting Taxonomy 2025}},
  organization = {IFRS Foundation},
  year         = {2025},
  note         = {Incorporates IFRS 18 and IFRS 19 disclosures. TODO: pin
                  exact publication date (Foundation states an annual Q1
                  release cadence; exact 2025 date not confirmed this pass)},
  url          = {https://www.xbrl.org/news/ifrs-accounting-taxonomy-2025-published-incorporating-ifrs-18-and-ifrs-19-disclosures/},
  urldate      = {2026-07-24}
}

@misc{esef_rts_2019_815,
  author  = {{European Commission}},
  title   = {{Commission Delegated Regulation (EU) 2019/815 of 17 December
              2018 supplementing Directive 2004/109/EC of the European
              Parliament and of the Council with regard to regulatory
              technical standards on the specification of a single
              electronic reporting format (ESEF Regulation)}},
  year    = {2018},
  note    = {As amended, incl. Delegated Regulation (EU) 2019/2100 (2019
             taxonomy update) and subsequent annual taxonomy-update
             amendments; maintained by ESMA under Transparency Directive
             2004/109/EC. Consolidated text below reflects the 2023-01-19
             in-force version},
  url     = {https://eur-lex.europa.eu/eli/reg_del/2019/815/2023-01-19/eng},
  urldate = {2026-07-24}
}

@standard{iso20022_part1_2026,
  author       = {{International Organization for Standardization}},
  title        = {{ISO 20022-1:2026 -- Financial services -- Universal
                    financial industry message scheme -- Part 1: Metamodel}},
  organization = {ISO/TC 68/SC 9},
  year         = {2026},
  edition      = {3},
  note         = {Published April 2026, 154 pp.; supersedes ISO 20022-1:2013.
                  Direct iso.org fetch was blocked this session (403/timeout)
                  -- metadata corroborated via ISO catalogue search index and
                  iso20022.org; re-verify by loading the URL in a browser
                  before final submission},
  url          = {https://www.iso.org/standard/20022-1},
  urldate      = {2026-07-24}
}

@online{iso20022_ra,
  title        = {{The Registration Authority}},
  organization = {ISO 20022 Registration Authority (RA services provided by SWIFT S.C., on behalf of ISO)},
  url          = {https://www.iso20022.org/registration-authority},
  urldate      = {2026-07-24}
}

@techreport{xbrl_gl_2015,
  author      = {{XBRL International, XBRL GL Working Group}},
  title       = {{XBRL Global Ledger Taxonomy Framework 2015}},
  institution = {XBRL International Inc.},
  year        = {2015},
  note        = {Recommendation, 2015-03-25; supersedes the 2007-04-17
                 Recommendation. Modular: COR/BUS/MUC/USK/TAF/SRCD. TODO:
                 confirm whether the 2016-12-01 Public Working Draft toward a
                 "2017" framework was ever finalized to Recommendation --
                 NOT confirmed in this research pass; treat 2015 as the last
                 CONFIRMED Recommendation only},
  url         = {http://www.xbrl.org/int/gl/2015-03-25/gl-framework-REC-2015-03-25.html},
  urldate     = {2026-07-24}
}

@online{wikipedia_xbrl_gl,
  title        = {{XBRL GL}},
  organization = {Wikipedia},
  note         = {SECONDARY source; used only for adoption-status framing
                  (Turkish e-defter example; working group's own "alphabet
                  without a language" self-critique). Do not cite for
                  technical-scope claims -- use xbrl_gl_2015 for that},
  url          = {https://en.wikipedia.org/wiki/XBRL_GL},
  urldate      = {2026-07-24}
}

@techreport{aicpa_ads_gl_2015,
  author      = {{AICPA Assurance Services Executive Committee}},
  title       = {{General Ledger Standard (Audit Data Standards)}},
  institution = {American Institute of CPAs (AICPA)},
  year        = {2015},
  note        = {Published July 2015 (source filename:
                 auditdatastandards.gl.july2015.pdf). Part of the modular
                 Audit Data Standards: Base Standard + General Ledger +
                 Order-to-Cash + Procure-to-Pay + Inventory (~2017) +
                 Fixed Asset (~Dec 2017)},
  url         = {https://www.aicpa-cima.com/resources/download/general-ledger-standard-audit-data-standards},
  urldate     = {2026-07-24}
}

@techreport{oecd_saft_v2_2010,
  author      = {{OECD Committee on Fiscal Affairs, Forum on Tax Administration}},
  title       = {{Guidance for the Standard Audit File -- Tax, Version 2.0}},
  institution = {OECD},
  year        = {2010},
  note        = {v1.0 published May 2005; v2.0 (April 2010) added
                 Inventory/Fixed Assets and moved the schema to XSD. No
                 global OECD v3.0 identified as of this research pass
                 (2026-07); adopting countries instead publish independent
                 localized/versioned variants (e.g., Portugal SAF-T PT since
                 2008, Poland JPK, Romania D406, Norway SAF-T Financial v1.3
                 from Jan 2025) -- itself evidence for the cross-jurisdiction
                 fragmentation gap cited in this note},
  url         = {https://web-archive-storage.oecd.org/aemint-web-archive-prod/web-archive/cc/ccd3b76ffdaf3c1f3e185a390dba41be2876b0e826925278bbb3e62ad37442bf.pdf},
  urldate     = {2026-07-24}
}

@online{wikipedia_saft,
  title        = {{SAF-T}},
  organization = {Wikipedia},
  note         = {SECONDARY source; used only for country-adoption-timeline
                  color. Version-history claims (v1.0/v2.0 dates, scope)
                  cross-checked against oecd_saft_v2_2010 and a 2019
                  OECD-authored UNECE conference deck},
  url          = {https://en.wikipedia.org/wiki/SAF-T},
  urldate      = {2026-07-24}
}
```

**Note for T1 integration:** the seed `references.bib` already has a `xbrl`
placeholder entry marked `TODO(T1/DR4)`. Replace it with `xbrl21_spec` (core
spec) and add `ixbrl11_spec` / `ifrs_taxonomy_2025` / `esef_rts_2019_815`
alongside it — the single generic `xbrl` entry conflates four distinct things
(the base spec, iXBRL, the IFRS taxonomy, and the EU legal mandate) that the
comparison table above treats separately on purpose.

## (d) The precise gap statement Kontablo fills

None of the reviewed standards combine transaction/journal-entry granularity
with a live, agent-callable, pre-transaction constraint-and-query interface,
a canonical ontology spanning many sovereign jurisdictions' charts of
accounts, and an explicit, typed, zero-silent-loss provenance guarantee.
FIBO and XBRL/ESEF/IFRS-Taxonomy encode rich machine-facing semantics but sit
*above* the entry level — instrument/contract/entity semantics or period-end
reporting facts, respectively — and neither attempts cross-jurisdiction
chart-of-accounts mapping. XBRL GL and OECD SAF-T/AICPA ADS do reach
entry-level granularity, but as static, post-hoc, batch-export formats with
no agent-native query surface and no unifying cross-jurisdiction ontology —
OECD's own SAF-T guidance explicitly delegates cross-country harmonization to
each revenue body, yielding incompatible national dialects rather than one
graph. Kontablo's gap is therefore not granularity in isolation — several
standards already have that — but the combination: a UUID-canonical,
multi-jurisdiction graph an autonomous agent queries *before* it posts (I3),
bounded by an ontology-as-constraint invariant (I1), with every untranslatable
item captured as a typed, counted record rather than a silent loss (I2) — a
combination absent from every standard reviewed here.

## (e) Fairness — where each standard is stronger than Kontablo, plus open gaps

**Where each standard beats Kontablo, stated plainly (no strawmanning):**

- **FIBO** — an order of magnitude richer semantic model of financial
  *instruments* (derivatives, corporate actions, securities lifecycle events)
  that Kontablo does not attempt to touch at all; a decade-plus,
  multi-bank consortium governance process (EDM Council members + OMG formal
  standardization) versus a single-author preprint; graph/OWL technology
  genuinely comparable to Kontablo's own graph-based approach, but applied one
  layer up the stack (domain/instrument semantics vs. bookkeeping/CoA
  resolution) — this makes FIBO genuinely complementary rather than
  competing, which is good for the paper's "complementary, not replacement"
  framing.
- **XBRL / ESEF / IFRS Taxonomy** — this is XBRL's decisive advantage and
  must be stated without hedging: *legally mandated* production use across
  tens of thousands of filers (SEC since 2009, ESMA/ESEF since FY2020), with
  a mature filing/validation ecosystem. Kontablo has zero regulatory mandate
  and zero production filings; its validation is synthetic. Any Related Work
  paragraph that doesn't concede this plainly will read as unbalanced to a
  reviewer who knows the space.
- **ISO 20022** — de facto global standard for interbank/payment messaging
  with massive, currently-accelerating network effects (SWIFT, FedNow,
  TARGET2 migrations). Kontablo doesn't touch settlement/messaging at all —
  it would sit beside/beneath it, the same relationship the hub already
  claims for AP2/A2A, not in front of it.
- **XBRL GL / AICPA ADS / OECD SAF-T** — the most important fairness point
  for this paper specifically: these three **already operate at entry-level
  granularity**, which undercuts any version of the gap statement that leads
  with granularity. SAF-T in particular carries real regulatory teeth
  (mandatory filing in a growing list of countries) that Kontablo entirely
  lacks; AICPA ADS is practitioner-validated in live audit-analytics tooling
  today, whereas Kontablo's entry-level claims (441-entry round-trip audit)
  are synthetic. The paper's gap claim must rest on the *live, agent-native,
  pre-transaction* property and the *cross-jurisdiction unification* property
  — not on "nobody else does entries."

**Open gaps / things to verify before citing in the paper:**

1. **XBRL GL post-2015 status is unresolved.** I could not confirm whether
   the 2016-12-01 Public Working Draft toward a "2017" Global Ledger
   framework was ever finalized to Recommendation. If the paper states "last
   Recommendation 2015," verify this first (source log #14) — a 2017+
   Recommendation would weaken (slightly) the "static/stalled" framing,
   though it would not change the core agent-native/cross-jurisdiction gap.
2. **ISO 20022 primary-page content is under-verified.** `iso.org` and
   `iso20022.org`'s main "about" page both failed to load directly this
   session (403/timeout, likely bot-blocking) on repeated attempts. The
   title/edition/date/scope claims are corroborated across multiple
   independent search results (ISO catalogue, ISO/TC68 committee page,
   iso20022.org Registration Authority page, SWIFT's own ISO 20022 pages) and
   I am confident in them, but a human should load
   `https://www.iso.org/standard/20022-1` directly in a browser before the
   paper goes to print, since this is likely to be a load-bearing citation.
3. **IFRS Accounting Taxonomy 2025's exact publication date** is not pinned
   (only "Q1 2025, incorporating IFRS 18/19" is confirmed) — low priority,
   easy to fix with one more direct fetch of ifrs.org if the exact date
   matters for the citation.
4. **The OMG FDTF 2011 working note (source #6) is fifteen years old and
   informal** — it is the *best available* evidence that FIBO's own
   standards body identified the transaction-semantics gap, but it is not a
   current, formally adopted OMG position, and I did not find a more recent
   (2020s) OMG/FIBO statement reconfirming or superseding it. Cite it as
   historical evidence of a design gap acknowledged in FIBO's own community,
   not as FIBO's current official self-assessment. If T1 wants a stronger
   or more current version of this specific claim, that would need another
   targeted search pass (not done here — out of this DR4 pass's scope, but
   flagged for a possible DR-follow-up).
5. **AICPA ADS field-level detail (`GL_Detail` schema) was only partially
   fetched** (page metadata confirmed; full PDF field list not pulled this
   pass) — fine for the comparison table above, but pull the actual PDF
   before writing any sentence that quotes specific field names.
6. **No claim above should be read as asserting SAF-T, XBRL GL, or AICPA ADS
   are "dead" or "failed."** SAF-T in particular is actively expanding
   (Romania's phased 2022–2025 rollout, Norway's 2025 v1.3 update). The
   accurate, defensible framing is "real regulatory adoption, but
   fragmented/single-jurisdiction and batch-oriented," not "abandoned."
