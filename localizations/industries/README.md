# Kontablo Industry Extensions — Index

**Version:** 0.2.0  
**Date:** 2026-03-23  
**Path:** `localizations/industries/`

## Purpose

Industry extensions add specialized Level 3 accounts to the Kontablo core taxonomy
for sectors with unique accounting standards or practices. They follow the overlay
architecture: the core schema is unmodified, and industry-specific accounts are
additive extensions activated per entity type.

---

## Available Extensions

| Extension | File | Standards | Key Jurisdictions | Status |
|-----------|------|-----------|-------------------|---------|
| **Banking / Financial Instruments** | `banking_ifrs9.yaml` | IFRS 9 | Global (esp. banks) | ✅ v0.1 |
| **Insurance** | `insurance_ifrs17.yaml` | IFRS 17 | Global (insurers) | ✅ v0.1 |
| **Energy & Extractive** | `energy_ifrs6.yaml` | IFRS 6, IAS 37, IFRS 15 | SA, BR, NG, RU, AU, CA | ✅ v0.1 |
| **Agriculture** | `agriculture_ias41.yaml` | IAS 41, IFRS 13, IAS 16 | BR, AR, NZ, AU, CN | ✅ v0.1 |
| **Real Estate** | `real_estate_ias40.yaml` | IAS 40, IFRS 16, IFRS 15 | AE, CN, BR, MX, UK, DE | ✅ v0.1 |
| **Telecommunications** | `telecom_ifrs15.yaml` | IFRS 15, IFRS 16, IAS 38 | US, UK, MX, BR, IN, CN, DE | ✅ v0.1 |
| **Healthcare & Pharma** | `healthcare_pharma_ias38.yaml` | IAS 38, IFRS 15, IAS 37 | US, UK, DE, CH, IN, IL | ✅ v0.1 |
| **Public Sector / Government** | `public_sector_ipsas.yaml` | IPSAS | BR, MX, CO, ZA, UK, AU, NZ, PH, KE, GH | 🚧 Drafted (v0.1.0-draft) — **not wired into `core/harness/ontology.py`'s resolver, not yet empirically validated.** Activation gated on real-data validation (H5), see [`research/real_data_validation_plan.md`](../../research/real_data_validation_plan.md). Domain explicitly claimed as in-scope 2026-07-18. |

---

## Planned Extensions (v0.3 Roadmap)

| Extension | Standards | Priority |
|-----------|-----------|----------|
| **Cryptocurrency / Digital Assets** | IAS 38 by analogy (no dedicated standard yet) | RESEARCH |
| **ESG / Carbon Accounting** | GRI, ISSB S2, EU CSRD | RESEARCH |
| **Construction** | IAS 11 / IFRS 15 (over time), IAS 37 (warranty) | MEDIUM |

---

## Usage

Each industry extension file contains:
- `metadata`: Industry scope, applicable standards, version
- `mappings`: Account definitions with UUIDs, IFRS tags, local code examples
- `aggregation_rules`: Industry-specific KPIs and subtotals
- `validation_rules`: Business rules applicable to the sector
- Industry-specific config blocks (e.g., `reit_specific`, `management_metrics`)

To activate an extension for an entity:
```yaml
# In entity localization config:
entity_type: real_estate_investment_trust
industry_extensions:
  - real_estate_ias40
  - banking_ifrs9   # if entity has financial instruments desk
```

---

## Account UUID Ranges (reserved)

| Range Start | Industry | Status |
|-------------|----------|--------|
| `40000000-...` | Banking / IFRS 9 | ✅ Active |
| `50000000-...` | Energy / Extractive | ✅ Active |
| `60000000-...` | Agriculture | ✅ Active |
| `70000000-...` | Real Estate | ✅ Active |
| `80000000-...` | Telecommunications | ✅ Active |
| `90000000-...` | Healthcare & Pharma | ✅ Active |
| `A0000000-...` | Public Sector / IPSAS | 🚧 Drafted, unwired (see status above) |
| `B0000000-...` | Construction | 🔲 Reserved |
| `C0000000-...` | Crypto / Digital Assets | 🔲 Reserved |
