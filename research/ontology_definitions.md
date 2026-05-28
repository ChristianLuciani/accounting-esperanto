# Kontablo Universal Node Definitions (Deterministic Boundaries)

This file defines the strict logical boundaries for the Kontablo Universal Level 3 accounts. These definitions are designed to be queried by AI Agents (via MCP) to ensure 100% deterministic mapping with zero ambiguity.

## 1. asset.current.cash
- **Deterministic Question:** Is the value represented by physical currency, legal tender at bank, or a near-money instrument redeemable at par in < 90 days?
- **Inclusion Criteria:**
  - Physical coins and banknotes (Caja/Caixa/Petty Cash).
  - Unrestricted bank deposits (Checking/Savings).
  - Digital wallet balances (USD-tethered, Central Bank Digital Currencies).
- **Exclusion Criteria:**
  - Restricted cash (Escrow accounts) -> Map to `asset.current.other`.
  - Marketable securities with price risk -> Map to `asset.current.investments`.
  - Cryptocurrencies with market volatility (BTC, ETH) -> Map to `asset.current.intangible_crypto`.

## 2. asset.current.receivables
- **Deterministic Question:** Is this a legally enforceable claim for payment from a third party for goods/services already delivered?
- **Inclusion Criteria:**
  - Unpaid customer invoices (Accounts Receivable).
  - Accrued revenue (Earned but not billed).
- **Exclusion Criteria:**
  - Employee loans -> Map to `asset.current.other_receivables`.
  - Tax refunds due from state -> Map to `asset.current.tax_assets`.

## 3. liab.current.payables
- **Deterministic Question:** Is this a present obligation to pay a third party for goods/services already received?
- **Inclusion Criteria:**
  - Trade supplier invoices (Accounts Payable).
  - Accrued expenses.
- **Exclusion Criteria:**
  - Bank loans -> Map to `liab.current.short_term_debt`.
  - Salary obligations -> Map to `liab.current.provisions_personnel`.

## 4. rev.operating.sales
- **Deterministic Question:** Is this an inflow of economic benefit arising from the company's primary business activities (Gross)?
- **Inclusion Criteria:**
  - Sale of primary products.
  - Service fees from primary business lines.
- **Exclusion Criteria:**
  - Gain on sale of assets -> Map to `other_income`.
  - Interest income -> Map to `finance_income`.

---

## Technical Mapping Logic (For AI Agents)
IF code_name matching "Caja" AND is_physical == True:
    TARGET_ID = "asset.current.cash"
    JUSTIFICATION = "Meets deterministic criteria for Physical legal tender."
ELIF code_name matching "Tien mat" AND country == "VN":
    TARGET_ID = "asset.current.cash"
    JUSTIFICATION = "Vietnamese VAS 111 (Tien mat) maps 1:1 to Universal Cash node."
