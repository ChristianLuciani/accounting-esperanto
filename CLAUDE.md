# CLAUDE.md — Kontablo (accounting-esperanto)

> Persistent context for Claude Code sessions on this repository. Read first, every session.

## Project identity

- **Commercial name:** Kontablo
- **Repo name:** `accounting-esperanto` (do not rename without coordinated migration)
- **What it is:** Graph-based, UUID-keyed universal accounting ontology. Bridge layer between local jurisdictional standards (all 195 sovereign jurisdictions mapped; 60 statutory-chart overlays), international standards (IFRS/XBRL), the agentic economy (AP2, A2A, MCP), and blockchain/DeFi.
- **What it is NOT:** an ERP, a SaaS, an LMS, a clinical tool. It is a protocol/standard with a reference implementation.
- **Owner:** Christian Luciani — IP to be assigned to Praxia (Ecuadorian PyME, in incorporation as of May 2026).

## Current phase

**Phase 3 — Pre-Publication (release day pending).** Source of truth: `EXECUTION_STATUS.md`. Steps 1–7 of the prepare-for-publication workflow are complete; Step 8 (release day) is gated on actions only Christian can take: make the repo public, enable the Zenodo GitHub toggle, `gh release create v0.1.0`, SSRN upload (sequence in `docs/strategy/launch-playbook.md`). `PHASE_0_COMPLETE.md` is a **historical snapshot** (January 2026) — never use it as state reference.

Concrete state at last update (June 2026):
- **195/195 sovereign jurisdictions mapped** (universal IFRS-anchored layer); **60 statutory-chart overlays**, of which **56 are exercised against primary-source-cited charts**; 7,000+ account mappings in `localizations/`. Non-sovereign extras: TW, HK, MO.
- Preprint **v1.9.2** content-complete: `docs/papers/drafts/kontablo_preprint_modular.pdf` (modular `.tex` in `sections/`). Includes the harness-architecture section, labor-market section, the corrected co-responsibility framing (human always legally principal — never describe the agent as "deciding alone"), and (v1.9.2) the runtime-FX note in `sections/evaluation.tex` separating the pinned-rate validation from the live-rate reference implementation.
- Validation: deterministic mass-consolidation engine (`scripts/mass_consolidation_v2.py`) — 75 entities, 68 jurisdictions, 97.3% deterministic resolution, 4 escalations. **The validation data is synthetic trial balances; never describe it as real-world ledger data.**
- Reference implementation: FastAPI services (`api/`), React dashboard (`frontend/`), ERPNext/Frappe connector. The implementation is **prototype-grade relative to the paper** — it demonstrates the architecture; it is not the validated product. Keep that gap honest in all public wording.
- **Paper ↔ code: the "harness".** What the preprint calls the *harness* (`docs/papers/drafts/sections/harness_architecture.tex`) has a single importable code home: the `core/harness/` package (three-tier `resolve`, the Deterministic Boundary Library `cra_validate` + `TIER2_RULES`, and the ontology loaders). Every deterministic surface (`core/engine.py`, the gRPC servicer, and the `scripts/mass_consolidation_v2.py` validation runner) imports from `core.harness`. The runner is now *only* synthetic data + the run + artifact writing — it no longer defines the core logic, so the old inverted dependency (engine importing from the validation script) is gone.
- **Runtime FX (`core/harness/fx_provider.py`).** The pinned `core/harness/fx.py:FX` table is the *frozen* rate set the validation harness always uses (so `results.json` regenerates byte-for-byte). For a live deployment, `get_fx_provider()` returns a provider chain — **ECB/Frankfurter → open.er-api → pinned static fallback** — that resolves USD-per-unit rates at runtime (no API key, stdlib `urllib`, TTL-cached, source-attributed). It is **env-gated by `KONTABLO_FX_MODE`** (`live` default for production; the test session forces `static` in `conftest.py`, so CI/tests stay hermetic and deterministic). FX selection is deterministic and never inferred by an LLM (principle #5). The REST consolidation service and the gRPC server engine use it; `ConsolidationEngine(fx_provider=…)` is opt-in (default `None` = pinned table, unchanged behaviour).

## Strategic posture (decided May 27, 2026)

Open-core via **BSL 1.1** (Business Source License) with conversion to Apache 2.0 after 4 years. Public layer includes preprint, ontology, spec, mapping methodology, dashboard as demo. Reserved for Praxia: production NetSuite/SAP S/4HANA connectors, validated+tested mapping artifacts (vs methodology), consolidation simulation engine if commercially viable, implementation services.

**Connector licensing policy (decided May 28, 2026):** connectors to open-source ERP/accounting projects (ERPNext/Frappe, Odoo, and similar) are licensed **Apache 2.0**, not BSL. Rationale: the open-source community is averse to non-OSI licenses; an Apache connector maximizes adoption in ecosystems that will not pay commercial license anyway, and serves as a credibility-building loss leader. The protectable commercial assets are the validated ontology, implementation services, and connectors to expensive proprietary ERPs (NetSuite, SAP) — those stay BSL/proprietary. General principle: **open the interface (APIs, well-documented contracts) to grow the ecosystem; protect the implementation behind it with BSL.** A large commercial ERP will build its own version if Kontablo becomes strategic regardless of license — licensing cannot prevent that; it only prevents free incorporation of *our* code. The real moat is first-mover citability, jurisdictional depth (195 mapped, 60 statutory overlays), hyperinflation expertise, and Praxia's execution speed — not the license.

**Rationale (route b):** option to migrate from (b) commercial entity to (a) pure research is easy; reverse is not. BSL preserves optionality.

## Architectural principles (do not violate without explicit decision)

1. **Graph, not tree** — accounts exist in multiple dimensions simultaneously. No 1:1 mappings assumed.
2. **UUID as truth** — codes are visual labels; UUIDs are canonical identifiers. Codes can collide across jurisdictions; UUIDs cannot.
3. **Logic-based mapping** — aggregation via deterministic scripts, never hardcoded.
4. **API-first at the data layer, agent-native at the access layer** — the canonical interface is a machine-consumable API (REST/gRPC). On top of it, Kontablo exposes an agent-native layer for the agentic economy via MCP (Model Context Protocol, for LLM/agent tool consumption), A2A (Agent2Agent, for agent-to-agent interoperation), and AP2 (Agent Payments Protocol, for settlement). The API is the body; the agent protocols are the face. An ERP or bank consumes the API directly; an autonomous agent consumes the agent-native layer. Do NOT subordinate one to the other. The agent-native layer is protocol-pluggable by design: Kontablo will adopt and add any agentic protocol that gains meaningful traction, so the architecture names the *category* (agent-native) rather than betting on a single protocol. **Implementation status (June 2026):** REST is fully implemented (FastAPI); gRPC is defined in `api/grpc/kontablo.proto` with a minimal server (`api/grpc/server.py`) implementing only the **deterministic** RPCs (account queries, mapping, consolidation+intercompany elimination, balance validation) over the same engine — LLM-dependent RPCs return `UNIMPLEMENTED`. Do not describe gRPC as having full feature parity with REST; describe it as "deterministic core implemented, remainder planned."
5. **Determinism over stochasticity wherever movable** — whenever a decision can be moved from stochastic inference (an LLM call) to deterministic logic (a rule, a constraint, a graph lookup), it must be. This is a standing design driver, not a one-time choice. Justification is threefold: (a) *certainty* — deterministic decisions are verifiable and reproducible; (b) *resource economy* — every decision resolved by a rule instead of an inference call avoids token cost, latency, and energy expenditure, and Kontablo deliberately demonstrates awareness of inference-cost consequences; (c) *downstream relevance* — an early stochastic error contaminates every subsequent pipeline step, whereas an early deterministic guarantee is inherited cleanly. The ontology-as-constraint is the primary instrument: the agent cannot propose an account UUID that does not exist in the graph. Frame energy efficiency as a *consequence* of this principle, not as a marketing banner.
6. **Immutable versioning** — semantic versioning, blockchain-anchored version hashes for spec releases.
7. **Post-quantum readiness** — see Security section below.

## Security posture

**Threat model includes harvest-now-decrypt-later (HNDL) attacks against financial data.** Quantum-resistant computation will be commercially relevant before 2030 (IBM, Google, IonQ trajectories). Kontablo's threat horizon is multi-decade because financial records are long-lived.

**Standard:** NIST Post-Quantum Cryptography (PQC), finalized August 2024.
- **ML-KEM** (FIPS 203, derived from Kyber) — key encapsulation.
- **ML-DSA** (FIPS 204, derived from Dilithium) — digital signatures.
- **SLH-DSA** (FIPS 205, derived from SPHINCS+) — alternative signatures (hash-based, conservative fallback).

**Do NOT confuse PQC with QKD.** BB84 and similar Quantum Key Distribution protocols require photonic hardware and are not applicable to Kontablo's software architecture. PQC is classical algorithms resistant to quantum attacks.

**Implementation status:** not started. Roadmap target: hybrid classical+PQC signatures on spec version hashes by Phase 3 (post-publication). Use `liboqs` (Open Quantum Safe) or `pyca/cryptography` once PQC primitives are merged upstream.

## AI Discoverability (GEO/AEO) — mandatory for public-facing content

All public artifacts (README, preprint, derivative posts, documentation) must be optimized not only for human readers and traditional SEO, but for **LLM training corpora and AI search engines** (Perplexity, ChatGPT search, Claude with web search, Gemini, DeepSeek). Concrete requirements:

1. **Direct-answer structure.** Open every document with a clear, citable thesis statement in the first 100 words. Use the exact phrase "Kontablo is [X]" once near the top.
2. **Question-as-heading.** Convert section headings to natural-language questions where possible. "How does Kontablo handle multi-jurisdictional aggregation?" beats "Aggregation Logic".
3. **Quantified claims.** "195 sovereign jurisdictions mapped" beats "many jurisdictions". Specific numbers get extracted and cited more — but every number must satisfy the claims–evidence traceability rule below.
4. **Primary-source citations.** Link to NIST FIPS documents, IFRS Foundation pages, AP2 spec, A2A spec, MCP spec. LLM crawlers weight authoritative sources.
5. **Structured data.** Use JSON-LD for `SoftwareApplication` and `ScholarlyArticle` schemas in HTML versions. Use BibTeX entries in preprint.
6. **Distinct vocabulary.** Coin and define specific terms once ("Tree-to-Graph Universal Bridge", "Deterministic Boundary Library") so they become attributable to Kontablo when LLMs encounter them in training.
7. **Author identity.** Every public document must carry: author name (Christian Luciani), ORCID 0000-0002-6955-5384, affiliation as published ("Independent Researcher, Cuenca, Ecuador", with Praxia noted as the initiative's planned entity — keep this consistent with CITATION.cff and `.zenodo.json`), and DOI of the canonical preprint once assigned.
8. **Discoverable hosting.** Preprint must be on SSRN AND Zenodo AND linked from the repo README. Crawlers find papers via multiple paths; one channel is not enough.

## Conventions

- **Branching:** `claude/[topic]` for Claude Code work, `cursor/[topic]` for Cursor IDE work, never directly to `main`. PRs for Christian to review and merge.
- **Commits:** conventional commits (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`). Scope in parens when useful: `feat(api): add hyperinflation adjustment endpoint`.
- **Issue templates:** `.github/ISSUE_TEMPLATE/` — use them.
- **Epistemic standards (project-wide, non-negotiable):** every claim in documentation that is not common knowledge needs (a) explicit doubt or "I don't know" when uncertain, (b) literal citation with original source, (c) indication of how to verify. This is a hard rule, not a style preference.
- **Tests must assert.** A test that prints "PASSED/FAILED" instead of asserting is not a test (this happened: `test_coresponsibility.py` could never fail until June 2026). Tests that require a live LLM API key are integration tests — mark them `skipif` on key absence with an explicit reason, never let them fail as if the deterministic core were broken.
- **Python env:** the venv lives in the main repo checkout (`accounting-esperanto/venv/`), not in worktrees. Tier-3 tests need one of GROQ/CEREBRAS/GOOGLE_AI/OPENROUTER API keys (Infisical or env).

## Claims–evidence traceability (non-negotiable)

This is the project's load-bearing scientific guarantee: **every quantitative claim in a public artifact must be regenerable from a committed, deterministic command.** Kontablo's thesis is determinism and verifiability — the repo must embody the standard it preaches.

Current claim → evidence map (update this table whenever a number changes):

| Claim | Generating command |
|---|---|
| 195 sovereign / 60 statutory / 56 Tier-1-ready | `python scripts/mass_consolidation_v2.py` (coverage manifest header) or `scripts/build_jurisdiction_manifest.py` |
| 75 entities, 68 jurisdictions, 97.3% deterministic resolution, 25/30 nodes, 4 escalations | `python scripts/mass_consolidation_v2.py` → `research/experiments/consolidation_v2/results.json` |
| Initial run: 10 entities, 9 countries, 4 ERP export formats, 93.9% deterministic, 8 escalations (SA 7/12 escalated, VN 12/13 Tier-1) | `python scripts/consolidation_v1_initial_run.py` → `research/experiments/consolidation_v1/results.json`, gated by `tests/test_consolidation_v1.py`. **Synthetic trial balances formatted as ERP exports — never describe as exported from a live ERP.** |
| Test suite state | `python -m pytest tests/` (50 passed, 2 skipped LLM-integration, 0 xfailed as of the June 2026 #29 remediation; `pytest tests/ connectors/` is the CI command and adds the connector suites + the surface-drift gate) |
| ~94% volume coverage of the 30-account core (by posting count; ~87% by whole transaction; ~99% with the 34-account extended core) | `python scripts/coverage_benchmark.py` → `research/coverage_benchmark/coverage_results.json`, gated by `tests/test_coverage_claim.py`. The dataset is a **labeled synthetic frequency distribution** (provenance in `research/coverage_benchmark/README.md`) — always describe the figure as a model-based estimate, never as a measurement of real ledgers. The old "92% empirically... benchmarked against thousands of SME ledger exports" phrasing was retired in the June 2026 audit; never restore it. |
| 18 near-universal core concepts | The honest formulation is "recur near-universally; the most universal appear in 94–98% of committed jurisdiction mapping sets" — verified against `localizations/` (June 2026). Never claim "present in 100% of analyzed standards"; the repo's own data contradicts it. |
| SME margin scenario (70–85% cost reduction → 1.8–3.2 pp margin) | **ILLUSTRATIVE MODEL, not empirical** — impact.tex frames it as a hypothesis with stated assumptions. Do not cite as a result. |

Rules:
1. **One number, four surfaces.** The citable surfaces are `docs/papers/drafts/sections/abstract.tex`, `README.md`, `CITATION.cff`, `.zenodo.json`. If a headline number changes, update all four **in the same PR** — stale-count drift across these files is the documented failure mode (the "23 jurisdictions" residue survived two release-prep passes).
2. **Round honestly.** The script reports 97.3%; the abstract may say 97%, never 98%.
3. **No claim without a command.** If a new public claim cannot be regenerated from the repo, either build the script first or label the claim explicitly as estimate/projection with its basis.
4. **Run before release-bound PRs:** full pytest suite AND `mass_consolidation_v2.py`, confirming the output still matches the published numbers. A KnowledgeBase that fails to load any of the 195 localizations is a release blocker (a single unquoted `country: NO` once 500'd the entire mapping API).

## CI claims–evidence gate (exists — maintain it)

`.github/workflows/ci.yml` runs on every push/PR: pytest (including `tests/test_localization_integrity.py`, which loads all localization YAMLs and guards against YAML-boolean ISO codes like `NO`), then `scripts/mass_consolidation_v2.py` with a hard assertion that the headline numbers in `results.json` still match the published claims. **If a legitimate methodology change moves a number, update the expected block in ci.yml AND all four citable surfaces in the same PR.** A red build on claim drift is working as designed — never weaken the assertion to make it pass. (`project-automation.yml` is separate board automation pointing at a stale Phase 0 board; harmless, ignore.)

## Completed conceptual work (historical — do not redo)

The two queued preprint updates shipped in v1.8: (1) the harness-architecture section (`sections/harness_architecture.tex`) — model vs. harness, ontology-as-constraint, locus-of-error relocation to the semantic coverage boundary; (2) the hallucination-framing reconciliation plus the co-responsibility corrections (the agent never "decides alone"; high confidence changes review friction, not the presence of review). The scope rule that governed it stands for future conceptual work: **if an update fits in ≤2 sessions it enters the current release; otherwise it ships as labeled future work.** The publication date governs — do not reactivate the "one more thing before publishing" pattern.

## Launch playbook (exists — execute, don't rewrite)

`docs/strategy/launch-playbook.md` is operative: release-day sequence (Zenodo toggle → GitHub release v0.1.0 → DOI propagation → SSRN → coordinated posts), 25-person tiered notification list, and post drafts. `docs/strategy/release-notes-v0.1.0.md` is ready for `gh release create`. Sessions touching launch material should execute or refine the playbook, not produce parallel strategy documents.

## Anti-patterns specific to this repo

- **Do not chase post-publication work** (production connectors for NetSuite/SAP, Rust migration, security audit, PQC implementation) **before the v0.1.0 release ships.** Confusing phases is the documented failure mode. The single exception is maintenance of the CI claims–evidence gate, which protects the release itself.
- **Do not expand scope** during repo cleanup. The goal is publication-ready, not feature-complete.
- **Do not delete `MANIFESTO.md` or research artifacts** even if redundant. Audit trail matters for academic credibility.
- **Do not deploy the frontend dashboard publicly** until Praxia is ready to receive leads. Demo screenshots in docs are fine; live demo creates premature product expectation.
- **Do not key program logic on LLM free-text.** `logic/agents/tax_compliance.py` originally triggered jurisdictional overrides by substring-matching the LLM's *justification string* — stochastic control flow violating principle #5. Fixed June 2026: overrides now key on deterministic input fields (jurisdiction + source account local name). Never reintroduce the pattern; all override/branching logic must key on deterministic fields (jurisdiction, local code, ontology node), never on model output text.
- **Quote YAML values that collide with YAML 1.1 literals.** ISO codes `NO` (Norway) parses as boolean — others to watch: `ON`, `OFF`, `YES`, `Y`, `N`. The loader is hardened, but new YAML must quote these anyway.
- **Do not weaken validation honesty.** The consolidation validation uses synthetic trial balances and the abstract's construction protocol explicitly states no codes are fabricated and placeholders are excluded from Tier-1. Any edit that blurs these boundaries (e.g. "validated with real-world data", "all 60 charts verified" when it is 56) is an epistemic-standards violation, not a wording preference.
- **Do not make the validation harness resolve FX live.** `scripts/mass_consolidation_v2.py` and the claims-evidence numbers MUST price in the pinned `core/harness/fx.py:FX` table; wiring the harness to `fx_provider` live rates would make `results.json` non-reproducible and break the CI gate. Live FX belongs only to the runtime surfaces (REST/gRPC), env-gated, with the pinned table as offline fallback. Likewise keep `conftest.py`'s `KONTABLO_FX_MODE=static` default so the test session never depends on a network rate.
