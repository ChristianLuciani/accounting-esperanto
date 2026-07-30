# Real-Data Validation Plan — Round 2

**Status: PREREGISTERED 2026-07-18.** The hypotheses and falsification thresholds in §3 and §7 are fixed as of this commit. Do not edit them once Phase 1 data collection begins — record any change as a dated, visible addendum instead of a silent edit. This is what makes the result falsifiable rather than narratable after the fact.

Kontablo is a graph-based universal accounting ontology validated, as of v0.2.1, on a **synthetic** matrix: `scripts/mass_consolidation_v2.py` resolves 75 entities across 68 jurisdictions with 97.3% deterministic resolution. This document plans the round-2 companion validation — the same architecture, tested against data Kontablo did not generate: real, publicly filed financial statements.

## 1. Why this round exists: the circularity finding

A significant share of the 97.3% figure is partly circular. `build_entities()` in `mass_consolidation_v2.py` derives Tier-1 synthetic entities from `core/schemas/level3_accounts.yaml`'s own `local_codes` table, and the Tier-1 resolver looks accounts up in that same table. The Tier-2 (name-only), frontier (crypto/carbon/Zakat), and deliberately-malformed entities are genuinely hard and not circular — but the component that inflates the headline number is close to "can the resolver find codes it was built from," which is close to tautological.

This is not a flaw to hide; it is exactly why a real-data round has scientific value. `research/coverage_benchmark/README.md` already names this gap in its own "Roadmap to a real-corpus run" — this document is that roadmap, executed.

**Round 2 does not replace the synthetic validation.** It answers a different, harder question: does the resolver survive contact with account data it never saw, sourced independently of Kontablo's own mapping tables? A lower number here is not a failure of the project — it is the measurement the synthetic experiment structurally cannot produce.

## 2. Domain scope decision: public sector is claimed (decided 2026-07-18)

Kontablo explicitly claims public-sector / government accounting (IPSAS) as an in-scope domain, not just corporate IFRS. Concretely, this round validates — and if it clears the threshold in §3, promotes from draft to active — the existing `localizations/industries/public_sector_ipsas.yaml` extension (39 mappings, UUID range `A0000000-...`, drafted 2026-03-27), which is currently **not** wired into `core/harness/ontology.py`'s resolver and is listed in `localizations/industries/README.md` only under "Planned Extensions (v0.3 Roadmap)" despite the file already existing in substantial draft form. §8 corrects that index entry in this same PR — leaving the two out of sync is exactly the stale-status failure mode this project has hit before.

Until H5 (§3) clears its threshold against real data, all public-facing wording must describe public-sector coverage as **drafted, not yet empirically validated** — the same discipline `CLAUDE.md` already applies to the 97.3% figure.

## 3. Pre-registered hypotheses and falsification thresholds

Each hypothesis is scored independently; a low score on one does not invalidate the others — it maps where the semantic coverage boundary actually sits, which is the harness's own stated design point (`docs/papers/drafts/sections/harness_architecture.tex`: "locus of error relocated to the semantic coverage boundary").

| # | Hypothesis | Measured on | Supports thesis | Partial / defines boundary | Weakens thesis |
|---|---|---|---|---|---|
| **H1** | Standardized-taxonomy alignment: real `us-gaap:*` / `ifrs-full:*` face-statement tags resolve to the correct Kontablo node | EDGAR + ESEF, temporal holdout (see §6) | ≥ 75% weighted | 50–75% | < 50% |
| **H2** | Company-specific taxonomy extensions are correctly escalated, never silently force-mapped | Same corpora, extension-tagged facts only | 100% of extensions escalate (`resolved=false`) | — | Any extension silently mapped with high confidence |
| **H3** | Real, uncurated, name-only local captions (no shared code or tag standard) resolve via Tier 2/3 | UK Companies House abbreviated/micro-entity accounts | ≥ 60% | 30–60% | < 30% |
| **H4** | Reconstructed subtotals from real filed line items match the entity's own reported subtotals | Companies House case study (§9), tolerance = rounding only | ≥ 90% of subtotal lines reconcile | 70–90% | < 70% (investigate ingestion bug per §7 before concluding anything about the ontology) |
| **H5** | Public-sector / IPSAS-GFS crosswalk resolves real government fiscal data | IMF GFS + Eurostat COFOG, temporal holdout | ≥ 70% weighted | 40–70% | < 40% — keep public-sector wording qualified as unvalidated |

These thresholds are proposed by this plan, not unilaterally final — flag any number here you'd set differently before merging; they are cheap to change now and expensive to change after Phase 1 data collection starts.

## 4. Source taxonomy by normalization distance

The core design insight: sources with the cleanest data-reuse licenses (EDGAR, GLEIF) are the *least* diagnostic (they test taxonomy alignment, which upstream filers already did the hard work of standardizing); the most diagnostic source (native local captions/codes) has the most ambiguous redistribution rights. This asymmetry drives the reproducibility model in §7.

| Distance | What it tests | Sources | Format | Redistribution |
|---|---|---|---|---|
| **1 — Standardized global taxonomy** | Taxonomy alignment (the easy case) | [SEC EDGAR Financial Statement Data Sets](https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets) (`us-gaap:*`), [filings.xbrl.org](https://filings.xbrl.org/docs/api) ESEF filings (`ifrs-full:*`) | EDGAR: flat bulk files (`num.txt`/`sub.txt`/`tag.txt`/`pre.txt`). ESEF: Inline XBRL instance documents (need a parser — Arelle or equivalent) | EDGAR is U.S. public domain. ESEF filings are the issuers' own public disclosures; cite filings.xbrl.org's terms before vendoring extracted facts in bulk |
| **2 — Standardized taxonomy + real company extensions** | Semantic coverage boundary / correct escalation behavior | Same EDGAR/ESEF corpora, isolating non-base-taxonomy elements | Same as above | Same as above |
| **3 — Real free-text captions, no shared code/tag standard** | Tier 2/3 name-based resolution on real, uncurated language — the closest public proxy to "local chart, local language" | [UK Companies House Accounts Data Product](https://download.companieshouse.gov.uk/en_accountsdata.html) (abbreviated/micro-entity iXBRL — minimal tagging, plain captions) | Bulk iXBRL ZIP, confirmed | **No explicit reuse license published** ([analysis](https://osm.mathmos.net/notes/companies-house-data.html)) — do not vendor raw filings; use the content-addressed manifest model in §7 |
| **4 — Real native coded local chart, exercised against a real filed trial balance in that code system** | The literal strong claim: local code → Kontablo UUID, on real data | **None identified.** Companies that publish statutory accounts publicly report in captions or standardized tags, not their internal chart-of-accounts codes; internal TBs are not public. | — | — |

**Distance 4 is an honest gap, not an oversight.** No free public source was found that gives a real trial balance keyed by a real local chart-of-accounts code (e.g., a real SKR04 or PUC-Colombia coded ledger). This stays an open backlog item — see §10 — rather than something round 2 pretends to solve.

Government/public-sector sources (for H5), evaluated separately since their granularity differs (fiscal aggregates by function, not entity-level trial balances):

| Source | Gives | Format | Access |
|---|---|---|---|
| [IMF Government Finance Statistics (GFS/COFOG)](https://data.imf.org/en/Resource-Pages/IMF-API) | National government revenue/expense by function, ~190 countries | SDMX / CSV / JSON | API confirmed this session |
| [Eurostat Government Finance Statistics](https://ec.europa.eu/eurostat/databrowser/bulk?lang=en) (`gov_10a_exp`, COFOG/ESA2010) | EU general-government expenditure by function | SDMX, bulk download | Confirmed this session |
| [UK Whole of Government Accounts](https://www.gov.uk/government/collections/whole-of-government-accounts) | Real IFRS/FReM-based consolidated public-sector statement, one country, annual | **PDF only — confirmed this session, no structured bulk found** | Case-study anchor only, not bulk-ingestible; do not plan an automated pipeline against it |

IMF GFS and Eurostat COFOG are the primary H5 sources; UK WGA is a single manually-checked sanity anchor, not a pipeline input.

## 5. Existing ingestion contract (nothing here changes)

Neither `ConsolidationEngine` (`core/engine.py`) nor the harness resolver needs modification. Both already consume a fixed row shape:

- `mass_consolidation_v2.py` style: `{code, name, nature, amt}`
- `core/engine.py` `LocalEntry`: `{code, name, debit, credit, nature, intercompany_with}`

All round-2 work is ingestion: new parsers that translate real filings into this existing shape, exactly the pattern `consolidation_v1_initial_run.py` already uses for its four simulated ERP CSV formats — except the round-2 sources are real filings, not synthetic CSVs.

## 6. Gold standard and accuracy protocol

Real data gives coverage and determinism for free (did the resolver find *a* mapping, did it stay deterministic). It does **not** give correctness for free — "resolved" is not "resolved right." Protocol:

1. **Stratified random sample** of resolved facts per source (target n≥300 per H1/H3, more if variance is high).
2. **Independent double-labeling** — two labelers (may include an LLM labeler and a human, or two independently-instructed LLM passes) assign the "correct" Kontablo node without seeing the resolver's answer.
3. **Inter-annotator agreement** (Cohen's κ) reported; disagreements adjudicated by a third pass before scoring.
4. **Train/test split is temporal, not random**, to avoid the same leakage risk as the crosswalk itself (§7): build the `us_gaap_tags.yaml` / `gfs_cofog_tags.yaml` crosswalks from filings up to a cutoff date, score only against filings after it, including any tags/elements that did not exist in the training window.
5. **Baseline comparators**, so the number is falsifiable rather than free-floating: (a) naive English-label string match, (b) Kontablo's determinstic resolver, (c) optionally an unconstrained LLM given the same fact with no ontology constraint — to make principle #5's claim (constrained determinism prevents hallucinated UUIDs; an unconstrained model can propose non-existent ones) an empirical result instead of an assertion.

## 7. Reproducibility and licensing model

The pinned FX table (`core/harness/fx.py`) guarantees the synthetic experiment regenerates byte-for-byte. Public registries are living systems — they update, republish, and occasionally correct filings — so round 2 cannot use the same mechanism. Two regimes, by source license:

- **Clean-license sources (EDGAR, GLEIF, IMF, Eurostat — public domain / CC0 or equivalent):** vendor the downloaded snapshot (or deposit it as a Zenodo data artifact with its own DOI, a pattern this project already uses for the preprint). `results.json` regenerates offline from the frozen snapshot. As with FX, round 2 never fetches live inside the CI claims-evidence gate — download once, freeze, commit, run against the frozen copy.
- **Ambiguous-license sources (Companies House, any national registry without a published reuse license):** do **not** redistribute the raw filings. Commit a **content-addressed manifest** instead — exact accession number/URL + SHA-256 of the downloaded file + retrieval date — plus Kontablo's own derived output (the mapping and the aggregate statistics, which are original work). Anyone can reproduce by re-downloading the named accession and checking the hash, without this repo redistributing data it may not have rights to redistribute.

**Tooling license note:** robust iXBRL parsers (e.g., Arelle) are GPL-licensed. Acceptable as a research/ingestion-script dependency not distributed inside the BSL/Apache product surface — confirm this explicitly before pinning it as a hard dependency of anything under `core/`.

## 8. Correction bundled into this PR: `localizations/industries/README.md`

The industries index currently lists "Public Sector / Government" only under §"Planned Extensions (v0.3 Roadmap)" and marks UUID range `A0000000-...` as "🔲 Reserved," even though `public_sector_ipsas.yaml` already exists as a substantial draft (39 mappings). This PR corrects the status to **"🚧 Drafted, not wired into the resolver, validation pending (see this document)"** — accurate as of today, promotable to "✅ Active" only after H5 clears its threshold and the extension is actually loaded by `core/harness/ontology.py`. This is a one-table-row factual correction bundled here because it is the same subject matter this document opens; it does not touch any other file's claims.

## 9. Known ingestion pitfalls (budget engineering time for these)

Real filings are presentation trees, not clean trial balances. Two correctness bugs are near-certain if not guarded against:

- **Subtotal double-counting.** An XBRL presentation tree includes both a subtotal and its children. Summing both inflates totals. Must walk the presentation/calculation linkbase and count leaves only, never aggregates.
- **Sign convention.** `us-gaap` calculation linkbases use a `weight`/`negatedLabel` convention that can invert the sign relative to the engine's debit/credit convention. A silent sign-mapping bug breaks the assets = liabilities + equity check without raising an error — this is precisely what H4's subtotal-fidelity check (§3) is designed to catch.

## 10. Tier A design (H1, H2, H5)

1. **A1 — EDGAR / us-gaap (start here — cleanest license, flat files, no XBRL-instance parsing needed).** Bulk-download `num.txt`/`sub.txt`/`tag.txt`/`pre.txt` for a training window and a held-out window (§6). Filter to face-statement facts via `pre.txt`. Count real tag frequency — itself a deliverable: a real frequency distribution that can feed `research/coverage_benchmark`'s own stated "real-corpus" roadmap item. Build `core/schemas/us_gaap_tags.yaml` (curated crosswalk, ~200–400 tags covering the Pareto tail) from the training window only. Score against the held-out window per H1/H2.
2. **A2 — ESEF / ifrs-full.** No new crosswalk needed — `level3_accounts.yaml` already carries an `ifrs_tag` field per node. The work here is extraction: sample 50–100 filings across several countries via the filings.xbrl.org API, parse with an XBRL instance parser, extract the tag set, score against the same `ifrs_tag` field.
3. **A5 (H5) — GFS/COFOG public-sector crosswalk.** Build `core/schemas/gfs_cofog_tags.yaml` (GFS/COFOG function-and-economic-type code → Kontablo `A0000000-...` node) from IMF GFS + Eurostat COFOG bulk data, same temporal-holdout discipline as A1.

None of this touches `core/harness/`. Each is a standalone script producing a `results.json`; only after a crosswalk has cleared its threshold should wiring it into the live resolver be considered as a separate, later decision.

## 11. Tier B design (H3, H4) — a case study, not a statistical benchmark

Real internal subsidiary trial balances are not public anywhere identified (distance 4, §4). The best available proxy is UK Companies House: subsidiaries of multinationals are required to file individual statutory accounts.

1. **Mechanical candidate selection (anti-cherry-picking, fixed before looking at data):** use [GLEIF Level 2 "who owns whom"](https://www.gleif.org/en/lei-data/access-and-use-lei-data/level-2-data-who-owns-whom) to select the largest IFRS filer (by any objective, pre-stated criterion, e.g. filing recency) with ≥3 LEI-registered UK subsidiaries that file individually.
2. Extract each subsidiary's iXBRL statutory accounts (Companies House bulk). Map each face-statement line to a Kontablo node via Tier 2/3 (§3, H3) — most abbreviated/micro-entity accounts do not use a shared coding standard.
3. Build `LocalEntry` rows (§5 shape), run through `ConsolidationEngine` **unmodified**.
4. Score H4: does the reconstructed subtotal (current assets, total assets, assets = liabilities + equity) match what the subsidiary itself reported? This is an external, auditable check that does not depend on invisible intercompany eliminations — unlike comparing against the parent's consolidated IFRS 8 segment disclosure, which was considered and rejected as a verification anchor: segments are management-defined (often by customer geography, not entity) and the elimination gap is unbounded and invisible, so a mismatch there would not be attributable to Kontablo either way.
5. Document explicitly, in the experiment's README and any derived public wording: this validates **structural and mapping fidelity on real filed data**, not an audited consolidation. Never describe it as reconciling to the group's real consolidated result — that would be the exact epistemic-standards violation `CLAUDE.md` already prohibits for the synthetic experiments.

## 12. MVP sequence

| Phase | What | Distance / hypotheses | Effort |
|---|---|---|---|
| 1 | A1 — EDGAR us-gaap crosswalk + held-out benchmark | 1–2 / H1, H2 | Medium |
| 2 | A5 — GFS/COFOG public-sector crosswalk | H5 | Medium (reuses A1's methodology) |
| 3 | A2 — ESEF ifrs-full sample | 1–2 / H1, H2 | Medium-high (needs iXBRL parsing) |
| 4 | B — Companies House case study | 3–4 / H3, H4 | High, n=1 case study |
| Backlog | Distance-4 native coded local chart against a real TB; India MCA (per-filing fee, no free bulk); Argentine/Turkish IAS 29 hyperinflation issuers — reachable via **EDGAR 20-F filers** (foreign private issuers filing IFRS in Inline XBRL, mandatory since periods ending ≥ 2021-06-15), which is a better path than scraping CNV Argentina PDFs (no bulk XBRL repository found there) | 4 / narrative-only | Deferred, named explicitly rather than silently dropped |

Phase 2 (public-sector) is sequenced early, not deferred, per the §2 domain-scope decision — it reuses A1's exact methodology (bulk structured data, build-crosswalk-on-train/score-on-holdout) rather than requiring new technique.

## 13. Deliverables and file layout (for the execution phase, not built in this PR)

```
research/experiments/tag_resolution_v1/        # A1 + A2 (H1, H2)
research/experiments/public_sector_gfs_v1/      # A5 (H5)
research/experiments/consolidation_v3_real/     # B (H3, H4)
core/schemas/us_gaap_tags.yaml                  # new crosswalk (data only)
core/schemas/gfs_cofog_tags.yaml                # new crosswalk (data only)
scripts/real_data/download_edgar.py
scripts/real_data/download_esef_sample.py
scripts/real_data/download_gfs.py
scripts/real_data/download_companies_house.py
scripts/real_data/resolve_real_facts.py         # standalone; does not import into core.harness
```

Each experiment directory gets its own `results.json`, a README stating exact source URL(s), retrieval date, and file hash (per §7), and — where a headline number becomes public-facing — an update to the claims-evidence table in `CLAUDE.md` in the same PR, per this project's existing non-negotiable rule.

## 14. Explicitly out of scope for round 2

- Wiring any new crosswalk into the live `core/harness/` resolver — that is a separate decision to make only after a crosswalk clears its threshold.
- Distance-4 native local-chart validation — no source identified; stays a named backlog item (§12), not silently dropped.
- India MCA21 (per-filing fee blocks free bulk access) and Argentina CNV bulk XBRL (no public repository found) — superseded by the EDGAR 20-F path for the hyperinflation narrative specifically.
- Any change to the existing synthetic 97.3% figure or its citable surfaces (`abstract.tex`, `README.md`, `CITATION.cff`, `.zenodo.json`) — round 2 is additive, not a replacement, until and unless a real-data figure is deliberately chosen to supersede it.

## Sources cited in this plan (retrieved 2026-07-18)

- [SEC EDGAR Financial Statement Data Sets](https://www.sec.gov/data-research/sec-markets-data/financial-statement-data-sets)
- [SEC EDGAR Application Programming Interfaces](https://www.sec.gov/search-filings/edgar-application-programming-interfaces)
- [SEC iXBRL mandate for IFRS foreign private issuers](https://www.clm.com/foreign-private-issuer-alert-sec-mandates-xbrl-for-ifrs-companies-and-use-of-hyperlinks-in-exhibit-index/)
- [filings.xbrl.org API documentation](https://filings.xbrl.org/docs/api)
- [UK Companies House — Free Accounts Data Product](https://download.companieshouse.gov.uk/en_accountsdata.html)
- [Companies House bulk data licensing analysis (no explicit reuse license found)](https://osm.mathmos.net/notes/companies-house-data.html)
- [GLEIF Level 2 Data: "Who Owns Whom"](https://www.gleif.org/en/lei-data/access-and-use-lei-data/level-2-data-who-owns-whom)
- [IMF Data API / SDMX](https://data.imf.org/en/Resource-Pages/IMF-API)
- [Eurostat bulk download](https://ec.europa.eu/eurostat/databrowser/bulk?lang=en)
- [Eurostat government expenditure by function (COFOG), dataset `gov_10a_exp`](https://ec.europa.eu/eurostat/databrowser/view/gov_10a_exp/default/table?lang=en)
- [UK Whole of Government Accounts collection (PDF only, confirmed)](https://www.gov.uk/government/collections/whole-of-government-accounts)

---

# Addendum A — execution operationalizations (dated 2026-07-30)

**Status: recorded BEFORE any hypothesis was scored.** The plan above is
pre-registered and is not edited. This addendum records decisions the plan did
not specify, plus one factual correction to the plan itself. Each entry states
the decision, why it was needed, and which direction it could bias the result.

## A.1 Correction: the public-sector extension has 19 mappings, not 39

§2 and §8 both state that `localizations/industries/public_sector_ipsas.yaml`
carries "39 mappings". It carries **19** (`yaml.safe_load(...)["mappings"]`).
All YAML blocks summed — 19 mappings + 4 aggregation rules + 3 validation rules
+ 5 country-specific entries — total 31, so 39 does not correspond to any
reading of the file. This is the project's documented stale-count failure mode,
caught here on first contact with the file. The plan text is left as written;
this addendum is the correction of record. H5 is therefore measured against a
**19-node** drafted extension.

## A.2 H2: what "silently force-mapped" means operationally

H2 requires that company-specific extensions "escalate (`resolved=false`)" and
is weakened by "any extension silently mapped with high confidence". The plan
does not define *silently*. Operationalization:

- A **Tier-1 hit on an extension is a violation.** Tier 1 asserts exact code
  identity at confidence 1.0; an issuer-invented tag cannot have one, so this
  would mean the crosswalk was contaminated with non-standard codes.
- A **Tier-2 keyword hit is not a violation and is not silent.** Tier 2 is the
  designed name-based path, reports confidence 0.85 (not 1.0), and names the
  exact rule that fired (`tier2:<node>:<keyword>`), so the decision is auditable
  and reviewable rather than hidden.
- Tier-2 extension hits are reported as their own line, never folded into either
  bucket. Hiding them would overstate H2; calling them violations would penalize
  the resolver for doing what Tier 2 is documented to do.

## A.3 Gold sample is drawn from the whole population, not only resolved facts

§6.1 says "stratified random sample of resolved facts". Sampling only resolved
facts measures **precision** and is structurally blind to misses — a resolver
that escalates nearly everything would score perfectly. The sample is therefore
drawn from the entire holdout population so all four outcomes are scorable
(correct / wrong node / missed / false positive). **Direction of bias: this can
only lower the measured accuracy, never raise it.**

## A.4 Primary population for H1 is monetary facts

About 8% of real EDGAR standard face-statement facts are share counts,
per-share amounts, percentages or ratios (the taxonomy's own declared
`datatype`). A chart of accounts maps monetary ledger balances and structurally
has no node for "weighted average diluted shares outstanding"; counting those
against it would understate coverage for a reason unrelated to the ontology.

The monetary subset is the primary population. The exclusion is **deterministic**
— it reads the taxonomy's declared datatype, with no per-tag discretion — and the
full population is reported alongside it so the exclusion stays visible and
quantified. **Direction of bias: raises the reported number relative to scoring
all face-statement facts; both are published.**

## A.5 Gold labels are three-way, not two-way

Real face statements are presentation trees and carry **subtotals** (`Assets`,
`LiabilitiesAndStockholdersEquity`, `OperatingIncomeLoss`) alongside leaf
accounts. Kontablo's 30 core nodes are all leaves; aggregation is computed
through rollup lenses and never stored as a node.

Calling a subtotal "outside Kontablo's scope" would be false (Kontablo does
represent it, as a derived rollup); mapping it to a leaf node would also be
false and would double-count against that leaf. So the gold vocabulary is:

| label | class | correct resolver behavior |
|---|---|---|
| `<node id>` | leaf | resolve to that node |
| `AGGREGATE:<lens>` | aggregate | escalate |
| *(empty)* | out_of_scope | escalate |

Aggregate and out-of-scope tags are scored as **correct escalations** when the
resolver declines them, and as **false positives** when it maps them anyway.
Each class is also reported separately, so the share of real face-statement
fact volume that is aggregate rather than leaf is visible rather than buried.

## A.6 EDGAR inventory is collapsed across taxonomy versions

EDGAR keys presentation rows by `(tag, version)`, so one tag appears once per
taxonomy vintage. Uncollapsed, this would let the same tag be drawn twice into
the gold sample, and would report ~97% of holdout tags as "unseen in train"
purely because the version string advanced. The hypotheses concern a *tag*
resolving, not a tag-vintage pair, so the version dimension is summed away. An
element declared an issuer extension in any vintage is treated as an extension
throughout, so H2 cannot be softened by a later vintage relabelling it.

## A.7 Independence of the two labeling passes is limited

§6.2 permits "two independently-instructed LLM passes". Both passes here are the
same model family under different instructed reasoning orders (tag-first vs
node-first with default-to-no-match). This is **weaker independence than two
unaffiliated human CPAs**: correlated errors are possible and Cohen's kappa
overstates true independence. This caveat travels with any public wording of the
resulting accuracy figure and is recorded inside `gold/agreement.json` itself.
