# DR1 — Agent payment & interoperation protocols, and what they do NOT specify

> Deep-research note for Spoke 1 ("Agentic Provenance"). Feeds `T1` (Related
> Work + `references.bib`) and the positioning argument in `main.tex` (the
> paragraph around lines 89–100 and the "narrow contribution" paragraph around
> lines 322–337). Research date: 2026-07-24. All sources below were retrieved
> live via `WebSearch`/`WebFetch`/`gh api`/`curl` in this session — none are
> recalled from training data. Today's date for the purposes of "how current
> is this" framing is 2026-07-24; several cited specs postdate a 2025 training
> cutoff and are volatile (see §e).

---

## (a) Executive summary

- **Central finding — strongly corroborated, zero exceptions found:** across
  eleven independently-verified protocols/frameworks spanning the full
  agent-commerce stack (MCP, A2A, AP2, UCP, x402, ERC-8004, ACP, Visa Trusted
  Agent Protocol / Intelligent Commerce, Mastercard Agent Pay, Skyfire KYA,
  FIDO Alliance Agentic Authentication + Payments working groups), **none
  specifies anything about accounting-semantic correctness** — none defines,
  validates, or even mentions which economic/business account a moved value
  should be posted to, or how a booking is reconstructed. They converge on
  four concerns instead: **identity** (is this agent who it claims to be),
  **authorization** (did a human/principal actually consent to this), **value
  transfer/settlement** (did the money move, exactly once, to the right
  counterparty), and **interoperation** (can two agents built by different
  vendors talk at all). This cleanly and honestly substantiates the paper's
  positioning claim in `main.tex:93–96`.
- **The stack is layered, and the layers cross-reference each other in their
  own primary docs** — this is not the paper's framing imposed from outside,
  it is how the protocol authors describe themselves: UCP (commerce
  orchestration, Google+Shopify) explicitly runs over MCP or A2A as transport
  and explicitly supports "the AP2 Mandates Extension" for payment
  authorization; AP2 is explicitly "available as an extension for... A2A...
  and Universal Commerce Protocol"; ERC-8004 explicitly extends A2A with
  on-chain identity/reputation/validation registries; x402's own spec lists
  its transport-representation layer as depending on "HTTP, MCP, A2A." None
  of these cross-references ever touches accounting semantics.
- **Governance is actively de-vendoring in 2025–2026** — a trend worth naming
  in the paper as evidence these are becoming *infrastructure*, not one
  company's toy: A2A moved from Google to the **Linux Foundation**
  (2025-06-23, founding members AWS/Cisco/Google/Microsoft/Salesforce/SAP/
  ServiceNow); x402 moved from `coinbase/x402` to an independent
  **x402 Foundation** repo; AP2's credential/mandate layer was donated to the
  **FIDO Alliance** (Payments Technical Working Group, chaired by Mastercard
  and Visa, announced 2026-04-28, same day as AP2 v0.2.0).
- **A genuine spec-instability trap, caught by going to primary sources
  instead of secondary summaries:** most blog/vendor secondary sources (and
  the first-pass web search in this session) describe AP2 as having **three**
  mandates — "Intent Mandate, Cart Mandate, Payment Mandate." That is the
  **v0.1 model (2025-09-16)**. The **current v0.2 spec (released
  2026-04-28, fetched directly from the AP2 GitHub repo in this session)**
  restructured this to **two** mandate types — a `Checkout Mandate` (with
  `Open`/`Closed` sub-states) and a `Payment Mandate`. Any citation of AP2's
  mandate architecture in the paper must use current terminology or explicitly
  date-scope the older one. This is flagged prominently because it is exactly
  the kind of drift the project's own epistemic rules exist to catch.
- **Two tiers of source strength, both real but distinguishable:** (1) open
  protocols with public, versioned, primary specs I fetched directly —
  AP2, A2A, MCP, x402, ERC-8004, ACP, UCP — are strong, citable,
  spec-grounded sources; (2) proprietary network/vendor programs — Visa
  Trusted Agent Protocol, Mastercard Agent Pay, Skyfire KYA — are real and
  operative (Visa fetched directly; Mastercard only reachable via search-index
  snippets because `developer.mastercard.com`/`mastercard.com` 403'd direct
  fetch in this session) but are vendor commerce/security programs, not
  open standards, and should be cited as such rather than given the same
  epistemic weight as the spec-track protocols.
- **No sub-question came up empty.** Every protocol named in the task prompt
  (AP2, A2A, MCP, x402, ERC-8004, Skyfire, Visa, Mastercard) was verifiably
  sourced; the survey additionally surfaced two protocols not in the original
  prompt but directly load-bearing for the positioning argument — **UCP**
  (Universal Commerce Protocol, Google+Shopify) and the **OpenAI/Stripe
  Agentic Commerce Protocol (ACP)** — both fetched from primary sources and
  included because AP2's own docs cite UCP as a sibling extension point, and
  ACP is the OpenAI-ecosystem analogue to UCP+AP2 that a cs.MA reviewer would
  ask "what about ChatGPT checkout?" if it were omitted.

---

## (b) Vetted sources table

All rows are **VERIFIED** (retrieved live this session, working URL) unless
marked otherwise. "Type" follows the project's primary > secondary hierarchy.

| # | Source | Type | What it establishes | Verify by |
|---|---|---|---|---|
| 1 | Google, *AP2 specification.md* (v0.2), `github.com/google-agentic-commerce/AP2` | **official spec** (primary) | Full role model (5 roles), Mandate architecture (Checkout + Payment, current), explicit statement that "the exact details of the Commerce Protocol... are outside the scope of AP2" | `curl -s https://raw.githubusercontent.com/google-agentic-commerce/AP2/main/docs/ap2/specification.md` |
| 2 | Google, *AP2 docs index* (`docs/index.md`), same repo | **official spec/docs** (primary) | "What is AP2" framing, relationship to A2A/MCP/UCP, Core Principles list, Verifiable Digital Credential model | `curl -s https://raw.githubusercontent.com/google-agentic-commerce/AP2/main/docs/index.md` |
| 3 | Google, *AP2 FAQ* (`docs/faq.md`), same repo | **official docs** (primary) | Explicit Q&A: "How does AP2 address transaction accountability?" — answer is entirely about dispute evidence/liability, never touches booking/ledger semantics | `curl -s https://raw.githubusercontent.com/google-agentic-commerce/AP2/main/docs/faq.md` |
| 4 | Google, *AP2 CHANGELOG.md*, same repo | **official spec** (primary) | Version history: `0.1.0` (2025-09-16, original release), `0.2.0` (2026-04-28, current — mandate model restructured) | `curl -s https://raw.githubusercontent.com/google-agentic-commerce/AP2/main/CHANGELOG.md` |
| 5 | Google Cloud Blog, "Announcing Agent Payments Protocol (AP2)" | **official announcement** (primary) | Sept 16 2025 launch, 60+ launch partners incl. Mastercard/PayPal/Coinbase/Amex/Salesforce | https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol |
| 6 | GitHub, `google-agentic-commerce/AP2` license file | **primary artifact** | License = Apache-2.0 | `gh api repos/google-agentic-commerce/AP2/license` |
| 7 | A2A Project, *A2A Specification* (v1.0.0), `a2a-protocol.org/latest/specification/` | **official spec** (primary) | Agent Cards, Tasks (stateful lifecycle), transport bindings (JSON-RPC/gRPC/HTTP), explicit purpose statement ("bridge the communication gap between disparate agentic systems"); zero payment/accounting content | https://a2a-protocol.org/latest/specification/ |
| 8 | Google Developers Blog, "A2A: a new era of agent interoperability" | **official announcement** (primary) | Original A2A announcement, **2025-04-09**, 50+ launch partners (Atlassian, Box, Salesforce, SAP, ServiceNow, PayPal, etc.) | https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/ |
| 9 | Google Developers Blog, "Google Cloud donates A2A to Linux Foundation" | **official announcement** (primary) | **2025-06-23**: governance transfer to Linux Foundation; founding members AWS, Cisco, Google, Microsoft, Salesforce, SAP, ServiceNow | https://developers.googleblog.com/en/google-cloud-donates-a2a-to-linux-foundation/ |
| 10 | GitHub, `a2aproject/A2A` license file | **primary artifact** | License = Apache-2.0 | `gh api repos/a2aproject/A2A/license` |
| 11 | PR Newswire, "A2A Protocol Surpasses 150 Organizations..." | **press release** (secondary but verifiable) | Adoption-scale claim (150+ orgs, ~1 yr post-launch, production deployments) — use only for "this is not a toy" framing, not for scope claims | https://www.prnewswire.com/news-releases/a2a-protocol-surpasses-150-organizations-lands-in-major-cloud-platforms-and-sees-enterprise-production-use-in-first-year-302737641.html |
| 12 | Anthropic, *Model Context Protocol specification*, 2025-11-25 revision | **official spec** (primary) | Hosts/Clients/Servers model, Resources/Prompts/Tools, and — critical quote — "**While MCP itself cannot enforce these security principles at the protocol level**, implementors SHOULD..." (Security and Trust & Safety §) | https://modelcontextprotocol.io/specification/2025-11-25 |
| 13 | Anthropic, *MCP spec changelog*, 2025-11-25 vs 2025-06-18 | **official spec** (primary) | Confirms iterative SEP-driven revision process and a formal "Governance and process updates" track (SEP-932 formalized MCP governance) | https://modelcontextprotocol.io/specification/2025-11-25/changelog |
| 14 | Anthropic, "Introducing the Model Context Protocol" | **official announcement** (primary) | **2024-11-25** open-source release, opening framing ("connecting AI assistants to the systems where data lives"); no accounting/bookkeeping mention anywhere | https://www.anthropic.com/news/model-context-protocol |
| 15 | GitHub, `modelcontextprotocol/modelcontextprotocol` README | **primary artifact** | License = MIT (stated explicitly in README text; GitHub's auto-detector returns `NOASSERTION`, the README text is the authoritative statement) | https://github.com/modelcontextprotocol/modelcontextprotocol/blob/main/README.md |
| 16 | Coinbase / x402 Foundation, *x402 Specification v2*, dated **2025-12-9** | **official spec** (primary) | Explicit "Out of Scope" list (transport specifics, client budget mgmt, session handling); Architecture = Types/Logic/Representation; version table confirms v2.0 (2025-12-9) supersedes v0.2 (2025-10-3) | `curl -s https://raw.githubusercontent.com/coinbase/x402/main/specs/x402-specification-v2.md` (version table at line ~715–718) |
| 17 | GitHub, `coinbase/x402` README + governance note | **primary artifact** | Repo description: "open standard for internet native payments"; explicit governance-transfer note: "We've moved the x402 repo under the x402 Foundation repo... `coinbase/x402` is now a development fork"; License = Apache-2.0 | https://github.com/coinbase/x402 ; `gh api repos/coinbase/x402/license` |
| 18 | GitHub, `x402-foundation/x402` | **primary artifact** | Confirms independent foundation now hosts canonical issues/PRs, not Coinbase alone | https://github.com/x402-foundation/x402 |
| 19 | Ethereum, **EIP-8004** ("Trustless Agents"), status **Draft** | **standard, in-progress** (primary — official EIP registry) | Authors De Rossi/Crapis/Jordan Ellis/Reppel; created 2025-08-13; abstract verbatim: "propose to use blockchains to discover, choose, and interact with agents across organizational boundaries without pre-existing trust"; three registries (Identity/Reputation/Validation); **explicit quote: "Payments are orthogonal to this protocol and not covered here"** | https://eips.ethereum.org/EIPS/eip-8004 |
| 20 | Etherscan, ERC-8004 Identity Registry contract | **primary, independently checkable on-chain record** | Contract live at `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` on Ethereum mainnet — confirms "Draft" EIP status and "live reference deployment" are simultaneously true (a maturity nuance worth stating explicitly, not conflating) | https://etherscan.io/address/0x8004A169FB4a3325136EB29fA0ceB6D2e539a432 |
| 21 | Forbes, "AI Agents Gain Trust Via Ethereum: ERC-8004 On Mainnet" | **news** (secondary) | Corroborates Jan 29 2026 mainnet date in independent editorial coverage | https://www.forbes.com/sites/digital-assets/2026/02/05/ai-agents-gain-trust-via-ethereum-erc-8004-on-mainnet/ |
| 22 | OpenAI + Stripe, `agentic-commerce-protocol/agentic-commerce-protocol` README | **official spec** (primary) | "Interaction model and open standard for connecting buyers, their AI agents, and businesses to complete purchases"; maintained by OpenAI+Stripe; **beta**; version **2026-04-17**; License = Apache-2.0; no accounting-semantic language | https://github.com/agentic-commerce-protocol/agentic-commerce-protocol |
| 23 | Stripe, *Agentic Commerce Protocol* docs | **official docs** (primary) | Product-discovery/checkout/delegate-token flow detail, single-seller/single-amount/short-TTL token scoping | https://docs.stripe.com/agentic-commerce/acp |
| 24 | Visa, *Trusted Agent Protocol* developer overview | **official docs** (primary) | Part of Visa Intelligent Commerce; cryptographic, merchant-and-purpose-scoped, time-bound, non-replayable signatures for agent traffic; framed as solving agent-vs-bot classification, not accounting | https://developer.visa.com/capabilities/trusted-agent-protocol/overview |
| 25 | Mastercard, Agent Pay pages (multiple `mastercard.com` URLs) | **official product page** (secondary retrieval — see caveat) | "Agentic Tokens," Agent Pay Acceptance Framework (agent registration/verification before transacting), contribution to FIDO Payments Working Group. **Caveat: `WebFetch` was blocked with HTTP 403 on every direct `mastercard.com` URL tried; this content is search-index-snippet-verified only, not full-page-fetched.** Treat as one notch below the other rows. | https://www.mastercard.com/us/en/business/artificial-intelligence/mastercard-agent-pay.html (fetch blocked; content via search index) |
| 26 | Skyfire, "Know Your Agent (KYA)" page | **official product page** (primary) | Confirms KYA is a **Skyfire product/protocol**, not a body-submitted open standard; JWT-based, OAuth2/JWKS-compatible; explicitly about identity/authentication, not accounting | https://skyfire.xyz/know-your-agent-kya/ |
| 27 | BusinessWire, "Skyfire Launches Open KYAPay Protocol With Agent Checkout" | **press release** (secondary but verifiable) | 2025-06-26 launch date for KYAPay/Agent Checkout | https://www.businesswire.com/news/home/20250626772489/en/Skyfire-Launches-Open-KYAPay-Protocol-With-Agent-Checkout |
| 28 | FIDO Alliance, "FIDO Alliance to Develop Standards for Trusted AI Agent Interactions" | **official announcement** (primary) | **2026-04-28**: Agentic Authentication Technical WG (chaired by CVS Health/Google/OpenAI) + Payments TWG (chaired by Mastercard+Visa); three focus areas (Verifiable User Instructions, Agent Authentication, Trusted Delegation for Commerce) — explicitly about identity/authorization, not accounting/bookkeeping semantics | https://fidoalliance.org/fido-alliance-to-develop-standards-for-trusted-ai-agent-interactions/ |
| 29 | Google/Shopify, *Universal Commerce Protocol (UCP) specification overview*, v2026-04-08 | **official spec** (primary) | Discovery/negotiation, payment-handler architecture, transports = REST/MCP/A2A/Embedded; explicit statement it "supports the AP2 Mandates Extension"; zero accounting/ledger provisions | http://ucp.dev/2026-04-08/specification/overview/ |
| 30 | GitHub, `universal-commerce-protocol/ucp` license file | **primary artifact** | License = Apache-2.0 | `gh api repos/universal-commerce-protocol/ucp/license` |

---

## (c) BibTeX — strongest sources, ready to paste

Keys upgrade the seeds already in `references.bib` (`mcp_spec`, `a2a_spec`,
`ap2_spec` — currently stubs with `TODO(T1/DR1)` notes) and add the new
protocols. Every field below is drawn from a source in table (b); nothing is
invented. `urldate` = 2026-07-24 (this session).

```bibtex
% ---- Google Agent Payments Protocol (AP2) ----
@online{ap2_spec,
  title        = {{Agent Payments Protocol (AP2) Specification, v0.2}},
  author       = {{Google}},
  organization = {Google (google-agentic-commerce)},
  year         = {2026},
  url          = {https://github.com/google-agentic-commerce/AP2/blob/main/docs/ap2/specification.md},
  urldate      = {2026-07-24},
  note         = {License Apache-2.0. v0.2 released 2026-04-28, restructured
                  Mandate model (Checkout + Payment) vs the v0.1 (2025-09-16)
                  Intent/Cart/Payment model many secondary sources still
                  describe -- cite the version explicitly.}
}

@online{ap2_announcement,
  title        = {{Announcing Agent Payments Protocol (AP2)}},
  author       = {{Google Cloud}},
  year         = {2025},
  url          = {https://cloud.google.com/blog/products/ai-machine-learning/announcing-agents-to-payments-ap2-protocol},
  urldate      = {2026-07-24},
  note         = {2025-09-16 launch announcement; 60+ launch partners
                  including Mastercard, PayPal, Coinbase, American Express.}
}

% ---- Agent2Agent (A2A) ----
@online{a2a_spec,
  title        = {{Agent2Agent (A2A) Protocol Specification, v1.0.0}},
  author       = {{A2A Project}},
  organization = {Linux Foundation},
  year         = {2026},
  url          = {https://a2a-protocol.org/latest/specification/},
  urldate      = {2026-07-24},
  note         = {License Apache-2.0. Originally announced by Google
                  2025-04-09; governance donated to the Linux Foundation
                  2025-06-23 (founding members AWS, Cisco, Google, Microsoft,
                  Salesforce, SAP, ServiceNow).}
}

@online{a2a_lf_donation,
  title        = {{Google Cloud Donates A2A to Linux Foundation}},
  author       = {{Google Developers Blog}},
  year         = {2025},
  url          = {https://developers.googleblog.com/en/google-cloud-donates-a2a-to-linux-foundation/},
  urldate      = {2026-07-24},
  note         = {2025-06-23 governance transfer announcement.}
}

% ---- Model Context Protocol (MCP) ----
@online{mcp_spec,
  title        = {{Model Context Protocol (MCP) Specification, 2025-11-25 revision}},
  author       = {{Anthropic}},
  year         = {2026},
  url          = {https://modelcontextprotocol.io/specification/2025-11-25},
  urldate      = {2026-07-24},
  note         = {License MIT. Quote: ``While MCP itself cannot enforce
                  these security principles at the protocol level''
                  (Security and Trust \& Safety section) -- direct evidence
                  MCP is a tool/resource/prompt access protocol, silent on
                  semantic (e.g. accounting) correctness of tool effects.}
}

@online{mcp_announcement,
  title        = {{Introducing the Model Context Protocol}},
  author       = {{Anthropic}},
  year         = {2024},
  url          = {https://www.anthropic.com/news/model-context-protocol},
  urldate      = {2026-07-24},
  note         = {2024-11-25 open-source release announcement.}
}

% ---- Coinbase x402 ----
@online{x402_spec,
  title        = {{x402 Protocol Specification v2}},
  author       = {{x402 Foundation}},
  year         = {2025},
  url          = {https://github.com/coinbase/x402/blob/main/specs/x402-specification-v2.md},
  urldate      = {2026-07-24},
  note         = {License Apache-2.0. Document dated 2025-12-9. Governance
                  moved from Coinbase to an independent x402 Foundation
                  (github.com/x402-foundation/x402); coinbase/x402 is now a
                  development fork. Explicit ``Out of Scope'' list excludes
                  client-side budget management and session handling; no
                  accounting/bookkeeping provisions.}
}

% ---- ERC-8004 Trustless Agents ----
@online{erc8004,
  title        = {{ERC-8004: Trustless Agents}},
  author       = {{De Rossi, Marco and Crapis, Davide and Ellis, Jordan and Reppel, Erik}},
  year         = {2025},
  url          = {https://eips.ethereum.org/EIPS/eip-8004},
  urldate      = {2026-07-24},
  note         = {Status: Draft (Ethereum standards track). Created
                  2025-08-13. Quote: ``Payments are orthogonal to this
                  protocol and not covered here.'' Extends A2A with on-chain
                  Identity/Reputation/Validation registries. Reference
                  Identity Registry deployed to Ethereum mainnet 2026-01-29
                  at 0x8004A169FB4a3325136EB29fA0ceB6D2e539a432 (Etherscan) --
                  Draft standards status and live mainnet deployment are
                  simultaneously true; do not conflate the two.}
}

% ---- OpenAI/Stripe Agentic Commerce Protocol (ACP) ----
@online{acp_spec,
  title        = {{Agentic Commerce Protocol (ACP)}},
  author       = {{OpenAI and Stripe}},
  year         = {2026},
  url          = {https://github.com/agentic-commerce-protocol/agentic-commerce-protocol},
  urldate      = {2026-07-24},
  note         = {License Apache-2.0. Status beta; spec version 2026-04-17.
                  ``Interaction model and open standard for connecting
                  buyers, their AI agents, and businesses to complete
                  purchases.'' No accounting-semantic provisions.}
}

% ---- Universal Commerce Protocol (UCP) ----
@online{ucp_spec,
  title        = {{Universal Commerce Protocol (UCP) Specification}},
  author       = {{Google and Shopify}},
  year         = {2026},
  url          = {http://ucp.dev/2026-04-08/specification/overview/},
  urldate      = {2026-07-24},
  note         = {License Apache-2.0. Version 2026-04-08. Transports:
                  REST, MCP, A2A, Embedded. Explicitly supports the ``AP2
                  Mandates Extension'' for payment authorization. No
                  accounting/ledger-reconciliation provisions.}
}

% ---- FIDO Alliance agentic-commerce convergence point ----
@online{fido_agentic,
  title        = {{FIDO Alliance to Develop Standards for Trusted AI Agent Interactions}},
  author       = {{FIDO Alliance}},
  year         = {2026},
  url          = {https://fidoalliance.org/fido-alliance-to-develop-standards-for-trusted-ai-agent-interactions/},
  urldate      = {2026-07-24},
  note         = {2026-04-28. Agentic Authentication TWG (chaired by CVS
                  Health/Google/OpenAI) and Payments TWG (chaired by
                  Mastercard and Visa). Same-day as AP2 v0.2, which donated
                  its credential layer here. Scope: user-instruction
                  verification, agent authentication, trusted delegation --
                  not accounting semantics.}
}

% ---- Visa Trusted Agent Protocol ----
@online{visa_tap,
  title        = {{Trusted Agent Protocol}},
  author       = {{Visa}},
  year         = {2026},
  url          = {https://developer.visa.com/capabilities/trusted-agent-protocol/overview},
  urldate      = {2026-07-24},
  note         = {Part of Visa Intelligent Commerce. Cryptographic,
                  merchant-and-purpose-scoped signatures for agent traffic
                  classification (agent vs. bot), not accounting semantics.
                  Proprietary network program, not a body-submitted open
                  standard.}
}

% ---- Skyfire KYA ----
@online{skyfire_kya,
  title        = {{Know Your Agent (KYA)}},
  author       = {{Skyfire}},
  year         = {2026},
  url          = {https://skyfire.xyz/know-your-agent-kya/},
  urldate      = {2026-07-24},
  note         = {Proprietary Skyfire identity/payment product (JWT-based,
                  OAuth2/JWKS-compatible), not a body-submitted open
                  standard. KYAPay/Agent Checkout launched 2025-06-26 per
                  BusinessWire. No accounting-semantic provisions.}
}

% TODO(T1): Mastercard Agent Pay -- direct WebFetch of mastercard.com was
% blocked (HTTP 403) in this session; content below is search-index-verified
% only. Re-fetch https://www.mastercard.com/us/en/business/artificial-intelligence/mastercard-agent-pay.html
% directly (browser or a fetch tool that isn't blocked) before citing verbatim.
% @online{mastercard_agentpay,
%   title        = {{Mastercard Agent Pay}},
%   author       = {{Mastercard}},
%   year         = {2025},
%   url          = {https://www.mastercard.com/us/en/business/artificial-intelligence/mastercard-agent-pay.html},
%   urldate      = {TODO -- confirm via direct fetch, not search snippet},
%   note         = {Unveiled April 2025 per press-release URL slug
%                   (.../2025/april/mastercard-unveils-agent-pay...).
%                   ``Agentic Tokens'' + Agent Pay Acceptance Framework.
%                   Proprietary Mastercard program, not an open standard.}
% }
```

---

## (d) Mapping — source → paper claim/section

| Paper element | Best-supporting source(s) | Why |
|---|---|---|
| `main.tex:93–96` positioning sentence ("AP2 for payment authorization, A2A for agent interoperation... did the value move, and was it authorized?") | `ap2_spec` (roles + verification-responsibilities language), `ap2_spec` FAQ Q1 (source #3), `a2a_spec` (Tasks/Agent-Cards, zero payment content) | Both specs' own primary text uses exactly this authorization/interoperation framing — this is not the paper's spin, it is traceable to the spec authors' own words. |
| `main.tex:44–45` ("protocols such as AP2 and A2A") | `ap2_announcement`, `a2a_lf_donation` | Anchors the dates/partners claims if the intro adds specifics. |
| `main.tex:60,166–169` (MCP deterministic-tools framing, I1) | `mcp_spec` (source #12, the "cannot enforce... at the protocol level" quote) | Directly supports I1's premise that ontology-as-constraint must live *below* MCP, since MCP's own spec disclaims protocol-level enforcement of anything beyond consent/safety — it says nothing about semantic correctness of tool outputs at all, which is exactly the gap I1 fills. |
| `main.tex:322–337` ("AP2 and A2A operate at the settlement and interoperation layers... asserted architecture, not a production settlement stack") | `erc8004` ("Payments are orthogonal to this protocol and not covered here" — the single cleanest one-line proof-quote in the whole survey), `x402_spec` ("Out of Scope" list), `ucp_spec` (explicit AP2-extension relationship with zero accounting content) | These three give the paper three independent, differently-governed protocols (Ethereum standards-track, Coinbase/x402 Foundation, Google/Shopify) all independently silent on booking semantics — turns a single-example claim into a converging-evidence claim. |
| Related Work §, "agent payment/interop protocols" bullet (`TASKS.md` T1) | All of (b) rows 1–30; `bibtex` block in (c) | Directly populates the four-body-of-work Related Work structure T1 calls for; this survey is the first of the four. |
| Threat-model subsection (T4, "can a malicious agent defeat I1/I2/I3?") | `visa_tap` and `skyfire_kya` (both are literally agent-vs-bot / identity-fraud threat models from industry) | Useful contrast: those protocols model adversarial *identity* claims; Kontablo's I1/I2/I3 model adversarial *semantic* claims (a real agent submitting a wrong-but-existing UUID). Different threat class, worth one sentence distinguishing them. |
| Inference-cost framing (T5) | Not directly supported by DR1 sources — out of scope for this research question. | No source here speaks to LLM inference cost; that claim is self-contained to Kontablo's own `results.json`. |
| GEO/AEO "quantified claims" polish (T7) | `a2a_spec`/PR Newswire source #11 (150+ orgs), `ap2_announcement` (60+ partners) | If the intro wants one sentence establishing "these are not fringe protocols," these two adoption-scale numbers are citable and dated. |

---

## (e) Gaps / unverified / open questions

- **Mastercard Agent Pay — retrieval limitation, not a content gap.** Every
  `mastercard.com` and `developer.mastercard.com` URL attempted returned
  `HTTP 403` to `WebFetch` in this session (likely bot-blocking, not a
  missing page). The content reported in tables (b)/(c) came from
  `WebSearch`'s indexed snippets of those same official pages, which is a
  real retrieval method but weaker than a direct fetch — I did not personally
  see the full page text. **Action for whoever writes the Mastercard sentence
  in Related Work: re-fetch via a plain browser before quoting anything
  verbatim; the bibtex entry is commented out for exactly this reason.**
- **No academic/peer-reviewed prior art in this batch.** Every source in (b)
  is an industry spec, official blog, press release, or news article — that
  is *expected and correct* for DR1 (these are 2025–2026 industry protocols,
  not yet the subject of peer-reviewed papers), but it means DR1 alone cannot
  satisfy a reviewer looking for scholarly grounding. That is what DR2/DR3/DR4
  and their respective literatures are for; DR1's job was industry-protocol
  primary sourcing, and that job is done.
- **A2A's original 2025-04-09 announcement was corroborated by both a direct
  primary fetch (Google Developers Blog, source #8) and multiple independent
  secondary sources (Wikipedia, Galileo, Techzine, Apono) converging on the
  same date** — high confidence, but flagging that the *initial* WebSearch
  pass alone (before the direct fetch) would only have given secondary
  corroboration; worth remembering as a general lesson for DR2–DR4 that a
  second-pass primary fetch materially raised confidence here.
- **x402's relationship to "which networks/chains beyond EVM and Solana"
  and ERC-8004's real-world adoption depth (how many agents are actually
  registered on the mainnet Identity Registry, not just that the contract
  exists) were not investigated** — out of scope for DR1's question (protocol
  *specification* content, not adoption depth), but would matter if the paper
  later wants an adoption-scale claim for x402 or ERC-8004 specifically (it
  currently only has one for A2A and AP2, from sources #11 and #5).
  **Do not state an x402/ERC-8004 adoption number — none was verified.**
  (The 100M+-transactions x402 figure that appeared in an early `WebSearch`
  synthesis in this session was **not** independently confirmed against a
  primary source and should be treated as **UNVERIFIED — do not cite**.)
  Consumer Coinbase-blog and press coverage placed the figure in a wide,
  inconsistently-sourced range across different snapshots; without a single
  authoritative dated source this number does not meet the project's
  claims-evidence bar.
  **UNVERIFIED — do not cite: "well over 100 million transactions on Base"
  (x402 adoption claim, surfaced only in unattributed WebSearch synthesis).**
  **UNVERIFIED — do not cite: Visa "IOUs...supplemental content revenue"
  claim** that appeared in one `WebFetch` summary of the Visa Trusted Agent
  Protocol page — this reads as a probable tool misparse (no independent
  corroboration found, and the phrase does not fit the rest of the page's
  register); dropped from the tables above and flagged here only so it is
  not accidentally reintroduced from a session transcript later.
- **Coverage was intentionally capped at protocols directly named in the task
  plus two organically-surfaced, clearly load-bearing additions (UCP, ACP).**
  Other agent-commerce-adjacent efforts exist (e.g., various wallet-specific
  "agent mode" features, ISO 20022 usage-in-agent-context) but were left out
  as out of scope for DR1 — ISO 20022 belongs to DR4 (financial ontologies/
  standards), not DR1 (payment/interop protocols).
- **Open question for T1's drafting, not a research gap:** given eleven
  converging silent-on-accounting-semantics sources, the Related Work section
  can afford to cite 3–4 of the strongest (AP2, A2A, MCP, and either
  ERC-8004's "orthogonal" quote or x402's "Out of Scope" list) in the main
  positioning paragraph, and relegate the rest (UCP, ACP, Visa, Mastercard,
  Skyfire, FIDO) to a footnote or a single "and this pattern holds across
  every agent-commerce protocol surveyed, including X, Y, Z" sentence —
  citing all eleven inline would read as padding rather than rigor. This is
  a drafting recommendation, not a finding.
