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

Open-core via **BSL 1.1** (Business Source License) with conversion to Apache 2.0 after 4 years. Public layer includes preprint, ontology, spec, mapping methodology, dashboard as demo. Reserved for Praxia: production NetSuite/SAP S/4HANA connectors, validated+tested mapping artifacts (vs methodology), consolidation simulation engine if commercially viable, implementation services.

**Connector licensing policy (decided May 28, 2026):** connectors to open-source ERP/accounting projects (ERPNext/Frappe, Odoo, and similar) are licensed **Apache 2.0**, not BSL. Rationale: the open-source community is averse to non-OSI licenses; an Apache connector maximizes adoption in ecosystems that will not pay commercial license anyway, and serves as a credibility-building loss leader. The protectable commercial assets are the validated ontology, implementation services, and connectors to expensive proprietary ERPs (NetSuite, SAP) — those stay BSL/proprietary. General principle: **open the interface (APIs, well-documented contracts) to grow the ecosystem; protect the implementation behind it with BSL.** A large commercial ERP will build its own version if Kontablo becomes strategic regardless of license — licensing cannot prevent that; it only prevents free incorporation of *our* code. The real moat is first-mover citability, jurisdictional depth (23 mapped), hyperinflation expertise, and Praxia's execution speed — not the license.

**Rationale (route b):** option to migrate from (b) commercial entity to (a) pure research is easy; reverse is not. BSL preserves optionality.

## Architectural principles (do not violate without explicit decision)

1. **Graph, not tree** — accounts exist in multiple dimensions simultaneously. No 1:1 mappings assumed.
2. **UUID as truth** — codes are visual labels; UUIDs are canonical identifiers. Codes can collide across jurisdictions; UUIDs cannot.
3. **Logic-based mapping** — aggregation via deterministic scripts, never hardcoded.
4. **API-first at the data layer, agent-native at the access layer** — the canonical interface is a machine-consumable API (REST/gRPC). On top of it, Kontablo exposes an agent-native layer for the agentic economy via MCP (Model Context Protocol, for LLM/agent tool consumption), A2A (Agent2Agent, for agent-to-agent interoperation), and AP2 (Agent Payments Protocol, for settlement). The API is the body; the agent protocols are the face. An ERP or bank consumes the API directly; an autonomous agent consumes the agent-native layer. Do NOT subordinate one to the other. The agent-native layer is protocol-pluggable by design: Kontablo will adopt and add any agentic protocol that gains meaningful traction, so the architecture names the *category* (agent-native) rather than betting on a single protocol.
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
7. `LICENSING.md` — new file explaining the BSL choice, additional use grant, and the connector licensing policy (open-source ERP connectors = Apache 2.0; core = BSL; see Strategic posture).
8. `SECURITY.md` — new file with PQC roadmap, vulnerability disclosure policy, and threat model summary.

## Pending conceptual work for the preprint (NOT hygiene — needs a dedicated session)

The preprint was conceived before agentic concepts were mature. Two conceptual updates are queued, with a HARD scope rule: if the combined update fits in ≤2 Claude Code sessions, it enters the v1 release; if it requires more, it ships as explicitly-labeled future work in v1 and becomes the v2 preprint. The publication date governs — do not let conceptual expansion reactivate the "one more thing before publishing" pattern.

1. **New section: "The Kontablo Agent: Harness Architecture and the Locus of Error."** Distinguishes the *model* (stochastic, hallucinates) from the *harness* (context, tools, validation, source-grounding, constraints that make output reliable). Core argument: the ontology-as-constraint eliminates the *classical* class of accounting hallucination (the agent cannot emit a non-existent account UUID), so the residual error relocates to the *boundary of semantic coverage* — a transaction type not yet mapped, an undocumented jurisdictional rule, an unanticipated edge case. The reframe: the problem shifts from "how do we stop the LLM hallucinating" (intractable) to "how do we design the harness so the decision space is ontology-bounded and out-of-coverage cases escalate to a human rather than being confabulated" (tractable engineering). Connect to the co-responsibility governance architecture (ADR 008) as the mechanism that manages residual error: the harness defines when the agent decides alone, when it requires human co-signature, and when it escalates. This ties directly to architectural principle #5 (determinism over stochasticity).
2. **Reconcile any existing hallucination discussion** currently framed only in the classical LLM sense — audit where it appears before deciding surgical vs structural rewrite. Do NOT rewrite blindly; first locate all instances.

## Pending strategy artifact (separate document, separate session)

A launch playbook (`docs/strategy/launch-playbook.md`) is needed but does NOT yet exist — do not scatter it as bullets in this file. It must cover: (a) **citation strategy** — which foundational works/authors to cite to improve discoverability and situate the work in citable lineages; (b) **technical-influencer DM strategy** — identifying and reaching technical influencers who could amplify (one mention can be decisive); (c) **social media strategy** — coordinated multi-channel release. Build this in a dedicated session, grounded in the prepare-for-publication skill (Step 8 territory).

## Anti-patterns specific to this repo

- **Do not chase Phase 3 work** (production connectors for NetSuite/SAP, Rust migration, security audit) **before publication.** Phase 3 is post-publication validation. Confusing phases is the documented failure mode.
- **Do not expand scope** during repo cleanup. The goal is publication-ready, not feature-complete.
- **Do not delete `MANIFESTO.md` or research artifacts** even if redundant. Audit trail matters for academic credibility.
- **Do not deploy the frontend dashboard publicly** until Praxia is ready to receive leads. Demo screenshots in docs are fine; live demo creates premature product expectation.
