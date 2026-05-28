# Kontablo ERP Universality Roadmap

This document outlines the API abstraction endpoints for bridging the Kontablo Universal Level 3 Graph Ontology with the native data structures of the top 10 commercial ERP and accounting platforms worldwide.

## Supported Commercial Systems

1. **SAP (S/4HANA / Business One)**: Mapping B1 account segmentation to Kontablo L3 parameters.
2. **Oracle NetSuite**: Translating `Account` record types and custom segments.
3. **Microsoft Dynamics 365 / Business Central**: Adapting `G/L Account` tables and financial dimensions.
4. **Workday Financial Management**: Mapping Workday's tag-based custom subledgers.
5. **Intuit QuickBooks Online/Desktop**: Correlating deep sub-account trees to Kontablo flat universal nodes.
6. **Xero**: Utilizing the Xero Accounts API and tracking categories.
7. **Odoo**: Connecting `account.account` ORM models natively with Kontablo mapping fields.
8. **Zoho Books**: Integrating via Chart of Accounts endpoint with Kontablo metadata extension.
9. **Sage (Intacct / Sage 50)**: Standardizing GL structures across standard and advanced reporting nodes.
10. **ERPNext (Frappe)**: Full two-way connector available (see `connectors/erpnext/`).

## Architectural Principle

All proprietary tree-based (NetSuite, QBO) and flat-tag-based (Xero, Workday) structures are ingested via REST/GraphQL and flattened into Kontablo's Universal Graph. This guarantees that `asset.current.cash` is computationally identical regardless of its origin ERP, unblocking autonomous cross-platform M&A consolidation and unified analytics.
