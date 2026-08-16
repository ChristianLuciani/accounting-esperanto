# Architecture Decision Record: ADR-017
# Title: Agent-Protocol Adoption Policy — open standards first, transport adapters over one brain, and the condition that would force a redesign
# Date: 2026-07-29
# Status: ACCEPTED

## Context

Architectural principle #4 already states that the agent-native layer is
"protocol-pluggable by design" and that Kontablo "will adopt and add any agentic
protocol that gains meaningful traction." That is a posture, not a policy: it
says nothing about *which* protocols get engineering effort, *how much*
compatibility costs, or *what* would make a protocol urgent rather than optional.

Three forces make the policy necessary now.

**It is too early to know which protocols become the standards.** The 2025–2026
agent-commerce stack is still consolidating: A2A moved from Google to the Linux
Foundation (2025-06-23), x402 moved from `coinbase/x402` to an independent x402
Foundation repo, and AP2's credential/mandate layer was donated to the FIDO
Alliance Payments Technical Working Group (announced 2026-04-28). Betting on one
protocol is a survival risk. Breadth of compatibility today is insurance against
a landscape that has not settled.

**The protocols are not all in the same layer, so "compatible with" costs
wildly different amounts.** A protocol where Kontablo is a *tool server* costs an
adapter. A protocol where Kontablo is an *agent peer* costs an adapter plus a
design question. A protocol that *moves money* costs no engineering at all,
because Kontablo is not a participant in it — its relationship is the semantic
annotation on the payload. Treating these as one category leads either to
over-building or to claiming compatibility that does not exist.

**The layer boundary that makes this cheap is an empirical fact, not an
assumption — and it could stop being true.** A survey of eleven protocols and
vendor programs (`docs/papers/spokes/agentic-provenance/research/dr1_agent_protocols.md`)
found that **none** defines, validates, or mentions which economic concept a
moved value should be posted to. They converge instead on identity,
authorization, value transfer, and interoperation. That is why protocol churn is
absorbable. If it changed, the absorbability would change with it.

## Decision

**1. Open standards before vendor programs.** Attention and engineering go to
protocols with a public, versioned, primary specification under open governance
(MCP, A2A, AP2, UCP, ACP, x402, ERC-8004) before proprietary network or vendor
programs (Visa Trusted Agent Protocol, Mastercard Agent Pay, Skyfire KYA). Vendor
programs are tracked, not built against, until one becomes a standard. Rationale:
an open spec can be read, cited, and implemented without a commercial
relationship, and it does not disappear when one company changes strategy.

**2. Adopt by transport adapter, never by forking the brain.** Every new
protocol face is an adapter over the same `core.harness` / `core.engine` logic
that already backs REST, gRPC and MCP. No protocol adapter may contain
accounting logic of its own. This is what makes breadth affordable, and it is why
the harness was extracted as an importable package (ADR-016 lineage). A protocol
that could only be supported by duplicating resolution logic is a protocol we do
not support.

**3. Classify before estimating.** Every protocol is placed in one of three
positions relative to Kontablo, because the position determines the cost:

| Position | Kontablo's role | What compatibility costs |
|---|---|---|
| **Tool surface** (MCP-shaped) | a server the agent calls | an adapter over the existing brain |
| **Agent peer** (A2A-shaped) | an agent publishing deterministic skills | an adapter, plus a design decision — Kontablo does not negotiate, so "agent" fits awkwardly |
| **Commerce / settlement** (AP2, UCP, ACP, x402, ERC-8004) | **not a participant**; the semantic annotation on the payload | usually no engineering — the work is standards participation to make an accounting-semantics field expressible |

The third row is the one that gets mis-estimated. Kontablo does not move money
and does not need to implement a payment protocol to be useful to it.

**4. Standards participation is a first-class activity, not overhead.** For the
commerce/settlement row, the highest-leverage move is a spec contribution — an
extension, a transport binding, a field — not code. An open proposal still in
`proposal` status is the cheapest moment to influence a standard, and is
therefore treated as an opportunity with a deadline.

**5. Never claim compatibility that has not been exercised.** A compatibility
claim derived from *reading* a specification is a structural claim and must be
labeled as such. Only an interop test against a real client upgrades it to a
verified claim. This is the claims–evidence rule applied to interoperability:
"the spec says our transport is supported" and "we ran their client against our
server" are different sentences and must not be conflated in public wording.

**6. One escalation condition.** The only development that turns protocol work
from optional into urgent is **a protocol beginning to specify accounting
semantics** — which concept a moved value posts to, or a requirement that a
booking be reconstructible. That would collapse the layer boundary Kontablo's
positioning rests on, and it is the single condition worth watching continuously.
Everything else is a scheduling question.

The living state of all of this — per-protocol status, verified facts with dates
and sources, and the monitoring triggers — is maintained in
[`docs/strategy/protocol-compatibility-register.md`](../strategy/protocol-compatibility-register.md).
This ADR is the policy; that file is the state. Update the register per release;
update this ADR only when the policy itself changes.

## Consequences

**Easier.** Breadth becomes cheap and predictable: a new tool-surface protocol is
an adapter, and a new settlement protocol is usually a spec conversation. The
register gives a single answer to "are we compatible with X?" that distinguishes
*implemented* from *structurally reachable* from *not addressed*, so public
wording cannot drift into overclaiming. Prioritizing open governance keeps the
work citable and independent of any vendor's roadmap.

**Harder.** The register is a maintenance obligation: protocols that version by
date (UCP, ACP both do) invalidate verified facts silently, so a stale register is
worse than none. Rule 5 also means Kontablo will sometimes have to say "the spec
says this should work, and we have not tested it" where a competitor would simply
claim support — a deliberate cost of the epistemic standard.

**Accepted risk.** Declining to build against vendor programs means that if a
proprietary program becomes the de facto standard before it becomes an open one,
Kontablo arrives late. The judgment is that arriving late to one vendor program is
cheaper than spreading engineering across programs that mostly will not survive,
and that the adapter-over-one-brain rule keeps the catch-up cost low.
