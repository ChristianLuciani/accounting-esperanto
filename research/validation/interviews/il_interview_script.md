# Kontablo Expert Validation: Israel Interview Script (IL)

## Overview
- **Interviewer:** [Name]
- **Participant ID:** [RV-XXX]
- **Jurisdiction:** Israel
- **Date:** [YYYY-MM-DD]
- **Duration:** 45-60 minutes

---

## 1. Introduction (5 min)
(Standard introduction)

---

## 2. Professional Profile (5 min)
- "Could you briefly describe your experience with **Israeli GAAP** and **IFRS**?"
- "What is your role in reporting for Israeli entities (auditor, controller, CFO)?"

---

## 3. Core Mapping Review (20 min)
(Review Hebrew/English accounts to Kontablo mapping)

| Kontablo ID | Account Code/Name | Label (HE) | Confidence (1-5) | Comments/Corrections |
|-------------|-------------------|------------|------------------|----------------------|
| asset.current.cash | 1010/1020 | קופה / בנק | | |
| asset.current.receivables| 1100 | לקוחות | | |
| asset.current.vat_input| 2200 | מע"מ תשומות | | |
| asset.current.inventory | 1200 | מלאי | | |
| asset.noncurrent.ppe | 1300 | רכוש קבוע | | |
| liability.current.payables| 2100 | ספקים | | |
| liability.current.vat_output| 2210 | מע"מ עסקאות | | |
| liability.current.tax | 2300 | מוסדות - מס הכנסה | | |
| revenue.operating | 4001 | מכירות | | |
| expense.cogs | 5001 | עלות המכר | | |
| expense.admin | 6001 | משכורות | | |

---

## 4. Israel-Specific Questions (15 min)
- **VAT (Ma'am) Reporting:** "Israel has strict monthly VAT reporting (Ma'am 874). How is the distinction between 'Output' and 'Input' typically handled? Does Kontablo's high-level mapping create any audit trail issues?"
- **Withholding Tax:** "WHT (Niku'i Mas) is common in Israel. Should '1500' be separated from receivables in Kontablo to allow for easier reconciliation of tax certificates?"
- **Linked-Accounts (Indexation):** "Israeli GAAP often uses linked (צמוד) accounts (CPI, exchange rate). How should Kontablo handle the revaluation of these balances - as a separate finance expense/income line?"

---

## 5. Qualitative Discussion (10 min)
- **Feasibility:** "Does a 30-account core cover the routine transactions for a typical Israeli 'Hevra'?"

---

## 6. Closing (5 min)
(Standard closure)
