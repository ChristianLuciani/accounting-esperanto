# Draft: comment on Agentic Commerce Protocol SEP #135

> **FIRE WHEN:** the spoke-1 paper has its own DOI. Until then this is a draft.
>
> **Target:** [SEP #135 — "MCP Transport Binding for Agentic Checkout"](https://github.com/agentic-commerce-protocol/agentic-commerce-protocol/issues/135),
> Agentic Commerce Protocol (OpenAI + Stripe). Status `proposal`, opened
> 2026-02-12, last activity 2026-03-20.
>
> **Read before posting:** the thread has been quiet for months. Check whether it
> moved, merged, or was closed before posting a comment written against the
> 2026-03-20 state. If the SEP merged, this comment is obsolete and the
> extension draft becomes the only live move.

---

## Why comment at all

This is the cheapest possible participation — one comment on an open issue —
and its value is not persuasion. It is **presence in the thread before the spec
settles**, plus a dated public artifact.

There is also a substantive reason. SEP #135's motivation is framed entirely
around merchants: *"every agent framework that speaks MCP needs a bespoke adapter
to talk to ACP merchants."* A binding designed only for merchant endpoints may
not accommodate a **non-merchant service** that participates in the same
checkout flow — which is exactly what a semantic-resolution layer is. That is a
real, specific gap in their stated motivation, and pointing it out is useful to
them rather than self-serving.

## Tone constraints

- Offer a data point, do not pitch. No product framing, no links to anything
  commercial.
- Do not ask them to accommodate Kontablo. Ask whether the binding's shape
  accommodates a **category** of participant they have not named.
- Do not claim adoption or traction we do not have.
- One link maximum, to the DOI'd paper.

---

## Comment text

> **Implementer data point: a non-merchant participant in the same flow**
>
> We maintain a deterministic accounting-semantics service that already ships an
> MCP server — six tools, all graph lookups or fixed rules, no model in the call
> path — and we have been reading this SEP with an interest that is slightly
> off-centre from its stated motivation. Sharing it in case it is useful while
> the binding's shape is still open.
>
> The motivation here is framed around merchants: an agent that speaks MCP
> needing a bespoke adapter to reach ACP merchants. Our position in a checkout
> flow is different. We are not a merchant and we do not move value. We answer
> one question about a transaction — *which economic concept does this line item
> correspond to, in this jurisdiction's chart of accounts* — and we answer it
> deterministically, before the transaction commits, so that the buyer's and the
> seller's ledgers can post the same event identically.
>
> That makes us a third kind of participant: not the agent, not the seller, but a
> service both sides may consult about the same session. Two things about the
> binding matter for that shape, and both look like they are still decidable:
>
> 1. **Whether the OpenRPC mapping is scoped to the five checkout operations, or
>    to the transport generally.** If the binding standardises *how ACP concepts
>    map onto MCP tool calls* — headers, path params, status codes → JSON-RPC —
>    then a non-checkout service can adopt the same conventions and be callable
>    from the same client without special-casing. If it standardises only the
>    five operations, every adjacent service invents its own conventions again,
>    which is the fragmentation this SEP exists to remove, displaced one layer
>    out.
>
> 2. **Whether `transports` discovery is per-endpoint or per-participant.**
>    `rfc.discovery.md` puts `transports` in the seller's
>    `/.well-known/acp.json`. An agent that wants to consult a non-seller service
>    over MCP during a session has no equivalent discovery path today. Not
>    necessarily this SEP's problem — but worth knowing whether you consider it
>    in or out of scope, because the answer changes what adjacent services build.
>
> No ask attached. If the answer to both is "out of scope for this SEP", that is
> a perfectly good answer and we will work with it.
>
> For context on why the pre-transaction, deterministic framing matters to us,
> the invariants are written up here: [DOI].

---

## After posting

- Record the date and any response in `docs/strategy/protocol-compatibility-register.md`
  under the ACP row, per ADR-017 rule 4.
- **A reply that engages is the signal to proceed** to the accounting-semantics
  extension draft. Silence for 30 days is also a signal to proceed — but with
  the expectation lowered accordingly, and it should be recorded as such rather
  than quietly ignored.
