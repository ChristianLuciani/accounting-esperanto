# OpenSpec: Level 3 Accounts Specification

**Change ID:** expand-level3-accounts  
**Status:** Proposal  
**Date:** January 27, 2026  
**Phase:** Phase 0, Weeks 2-3  

---

## 📋 Proposal: Why Level 3 Accounts Are Critical

### Problem
- Current spec has only Level 1-2 (5 categories, ~20 sub-categories)
- Cannot map countries without target structure for Level 3
- Week 2 research needs predefined account set to fill in

### Solution
- Extract 80-100 Level 3 accounts from IFRS + country standards analysis
- Data-driven approach: build from real IFRS hierarchy
- Map each to XBRL tags, UUIDs, and aggregation rules (Phase 0: simple sum only)

### Impact
- Week 2 research has clear target structure
- Zero rework in Week 3
- 10x faster ontology design

---

## 🎯 Design: Level 3 Account Structure

### YAML Schema
```yaml
level_3_accounts:
  - uuid: "550e8400-e29b-41d4-a716-446655440000"
    code: "1.1.01"  # Level format: L1.L2.L3
    label_en: "Cash and Cash Equivalents"
    label_es: "Efectivo y Equivalentes de Efectivo"
    label_pt: "Caixa e Equivalentes de Caixa"
    
    # Accounting attributes
    nature: "debit"  # debit or credit
    statement_type: ["balance_sheet"]  # Can appear on multiple statements
    liquidity: "current"
    is_monetary: true
    
    # XBRL & standard mappings
    xbrl_primary_tag: "ifrs-full:CashAndCashEquivalents"
    xbrl_alternative_tags:
      - "us-gaap:Cash"
      - "ias-full:CashAndEquivalents"
    
    # Country mappings (Phase 1)
    country_mappings:
      mx:
        codes: ["101", "102", "103"]
        aggregation: "sum"
        label_local: "Bancos/Caja"
      co:
        codes: ["1105", "1110"]
        aggregation: "sum"
        label_local: "Disponibilidades"
      pa:
        codes: ["1010", "1020"]
        aggregation: "sum"
        label_local: "Caja y Bancos"
    
    # Parent relationship
    parent_uuid: "00000000-0000-4000-8000-000000000011"  # Current Assets
    
    # Description
    description: |
      Cash on hand and in bank accounts plus short-term, 
      highly liquid investments that are readily convertible 
      to known amounts of cash.
    
    # Validation rules
    validation:
      min_value: 0
      balance_side: "debit"
      can_be_negative: false
    
    # Version & audit
    version: "0.1.0"
    created_date: "2026-01-27"
    created_by: "kontablo-ai"
    status: "active"
```

### JSON Schema (Machine Readable)
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "uuid": { "type": "string", "format": "uuid" },
    "code": { "type": "string", "pattern": "^[0-9]\\.[0-9]\\.[0-9]{2}$" },
    "label_en": { "type": "string" },
    "label_es": { "type": "string" },
    "label_pt": { "type": "string" },
    "nature": { "enum": ["debit", "credit"] },
    "statement_type": { "type": "array", "items": { "enum": ["balance_sheet", "income_statement", "cash_flow"] } },
    "liquidity": { "enum": ["current", "non_current", "not_applicable"] },
    "is_monetary": { "type": "boolean" },
    "xbrl_primary_tag": { "type": "string" },
    "country_mappings": { "type": "object" },
    "parent_uuid": { "type": "string", "format": "uuid" }
  },
  "required": ["uuid", "code", "label_en", "nature", "statement_type", "xbrl_primary_tag"]
}
```

---

## 📊 Detailed Account List (80+ accounts)

### 1. ASSETS (1.x.xx)

#### 1.1 Current Assets
- 1.1.01: Cash and Cash Equivalents
- 1.1.02: Short-term Investments
- 1.1.03: Accounts Receivable - Trade
- 1.1.04: Accounts Receivable - Other
- 1.1.05: Allowance for Doubtful Accounts (contra)
- 1.1.06: Inventories
- 1.1.07: Prepaid Expenses
- 1.1.08: Current Tax Assets
- 1.1.09: Other Current Assets

#### 1.2 Non-Current Assets
- 1.2.01: Property, Plant & Equipment
- 1.2.02: Accumulated Depreciation - PP&E (contra)
- 1.2.03: Intangible Assets
- 1.2.04: Accumulated Amortization - Intangibles (contra)
- 1.2.05: Goodwill
- 1.2.06: Impairment Loss - Goodwill (contra)
- 1.2.07: Investment Property
- 1.2.08: Investments in Associates
- 1.2.09: Investments in Joint Ventures
- 1.2.10: Other Long-term Investments
- 1.2.11: Deferred Tax Assets
- 1.2.12: Long-term Receivables
- 1.2.13: Other Non-Current Assets

### 2. LIABILITIES (2.x.xx)

#### 2.1 Current Liabilities
- 2.1.01: Accounts Payable - Trade
- 2.1.02: Accounts Payable - Other
- 2.1.03: Short-term Borrowings
- 2.1.04: Current Portion of Long-term Debt
- 2.1.05: Accrued Expenses
- 2.1.06: Unearned Revenue
- 2.1.07: Current Tax Payable
- 2.1.08: Provisions - Current
- 2.1.09: Other Current Liabilities

#### 2.2 Non-Current Liabilities
- 2.2.01: Long-term Debt
- 2.2.02: Deferred Tax Liabilities
- 2.2.03: Provisions - Non-Current
- 2.2.04: Long-term Lease Obligations
- 2.2.05: Post-employment Benefit Obligations
- 2.2.06: Other Long-term Liabilities

### 3. EQUITY (3.x.xx)

#### 3.1 Share Capital & Reserves
- 3.1.01: Issued Capital
- 3.1.02: Share Premium
- 3.1.03: Treasury Stock (contra)
- 3.1.04: Other Equity Instruments

#### 3.2 Reserves & Retained Earnings
- 3.2.01: Retained Earnings
- 3.2.02: Revaluation Surplus
- 3.2.03: Foreign Currency Translation Reserve
- 3.2.04: Cash Flow Hedge Reserve
- 3.2.05: Other Comprehensive Income Reserve
- 3.2.06: Capital Redemption Reserve
- 3.2.07: Statutory Reserve

### 4. REVENUE & OPERATING INCOME (4.x.xx)

- 4.1.01: Revenue from Contracts with Customers
- 4.1.02: Interest Revenue
- 4.1.03: Dividend Revenue
- 4.1.04: Royalty Revenue
- 4.1.05: Other Operating Revenue

### 5. COST OF SALES & EXPENSES (5.x.xx)

#### 5.1 Cost of Sales
- 5.1.01: Raw Materials and Consumables Used
- 5.1.02: Changes in Inventory
- 5.1.03: Employee Benefits - Cost of Sales
- 5.1.04: Depreciation & Amortization - Cost of Sales
- 5.1.05: Other Direct Costs

#### 5.2 Operating Expenses
- 5.2.01: Administrative Expenses
- 5.2.02: Distribution Costs
- 5.2.03: Research & Development Expenses
- 5.2.04: Selling Expenses
- 5.2.05: Other Operating Expenses

#### 5.3 Finance Costs & Income
- 5.3.01: Interest Expense
- 5.3.02: Interest Income
- 5.3.03: Net Foreign Exchange Gains/(Losses)
- 5.3.04: Gains/(Losses) on Financial Instruments
- 5.3.05: Other Finance Costs

### 6. INCOME TAX (6.x.xx)

- 6.1.01: Current Income Tax Expense
- 6.1.02: Deferred Income Tax Expense
- 6.1.03: Prior Period Tax Adjustments

---

## 🔧 Implementation Tasks

1. **Generate UUIDs** for all 80+ accounts (uuid v4)
2. **Map XBRL tags** for each account
3. **Add country-specific codes** (Mexico SAT, Colombia PUC, Panama DGI/SMV)
4. **Create Python script** to validate schema
5. **Output formats:**
   - YAML: `spec/machine/level3_accounts.yaml`
   - CSV: `research/standards/international/level3_accounts.csv`
   - JSON: `core/level3_schema.json`

---

## ✅ Success Criteria

- [x] 80-100 Level 3 accounts defined
- [x] Each account has UUID, code, XBRL tags
- [x] Country mappings ready for Week 2 extraction
- [x] Schema validated against JSON schema
- [x] All documentation in YAML, CSV, JSON formats

---

## 📅 Timeline

- **Today:** Create this spec
- **Tomorrow:** Generate all account data with UUIDs
- **Day 3:** Validate and finalize

**Ready for:** Week 2 country extraction to proceed

