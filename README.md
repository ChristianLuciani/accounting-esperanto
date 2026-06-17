# Kontablo — Universal Accounting Ontology

**Kontablo is a graph-based, UUID-keyed universal accounting ontology** that bridges
local jurisdictional chart-of-accounts standards, international reporting frameworks
([IFRS](https://www.ifrs.org/)/[XBRL](https://www.xbrl.org/)), the agentic economy
([MCP](https://modelcontextprotocol.io/specification),
[A2A](https://a2a-protocol.org/), [AP2](https://ap2-protocol.org/specification/)),
and blockchain/DeFi protocols —
enabling deterministic, machine-verifiable financial data exchange across all 195
sovereign jurisdictions (complete global coverage), with statutory chart-of-accounts
overlays for the 60 jurisdictions that mandate a national chart.

| | |
|---|---|
| **Status** | Phase 3 — Pre-Publication |
| **Preprint** | `docs/papers/drafts/kontablo_preprint_modular.pdf` — SSRN/Zenodo submission pending |
| **License** | [BSL 1.1](LICENSE) → Apache 2.0 on 2030-05-28 · ERPNext & Odoo connectors: [Apache 2.0](connectors/erpnext/LICENSE) |
| **Author** | Christian Luciani · [ORCID 0000-0002-6955-5384](https://orcid.org/0000-0002-6955-5384) |

---

## What problem does Kontablo solve?

Every major jurisdiction maintains its own chart of accounts. These standards share
underlying economic concepts but differ in structure, naming, and hierarchy — creating
three compounding crises for cross-border financial systems:

1. **The M2M Void.** No machine-readable interoperability layer exists between accounting
   standards. ERP-to-ERP data exchange requires costly, brittle, hand-crafted mappings.
2. **The Babel Problem.** "Cash", "Caja", "Caisse", and "نقدية" denote the same economic
   node but are treated as distinct entities by every system. Semantic equivalence is
   undocumented at the machine level.
3. **The Hyperinflation Gap.** Most accounting standards assume monetary stability.
   Jurisdictions under hyperinflationary conditions (Venezuela, Argentina, Zimbabwe)
   require inflation-adjusted restatement that existing ontologies do not model.

Kontablo addresses all three through a single, UUID-keyed graph ontology where economic
nodes are jurisdiction-independent and local codes are metadata, not identity.

---

## How is Kontablo architected?

### What does "graph-based" mean here?

Traditional charts of accounts are trees: each account has exactly one parent.
Kontablo is a **directed graph**: each account node exists in multiple dimensions
simultaneously. "Cash" is at once a Balance Sheet node, a Current Asset node, and a
Liquidity Level 1 node. No information is lost by forcing a single hierarchy.

The **Tree-to-Graph Universal Bridge** is Kontablo's core translation mechanism:
it accepts a tree-structured chart from any ERP or jurisdiction and resolves it to
graph nodes via a three-tier confidence system (exact match → pattern disambiguation
→ semantic AI fallback). The result is always a UUID, never a local code.

### How much of real accounting activity does the 30-account core capture?

A reproducible transaction-frequency benchmark
([`research/coverage_benchmark/`](research/coverage_benchmark/),
[`scripts/coverage_benchmark.py`](scripts/coverage_benchmark.py)) estimates that
the **30-account Level 3 minimum core covers ~94% of routine transaction volume**
by posting count (~87% counted by whole transaction). A **34-account extended
core** — adding payroll, deferred revenue (IFRS 15), withholding-tax, and
non-trade-receivable nodes — reaches **~99%**. The remaining few percent is a
deliberately-retained *principled residual* (suspense, intercompany, novel
instruments) that escalates to a human via the Co-responsibility Architecture
rather than being force-mapped. The figure is a **model-based estimate** over a
transparently-parameterized synthetic distribution grounded in the standard
double-entry "special journals" taxonomy — not a measurement of a private ledger
corpus, and labeled as such. Regenerate it with one command; the claims–evidence
test [`tests/test_coverage_claim.py`](tests/test_coverage_claim.py) pins it to
every surface that cites it.

### What makes Kontablo deterministic?

**UUID as truth.** Every economic concept has a stable, collision-resistant UUID.
Local codes (e.g. MX-SAT `1.1.01`, FR-PCG `512000`) are stored as mapping metadata.
Two systems referencing the same UUID are guaranteed to be discussing the same economic
node, regardless of jurisdiction or language.

**Deterministic Boundary Library.** A set of hard logical constraints enforced before
any agent decision: Cash vs Non-Current, Debit vs Credit nature, Balance Sheet vs
Income Statement classification. These boundaries cannot be overridden by inference —
an agent cannot emit a UUID that does not exist in the ontology graph. This eliminates
the classical class of accounting hallucination and relocates residual error to the
boundary of semantic coverage (unmapped transaction types), which escalates to a human
rather than being confabulated.

**Logic-based mapping.** Aggregation and translation are produced by deterministic
scripts, not hardcoded tables and not stochastic inference. The same input always
produces the same output.

### How does the agent-native layer work?

Kontablo exposes three agent-economy interfaces above the core API:

| Protocol | Role |
|---|---|
| **[MCP](https://modelcontextprotocol.io/specification)** (Model Context Protocol) | LLM/agent tool consumption — query the ledger, resolve UUIDs, validate transactions |
| **[A2A](https://a2a-protocol.org/)** (Agent2Agent) | Agent-to-agent interoperation across financial workflows |
| **[AP2](https://ap2-protocol.org/specification/)** (Agent Payments Protocol) | Settlement coordination between autonomous agents |

The REST API is the canonical data interface and is fully implemented (FastAPI).
A gRPC interface is defined in [`api/grpc/kontablo.proto`](api/grpc/kontablo.proto)
with a minimal server ([`api/grpc/server.py`](api/grpc/server.py)) that implements
the **deterministic** RPCs — account queries, mapping, consolidation with
intercompany elimination, balance-sheet validation — over the same engine that
backs REST. RPCs that would depend on stochastic LLM inference are intentionally
left `UNIMPLEMENTED` rather than faked. The agent-native layer sits above the API.
An ERP integrates via the API directly; an autonomous agent uses the agent-native layer.
Neither is subordinate. Kontablo will adopt any agentic protocol that gains meaningful
traction — the architecture names the category, not a single protocol.

### What is the Co-responsibility Governance Architecture?

Defined in [ADR 008](docs/adr/008-co-responsibility-governance.md), this mechanism
establishes that **the human is always the ultimate legal principal** in any
Kontablo-mediated transaction. Accountability cannot be transferred to an agent.

The architecture has two non-negotiable properties:

- **Full auditability.** Every transaction, agent decision, and confidence score is
  recorded in an append-only audit trail (cryptographic sealing of that trail is a
  roadmap item, not yet implemented). Zero-corruption is an explicit design goal:
  Kontablo aims to make financial flows observable, traceable, and verifiable by
  every technically available means.
- **Human veto power.** The human retains the right to review and reverse any agent
  decision at any time. If an agent produces an incorrect or fraudulent transaction,
  the human can correct it — and the audit trail preserves both the original action
  and the correction.

Within these constraints, co-responsibility defines three participation modes that
govern *automation convenience*, not accountability:

| Mode | Condition | Human role |
|---|---|---|
| Auto-approval | High confidence, ontology-bounded | Pre-authorized; receives audit record |
| Co-signature | Medium confidence, boundary-adjacent | Explicit approval required before execution |
| Escalation | Out-of-coverage | Full human decision; agent presents options only |

In M2M scenarios (agent-to-agent without a human in the real-time loop), co-responsibility
is embedded in the pre-configured protocol rules. The human set those rules and retains
retroactive veto over any transaction the automated process produced. The harness —
not the model — enforces these boundaries.

---

## Which jurisdictions does Kontablo cover?

All **195 sovereign jurisdictions** are mapped (complete global coverage), with
7,000+ account mappings in `/localizations`. Coverage operates in two layers:

- **Universal IFRS-anchored layer** — every jurisdiction is covered by the
  UUID-keyed Level 3 taxonomy, including jurisdictions with no mandated national
  chart (IFRS-pure, e.g. United Kingdom, Estonia, Botswana, Namibia).
- **Statutory chart overlays** — the **60 jurisdictions that mandate a national
  chart of accounts** additionally receive code-level mappings against
  primary-source-cited statutory charts. Examples: SYSCOHADA (shared by 17 OHADA
  member states), French PCG (also applied in Monaco), Spanish PGC, Portuguese SNC,
  Belgian PCMN, Luxembourg PCN, Austrian EKR, Chinese CAS, Peruvian PCGE, Mexican
  SAT, Brazilian SPED, plus the Moroccan, Algerian, Romanian, Czech, Slovak,
  Hungarian, Bulgarian, Ukrainian, Kazakh, Tunisian, Belarusian, Serbian, Croatian,
  Slovenian, Moldovan and Greek national charts.

Special contexts modeled:
[IAS 29](https://www.ifrs.org/issued-standards/list-of-standards/ias-29-financial-reporting-in-hyperinflationary-economies/)
hyperinflation (Venezuela, Lebanon, Zimbabwe, Argentina, and others), Islamic
finance jurisdictions, and distribution-only corporate income tax regimes
(Estonia, Latvia, Georgia).

Multi-lingual semantic mapping is operational for Spanish, French, Arabic, and Vietnamese.

---

## How can I verify Kontablo's claims?

Every quantitative claim in the preprint abstract is regenerable from this
repository with deterministic commands — no API keys, no network calls:

```bash
pip install -r requirements.txt

# Coverage manifest (195 sovereign / 60 statutory charts / 56 Tier-1-ready)
# and the validation matrix: 75 entities, 68 jurisdictions, 97.3% deterministic
# resolution, 25/30 universal nodes populated, 4 escalations to human review.
python scripts/mass_consolidation_v2.py
# → results in research/experiments/consolidation_v2/results.json

# Test suite, including integrity checks across all localization YAMLs
python -m pytest tests/
```

CI re-runs both on every push and fails the build if any published number
stops reproducing (see `.github/workflows/ci.yml`).

Honest bounds on what is claimed: the validation matrix uses **synthetic
trial balances**, not production ledger data; statutory-chart coverage is
exercised against primary-source-cited charts for **56 of the 60**
statutory-chart jurisdictions; no account codes are fabricated, and
jurisdictions without a mandated chart are covered by the IFRS-anchored
layer, not asserted to have national codes. The construction protocol is
documented in the preprint (Appendix and Section on expanded validation).

---

## What is in this repository?

```
/core           — Ontology schemas and UUID-keyed account mapping (v0.1)
/localizations  — Chart-of-accounts mappings for all 195 sovereign jurisdictions
/spec           — The standard in human-readable and machine-readable form
/openspec       — 6 OpenSpec change proposals (aggregation, versioning, multi-language, etc.)
/api            — FastAPI REST service + gRPC server (deterministic RPCs) for mapping/consolidation
/frontend       — React + Framer Motion reference dashboard (local demo only)
/examples       — Runnable transnational reconciliation walkthroughs (self-contained + two-ERP)
/connectors     — ERP connectors (ERPNext/Frappe & Odoo: Apache 2.0; proprietary ERPs: separate license)
/logic          — Deterministic mapping rules, validators, Deterministic Boundary Library
/docs/adr       — 13 Architecture Decision Records
/docs/papers    — Academic preprint (PDF + LaTeX source)
/bibliography   — Primary sources: IFRS taxonomy, jurisdiction standards
/research       — Comparative analysis, ERP compatibility research
```

---

## What is Kontablo NOT?

- **Not an ERP.** Kontablo does not manage transactions, invoices, or payroll. It is a
  protocol layer that other systems integrate with.
- **Not a SaaS product.** There is no hosted service. The reference implementation is
  a local FastAPI service and a demo dashboard. Production deployment is the
  responsibility of the integrating system.
- **Not a learning management system or courseware.**
- **Not a replacement for jurisdiction-specific accounting software.** Kontablo sits
  above existing software as a translation and validation layer.
- **Not feature-complete.** The v1 release delivers the ontology, specifications,
  and reference connectors. Production connectors for NetSuite and SAP S/4HANA
  are post-publication work.

---

## How do you cite Kontablo?

**BibTeX:**

```bibtex
@misc{luciani2026kontablo,
  title        = {Kontablo: A Graph-Based Universal Accounting Ontology
                  for Multi-Jurisdictional Financial Integration},
  author       = {Luciani, Christian},
  year         = {2026},
  note         = {Preprint. SSRN/Zenodo submission pending. Available at
                  \url{https://github.com/ChristianLuciani/accounting-esperanto}},
  institution  = {Independent Researcher, Cuenca, Ecuador},
  orcid        = {0000-0002-6955-5384}
}
```

**APA:**

Luciani, C. (2026). *Kontablo: A graph-based universal accounting ontology for
multi-jurisdictional financial integration* [Preprint]. Praxia.
https://github.com/ChristianLuciani/accounting-esperanto

*DOI will be added upon SSRN/Zenodo publication.*

---

## Who develops Kontablo?

**_Christian Luciani_** 
Independent Researcher · Cuenca, Ecuador
[ORCID 0000-0002-6955-5384](https://orcid.org/0000-0002-6955-5384)
Contact: cluciani@gmail.com

This is a personal publication. Praxia — a planned Ecuadorian technology firm
specializing in financial data infrastructure — is the intended commercial vehicle
for Kontablo's production layer but does not yet exist as a legal entity.

---

## What is the roadmap beyond the v1 release?

**Phase 3 — Expert Validation and Production Connectors** (post-publication):
- Structured validation interviews with 15+ international CPAs across mapped jurisdictions.
- Production-grade NetSuite and SAP S/4HANA connectors (commercial license).
- JWT authentication on the consolidation API.
- Hybrid classical + post-quantum signatures (ML-KEM / ML-DSA per
  [NIST FIPS 203](https://csrc.nist.gov/pubs/fips/203/final) /
  [NIST FIPS 204](https://csrc.nist.gov/pubs/fips/204/final))
  on spec version hashes.
- Deepening statutory chart coverage: account-level granularity beyond the v1
  baseline, and resolution of the 4 statutory-chart jurisdictions not yet
  exercised against primary-source-cited charts (56 of 60 covered at v1).

Commercial API hosting, SaaS, and implementation services are out of scope for
this repository. See [LICENSING.md](LICENSING.md) for commercial use options.

---

## License and contributing

Kontablo core is licensed under **BSL 1.1** (Business Source License). It converts
automatically to Apache 2.0 on **May 28, 2030**. See [LICENSE](LICENSE) and
[LICENSING.md](LICENSING.md) for the full terms, Additional Use Grant, and rationale.

ERPNext/Frappe and Odoo connectors: **Apache 2.0**. See [connectors/erpnext/LICENSE](connectors/erpnext/LICENSE) and [connectors/odoo/LICENSE](connectors/odoo/LICENSE).

Contributing guidelines, branch naming, and the Contributor License Agreement
(required for BSL projects) are documented in [CONTRIBUTING.md](CONTRIBUTING.md)
— forthcoming before first public release.

Security disclosures and the post-quantum cryptography roadmap: [SECURITY.md](SECURITY.md)
— forthcoming before first public release.
