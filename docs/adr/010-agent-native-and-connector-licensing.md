# ADR 010: Agent-Native Access Layer and Open-Source Connector Licensing

**Status:** Accepted
**Date:** 2026-05-28
**Deciders:** Christian Luciani

## Context

Two decisions were consolidated on 2026-05-28 during a strategy session:

1. **Interface framing.** Kontablo's original principle was "API-first". As the agentic economy matured (MCP, A2A, AP2 protocols), it became necessary to clarify the relationship between the data API and agent-facing protocols, to avoid either (a) treating them as the same level of abstraction, or (b) subordinating the API to a single protocol that may not retain dominance.

2. **Connector licensing.** The repo previously left the ERPNext connector's license undecided ("tentatively Apache 2.0"). A general policy was needed, since connectors to other open-source ERPs (Odoo, etc.) will follow.

## Decision

### Interface: API-first at the data layer, agent-native at the access layer

The canonical interface is a machine-consumable API (REST/gRPC). On top of it, Kontablo exposes an **agent-native** access layer via MCP (Model Context Protocol — LLM/agent tool consumption), A2A (Agent2Agent — agent interoperation), and AP2 (Agent Payments Protocol — settlement). An ERP or bank consumes the API directly; an autonomous agent consumes the agent-native layer. Neither is subordinate to the other.

The agent-native layer is **protocol-pluggable by design**: the architecture commits to the *category* (agent-native) rather than a single protocol, and will adopt any agentic protocol that gains meaningful traction. This is a deliberate hedge — at the time of this decision, MCP/A2A/AP2 adoption as de-facto standards is still in progress and unverified for permanence.

### Licensing: open the interface, protect the implementation

- **Connectors to open-source ERP/accounting projects (ERPNext/Frappe, Odoo, and similar): Apache 2.0.**
- **Core (ontology, spec, mapping engine, mapping methodology): BSL 1.1**, converting to Apache 2.0 after 4 years.
- **Connectors to proprietary commercial ERPs (NetSuite, SAP S/4HANA) and validated+tested mapping artifacts: BSL / proprietary, reserved for Praxia.**
- **General principle:** open the *interface* (APIs, documented contracts) to grow the ecosystem; protect the *implementation* behind it.

## Consequences

### Positive
- Apache-licensed open-source connectors maximize adoption in communities that would not pay a commercial license anyway, and act as credibility-building loss leaders.
- The agent-native framing positions Kontablo for the agentic economy without betting the architecture on one protocol's survival.
- BSL on the core preserves the route-(b) commercial optionality (migrating b→a is easy; a→b is not).

### Negative / Open
- A large commercial ERP can build its own equivalent if Kontablo becomes strategically important. Licensing cannot prevent this — it only prevents free incorporation of *our* code. The real moat is first-mover citability, jurisdictional depth (23 mapped), hyperinflation expertise, and Praxia's execution speed.
- Mixed-license repo (Apache submodules inside a BSL repo) requires clear per-directory LICENSE files and a `LICENSING.md` to avoid confusion. Pending implementation.

## References
- `CLAUDE.md` — Strategic posture and architectural principle #4.
- Pending: `LICENSING.md`, `LICENSE` (BSL 1.1 from mariadb.com/bsl11/).
- Protocol specs to cite (verify current status in preprint session): Model Context Protocol, A2A, AP2.
