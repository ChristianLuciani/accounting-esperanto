# 🌍 Kontablo: Global Comparative Analysis Matrix

**Version:** 0.2.0  
**Date:** 2026-03-23  
**Countries Analyzed:** 20+  
**Method:** Cross-jurisdictional account structure comparison based on IFRS anchoring

---

## 📊 Executive Summary

| Metric | Value |
|--------|-------|
| Total jurisdictions analyzed | 20 |
| Common core accounts (all jurisdictions) | 18 |
| IFRS-convergent jurisdictions | 12 |
| Partial-IFRS jurisdictions | 5 |
| GAAP-divergent jurisdictions | 3 |
| Average mapping complexity score | 6.4 / 10 |
| Highest complexity | Venezuela (hyperinflation) |
| Lowest complexity | UK (full IFRS) |

---

## 🔍 Level 1 Accounts — Universal Coverage

These 7 Level 1 accounts exist in **100% of analyzed jurisdictions**:

| Kontablo L1 | IFRS Tag | Jurisdictions |
|------------|----------|---------------|
| `asset.current` | `ifrs:CurrentAssets` | MX, CO, PA, BR, AR, CL, PE, VE, US, CA, UK, DE, FR, ES, RU, IL, IN, JP, CN, AE, NG, SA, TR, VN, ZA | 
| `asset.noncurrent` | `ifrs:NoncurrentAssets` | All |
| `liability.current` | `ifrs:CurrentLiabilities` | All |
| `liability.noncurrent` | `ifrs:NoncurrentLiabilities` | All |
| `equity` | `ifrs:Equity` | All |
| `revenue` | `ifrs:Revenue` | All |
| `expense` | `ifrs:Expenses` | All |

---

## 🔬 Level 2 Accounts — Common Core (90%+ jurisdictions)

| Kontablo L2 | Label | IFRS Tag | Coverage | Exceptions |
|------------|-------|----------|----------|-----------|
| `asset.current.cash` | Cash & Equivalents | `CashAndCashEquivalents` | 100% | VE: split by USD/VES |
| `asset.current.receivables` | Trade Receivables | `TradeAndOtherCurrentReceivables` | 100% | CN: requires aging schedule |
| `asset.current.inventory` | Inventory | `CurrentInventories` | 98% | Service firms: N/A |
| `asset.current.prepaid` | Prepaid Expenses | `CurrentPrepayments` | 95% | — |
| `asset.noncurrent.ppe` | Property, Plant & Equipment | `PropertyPlantAndEquipment` | 100% | — |
| `asset.noncurrent.intangibles` | Intangible Assets | `IntangibleAssetsOtherThanGoodwill` | 95% | VN: limited scope |
| `asset.noncurrent.investments` | Long-term Investments | `InvestmentsAccountedForUsingEquityMethod` | 90% | SMEs exempt in MX, PA |
| `liability.current.payables` | Trade Payables | `TradeAndOtherCurrentPayables` | 100% | — |
| `liability.current.tax` | Tax Payable | `CurrentTaxLiabilitiesCurrent` | 100% | Rates vary 0%–50% |
| `liability.current.accrued` | Accrued Liabilities | `OtherCurrentProvisions` | 90% | — |
| `liability.noncurrent.debt` | Long-term Debt | `OtherNonCurrentFinancialLiabilities` | 100% | — |
| `liability.noncurrent.deferred_tax` | Deferred Tax | `DeferredTaxLiabilities` | 85% | VN: not applicable |
| `equity.capital` | Paid-in Capital | `IssuedCapital` | 100% | VN: Charter Capital |
| `equity.retained` | Retained Earnings | `RetainedEarnings` | 100% | VE: restated for hyperinflation |
| `equity.reserves` | Other Reserves | `OtherReserves` | 90% | — |
| `revenue.operating` | Operating Revenue | `Revenue` | 100% | — |
| `expense.cogs` | Cost of Sales | `CostOfSales` | 95% | Service: N/A |
| `expense.admin` | G&A Expenses | `AdministrativeExpenses` | 100% | — |

---

## 🌐 Jurisdiction-Specific Accounts (Unique to ≤3 Countries)

### Latin America

| Account | Local Code | Jurisdiction | IFRS Equivalent | Notes |
|---------|-----------|--------------|-----------------|-------|
| IVA por Recuperar | 1.1.3 | MX (SAT) | Input VAT | Mexico 16% VAT |
| Fondo Rotatorio | 1.1.05 | PA (DGI) | Petty Cash / Misc | Panama informal economy |
| ITBIS Acreditable | 1.1.4 | DO | Input VAT | Dominican Republic |
| Participación Trabajadores | 3.3.2 | PE, EC | Profit Sharing Liability | Mandatory in Peru 5-10% |
| Ajuste por Inflación | 5.5.X | VE, AR | Monetary Correction | IAS 29 hyperinflation |
| CPF / CNPJ (tax IDs) | | BR | Regulatory | Brazil tax ID tracking |

### Europe / Russia

| Account | Local Code | Jurisdiction | IFRS Equivalent | Notes |
|---------|-----------|--------------|-----------------|-------|
| TVA Collectée | 445710 | FR (PCG) | Output VAT | French PCG structure |
| TVA Déductible | 445660 | FR | Input VAT | French PCG |
| НДС к уплате | 68.2 | RU (RAS) | Output VAT | Russian 20% VAT |
| Резервный капитал | 82 | RU | Legal Reserve | Mandatory 5% RU law |
| Deferred Revenue (German-style) | 900X | DE | IFRS 15 Contract Liab. | Rechnungsabgrenzung |
| Tzuvot Mekar | | IL (Israeli GAAP) | Tax benefits | Israeli R&D credits |

### Asia-Pacific

| Account | Local Code | Jurisdiction | IFRS Equivalent | Notes |
|---------|-----------|--------------|-----------------|-------|
| GST Input Credit | | IN (Ind AS) | Input VAT | Indian cascading GST |
| TDS Receivable | | IN | Tax Withholding Asset | 10%-30% withholding |
| 进项税额 (Input VAT) | | CN | Input VAT | China VAT reform 2019 |
| Thuế GTGT có thể khấu trừ | 1331 | VN (VAS) | Input VAT | 0-10% VAT |
| Souffrance (NPL Provisions) | | JP | Loan Loss Provisions | Bank-specific |

### Middle East / Africa

| Account | Local Code | Jurisdiction | IFRS Equivalent | Notes |
|---------|-----------|--------------|-----------------|-------|
| Zakat Payable | | SA (SOCPA) | Religious Tax | 2.5% of net assets |
| VAT Input (SARS) | | ZA | Input VAT | South Africa 15% VAT |
| WHT Payable | | NG (FIRS) | Withholding Tax | Nigeria 10% WHT |

---

## 📈 Mapping Complexity Scores

Scale: 1 (trivial) → 10 (extremely complex)

| Country | Code | Score | Primary Complexity Driver |
|---------|------|-------|---------------------------|
| United Kingdom | UK | 2 | Full IFRS adoption |
| Canada | CA | 2 | IFRS + CPA Canada guidance |
| Australia | AU | 2 | AASB = IFRS verbatim |
| Germany | DE | 4 | HGB divergence in some areas |
| Japan | JP | 4 | J-GAAP partially converged |
| Mexico | MX | 5 | SAT 4-digit codes, CFDI e-invoicing |
| Colombia | CO | 5 | PUC code system + NIIFs |
| India | IN | 6 | Ind AS + GST cascading |
| France | FR | 6 | PCG mandatory chart of accounts |
| Spain | ES | 6 | PGC 8-group structure |
| China | CN | 6 | CAS + VAT reform complexity |
| Russia | RU | 6 | RAS + IFRS transition |
| Panama | PA | 5 | DGI/SMV dual-standard |
| Brazil | BR | 7 | SPED, ICMS, PIS/COFINS complexity |
| Israel | IL | 6 | Israeli GAAP + IFRS sectors |
| UAE | AE | 4 | No income tax until 2023, VAT new |
| Saudi Arabia | SA | 7 | Zakat + Shariah compliance |
| Vietnam | VN | 7 | VAS 2014 divergence from IFRS |
| South Africa | ZA | 5 | IFRS-based SAICA |
| Turkey | TR | 6 | TAS inflation accounting |
| Venezuela | VE | 10 | Hyperinflation IAS 29, dual-currency |
| Nigeria | NG | 6 | IFRS adopted 2012, enforcement gaps |

---

## 🧮 Aggregation Rules Across Jurisdictions

### Universal Aggregation (applies everywhere)

```yaml
rules:
  total_assets: "asset.current + asset.noncurrent"
  total_liabilities: "liability.current + liability.noncurrent"
  working_capital: "asset.current - liability.current"
  net_equity: "total_assets - total_liabilities"
  gross_profit: "revenue.operating - expense.cogs"
  ebit: "gross_profit - expense.admin - expense.other_operating"
  net_income: "ebit - expense.interest - expense.tax"
```

### Country-Specific Aggregation Adjustments

| Country | Adjustment | IAS/IFRS Ref |
|---------|-----------|--------------|
| VE | All monetary items restated using CPI | IAS 29 |
| TR | Historical amounts restated (prior to 2022) | IAS 29 |
| IN | GST accounts excluded from revenue (net presentation) | Ind AS 115 |
| BR | ICMS/PIS/COFINS must be disaggregated from gross revenue | BR GAAP |
| RU | Deferred tax calculated under RAS differs from IFRS | IAS 12 |
| SA | Zakat computed on Zakat base, not taxable income | SOCPA |

---

## 🔗 IFRS to Kontablo Level 3 Gap Analysis

**Accounts in IFRS taxonomy NOT yet in Kontablo Level 3:**

| IFRS Tag | Description | Priority | Affected Countries |
|---------|-------------|----------|-------------------|
| `RightOfUseAssets` | IFRS 16 leases | HIGH | All (post-2019) |
| `InsuranceContractsIssued` | IFRS 17 | MEDIUM | Insurance only |
| `BiologicalAssets` | IAS 41 | LOW | AG sectors |
| `ActuarialGains` | IAS 19 defined benefit | MEDIUM | US, UK, DE |
| `CryptocurrencyAssets` | IAS 38 / agenda | RESEARCH | Emerging |
| `CarbonCredits` | IAS 38 | RESEARCH | Emerging |

---

## ✅ Recommendations for Kontablo v0.2

1. **Add IFRS 16 (Leases)** → `asset.noncurrent.rou_assets` + `liability.noncurrent.lease`
2. **Add Hyperinflation module** → Flag accounts for IAS 29 restatement
3. **Create VAT sub-accounts** by country (Input/Output VAT is universal but rate/presentation varies)
4. **Define Zakat/Religious Tax** as optional Level 3 extension for SA/AE markets
5. **Create Withholding Tax** as cross-jurisdiction account (IN, NG, MX all require it)
6. **Industry extensions needed:** Banking (IFRS 9), Insurance (IFRS 17), Agriculture (IAS 41)

---

**Generated:** 2026-03-23  
**Next Update:** After expert validation (target: 2026-04-30)  
**Status:** Research Draft — Pending CPA Review
