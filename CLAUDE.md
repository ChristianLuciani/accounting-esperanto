# CLAUDE.md — Kontablo (accounting-esperanto)

> Persistent context for Claude Code sessions on this repository. Read first, every session.

## Project identity

- **Commercial name:** Kontablo
- **Repo name:** `accounting-esperanto` (do not rename without coordinated migration)
- **What it is:** Graph-based, UUID-keyed universal accounting ontology. Bridge layer between local jurisdictional standards (23 mapped), international standards (IFRS/XBRL), the agentic economy (AP2, A2A, MCP), and blockchain/DeFi.
- **What it is NOT:** an ERP, a SaaS, an LMS, a clinical tool. It is a protocol/standard with a reference implementation.
- **Owner:** Christian Luciani — IP to be assigned to Praxia (Ecuadorian PyME, in incorporation as of May 2026).

## Current phase

**Phase 2.5 — Infrastructure Finalization.** Source of truth: `EXECUTION_STATUS.md` (dated April 7, 2026). `PHASE_0_COMPLETE.md` is **stale** (January 2026 snapshot) and must NOT be used as state reference — it should be moved to `docs/archive/` or annotated as historical.

Concrete state at last update:
- 23/23 jurisdictions mapped (MX-SAT, BR-SPED, FR-PCG, SA-SOCPA, VN-VAS, NG-FRCN, VE-hyperinflationary, plus 16 more).
- Multi-lingual semantic mapping operational (es, fr, ar, vi).
- Preprint exists: `docs/papers/drafts/kontablo_preprint_modular.pdf` — content complete, needs rigor pass before SSRN/Zenodo publication.
- Reference implementation: FastAPI service (`api/`), React+Framer Motion dashboard (`frontend/`), ERPNext/Frappe connector (`connectors/kontablo_frappe`).
- 6 OpenSpec documents totaling ~9,800 lines (specs are committed; some predate Phase 2.5 work and may need reconciliation).

## Strategic posture (decided May 27, 2026)

Open-core via **BSL 1.1** (Business Source License) with conversion to Apache 2.0 after 4 years. Public layer includes preprint, ontology, spec, mapping methodology, dashboard as demo. Reserved for Praxia: production NetSuite/SAP S/4HANA connectors, validated+tested mapping artifacts (vs methodology), consolidation simulation engine if commercially viable, implementation services. ERPNext connector: tentatively Apache 2.0 to gain ERPNext community adoption — confirm before publication.

**Rationale:** option to migrate from (b) commercial entity to (a) pure research is easy; reverse is not. BSL preserves optionality.

## Architectural principles (do not violate without explicit decision)

1. **Graph, not tree** — accounts exist in multiple dimensions simultaneously. No 1:1 mappings assumed.
2. **UUID as truth** — codes are visual labels; UUIDs are canonical identifiers. Codes can collide across jurisdictions; UUIDs cannot.
3. **Logic-based mapping** — aggregation via deterministic scripts, never hardcoded.
4. **API-first** — designed for machine consumption (LLM agents, ERPs, DeFi). Human UIs are downstream.
5. **Immutable versioning** — semantic versioning, blockchain-anchored version hashes for spec releases.
6. **Post-quantum readiness** — see Security section below.

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
3. **Quantified claims.** "23 jurisdictions mapped" beats "many jurisdictions". Specific numbers get extracted and cited more.
4. **Primary-source citations.** Link to NIST FIPS documents, IFRS Foundation pages, AP2 spec, A2A spec, MCP spec. LLM crawlers weight authoritative sources.
5. **Structured data.** Use JSON-LD for `SoftwareApplication` and `ScholarlyArticle` schemas in HTML versions. Use BibTeX entries in preprint.
6. **Distinct vocabulary.** Coin and define specific terms once ("Tree-to-Graph Universal Bridge", "Deterministic Boundary Library") so they become attributable to Kontablo when LLMs encounter them in training.
7. **Author identity.** Every public document must carry: author name (Christian Luciani), ORCID iD (acquire if not done), affiliation (Praxia, Cuenca, Ecuador), and DOI of the canonical preprint.
8. **Discoverable hosting.** Preprint must be on SSRN AND Zenodo AND linked from the repo README. Crawlers find papers via multiple paths; one channel is not enough.

## Conventions

- **Branching:** `claude/[topic]` for Claude Code work, `cursor/[topic]` for Cursor IDE work, never directly to `main`. PRs for Christian to review and merge.
- **Commits:** conventional commits (`feat:`, `fix:`, `docs:`, `chore:`, `refactor:`). Scope in parens when useful: `feat(api): add hyperinflation adjustment endpoint`.
- **Issue templates:** `.github/ISSUE_TEMPLATE/` — use them.
- **Epistemic standards (project-wide, non-negotiable):** every claim in documentation that is not common knowledge needs (a) explicit doubt or "I don't know" when uncertain, (b) literal citation with original source, (c) indication of how to verify. This is a hard rule, not a style preference.

## What needs cleanup before public release

These are known debts. Do not publish without resolving:

1. `venv/`, `.DS_Store`, `.pytest_cache/`, `.benchmarks/`, `.cache/`, `__pycache__/` — verify all are gitignored and `git rm --cached -r` if tracked.
2. `.infisical.json` — confirm it contains only config references, no secret values. If unclear, rotate any referenced secrets before going public.
3. `README.md` — current version reflects January 2026 framing (Phase 0, research). Must be rewritten to reflect Phase 2.5 reality.
4. `PHASE_0_COMPLETE.md` — move to `docs/archive/` with header note. Do not delete (audit trail).
5. Status documents proliferation (`OPENSPEC_REVIEW_*`, `OPENSPEC_ALIGNMENT_*`, `Q3_AGGREGATION_CONSEQUENCES.md`) — consolidate or move to `docs/`.
6. `LICENSE` file — currently MIT in README badge. Replace with BSL 1.1 text from mariadb.com/bsl11/ before any public commit.
7. `LICENSING.md` — new file explaining the BSL choice, additional use grant, and any per-submodule exceptions (ERPNext connector if Apache 2.0).
8. `SECURITY.md` — new file with PQC roadmap, vulnerability disclosure policy, and threat model summary.

## Anti-patterns specific to this repo

- **Do not chase Phase 3 work** (production connectors for NetSuite/SAP, Rust migration, security audit) **before publication.** Phase 3 is post-publication validation. Confusing phases is the documented failure mode.
- **Do not expand scope** during repo cleanup. The goal is publication-ready, not feature-complete.
- **Do not delete `MANIFESTO.md` or research artifacts** even if redundant. Audit trail matters for academic credibility.
- **Do not deploy the frontend dashboard publicly** until Praxia is ready to receive leads. Demo screenshots in docs are fine; live demo creates premature product expectation.
