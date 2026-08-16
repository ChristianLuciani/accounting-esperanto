# Draft: RFC — Accounting Semantics Extension (Agentic Commerce Protocol)

> **FIRE WHEN:** the spoke-1 paper has its own DOI, **and** the SEP #135 comment
> has drawn a response or gone 30 days without one.
>
> **Target:** [Agentic Commerce Protocol](https://github.com/agentic-commerce-protocol/agentic-commerce-protocol)
> (OpenAI + Stripe) — Extensions Framework, `rfcs/rfc.extensions.md`. Modelled on
> the shipped worked example `rfcs/rfc.discount_extension.md`.
>
> **Not the Agent Client Protocol (Zed) and not the Agent Communication Protocol
> (IBM/BeeAI).** See `README.md` in this directory.
>
> **Verify before firing.** Every schema fact below was read from
> `spec/2026-04-17/` on 2026-07-29. ACP shipped five spec versions in roughly
> seven months. Re-read `rfc.extensions.md` and `schema.agentic_checkout.json`
> before posting; if field names or extension rules moved, this draft is stale.

---

## Design decisions worth reviewing before this is filed

Three choices determine whether this gets read or dismissed. They are ours to
defend, so they belong in front of the RFC rather than buried in it.

**1. The field is `accounting_semantics`, not `kontablo_*`.** An extension named
after us would be read as vendor capture and rejected on sight. The field is
generic and carries an `ontology` discriminator, so FIBO, XBRL GL, or a national
SAF-T dialect can populate it too. The strategic consequence is deliberate:
Kontablo becomes *an* ontology named in an open standard rather than *the*
ontology the standard depends on. That is a weaker claim and a much more likely
one to land — and the citable win (being the worked example) survives either way.

**2. Unresolved line items are declared, not omitted.** The `unresolved[]` array
is the distinctive element and the one most likely to be argued about. It is
invariant I2 from the paper expressed as a wire format: a line item whose
accounting meaning could not be determined produces a typed record, never a
silent gap. Expect pushback that it is unnecessary. It is not: without it, a
consumer cannot distinguish "this line has no accounting annotation" from "the
annotation was attempted and failed", and those require different handling.

**3. It is non-normative for settlement.** The extension touches no amount, no
payment method, no authorization. It cannot change what is charged. Saying this
loudly and early removes most of the reason a payments reviewer would object.

---

# RFC: Accounting Semantics Extension

**Status:** Draft
**Version:** 2026-07-29
**Scope:** Optional, machine-resolvable accounting classification for checkout line items
**Depends on:** RFC: ACP Extensions Framework

This RFC defines the **Accounting Semantics Extension**. It lets an agent and a
seller agree, before a transaction commits, on which economic concept each line
item corresponds to — so that both parties' ledgers can record the same event
identically, and so that the classification is reconstructible afterwards.

---

## 1. Scope & Goals

- Carry an **ontology-qualified concept identifier** per line item, resolvable by
  both parties to the same meaning.
- Carry the **provenance of that resolution** — how it was determined, and with
  what certainty.
- **Declare line items whose accounting meaning could not be determined**, rather
  than omitting them.
- Remain **ontology-neutral**: the extension names no specific taxonomy.
- Remain **non-normative for settlement**: nothing here affects amounts, payment
  methods, authorization, or fulfilment.

**Out of scope:** journal-entry construction, double-entry balancing, tax
calculation, ledger posting, ontology definition or distribution, and any
requirement that either party act on the annotation.

---

## 2. Motivation

### 2.1 ACP already accepts that a line item carries fiscal metadata

`LineItem` in `spec/2026-04-17/json-schema/schema.agentic_checkout.json` already
models `category`, `tags`, `tax_exempt`, and `tax_exemption_reason`. The protocol
has therefore already conceded that a line item needs classificatory and fiscal
metadata beyond price and quantity, and that both parties benefit from agreeing
on it in-band.

What is absent is the **posting coordinate**: which account, in which chart, this
line becomes when each side records it. `tax_exempt` says a tax rule does not
apply; it does not say what the item *is*.

### 2.2 Why the gap has a cost

When an autonomous agent transacts, both sides must eventually record the event.
Today each side classifies independently, after the fact, from an unstructured
description. Two consequences follow, and neither is hypothetical for anyone who
has reconciled cross-border ledgers:

- The two sides can classify the same event differently, and nothing in the
  transaction detects the divergence. It surfaces at reconciliation, long after
  the contaminated figure has propagated.
- The classification is not reconstructible. Given a posted figure, there is no
  path back to which line item produced it and on what basis.

At human transaction volumes this is absorbed by review. The premise of
agent-driven commerce is that per-transaction human review does not scale — which
moves the problem from a staffing question to a protocol one.

### 2.3 Why an extension rather than `custom_attributes`

`LineItem.custom_attributes` exists, and it is the obvious first suggestion. It
does not work for this, by its own definition. The schema describes
`CustomAttribute` as *"Custom key-value attribute for **merchant-specific**
metadata on line items"*, typed as two free strings — `display_name` and `value`
— with the example `{"display_name": "Engraving", "value": "Happy Birthday!"}`.

It is merchant-specific and display-oriented by design. An accounting identifier
must be the opposite: **shared** between counterparties and **machine-resolvable**
to the same concept by both. A free-string bag cannot be negotiated, cannot be
discovered, and gives a consumer no way to know whether the value means anything.
The Extensions Framework exists precisely so that additive, typed, negotiated
fields do not have to be smuggled through untyped ones.

### 2.4 Why before the transaction, not after

Post-hoc classification is the status quo and it is what fails. An annotation
agreed *during* the session is checkable by both parties while the transaction is
still reversible; the same annotation derived afterwards is a reconstruction, and
a disagreement discovered then is already an incident.

---

## 3. Extension Declaration

Sellers advertise support via `capabilities.extensions`; agents declare it in
requests. Matching the framework's `ExtensionDeclaration` shape:

```json
{
  "capabilities": {
    "extensions": [
      {
        "name": "accounting_semantics",
        "extends": [
          "$.CheckoutSessionCreateRequest.accounting_semantics",
          "$.CheckoutSessionUpdateRequest.accounting_semantics",
          "$.CheckoutSession.accounting_semantics"
        ]
      }
    ]
  }
}
```

The name satisfies the framework's `name` pattern and MAY carry a dated version
suffix (`accounting_semantics@2026-07-29`).

Per the Extensions Framework this extension **MUST NOT** modify any existing
required field and **MUST NOT** change the semantics of any existing field. It
adds exactly one optional object to the checkout object.

---

## 4. Schema

### 4.1 `accounting_semantics`

| Field | Type | Required | Description |
|---|---|---|---|
| `ontology` | string | yes | Identifier of the ontology the concepts belong to. Opaque to ACP |
| `ontology_version` | string | no | Version of that ontology, so an annotation remains interpretable after the ontology moves |
| `postings` | `Posting[]` | no | Resolved classifications, keyed by line item |
| `unresolved` | `Unresolved[]` | no | Line items whose classification could not be determined |

### 4.2 `Posting`

| Field | Type | Required | Description |
|---|---|---|---|
| `line_item_id` | string | yes | MUST match a `LineItem.id` in the same session |
| `concept_id` | string | no | Human-readable concept identifier, for display and debugging |
| `concept_uuid` | string | yes | Stable machine identifier of the concept within `ontology` |
| `jurisdiction` | string | no | ISO 3166-1 alpha-2, where the classification is jurisdiction-specific |
| `resolution` | `Resolution` | no | How the classification was determined |

### 4.3 `Resolution`

| Field | Type | Required | Description |
|---|---|---|---|
| `method` | string | yes | `exact` \| `rule` \| `inferred` \| `manual` |
| `confidence` | number | no | `0.0`–`1.0` |
| `rule_id` | string | no | Stable identifier of the specific rule that fired, so the decision is reproducible without re-running the resolver |
| `resolved_at` | string | no | RFC 3339 timestamp |

`method: inferred` exists so that a party using a statistical classifier can say
so honestly. A consumer can then treat `exact` and `inferred` differently, which
it cannot do if both arrive as a bare identifier.

### 4.4 `Unresolved`

| Field | Type | Required | Description |
|---|---|---|---|
| `line_item_id` | string | yes | MUST match a `LineItem.id` in the same session |
| `reason` | string | yes | `no_match` \| `ambiguous` \| `out_of_scope` \| `escalated` |
| `note` | string | no | Human-readable detail |

**A consumer MUST NOT treat an entry in `unresolved` as equivalent to an absent
annotation.** An absent annotation means nothing was attempted; an `unresolved`
entry means classification was attempted and did not succeed, and the item may
require review before posting.

---

## 5. Example

```json
{
  "id": "cs_01J8Z...",
  "line_items": [
    { "id": "li_001", "item": { "id": "sku_compute_hr" }, "quantity": 40, "totals": [] },
    { "id": "li_002", "item": { "id": "sku_advisory" },   "quantity": 1,  "totals": [] }
  ],
  "accounting_semantics": {
    "ontology": "kontablo",
    "ontology_version": "0.3.0",
    "postings": [
      {
        "line_item_id": "li_001",
        "concept_id": "expense.admin",
        "concept_uuid": "00000000-0000-4000-8000-000000000401",
        "jurisdiction": "de",
        "resolution": {
          "method": "exact",
          "confidence": 1.0,
          "rule_id": "tier1:de:6300",
          "resolved_at": "2026-07-29T14:02:11Z"
        }
      }
    ],
    "unresolved": [
      {
        "line_item_id": "li_002",
        "reason": "no_match",
        "note": "no deterministic rule matched; queued for human review"
      }
    ]
  },
  "capabilities": {
    "extensions": [
      {
        "name": "accounting_semantics",
        "extends": [
          "$.CheckoutSession.accounting_semantics"
        ]
      }
    ]
  }
}
```

Note what the example is doing: two line items, one classified with its exact
rule named, one **declared as unclassified rather than dropped**. A consumer can
post the first automatically and route the second to review. That distinction is
the point of the extension.

---

## 6. Interoperability

- **Ontology-neutral by construction.** `ontology` is opaque to ACP. FIBO,
  XBRL GL, AICPA ADS, or a national SAF-T dialect are equally expressible.
- **No coupling to settlement.** The extension is inert with respect to
  authorization and capture. A seller that ignores it is fully conformant.
- **Degrades cleanly.** An agent that declares the extension against a seller
  that does not support it simply receives no annotation back; nothing fails.
- **Transport-independent.** Nothing here depends on REST versus the MCP
  transport binding under discussion in SEP #135.

---

## 7. Known limitations

Stated plainly, because a reviewer will find them anyway.

- **Session-level attachment forces a keyed mapping.** The Extensions Framework
  attaches extensions to `CheckoutSessionCreateRequest`,
  `CheckoutSessionUpdateRequest` and `CheckoutSession`, not to `LineItem`. So the
  annotation references line items by `id` instead of sitting on them. Inline
  annotation would be cleaner; this is the shape the framework permits, and it
  works because `LineItem.id` is required.
- **The extension does not make classification correct.** It makes it *explicit,
  attributable, and reconstructible*. A party can populate a well-formed
  `concept_uuid` that is simply the wrong concept. This bounds a class of error;
  it does not eliminate it.
- **No conformance suite is proposed here.** Validating that two parties resolve
  the same identifier to the same meaning requires a shared ontology, which is
  out of scope for ACP and belongs to whichever ontology `ontology` names.

## 8. Disclosure about the reference implementation

The author maintains one implementation of a resolution layer of this shape. In
the interest of not overstating it:

- Its validation data is **synthetic trial balances**, not exports from live
  ledgers. It demonstrates architectural properties, not real-world posting
  distributions.
- The implementation is **prototype-grade** relative to its specification.
- Its ontology covers many jurisdictions but is **not complete**, and does not
  claim to be.

None of that affects the extension's design, which is deliberately independent of
any one ontology. It is disclosed so the proposal is not read as resting on
claims that have not been made.
