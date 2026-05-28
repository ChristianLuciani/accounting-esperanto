# ADR 009: Determinism Over Stochasticity (Code Over Inference)

**Status:** Accepted
**Date:** 2026-05-28
**Deciders:** Christian Luciani

## Context

Kontablo operates as (or is consumed by) agentic systems. A naive agentic design routes most decisions through an LLM (stochastic inference). This is expensive in tokens, latency, and energy; it is non-reproducible; and stochastic errors compound downstream. As agentic concepts matured after Kontablo's initial design, it became clear that the reliability of an agentic system comes far more from its harness (the deterministic scaffolding around the model) than from model intelligence itself.

## Decision

Adopt **"determinism over stochasticity wherever movable"** as a standing architectural driver: whenever a decision can be moved from stochastic inference to deterministic logic (a rule, a constraint, a graph lookup, a typed schema), it must be moved. The ontology-as-constraint is the primary instrument — an agent cannot emit an account UUID that does not exist in the graph.

This is **not a one-time decision but an iterative loop**: as the system grows, we continuously identify decisions currently resolved by inference that can be migrated to deterministic logic.

### Criteria for migrating a decision to deterministic logic

A decision is a candidate for migration when ANY of these hold:
1. **Finite, enumerable decision space** — the set of valid outputs is known and closed (e.g., the valid account UUIDs, the valid jurisdictions). If the answer must come from a fixed set, a lookup/constraint beats inference.
2. **Verifiable correctness** — there exists a deterministic check that can confirm the output is correct. If we can write the validator, we can often write the resolver.
3. **High downstream fan-out** — the decision feeds many subsequent steps, so an error here contaminates a large subtree. High-fan-out decisions are prioritized for determinism.
4. **Repetition at scale** — the decision recurs frequently, so the cumulative inference cost (tokens, latency, energy) is significant.
5. **Regulatory or audit sensitivity** — the decision must be reproducible and explainable for compliance. Stochastic outputs are hard to audit.

A decision should REMAIN stochastic (handled by the model) when:
- The input space is genuinely open-ended (natural-language interpretation of an ambiguous source document).
- No closed set of valid outputs can be pre-specified.
- The cost of encoding the rule exceeds the cost of occasional inference plus human review.

### Signals / alerts we monitor to uphold the principle

These are the observability hooks that tell us the principle is (or is not) being honored. **Most are aspirational pending instrumentation — see Consequences.**
- **Inference-call ratio** — proportion of pipeline decisions resolved by inference vs deterministic logic. A rising ratio without a rising open-endedness of inputs is a red flag.
- **Token cost per transaction processed** — should trend down as more logic migrates to deterministic paths.
- **Residual-error locus** — where do errors actually occur? If errors cluster in decisions that *could* have been deterministic, those are migration targets (see ADR on harness / locus of error, pending).
- **Reproducibility rate** — fraction of decisions that yield identical output on re-run with identical input. Deterministic paths should be 100%.

## Consequences

### Positive
- Lower inference cost (tokens, latency, energy) — Kontablo demonstrates awareness of inference-cost consequences, a deliberate posture, not a marketing banner.
- Higher certainty and reproducibility, which matters for audit and compliance.
- Cleaner downstream propagation — early deterministic guarantees are inherited; early stochastic errors are not.

### Negative / Open
- Encoding rules has an up-front cost; over-aggressive determinism can produce brittle systems that fail on unanticipated inputs instead of degrading gracefully.
- The monitoring signals above are **not yet instrumented**. This ADR documents the principle and criteria; building the observability (inference-call ratio, token-cost tracking, residual-error locus analysis) is **future work and an explicit iteration loop**, not a completed capability. Do not claim these metrics exist until instrumented.

### Demonstration status
A concrete worked example (a decision migrated from inference to deterministic logic, with before/after token and reproducibility measurement) would strengthen the preprint. **As of this ADR, no such measured example exists.** If one can be produced within the publication scope, include it in the preprint; otherwise, the principle ships as stated design philosophy with the worked example labeled explicit future work.

## References
- Architectural principle #5 in `CLAUDE.md`.
- Relates to harness architecture and locus-of-error reframe (pending preprint section).
- Relates to ADR co-responsibility governance (residual error handled by governance, not by expecting model perfection).
- External grounding to verify before citing in preprint: literature on constrained decoding / grammar-constrained generation, and on LLM-agent harness design. Claude has NOT verified specific citations here — this requires a literature check in the preprint session.
