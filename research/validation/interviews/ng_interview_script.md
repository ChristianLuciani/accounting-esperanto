# Kontablo Expert Validation: Nigeria Interview Script (NG)

## Overview
- **Interviewer:** [Name]
- **Participant ID:** [RV-NG-XXX]
- **Jurisdiction:** Nigeria
- **Date:** [YYYY-MM-DD]
- **Duration:** 45-60 minutes

---

## 1. Introduction (5 min)
(Standard introduction)

---

## 2. Professional Profile (5 min)
- "Could you briefly describe your experience with **FRCN (Financial Reporting Council of Nigeria)** requirements and local tax compliance (FIRS)?"
- "What accounting software is common for Nigerian SMEs and multinationals in your experience (SAGE, Quickbooks, Odoo)?"

---

## 3. Core Mapping Review (20 min)
(Review standard Nigerian practices (often IFRS-based with local nuances))

| Kontablo ID | Label (EN/Local) | Confidence (1-5) | Comments/Corrections |
|-------------|-------------------|------------------|----------------------|
| asset.current.cash | Cash and Bank | | |
| asset.current.receivables| Trade Debtors | | |
| asset.current.wht_receivable| WHT (Withholding Tax) Asset| | |
| asset.current.vat_input| VAT Input | | |
| liability.current.payables| Trade Creditors | | |
| liability.current.tax | Income Tax Liability | | |
| liability.current.wat_payable| WHT (Withholding Tax) Liability| | |
| revenue.operating | Sales Revenue | | |
| expense.admin | Administrative Expenses | | |

---

## 4. Nigeria-Specific Questions (15 min)
- **Withholding Tax (WHT):** "WHT is a critical part of Nigerian commerce. Does Kontablo's current taxonomy for `asset.current.other_tax` and `liability.current.tax` accurately capture the nuance of WHT credits versus final tax liabilities?"
- **Multiple Exchange Rates:** "How do you handle the discrepancy between official (Naira) and parallel market rates in your ledgers? Should Kontablo allow for custom exchange rate overrides at the entry level?"

---

## 5. Co-responsibility & AI Governance (5 min)
- "Nigerian regulatory space is moving toward digitalization. Do you believe the 'Inconsistency Flag' mechanism in Kontablo increases audit confidence in a way that aligns with FRCN's future digital reporting goals?"

---

## 6. Closing (5 min)
(Standard closure)
