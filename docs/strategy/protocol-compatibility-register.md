# Agent-protocol compatibility register

**Living document. Policy: [ADR-017](../adr/017-agent-protocol-adoption-policy.md).**
This file is the *state*; the ADR is the *policy*. Review per Kontablo release,
and before any public claim of protocol compatibility.

**Last full verification: 2026-07-29** (Agent Client Protocol verdict and the ACP name-collision warning added the same day). Facts marked *verified* were retrieved
from the protocol's own primary specification on that date, with the source
given. Facts inherited from the DR1 protocol survey
(`docs/papers/spokes/agentic-provenance/research/dr1_agent_protocols.md`,
verified 2026-07-24) are marked as such.

---

## ⚠️ Read this before writing "ACP" anywhere

**Three different protocols are called ACP.** This has already cost one round of
misdirected research (2026-07-29: a survey of the commerce ACP was carried out
when the protocol under discussion was the editor one). Always write the name in
full on first use.

| Name | Owner | What it is | Status here |
|---|---|---|---|
| **Agentic Commerce Protocol** | OpenAI + Stripe | Agent-driven checkout and commerce | In the open-standards section below |
| **Agent Client Protocol** | Zed | Editor ↔ coding-agent communication | **Out of scope** — see below |
| **Agent Communication Protocol** | IBM / BeeAI | Agent-to-agent messaging | Not surveyed; reported to have largely converged toward A2A. Verify before citing |

Unqualified "ACP" in this register always means the **Agentic Commerce
Protocol**. Everywhere else, spell it out.

This is a general argument for the project's own naming discipline: Kontablo
coins its distinctive terms in full ("loss ledger", "pre-transaction fiber
query", "ontology-as-constraint") precisely so they cannot collide this way.

---

## How to read the status column

Per ADR-017 rule 5, three different things are deliberately not collapsed into
one word:

| Status | Means |
|---|---|
| **Implemented** | Kontablo exposes this face; there is code and there are tests |
| **Structurally reachable** | The protocol's own spec names a transport Kontablo already implements, so it *should* work — **read from the spec, not exercised against a client.** Not a verified interop claim |
| **Not addressed** | No adapter, no spec work. Not a judgment that it is unimportant |
| **Track only** | Vendor program, not an open standard — watched, not built against |

Saying "we support X" when the register says *structurally reachable* is an
epistemic-standards violation, not a marketing shortcut.

---

## Open standards — where attention goes first

### MCP — Model Context Protocol
- **Layer:** tool surface. Kontablo is a server the agent calls.
- **Governance:** open spec, Anthropic-originated.
- **Status: IMPLEMENTED.** `api/mcp/server.py`, official MCP/FastMCP SDK, stdio
  transport. Six deterministic tools (`resolve_account`, `get_account`,
  `validate_balance_sheet`, `consolidate_trial_balances`, `get_node_fiber`,
  `list_jurisdictions`); none calls a language model. Tests:
  `tests/mcp/test_mcp_server.py` (hermetic, keyless). Verify with
  `grep -c "@server.tool(" api/mcp/server.py` → 6.
- **Honesty bar:** deterministic core implemented, Tier-3/LLM tools planned.
  **Not** feature parity with REST.
- **Why it matters disproportionately:** MCP is the transport that other
  protocols name. Two independent commerce protocols (UCP, ACP) route to MCP,
  so this one adapter does most of the compatibility work in the stack.

### UCP — Universal Commerce Protocol (Google + Shopify)
- **Layer:** commerce orchestration. Kontablo is not a participant.
- **Governance:** Apache-2.0, spec versioned by date (`2026-04-08` current at
  verification).
- **Status: STRUCTURALLY REACHABLE via the MCP transport — no new code.**
- **Verified 2026-07-29** (`https://ucp.dev/2026-04-08/specification/overview/`):
  UCP defines **four** transports — REST (core), **MCP** (JSON-RPC), **A2A**, and
  Embedded. Businesses "MAY expose an A2A agent."
- **Verified constraint that matters for design:** UCP has **no
  arbitrary-metadata extension on carts or line items.** Its extension model is
  *capability-level* — extensions declare functionality via an `extends` field on
  capability definitions. There is a separate `signals` mechanism for
  environmental context (IP, user agent, attestations), which is **not** an
  extensible metadata system for commerce objects. So the naive
  "add a `kontablo_uuid` field to the line item" play is **not available** here;
  carrying accounting semantics through UCP would require a capability extension,
  which is a heavier standards move.
- **Next action:** run a UCP client against the Kontablo MCP server to upgrade
  *structurally reachable* → *verified*. Until then, do not claim UCP support in
  public wording.

### ACP — Agentic Commerce Protocol (OpenAI + Stripe)
- **Layer:** commerce orchestration. Kontablo is not a participant.
- **Governance:** Apache-2.0, spec versioned by date. Version history in-repo:
  `2025-09-29` → `2025-12-12` → `2026-01-16` → `2026-01-30` → `2026-04-17`
  (current at verification). Fast cadence — re-verify often.
- **Status: NOT ADDRESSED today; a live open proposal is the entry point.**
- **Verified 2026-07-29** (GitHub API against
  `agentic-commerce-protocol/agentic-commerce-protocol`):
  - Primary transport is REST, described by OpenAPI
    (`spec/2026-04-17/openapi/`), with JSON Schema data models.
  - **An MCP transport binding exists as an open proposal: SEP #135,
    "[SEP][Proposal]: MCP Transport Binding for Agentic Checkout", status
    `proposal`, type Major Change, opened 2026-02-12, last updated 2026-03-20.**
    Its abstract: ACP's REST API "means every agent framework that speaks MCP
    needs a bespoke adapter to talk to ACP merchants"; the SEP proposes "an
    OpenRPC schema that maps ACP's 5 checkout operations to MCP tools" and is
    "purely additive."
  - The binding is already visible in shipped artifacts: `rfcs/rfc.discovery.md`
    defines a `/.well-known/acp.json` document whose `transports` enum includes
    **`mcp`** ("Model Context Protocol server"), with the worked example
    `"transports": ["rest", "mcp"]`; and
    `spec/2026-04-17/openrpc/openrpc.agentic_checkout.json` is present in the
    current spec version (OpenRPC being the JSON-RPC description format MCP
    uses). Earlier spec versions have no `openrpc/` directory.
  - **Extension mechanism** (`rfcs/rfc.extensions.md`): extensions attach at the
    **checkout-session** level — `CheckoutSessionCreateRequest`,
    `CheckoutSessionUpdateRequest`, `CheckoutSession` — not at cart or line-item
    level. They declare their fields with JSONPath in an `extends` array and are
    negotiated through `capabilities.extensions`. Normative limits: extensions
    "**MAY** add new optional fields to the checkout object" but "**MUST NOT**
    modify existing required fields" and "**MUST NOT** change the semantics of
    existing fields."
- **Design consequence:** an accounting-semantics extension *is* expressible
  here (an optional field on the checkout object), but because extensions attach
  at session level rather than per item, it must carry a **mapping** — line-item
  identifier → Kontablo UUID — rather than annotating items in place.
- **Contribution drafted and staged:** `docs/standards/acp-sep135-mcp-transport-comment.md`
  (comment on SEP #135) and `docs/standards/acp-accounting-semantics-extension.md`
  (an `accounting_semantics` extension RFC, deliberately ontology-neutral). Both
  carry a FIRE WHEN gate — not to be posted before the spoke-1 paper has a DOI,
  because a contribution that can cite a published result is a different document
  from one that cannot.
- **Next action — this is the cheapest high-leverage move on the board.**
  SEP #135 is `proposal` and open. An open proposal is the moment an outside
  contributor has influence; once it merges, the window narrows to filing a new
  extension against a settled spec. Two separable moves: (a) participate in
  SEP #135 so the MCP binding lands in a shape Kontablo can serve; (b) draft an
  accounting-semantics extension against `rfcs/rfc.extensions.md`.

### A2A — Agent2Agent
- **Layer:** agent-to-agent task delegation. Kontablo would be an agent peer.
- **Governance:** **Linux Foundation since 2025-06-23** (founding members AWS,
  Cisco, Google, Microsoft, Salesforce, SAP, ServiceNow) — de-vendored, open to
  contribution. *(DR1)*
- **Status: NOT ADDRESSED.**
- **Cost and the honest caveat:** an adapter over the existing brain, plus a
  design question. A2A is built for peers that negotiate and delegate tasks;
  Kontablo is deterministic and does not negotiate. It would publish an agent
  card advertising deterministic skills — legitimate, but against the grain of
  A2A's design intent, and worth deciding deliberately rather than by analogy to
  the MCP adapter.
- **Second-order value:** UCP names A2A as a transport, and ERC-8004 and x402
  build on it, so an A2A face compounds.

### AP2 — Agent Payments Protocol
- **Layer:** payment authorization. Kontablo is not a participant.
- **Governance:** Google-originated; the **credential/mandate layer was donated
  to the FIDO Alliance** Payments Technical Working Group (chaired by Mastercard
  and Visa), announced 2026-04-28, the same day as AP2 v0.2.0. *(DR1)*
- **Status: NOT ADDRESSED.** The paper describes AP2 integration as asserted
  architecture, not running code — keep it that way in all public wording.
- ⚠️ **Documented citation trap.** Most secondary sources describe AP2 as having
  **three** mandates ("Intent, Cart, Payment"). That is the **v0.1 model
  (2025-09-16)**. The **v0.2 spec (2026-04-28)** restructured to **two** mandate
  types — a `Checkout Mandate` (with `Open`/`Closed` sub-states) and a
  `Payment Mandate`. Any citation must use current terminology or explicitly
  date-scope the older one. *(DR1)*
- **Intervention assessment:** influencing AP2's semantics now means
  participating in a FIDO Alliance working group chaired by the card networks.
  Heavy institutional lift, low near-term return for an independent researcher.
  Track; do not pursue.

### x402
- **Layer:** settlement. Kontablo is not a participant.
- **Governance:** moved from `coinbase/x402` to an independent **x402 Foundation**
  repo. *(DR1)*
- **Status: NOT ADDRESSED**, and largely covered indirectly — x402's own spec
  lists its transport-representation layer as depending on **HTTP, MCP, A2A**.
  *(DR1)* Carries an explicit out-of-scope list; says nothing about accounting
  semantics.

### ERC-8004
- **Layer:** on-chain identity, reputation, validation registries. Extends A2A.
- **Governance:** Ethereum EIP process.
- **Status: NOT ADDRESSED.**
- **Verbatim, and load-bearing for Kontablo's positioning:** "Payments are
  orthogonal to this protocol and not covered here." *(DR1)* A protocol that
  explicitly disclaims payments is not going to define posting semantics.

---

## Out of scope — recorded so the question is not re-asked

### Agent Client Protocol (Zed) — not Kontablo's layer
- **What it is, verbatim from its own README:** it "standardizes communication
  between *code editors* (interactive programs for viewing and editing source
  code) and *coding agents* (programs that use generative AI to autonomously
  modify code)."
- **Verified 2026-07-29** via the GitHub API on
  `agentclientprotocol/agent-client-protocol`: created 2025-06-23, ~3.8k stars,
  pushed the same day it was checked — genuinely active, not abandoned. Stable
  protocol version `1`; JSON-RPC wire format with capability negotiation at
  `initialize` via `protocolVersion`; JSON Schema artifacts under `schema/v1` and
  `schema/v2`; Rust crates `agent-client-protocol` and
  `agent-client-protocol-schema`.
- **Verdict: OUT OF SCOPE.** It is developer tooling, not the agent economy.
  There is no transaction in its path, no value transfer, and therefore no
  accounting semantics to supply. Kontablo has nothing to offer it and nothing to
  gain from it. Its traction is real but irrelevant to this layer.
- **Why it is recorded anyway.** Two reasons. First, it is structurally the same
  *shape* as MCP in a different domain — a JSON-RPC tool/context protocol between
  a host and an agent — which is evidence for ADR-017's category argument that
  agent-native transports proliferate and betting on one is a survival risk.
  Second, so this question is not researched twice.
- **Monitoring condition — the only thing that would change the verdict:** if it
  developed a *general* tool-calling surface and began displacing MCP outside
  coding, Kontablo would need an adapter for it, on exactly the same
  adapter-over-one-brain terms as any other tool-surface protocol. Today it is
  coding-specific. Watch for scope expansion beyond editors and coding agents,
  not for adoption growth — growth within its own domain changes nothing here.

---

## Vendor programs — track only, do not build against

Per ADR-017 rule 1. These are real and operative, but they are commerce and
security *programs*, not open standards, and must not be given the same
epistemic weight as the spec-track protocols above. *(All DR1.)*

| Program | Note |
|---|---|
| Visa Trusted Agent Protocol / Intelligent Commerce | Fetched directly in DR1; real and operative |
| Mastercard Agent Pay | Only reachable via search-index snippets — `developer.mastercard.com` and `mastercard.com` returned 403 on direct fetch. Cite as a vendor program, never as a spec |
| Skyfire KYA | Vendor identity/payment program |
| FIDO Alliance Agentic Authentication + Payments WGs | A standards body rather than a vendor, but institutional; relevant mainly because AP2's mandate layer landed there |

**Escalation rule for this table:** a vendor program moves up to the open-standards
section only when it publishes a public, versioned specification under governance
that does not require a commercial relationship to implement.

---

## What needs monitoring, and what each trigger means

Ordered by consequence, not by likelihood.

### 1. ESCALATE — a protocol starts specifying accounting semantics
**The only condition that threatens a redesign.** Watch for any of these
protocols beginning to define, validate, or require: which economic concept a
moved value posts to; a chart-of-accounts or taxonomy binding; or a requirement
that a booking be reconstructible from the payload.

**Current state: zero of eleven protocols surveyed do any of this** (DR1,
2026-07-24 — MCP, A2A, AP2, UCP, x402, ERC-8004, ACP, Visa TAP, Mastercard Agent
Pay, Skyfire KYA, FIDO agentic WGs; no exceptions found). They converge on
identity, authorization, value transfer, and interoperation.

If this changes, the layer boundary that makes Kontablo's positioning coherent —
and that makes every other row in this register cheap — is under pressure, and
the response is a strategy decision, not an adapter.

### 2. ACT — an open protocol opens a window where accounting semantics fit
An extension mechanism, a transport binding, or a metadata field under active
proposal. These windows close. **Live now: ACP SEP #135** (MCP transport binding,
`proposal`, open) and the **ACP Extensions RFC**. This is where standards
participation buys the most per hour, and where ADR-017 rule 4 applies.

### 3. VERIFY — a protocol we claim reachability with changes its spec
UCP and ACP both version by date, and ACP's cadence is roughly quarterly
(`2025-09-29` → `2026-04-17` across five versions). A transport list or extension
rule can change without notice, silently invalidating a *structurally reachable*
status here. Re-verify the transport table of every protocol in the open-standards
section at each Kontablo release, and always before a public compatibility claim.

### 4. UPGRADE — turn structural claims into tested ones
The register currently contains **one** *structurally reachable* entry (UCP via
MCP) and **zero** verified interop tests. Running a real UCP or ACP client against
`api/mcp/server.py` is the single cheapest thing that would strengthen the
compatibility story, because it converts a spec-reading claim into an evidenced
one under the project's own claims–evidence rule.

### 5. IGNORE unless promoted — vendor programs
Track adoption; do not spend engineering. Promotion criterion is in the vendor
table above.

---

## Summary — one line per protocol

| Protocol | Layer | Governance | Status |
|---|---|---|---|
| MCP | tool surface | open | **Implemented** (6 deterministic tools) |
| UCP | commerce | open (Apache-2.0) | **Structurally reachable** via MCP transport — untested |
| ACP | commerce | open (Apache-2.0) | Not addressed — **MCP binding is a live open proposal (SEP #135)** |
| A2A | agent peer | open (Linux Foundation) | Not addressed — adapter + a design question |
| AP2 | payment auth | open → FIDO Alliance | Not addressed — asserted architecture only |
| x402 | settlement | open (x402 Foundation) | Not addressed — depends on HTTP/MCP/A2A anyway |
| ERC-8004 | identity/reputation | open (EIP) | Not addressed — disclaims payments explicitly |
| Visa TAP · Mastercard Agent Pay · Skyfire KYA | vendor | proprietary | **Track only** |
| Agent Client Protocol (Zed) | editor ↔ coding agent | open | **Out of scope** — no transaction in its path |
