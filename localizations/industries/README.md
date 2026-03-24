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
|-----------|------|-----------|-------------------|--------|
| **Banking / Financial Instruments** | `banking_ifrs9.yaml` | IFRS 9 | Global (esp. banks) | ✅ v0.1 |
| **Insurance** | `insurance_ifrs17.yaml` | IFRS 17 | Global (insurers) | ✅ v0.1 |
| **Energy & Extractive** | `energy_ifrs6.yaml` | IFRS 6, IAS 37, IFRS 15 | SA, BR, NG, RU, AU, CA | ✅ v0.1 |
| **Agriculture** | `agriculture_ias41.yaml` | IAS 41, IFRS 13, IAS 16 | BR, AR, NZ, AU, CN | ✅ v0.1 |
| **Real Estate** | `real_estate_ias40.yaml` | IAS 40, IFRS 16, IFRS 15 | AE, CN, BR, MX, UK, DE | ✅ v0.1 |

---

## Planned Extensions (v0.3 Roadmap)

| Extension | Standards | Priority |
|-----------|-----------|----------|
| **Telecommunications** | IFRS 15 (bundled contracts), IFRS 16 (tower leases) | HIGH |
| **Healthcare / Pharma** | IAS 38 (R&D), IFRS 15 (complex contracts) | MEDIUM |
| **Public Sector / Government** | IPSAS (International Public Sector Accounting Standards) | MEDIUM |
| **Cryptocurrency / Digital Assets** | IAS 38 by analogy (no dedicated standard yet) | RESEARCH |
| **ESG / Carbon Accounting** | GRI, ISSB S2, EU CSRD | RESEARCH |

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

| Range Start | Industry |
|-------------|----------|
| `40000000-...` | Banking / IFRS 9 |
| `50000000-...` | Energy / Extractive |
| `60000000-...` | Agriculture |
| `70000000-...` | Real Estate |
| `80000000-...` | Telecom (reserved) |
| `90000000-...` | Healthcare (reserved) |
| `A0000000-...` | Public Sector (reserved) |
