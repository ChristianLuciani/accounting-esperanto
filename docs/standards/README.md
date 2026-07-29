# Outbound standards work

Drafts of contributions Kontablo makes **to other people's standards**. Distinct
from `docs/adr/` (our own decisions) and `docs/strategy/protocol-compatibility-register.md`
(the state of the landscape).

This directory exists because [ADR-017](../adr/017-agent-protocol-adoption-policy.md)
rule 4 makes standards participation a first-class activity rather than
overhead: for the commerce/settlement layer, where Kontablo is **not a
participant**, a spec contribution is the highest-leverage move available and
costs no engineering.

## Why drafts live here, in the public tree

A proposal to a public standard is a public act, so there is nothing to protect
by hiding it — and a dated, versioned draft in a public repository establishes
priority on the idea even if the proposal is never accepted. That is the main
value to bank on: **most outside contributions to a large-vendor standard do not
merge**, and the draft has to be worth writing anyway.

The *targeting and timing* of outreach is a different matter and stays in the
gitignored `docs/internal/` playbook. This directory holds the technical
artifact; the playbook holds who to talk to and when.

## Firing rule

Every draft here carries a **FIRE WHEN** gate at the top. Do not post any of
them before their gate is satisfied.

The default gate is **the spoke-1 paper having its own DOI**. Reason: a
contribution that can cite a published, DOI'd result is a different document
from one that says "we have a repository." The sequencing is not cosmetic — it
is the difference between a vendor pitch and a citable proposal.

## Contents

| Draft | Target | Fire when |
|---|---|---|
| [`acp-sep135-mcp-transport-comment.md`](acp-sep135-mcp-transport-comment.md) | Agentic Commerce Protocol, SEP #135 (open proposal) | Spoke-1 DOI assigned |
| [`acp-accounting-semantics-extension.md`](acp-accounting-semantics-extension.md) | Agentic Commerce Protocol, Extensions Framework | Spoke-1 DOI assigned, **and** the SEP #135 comment has had a response or 30 days of silence |

## ⚠️ Three different protocols are called ACP

This trap has already cost one round of misdirected research. Every document in
this directory states which one it means, in full, on first use.

| Name | Owner | What it is | Kontablo's relationship |
|---|---|---|---|
| **Agentic Commerce Protocol** | OpenAI + Stripe | Agent-driven checkout and commerce | The target of the drafts here |
| **Agent Client Protocol** | Zed | Editor ↔ coding-agent communication | **Out of scope** — see the register |
| **Agent Communication Protocol** | IBM / BeeAI | Agent-to-agent messaging | Not surveyed; largely converged toward A2A |

Never write "ACP" unqualified in a public artifact.
