# ADR 018: LoRA Fine-Tuned Small Language Model for Tier-3 Semantic Mapping ("Kontablo-SLM")

**Status:** Proposed
**Date:** 2026-07-16
**Deciders:** Christian Luciani

---

## Context

Kontablo's Three-Tier Resolution Pipeline (`core/harness/resolution.py`) resolves the large
majority of accounts deterministically (Tier 1 exact lookup, Tier 2 multilingual keyword rules).
Tier 3 — the semantic AI fallback for unmapped or ambiguous accounts — is currently served by
an **agent-agnostic router over generic cloud models** (`scripts/ai_router.py`: Groq, Cerebras,
Gemini, OpenRouter — general-purpose 8B–70B models with no accounting-specific training), per
the design in `openspec/microsaas_mapping_api.md`.

The preprint section "The Kontablo Agent: Harness Architecture and the Locus of Error"
(`docs/papers/drafts/sections/harness_architecture.tex`) explicitly frames this as unfinished
work: Kontablo v0.1.0 operates at neurosymbolic coupling maturity **L2–L3** (tool discovery
constrained, process-gated escalation), and states that **L4–L5 — output-side semantic
validation and evolution from agent experience — are "explicitly deferred to future work."**
This ADR is that future work, scoped for the first time.

ADR-011 (Client-Specific Determinism Agent) already established the closest architectural
precedent: an agent that observes a client's Tier-3 resolution history and proposes candidate
deterministic rules, gated by mandatory human co-signature, operating on client infrastructure.
This ADR proposes a complementary but distinct mechanism — improving the **model** that serves
Tier 3 itself, rather than migrating individual patterns out of Tier 3 into Tier 1/2.

### External evidence reviewed (2026-07-16)

- **MiniCPM family (OpenBMB).** MiniCPM5-1B (released 2026-05-19, Apache 2.0; benchmark and
  release details per github.com/openbmb/minicpm) reports a 1B-class SOTA average score of
  42.57 vs. 35.61 for the next-best open-source model in that size class, with LoRA
  fine-tuning documented out of the box across TRL+PEFT, LLaMA-Factory, ms-swift, unsloth, and
  xtuner, and native structured tool-call output (XML → OpenAI-compatible `tool_calls`).
  MiniCPM4-8B reaches parity with Qwen3-8B using 4.5× fewer training tokens (8T vs. 36T,
  arXiv:2506.07900), and is a more credible accuracy baseline than the 1B variant for a
  195-jurisdiction semantic task. A 0.5B/1B variant is retained as the candidate for genuinely
  on-device, client-local deployment (see ADR-011 data-sovereignty framing).
- **LoRA in financial/accounting domains.** FinLoRA (arXiv:2505.19819) benchmarks five LoRA
  methods across 19 financial datasets (including XBRL analysis over 150 SEC filings) and
  reports a 36% average improvement over base models at documented, "affordable and scalable"
  compute cost. Zupan (2025, *Intelligent Systems in Accounting, Finance and Management*,
  DOI 10.1002/isaf.70011) demonstrates supervised fine-tuning of a 7B model specifically for
  generating double-entry bookkeeping postings — directly analogous to Kontablo's Tier-3 task.
  Both are existing evidence, not novel claims Kontablo would need to originate.
- **Self-scaffolding / self-adapting model research.** Two distinct approaches were identified
  and must not be conflated:
  - **Ornith-1.0** (DeepReinforce AI, 2026-06-25, MIT license): a model trained via RL to
    generate *both* a task-specific scaffold/harness and the solution that scaffold guides,
    jointly optimized during **training time**. No production weight self-modification occurs;
    the self-improvement is confined to the training loop, and the public release does not
    include the RL training code needed to reproduce the method. Its relevance to Kontablo is
    as a **methodology reference for harness/rule-proposal generation** (resonant with, and
    potentially informative for, ADR-011's rule-proposal mechanism) — not as a pattern for
    live model adaptation.
  - **SEAL** (MIT, arXiv:2506.10943): a model that generates its own fine-tuning data and
    applies it as persistent weight updates via an RL loop, at or after deployment. The
    paper's own continual-learning experiments report **catastrophic forgetting** — repeated
    self-edits degrade performance on earlier tasks without an explicit retention mechanism.

---

## Decision

**Propose** (not Accept) a subproject — working name **Kontablo-SLM** — to replace or augment
the generic-model Tier-3 router with a LoRA adapter fine-tuned specifically for Kontablo's
account-mapping task, subject to the hard constraints below.

### What this is

A **versioned, offline-trained LoRA adapter** on a MiniCPM4/5 base model, trained on data
Kontablo already has: the 7,000+ account mappings in `localizations/`, and the escalation/
resolution logs produced by `scripts/mass_consolidation_v2.py`. It is evaluated against the
same benchmark methodology as `scripts/coverage_benchmark.py`, before being considered as a
Tier-3 backend.

### What this explicitly is not

**No production weight self-modification.** The model does not update its own weights in
response to live experience, in production, unsupervised — the SEAL pattern. This is a hard
constraint, not a tuning choice, for two independent reasons:

1. It would violate architectural principle #5 (determinism over stochasticity wherever
   movable, ADR-009): a model whose decision function silently drifts in production is the
   opposite of the auditable, reproducible harness Kontablo is built around, and breaks the
   immutable-versioning guarantee (principle #6) that every other deterministic surface in
   this repo is held to.
2. It is not even reliable on its own terms — SEAL's authors document catastrophic forgetting
   from repeated self-edits without an explicit retention mechanism. Adopting a known-unstable
   technique inside a ledger-grade system would be indefensible under the project's epistemic
   standards.

Ornith-1.0's self-scaffolding idea is retained only as a possible **input to the offline
training/rule-authoring pipeline** (e.g., informing how ADR-011's rule-proposal generation is
structured) — never as a live in-production weight-update mechanism. Any future proposal to
blur this line requires a new ADR, not an amendment to this one.

### Phased approach

1. **Phase 0 — cheap validation.** LoRA fine-tune MiniCPM4-8B on existing mapping/escalation
   data. Evaluate against the current `ai_router.py` generic-model baseline using the existing
   coverage-benchmark methodology. No production integration at this stage.
2. **Phase 1 — dual-model strategy (only if Phase 0 validates).** MiniCPM4-8B (or larger) as
   the accuracy-optimized Tier-3 backend; MiniCPM5-1B / MiniCPM4-0.5B as the candidate for
   genuinely on-device, client-local deployment under the ADR-011 data-sovereignty model.
3. **Mandatory release gate**, for any adapter version considered for production Tier-3 use:
   - Passes a fixed regression benchmark against the previous adapter version and against the
     generic-model baseline before replacing either.
   - Carries an immutable version identifier (hash), consistent with principle #6.
   - Retraining is a deliberate, offline, human-initiated act — never an automatic response to
     accumulated experience.

### Licensing (open decision, not resolved by this ADR)

Per ADR-010, "validated+tested mapping artifacts" are reserved as BSL/proprietary for Praxia,
distinct from the Apache-licensed open-source connectors. A LoRA adapter trained on Kontablo's
validated mapping corpus falls into that reserved category by the same logic. The *training
script/recipe* could plausibly follow the "open the interface, protect the implementation"
pattern (Apache), while the *trained weights* remain BSL/proprietary — but this split is a
licensing decision for Christian to make explicitly before Phase 0 output is used for anything
beyond internal evaluation. This ADR does not resolve it.

### Phase scope

This is a **Phase 3+ / post-v0.1.0 exploratory proposal**. It does not authorize any
implementation. The trigger conditions mirror ADR-011's: Phase 0 requires only existing data
and no new infrastructure, so it may proceed as a low-cost experiment; Phase 1 requires an
explicit resourcing decision and the licensing question above to be settled.

---

## Consequences

### Positive

- Directly closes the L4–L5 gap the preprint already flags as future work, using evidence
  (FinLoRA, Zupan 2025) that the approach is viable in adjacent domains rather than speculative.
- Reuses existing assets (7,000+ mappings, escalation logs, coverage-benchmark harness) — Phase
  0 requires no new data collection.
- A specialized small model is plausibly *more* deterministic-friendly than the current generic
  70B router: narrower output distribution, cheaper to constrain and validate, cheaper to run
  on-device (serving ADR-011's data-sovereignty goal directly).
- Coins a citable, attributable name ("Kontablo-SLM") early, consistent with the project's
  AI-discoverability conventions (CLAUDE.md GEO/AEO section).

### Negative / Risks

- **Licensing ambiguity** (above) must be resolved before any adapter output leaves internal
  evaluation — publishing benchmark numbers without a licensing decision risks the same
  claims-evidence drift the project's CI gate exists to prevent.
- **Training data is the same synthetic/validated corpus used elsewhere in the repo** — any
  public claim about Kontablo-SLM's accuracy must carry the same epistemic caveat already
  applied to `mass_consolidation_v2.py` and `coverage_benchmark.py`: synthetic, not real-world
  ledger data, until a production deployment says otherwise.
- **Ornith-1.0's public release excludes its RL training code** — the self-scaffolding
  methodology reference is directional, not a reproducible recipe Kontablo can directly adopt.
- **Scope creep pressure.** As with ADR-011, the existence of this ADR creates pressure to
  start Phase 1 before Phase 0 results justify it. Phase 0 must produce a benchmark comparison
  before any resourcing conversation about Phase 1 happens.

### Neutral

- Does not require any change to the ontology, the Deterministic Boundary Library, or the
  Tier-1/Tier-2 rules — this ADR only concerns what serves Tier 3.

---

## References

- **ADR-009** (`009-determinism-over-stochasticity.md`) — principle #5; this ADR's hard
  constraint against live weight self-modification is a direct application of it.
- **ADR-010** (`010-agent-native-and-connector-licensing.md`) — "open the interface, protect
  the implementation" licensing principle; source of the BSL-vs-Apache framing applied here.
- **ADR-011** (`011-client-specific-determinism-agent.md`) — closest architectural precedent;
  same phase-gating discipline and on-device/data-sovereignty framing adopted here.
- **`docs/papers/drafts/sections/harness_architecture.tex`** — establishes the L2–L5
  neurosymbolic coupling maturity model and defers L4–L5 to future work; this ADR is that work.
- **`core/harness/resolution.py`**, **`scripts/ai_router.py`**, **`openspec/microsaas_mapping_api.md`**
  — current Tier-3 implementation this ADR proposes to eventually complement or replace.
- MiniCPM5 / MiniCPM4 — https://github.com/openbmb/minicpm ; https://huggingface.co/openbmb/MiniCPM4-8B ;
  MiniCPM4 paper, arXiv:2506.07900.
- FinLoRA — arXiv:2505.19819.
- Zupan (2025), "Developing an Accounting Virtual Assistant Through Supervised Fine-Tuning of a
  Small Language Model," *Intelligent Systems in Accounting, Finance and Management*,
  DOI 10.1002/isaf.70011.
- Ornith-1.0 — https://github.com/deepreinforce-ai/Ornith-1
- SEAL: Self-Adapting Language Models — arXiv:2506.10943.
