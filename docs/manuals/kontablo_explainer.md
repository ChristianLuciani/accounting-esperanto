# Kontablo: What It Is and Why It Matters
## A One-Page Guide for Accounting Professionals

**Version:** 0.2.0 | **Date:** March 2026 | **For:** Expert Validation Participants

---

## The Problem Kontablo Solves

When a company operates in Mexico, Brazil, and Germany simultaneously, its accountants face a painful reality: the same transaction—say, a customer invoice—is recorded differently in each jurisdiction.

| Country | Account Code | Label | Standard |
|---------|-------------|-------|----------|
| Mexico | 105 | Clientes | SAT / IMCP |
| Brazil | 1.1.2.01 | Clientes — Duplicatas | CPC / CFC |
| Germany | 1400 | Forderungen aLuL | HGB / SKR03 |
| International | TradeReceivables | Trade Receivables | IFRS |

Despite referring to the exact same economic reality, these four codes don't speak to each other. Consolidating them requires manual mapping—work that is slow, expensive, and error-prone.

**Kontablo is the translation layer that connects them all.**

---

## How Kontablo Works — Three Layers

```
LAYER 1 (Universal Core)
   asset.current.receivables
         ↑ maps to ↓
LAYER 2 (Local Code)     LAYER 3 (IFRS Tag)
   MX: 105                 TradeAndOtherCurrentReceivables
   BR: 1.1.2.01             (IFRS Taxonomy 2024)
   DE: 1400
   FR: 411
   VN: 131
   RU: 62
   IL: 14
   IN: 1100
```

Kontablo defines **30 universal "Level 3" accounts** that exist in some form in every jurisdiction we've studied. Each account has:

- A **stable ID** (e.g., `asset.current.receivables`) that never changes
- A **UUID** for machine-to-machine reference
- A **direct link** to the IFRS taxonomy tag
- A **local code table** populated across the committed localizations (195 jurisdictions mapped; 60 statutory-chart overlays)
- **Aggregation rules** for automated financial statement preparation

---

## The 30 Core Accounts at a Glance

| Segment | Accounts |
|---------|----------|
| **Current Assets (6)** | Cash, Bank, Receivables, VAT Input, Inventory, Prepaid |
| **Non-current Assets (6)** | PP&E, ROU Assets, Intangibles, Goodwill, Investments, ROU Leases |
| **Current Liabilities (5)** | Payables, VAT Output, Tax, Accrued, Short-term Debt |
| **Non-current Liabilities (3)** | LT Debt, Lease Liabilities, Deferred Tax |
| **Equity (3)** | Capital, Retained Earnings, Reserves |
| **Revenue (2)** | Operating Revenue, Other Income |
| **Expenses (5)** | COGS, Admin, Depreciation, Finance Costs, Income Tax |
| **Total** | **30 accounts covering ~94% of routine transaction volume (~99% with a 34-account extended core)** |

---

## What Kontablo Is NOT

| Myth | Reality |
|------|---------|
| "A new chart of accounts" | No — it's a **mapping layer** over existing charts |
| "It replaces IFRS" | No — it's **anchored to IFRS**, extending its reach |
| "Only for multinationals" | No — even a local SME benefits from standardized AI bookkeeping |
| "A tax compliance tool" | No — it maps to local tax codes but doesn't replace tax compliance |
| "A software product" | Not yet — currently an **open specification** (BSL 1.1 license) |

---

## The Graph Architecture (Why It's Different)

Traditional charts of accounts are **trees**: one parent, many children, strictly hierarchical. This breaks down when:

- A local account maps to **two** IFRS concepts (1→N)
- **Multiple** local codes merge into one IFRS line item (N→1)
- The same account **behaves differently** depending on whether an entity is in hyperinflation

Kontablo uses a **graph model**, where accounts are nodes and relationships are typed edges:
- `parent_of` (aggregation hierarchy)
- `maps_to` (local code → Kontablo)
- `equivalent_to` (Kontablo → IFRS tag)
- `adjusted_by` (for hyperinflation, FX translation)

This allows AI systems to navigate complex multi-hop queries like:
*"Which Mexican SAT codes are equivalent to the IFRS Revenue tag, and how are they presented in Brazil?"*

---

## AI Applications

Kontablo is designed as the **semantic backbone** for AI-powered accounting:

1. **Automatic transaction classification**: AI reads a supplier invoice and maps it to the correct Kontablo account → triggers the right local code in any jurisdiction
2. **Cross-border consolidation**: Kontablo accounts are the pivot — eliminate intercompany balances, convert currencies, apply IFRS adjustments automatically
3. **Audit trail**: Every transaction links to a Kontablo account → IFRS tag → creates full audit visibility of the accounting rationale

---

## What We're Asking You to Validate

We have mapped **30 Kontablo accounts** to the local accounting codes of your jurisdiction. We want your professional judgment on:

1. **Are the proposed mappings correct?** (Confidence 1–5 per account)
2. **What accounts are missing?** (Gaps in the 30-account core)
3. **Does the concept work in practice** for the transactions you see daily?

Your feedback directly shapes the Kontablo v0.3 specification and will be cited in the academic paper (with your consent, anonymized).

---

## Licensing

Kontablo is published under the **Business Source License 1.1 (BSL 1.1)**, converting to Apache 2.0 after four years. Connectors to open-source ERP platforms (ERPNext/Frappe, Odoo) are licensed Apache 2.0. The ontology specification and research data are available for public auditing and collaborative extension:  
**https://github.com/ChristianLuciani/accounting-esperanto**

Questions? Contact: [researcher email] | LinkedIn: [profile]
