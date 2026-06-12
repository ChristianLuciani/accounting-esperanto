# Adversarial Pre-Publication Review — Kontablo preprint v1.8 + repository

**Reviewer posture:** hostile-by-instruction. Simultaneously: a skeptical accounting-information-systems referee, a Hacker News commenter with the LaTeX source open, a reproducibility auditor, and a security/code reviewer. Every claim was presumed wrong until the repo proved it.

**Scope:** `docs/papers/drafts/kontablo_preprint_modular.tex` + `sections/` + `figures/` (compiled PDF, 48 pp.), all four citable surfaces, `api/`, `logic/`, `core/`, `scripts/`, `connectors/`, `tests/`, CI, bibliography (web-verified), and the two generating scripts in the CLAUDE.md claims table.

**Reviewed at:** 2026-06-12, branch `claude/adversarial-review`, base commit `9d52a90`.

---

## 0. Reproduction results (what the repo proved)

Every generating command in the claims–evidence table was re-run in a clean environment:

| Command | Published claim | Reproduced? |
|---|---|---|
| `python -m pytest tests/` | suite green | ✅ 44 passed, 2 skipped (LLM-integration, properly `skipif`-gated). Note: CLAUDE.md's table says "23 passed" — stale, in the safe direction. |
| `python scripts/mass_consolidation_v2.py` | 195/60/56; 75 entities; 68 jurisdictions; 366 entries; 97.3%; 25/30 nodes; 4 escalations | ✅ all eight numbers reproduce **exactly**, and the regenerated `results.json`/`per_entry.csv` are byte-identical to the committed artifacts |
| `python scripts/coverage_benchmark.py` | ~94% / ~99% (87.3% / 97.1% strict) | ✅ 94.2 / 98.8 (87.3 / 97.1) reproduce exactly, byte-identical output |

The engine-side claims discipline is real and is the strongest thing about this project. The failures below are concentrated in (a) the metadata surfaces, (b) the first half of `evaluation.tex`, (c) prose that asserts unimplemented cryptography in the present tense, and (d) one materially misdescribed citation.

---

## BLOCKERS

### B1. `CITATION.cff:10` — "23 jurisdictions" on a canonical citable surface

> **The attack:** "Your citation file — the artifact GitHub and Zenodo render as *the* canonical description of this work — says the ontology is validated across **23 jurisdictions**. Your abstract says 195. Your own CLAUDE.md names exactly this drift as the project's documented failure mode, and it has now survived a third release-prep pass. Why should I believe any number in this paper if the four files you yourselves designated as load-bearing don't agree?"

**Evidence:** `CITATION.cff:10` — "…across 23 jurisdictions through a Tree-to-Graph Universal Bridge…". `abstract.tex`, `README.md` correctly say 195/60/56/75/68.

**Remediation:** rewrite to the current 195-sovereign / 60-statutory / 56-Tier-1 wording. Must ship in the same PR as B2 (one-number-four-surfaces rule).

### B2. `.zenodo.json:3` — "23 global jurisdictions" AND "10 entities in 9 countries"

> **The attack:** "The metadata that will mint your DOI contradicts the paper it describes by 172 jurisdictions and understates the validation matrix by 65 entities — twice in one sentence. This is the literal scholarly record and it is wrong on the day you flip the Zenodo toggle."

**Evidence:** `.zenodo.json` description: "…empirically validated across 23 global jurisdictions…" and "…mass-consolidation engine across 10 entities in 9 countries…". Release Step 8 *is* the Zenodo toggle, so this is release-gating by definition.

**Remediation:** rewrite description to match abstract v1.8 (195/60/56; 75 entities, 68 jurisdictions; 4 hyperinflation cases).

### B3. `evaluation.tex:3-6` — the 10-entity/9-country "initial run" is unreproducible and implies real ERP data

> **The attack:** "You claim the simulation 'ingested raw, unmapped trial balances from 10 distinct entities across 9 countries' and that 'each subsidiary ledger was exported from a different source ERP (ERPNext, Zoho Books, Odoo, SAP B1).' Where are these exports? `research/experiments/` contains exactly one consolidation experiment — `consolidation_v2` — and a sheaf toy. There is no committed artifact, no generating command, no fixtures. Either the ledgers exist and you're hiding the data, or they don't and 'exported from SAP B1' is fiction. 'Empirically validate', 'high-fidelity', and 'real-world utility' in the same paragraph make it worse: your own CLAUDE.md forbids describing synthetic validation as real-world data."

**Evidence:** `sections/evaluation.tex:3` ("To empirically validate… high-fidelity… ingested raw, unmapped trial balances from 10 distinct entities across 9 countries"); `:6` ("Each subsidiary ledger was exported from a different source ERP… To validate Kontablo's real-world utility"). No corresponding artifact anywhere in the repo — direct violation of claims–evidence rule 3 ("no claim without a command") and the validation-honesty anti-pattern. **Contamination spreads downstream:** `evaluation.tex:309` claims "Tier~3 semantic fallback was invoked more frequently" for VN/SA — but the committed, reproducible run *never invokes Tier 3 at all* (it escalates instead, by design, `mass_consolidation_v2.py:8-10`); that observation can only come from the uncommitted initial run. Same for the "complexity 7/10" scores.

**Remediation (decision required from the author, not surgically fixable):** either (a) commit the initial-run artifact + generating script and keep the text, with "synthetic" stated plainly and "exported from X ERP" corrected to whatever actually happened (ERP *formats* simulated?); or (b) cut/rewrite the initial-run narrative to a brief historical note and make the reproducible v2 run the sole evidentiary basis, deleting every downstream sentence that depends on the initial run (Tier-3 frequency claims, complexity scores). Option (b) is cleaner and costs ~half a page.

### B4. ICAEW citation — sample size overstated ~14×

> **The attack:** "You cite 'ICAEW's May 2026 survey of **500 UK accounting firms**' for the 68%/83%/71% figures. The actual source is ICAEW's *Evolution of Mid-Tier Accountancy Firms* research, which surveyed **leaders from 35 mid-tier firms** in February–March 2026. The percentages are real; the evidentiary base you assign them is invented, fourteen times larger than reality, and stripped of the 'mid-tier' qualifier that bounds its generalizability. In a paper whose thesis is claims–evidence traceability, this is disqualifying until fixed."

**Evidence:** `kontablo_preprint_modular.tex:114` ("Survey of 500 UK Firms") and `sections/labor_market.tex:109` ("survey of 500 UK accounting firms"). Verified against ICAEW's own coverage ("research surveyed leaders from 35 firms in February and March 2026"; 68%/83%/71% figures confirmed): icaew.com "AI: are junior accountants worried about roles?" (Jun 2026); accountancytoday.co.uk (2026-05-26).

**Remediation:** correct to "ICAEW's 2026 mid-tier firms study (35 firm leaders surveyed, Feb–Mar 2026)" and soften the "practitioner-level evidence" weight accordingly. The figures themselves survive.

---

## MAJOR

### M1. Unimplemented cryptography asserted in the present tense

> **The attack:** "Section 'governance' says audit fields 'are cryptographically hashed and sealed as part of the transaction block,' making post-facto tampering 'impossible… without triggering a hash mismatch.' Section 'agentic economy' says every write 'requires the transaction payload to be signed by the initiating agent's private key' and promises ledger states 'validated using cryptographic signatures and consensus rules.' I grepped your implementation: there is **no hashing or signature code anywhere** in `api/`, `logic/`, `core/`, or `connectors/` — the only `hashlib` in the repo checksums bibliography PDFs. Your own CLAUDE.md says cryptographic implementation status is 'not started.' This is vaporware narrated as architecture."

**Evidence:** `sections/governance.tex:80` (hashed/sealed/"impossible"); `sections/agentic_economy.tex:11` ("consensus rules"), `:36` ("requires… signed by the initiating agent's private key"); `sections/abstract.tex:6` + `harness_architecture.tex:226` ("immutable audit trail"). Grep of all Python for `hashlib|sha256|signature|private_key`: only `scripts/research/verify_bibliography.py` and unrelated extraction scripts.

**Remediation:** move every such sentence to explicit design-intent voice ("the specification requires…", "v0.x implements append-only logging; cryptographic sealing is roadmap") or future tense. "Impossible" must go. This is a wording pass, not a research change — but it touches ~5 locations including the abstract ("immutable inconsistency audit trail").

### M2. "Eliminates the classical accounting hallucination class" — contradicted by the served code path

> **The attack:** "The abstract's flagship claim is that the Deterministic Boundary Library 'eliminates the classical accounting hallucination class at the harness level' — the agent cannot propose a UUID outside the graph. Then I read `logic/agents/semantic_matcher.py:62-75`: the Tier-3 path splits the raw LLM response on `|` and posts `uuid.strip()` **directly** into the mapped result at a fixed 0.8 confidence, with no check that the UUID exists in the ontology, and a bare `except: pass` swallowing provider errors. The REST endpoint your own ERPNext connector calls is served by this code. The hallucination class you claim to have eliminated is alive in your reference implementation."

**Evidence:** `logic/agents/semantic_matcher.py:62-75` (unvalidated LLM UUID accepted); contrast `api/src/services/mapping.py:113-114`, which *does* validate via `get_account()` — the two pipelines diverge. Abstract and `.zenodo.json` both carry the "eliminates" claim.

**Remediation:** add the membership check (fall to the escalation path if the UUID is not in the KB) and remove the bare `except`. Alternatively (or additionally) scope the paper claim: "eliminates … *when the boundary check is enforced*; the reference implementation enforces it at [pipeline X]". The fix is ~5 lines; the claim is only honest after it ships.

### M3. CI claims–evidence gate never checks the four citable surfaces — which is exactly how B1/B2 survived

> **The attack:** "Your README brags about a CI gate that fails on claim drift. The gate (`.github/workflows/ci.yml`) asserts `results.json` matches the published numbers — and it does — but no step ever greps `CITATION.cff`, `.zenodo.json`, `README.md`, or `abstract.tex` for those numbers. `tests/test_coverage_claim.py` checks all four surfaces, but only for the 94/99 coverage figures and retired phrases, not for 195/75/68/56. The gate is green while your DOI metadata is wrong by 172 jurisdictions: you gated the artifact and forgot to gate the claim."

**Evidence:** `.github/workflows/ci.yml:34-70` (engine numbers asserted, correctly); `tests/test_coverage_claim.py:72-92` (surface scan limited to coverage figures; its `"94"` bare-substring assertion would also pass on "1994").

**Remediation:** extend `test_coverage_claim.py` (or add a CI step) asserting that all four surfaces contain "195", "75 entities", "68", "56" and do **not** contain "23 jurisdiction", "10 entities", "9 countries". Tighten the `"94"` match to a `~94%`-shaped pattern.

### M4. The synthetic "trial balances" do not balance — and the consolidated balance sheet is out of balance by USD 5.4M

> **The attack:** "You call the inputs 'synthetic trial balances' and print a 'CONSOLIDATED BALANCE SHEET'. A trial balance, by definition, balances. Yours don't: summing your own committed `results.json`, Assets = 14.75M but Liabilities + Equity + (Rev − Exp) = 20.18M — the consolidated statement violates the accounting equation by **USD 5,433,962**. The validation harness for a *universal accounting standard* produces financial statements that fail the first invariant every bookkeeping student learns. Also: you describe this as 'consolidation' but perform no intercompany eliminations — it is FX-normalized aggregation."

**Evidence:** `research/experiments/consolidation_v2/results.json` (`consolidated_usd` sums as above); `mass_consolidation_v2.py:413-425` — per-account `BASE_USD` face values are assigned independently with no debit=credit constraint per entity. The sheaf toy (`research/experiments/kirchhoff_hodge_toy/`) actually demonstrates intercompany elimination — but it is not wired into this harness.

**Remediation:** either (a) generate balanced entity trial balances (add an equity plug per entity — one line of code) and note that balance validation is exercised, or (b) rename the artifact honestly ("account-balance panels", "FX-normalized aggregation") and state explicitly that double-entry balancing and intercompany elimination are out of scope for this harness. (a) is strictly better and cheap; whichever is chosen, the headline numbers must be regenerated and re-pinned in CI.

### M5. The 97.3% deterministic-resolution figure is an internal-consistency check, not a mapping-accuracy result — and the paper buries the disclosure in a table caption

> **The attack:** "Where does the denominator come from? 310 of 366 entries are 'Tier-1 exact' — but those entries were *generated by iterating over the ontology's own `local_codes` table* (`build_entities`, `mass_consolidation_v2.py:243-268`) and then 'resolved' by looking them up in an index built from the same table. Tier-1 success is guaranteed by construction, modulo collisions. The Tier-2 entries are names you wrote, matched against keyword rules you wrote. The 4 escalations are names you deliberately wrote to be out-of-vocabulary (Bitcoin, carbon credits, Zakat, Sonderposten). 97.3% is the score of an exam where the examiner wrote both the questions and the answer key. Feed it one real ledger export — 'A/R Trade', 'Acct 1100-01-DEPT7', a typo'd 'Recievables' — and Tier-2's substring matching collapses. You disclose the generation method in *one table caption* (`evaluation.tex:252-253`)."

**Evidence:** as cited; `per_entry.csv` confirms all 4 escalations are the authored frontier entries. No noise/perturbation/adversarial-input experiment exists anywhere in the repo.

**Steelman of the defense (which the paper should make explicitly, in body text, not caption):** the run *is* honestly framed as exercising the pipeline mechanics + the ontology's own data quality (and it genuinely caught 4 real code collisions — the corrective-loop result is the most defensible finding in the section). What it is **not** is evidence about resolution rates on real-world ledgers, and the abstract's "the deterministic tiers resolve 97% of entries" reads as exactly that.

**Remediation:** (1) promote the construction disclosure from caption to body text with a named limitation paragraph; (2) re-scope the abstract sentence ("on a synthetic matrix constructed from the ontology's committed code sets, the deterministic tiers resolve 97% …"); (3) commit a perturbation experiment (typos, prefixed codes, abbreviations) as labeled future work or as a falsifiable robustness number — even a bad number reported honestly beats this attack.

### M6. The injected-error catalog is detected 8/8 *by construction*

> **The attack:** "Three of your five 'deterministic accounting invariants' (statement class, VAT direction, equity/liability — `cra_validate`, `mass_consolidation_v2.py:199-222`) only execute on entries pre-labeled `forced_id` — i.e., the alarm system is told in advance which entries are the burglars. And every injected name contains the exact substring its check greps for ('IVA Acreditable (input)' → the check looks for 'input'/'acreditable'). 8/8 detection of attacks designed to be detected is a demo, not a detection rate. What is the CRA's recall on *mislabeled but plausible* proposals — 'Sundry debtors' forced to a payables node?"

**Evidence:** as cited. The paper (`evaluation.tex:270-277`) reports "No injected error passed silently" without stating the forced-only scoping or the keyword coupling.

**Remediation:** state the construction honestly in the paper ("the catalog demonstrates that each invariant class is *mechanically wired*, not a detection-rate measurement"); ideally add negative controls (correct mappings that must NOT flag — partially present) and at least one adversarial case the keywords *miss*, reported as a known false negative. The nature and liquidity checks (1–2) run unconditionally and are genuinely stronger — say so and lean on them.

### M7. PwC AI Jobs Barometer — edition conflation and an unsupported qualifier

> **The attack:** "You cite 'PwC AI Jobs Barometer (2025)… across 15 countries… 56% wage premium for roles requiring AI-complementary skills, and a 7.5% year-on-year growth in postings requiring such skills in finance-adjacent functions.' Three problems: the 56% figure is from the **2025** Barometer (≈1 billion ads, six continents); '15 countries' describes the **2024** edition (whose premium was 25%); and PwC reports the 7.5% growth for AI-skill postings **across all sectors** — 'in finance-adjacent functions' is your addition, not theirs. Also, PwC measures jobs *requiring AI skills*, not 'AI-complementary skills' — a distinction your recomposition argument leans on."

**Evidence:** `sections/labor_market.tex:88-92`; `kontablo_preprint_modular.tex:116`. Verified against pwc.com 2025 Global AI Jobs Barometer press releases.

**Remediation:** cite one edition consistently, drop or source the finance-adjacent qualifier, and align "AI skills" terminology. (BLS 2025a/b, IMF 2026/004, OG-RAG EMNLP 2025, Mäkelä & Stephany arXiv:2412.19754, Robert Half 73-days figure, and both load-bearing arXiv papers — 2603.04663 incl. the 1.2% figure, and 2604.00555 incl. IPKE, the Vietnamese 2× lift, and the 1,800-run design — were all verified accurate. See §Citations verified below.)

### M8. Category-theory and sheaf claims: asserted, never constructed — and decoupled from the implementation

> **The attack:** "You claim the import/export streams 'are exactly' Spivak's data-migration functors Σ_F ⊣ Δ_F, making the round trip 'canonical rather than arbitrary' (`mathematical_foundations.tex:29-48`). But you never define the schema categories, never construct F, and never verify the adjunction — and you *can't*, as stated: your own export step 'selects a primary reporting dimension and discards the secondary analytical edges' (`:62-64`), i.e., it depends on a **choice**, which is precisely what 'canonical' forbids. One subsection later, the CRA's Inconsistency Flag 'is not a heuristic warning but the detection of… a non-zero cohomology class' (`:79-81`) — yet the implemented flag is a substring check on account names (`mass_consolidation_v2.py:179-224`). No sheaf, stalk, or restriction map is ever instantiated in the pipeline. This is decoration wearing the costume of foundation."

**Evidence:** as cited. **Mitigating fact the paper inexplicably hides:** `research/experiments/kirchhoff_hodge_toy/` contains a real, tested, numpy-only cellular-sheaf computation (δ⁰, Moore–Penrose reconciliation, H⁰/H¹ dimensions, intercompany scenario) with an exemplary epistemic header ("mechanics validation, NOT a proof of the general theorem"). The preprint never cites it.

**Remediation:** (1) downgrade "is exactly… canonical" to "is structurally analogous to functorial data migration; a full categorical treatment is future work" — or actually construct F and prove the adjunction for a minimal chart pair; (2) replace "is the detection of a non-zero cohomology class" with "is *designed to play the role of*…", and cite the toy experiment as the current state of formal validation; (3) the Cover's-theorem passage is already correctly hedged as analogy — use that same register throughout.

### M9. Reference implementation bugs a hostile reviewer can demo live

Four findings from the code audit, each one `curl` away from a take-down comment:

- **`api/src/services/mapping.py:93-103`** — every CSV code match returns hardcoded `asset.current.receivables` at confidence 0.8 (comment admits "Placeholder"). Cash maps to Trade Receivables, "80% confident."
- **`core/engine.py:173-178` + `api/grpc/server.py:198,213`** — `target_currency` is decorative: everything converts to USD and is then *labeled* as the requested currency. Request EUR, get USD numbers stamped EUR.
- **`api/src/services/consolidation.py:31-39` + `core/engine.py:170`** — unknown FX pairs silently default to rate 1.0. A GBP subsidiary consolidates at parity with no warning, from the component whose thesis is verifiability.
- **`api/rest/main.py:22-30`** — `KnowledgeBase()` startup failure is caught and logged, leaving `kb` undefined and turning every request into a NameError-500: the structural ghost of the documented "Norway YAML" incident. Fail fast instead.

**Remediation:** fix or honestly degrade each (validate-or-reject, never silently default). CLAUDE.md already concedes the implementation is "prototype-grade" — the paper survives these only if the README/paper say so where the endpoints are described, and silent-wrong-number paths (FX 1.0, hardcoded receivables) are removed before anyone demos the API. These are pre-publication because the repo goes public with the paper.

### M10. `LICENSING.md` contradicts the shipped licenses and carries its own stale number

**Evidence:** (a) `LICENSING.md:60`: "the real moat is first-mover citability, **23-jurisdiction depth**…" — stale count in the public licensing rationale. (b) The Apache-exception table lists only `connectors/erpnext/`, but `connectors/odoo/LICENSE` is also Apache 2.0 (correctly, per the May 28 policy) — the governing document understates its own grants; `README.md:301` likewise mentions only ERPNext. (c) `.zenodo.json` says BSL converts "2030-06-01"; `LICENSE` Change Date is 2030-05-28 — two public dates for one legal event.

**Remediation:** add the Odoo row, fix the count, reconcile the date (LICENSE governs).

### M11. Abstract is 599 words and carries an internal numeric error in the evaluation table

- The abstract (599 words, ~1.5 pages with the etymology footnote) is roughly **2×** what SSRN renders comfortably and what referees will read; the statutory-chart enumeration (26 chart names) belongs in the body. AI-discoverability (CLAUDE.md GEO rules) argues for a strong first 100 words, not for length.
- `evaluation.tex:239`: "Escalated to human via CRA: 4 (**1.5%**)" — 4/366 = **1.1%** (and `results.json` says 1.1). Trivial, but it is a wrong number inside the flagship claims table, in a paper about claims–evidence traceability.

---

## MINOR

1. **`abstract.tex:6` / `evaluation.tex:209` — "a dozen written scripts."** In the abstract, the phrase floats free and reads as "shell scripts." The data contain ~12 *languages* but only ~5 *writing systems* (Latin, Cyrillic, Arabic, Hangul, Greek). Say "twelve languages across five writing systems" — accurate and stronger.
2. **IAS 29 framing.** The harness applies a parallel-rate FX override (`rate_override`, `mass_consolidation_v2.py:271-287`). IAS 29 proper requires CPI restatement of non-monetary items *before* translation. The paper's "dual-rate hyperinflation stress tests" hedge is mostly honest, but `evaluation.tex` should state explicitly that index restatement is not exercised — a financial-reporting referee will check.
3. **`docs/papers/drafts/kontablo_paper_v01.md`** — a superseded v1.75 draft with "23 jurisdictions" / "20+ jurisdictions" / "9 regulatory environments" sits in the same directory as the canonical preprint *with GEO-optimized frontmatter* — an AI crawler will cheerfully cite the wrong numbers. Per the no-deletion rule: add a SUPERSEDED banner, strip the SEO frontmatter, or move under `docs/archive/`. Same for `docs/manuals/kontablo_explainer.md:47` ("23 jurisdictions") and `EXECUTION_STATUS.md:17` ("SYSCOHADA (12 países OHADA)" vs the 17 stated everywhere else).
4. **`logic/agents/semantic_matcher.py:74-75`** — bare `except Exception: pass` (also part of M2). **`tests/microsaas/test_mapping_api.py:77-88`** — `test_france_pcg_codification`'s real assertion is commented out; it can only fail on a 500 (the banned "test that can't fail" class).
5. **`api/grpc/server.py:59`** — deterministic Tier-2 keyword resolution is reported on the wire as `MATCH_SEMANTIC_AI` ("closest proto enum"). The determinism-first protocol labels its deterministic tier as AI in machine-readable output; add a `MATCH_KEYWORD_RULE` enum.
6. **`api/src/services/ai.py:1`** — the deprecated, EOL `google.generativeai` SDK is imported unconditionally at module import time; the *deterministic* API dies at import if the dead SDK breaks. Lazy-import it (or migrate to `google-genai`). `api/src/main.py:34-40`: CORS `allow_origins=["*"]` with `allow_credentials=True` is spec-invalid. No `timeout=` on any `requests` call in either connector.
7. **`requirements.txt` is unpinned.** The reproducibility guarantee currently depends on what pip resolves on the day; pin (or constrain) for the v0.1.0 tag.
8. **Float money throughout**, with inconsistent rounding (`core/engine.py:190-191` rounds pre-accumulation; `consolidation.py:47-48` post). Fine for a prototype that *says* it's a prototype; pick one discipline.
9. **Coverage benchmark — residual is author-defined.** The legs are written directly in ontology vocabulary, so only labels the author chose to call `residual.*` can be uncovered; the dominant tail weight (20/month miscellaneous) is an explicit assumption. Provenance disclosure in `transaction_frequency.yaml` is exemplary, and sensitivity is decent (doubling the misc tail to 40/month only moves 94.2% → 93.2%; even 60/month gives 92.3%) — but that sensitivity sweep exists only in this review. Commit it (`--misc-weight` flag + table in the benchmark README) and cite it; it converts a vulnerability into a defense.
10. **`ontology.tex:39`** — "18 Universal Accounts: **Mandated** for all enterprise profiles" sits in tension with the carefully honest near-universal framing at `:67` (94–98%). Use "near-universal core" consistently; "universal/mandated" is the phrasing the June audit retired.

## NIT

- `mass_consolidation_v2.py:235` uses `"uk"` (ISO 3166-1 is `GB`); `JCCY` dict defines `"gr"` twice (`:392`, `:397`).
- CLAUDE.md claims table: "23 passed, 2 skipped" — actual 44 passed, 2 skipped.
- PDF is 48 pages; internal references to "47 pp." (if any circulate) should be checked at camera-ready.
- arXiv:2603.04663 bib entry still reads "Authorship to be confirmed at camera-ready" — the paper exists and is retrievable; resolve before release, not after.
- Author-name order for arXiv:2604.00555: source lists "Thanh Luong Tuan"; check Vietnamese name-order convention before camera-ready ("Luong Tuan, T." may invert family/given).
- `tests/test_coresponsibility.py` still prints banners/emoji (it does assert now — the June 2026 fix held).

---

## Citations verified accurate (no action)

| Source | Checked claim | Verdict |
|---|---|---|
| arXiv:2603.04663 (VeNRA) | exists; deterministic fact ledger; hallucination "compressed to 1.2%" | ✅ verified (title, March 2026 submission, 1.2% figure) |
| arXiv:2604.00555 (Luong Tuan & Sanyal) | exists; IPKE; Vietnamese domains 2× ontology lift; 1,800 runs; FAOS | ✅ verified on every load-bearing claim |
| IMF Notes 2026/004 (Davidovic & Tourpe) | authors, title, the "deterministic logic vs probabilistic AI" quote, URL | ✅ exact |
| OG-RAG, EMNLP 2025 (Sharma, Kumar & Li) | venue; +55% fact recall; +40% correctness | ✅ exact (EMNLP 2025 main, pp. 32962–32981) |
| BLS 2025a/b | +5% accountants 2024–34; 124,200 openings; −6% clerks, automation-attributed | ✅ exact |
| Mäkelä & Stephany (arXiv:2412.19754) | 12M US vacancies; ~2× complementary-skill requirement | ✅ verified |
| Robert Half 2026 | CPA roles 73 days to fill, +41% | ✅ figures confirmed (pin the primary URL in the bib) |

## Repository: verified clean

- **Determinism principle held everywhere checked:** the `tax_compliance.py` June-2026 fix is intact (overrides key on `country` + `local_name`, never on model text); no control flow keyed on LLM free-text found in `logic/`, `api/`, `scripts/`, `connectors/` (M2 is an acceptance gap, not text-keyed branching).
- **Secrets hygiene clean:** no tracked `.env`/`.infisical.json`; `.gitignore` covers them; no live keys (only documented placeholders and `api_key="k"` test fixtures).
- **YAML hardening real:** bool-country fallback in `logic/knowledge_base.py:29-32` plus `tests/test_localization_integrity.py` in CI.
- **CI engine assertions correct:** the expected block matches all eight published numbers; fail-on-drift philosophy intact.
- **gRPC honesty matches CLAUDE.md:** deterministic RPCs implemented over `core/engine.py`; LLM-dependent RPCs return `UNIMPLEMENTED` with honest messages.
- **`impact.tex` SME scenario** is correctly framed as illustrative hypothesis with stated assumptions. **`ontology.tex:67`** carries the honest 94–98% near-universality formulation. **Benchmark provenance headers** (`transaction_frequency.yaml`, `coverage_benchmark.py`) are a model of how to label synthetic data.

---

## Verdict: **not ready — publish after blockers** (and it is close)

**The honest argument.** This project's differentiator is that it preaches claims–evidence traceability and then mostly practices it: every headline number regenerates byte-identically from committed commands, the synthetic-data disclosures in the research artifacts are better than the field's norm, the determinism principle survives a hostile grep, and the secrets/license hygiene is clean. Most papers in this space could not survive §0 of this review. **But** the four blockers are each individually disqualifying for *this* paper specifically, because each one is a violation of the standard the paper itself proposes: two citable surfaces carry numbers wrong by an order of magnitude on DOI-minting day (B1, B2); the evaluation section opens with an unreproducible run described in real-data language (B3); and one citation invents a 500-firm survey out of a 35-leader study (B4). A hostile reviewer doesn't need to attack the methodology — they only need to quote the paper's own rules back at it.

The MAJORs divide into two groups. M1–M4 and M9–M11 are wording/code fixes achievable in days. M5, M6, and M8 are framing corrections — the difference between "97.3% deterministic resolution" (sounds like field accuracy) and "97.3% deterministic resolution on a matrix constructed from the ontology's own committed code sets" (what was measured). The work does not need new experiments to be publishable; it needs the prose lowered to the altitude of the evidence — which is exactly the discipline the paper advocates.

**Recommended path:** fix B1+B2+M3 in one PR (surfaces + gate, same change set); decide B3 (option b recommended); fix B4, M1, M2, M7, M11 as a wording/bugfix pass; re-run both generating scripts and pytest; then release. M5/M6/M8 framing edits fit in the same pass if the ≤2-sessions scope rule is respected; everything else is post-publication backlog that should NOT delay v0.1.0.

*This review was produced adversarially on purpose. Findings are deliberately phrased as the hostile reviewer would phrase them; severity reflects damage to credibility at launch, not moral weight.*
