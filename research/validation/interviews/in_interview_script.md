# Kontablo Expert Validation: India Interview Script (IN)

## Overview
- **Interviewer:** [Name]
- **Participant ID:** [RV-XXX]
- **Jurisdiction:** India
- **Date:** [YYYY-MM-DD]
- **Duration:** 45-60 minutes

---

## 1. Introduction (5 min)
(Standard introduction)

---

## 2. Professional Profile (5 min)
- "Could you briefly describe your experience with **Ind AS** and **ICAI** requirements?"
- "What is your role in **GST** compliance and reporting?"

---

## 3. Core Mapping Review (20 min)
(Review Ind AS / GST accounts to Kontablo mapping)

| Kontablo ID | Schedule III / GST Account | Label | Confidence (1-5) | Comments/Corrections |
|-------------|----------------------------|-------|------------------|----------------------|
| asset.current.cash | 1001/1002 | Cash and Bank | | |
| asset.current.receivables| 1100 | Trade Receivables | | |
| asset.current.vat_input| 1400/1401/1402 | Input GST (CGST/SGST/IGST)| | |
| asset.current.inventory | 1200 | Inventories | | |
| asset.noncurrent.ppe | 1300 | PPE | | |
| liability.current.payables| 2100 | Trade Payables | | |
| liability.current.vat_output| 2201/2202/2203 | Output GST | | |
| liability.current.tax | 2500 | Provision for Tax | | |
| revenue.operating | 4001 | Revenue from Operations | | |
| expense.cogs | 5001 | Cost of Materials | | |
| expense.admin | 6001 | Salaries and Wages | | |

---

## 4. India-Specific Questions (15 min)
- **GST Complexity:** "India has a unique 3-tier GST (CGST, SGST, IGST). How do you typically handle Input Tax Credit (ITC) matching? Does mapping everything to a single 'vat_input' account in Kontablo lose vital compliance detail?"
- **Schedule III Consistency:** "The Companies Act (Schedule III) has specific disclosure requirements. Does Kontablo's L3 taxonomy align with your statutory reporting requirements?"
- **Statutory Dues:** "How do you handle statutory dues like PF, ESI, and LWF? Should these be separate from 'liability.current.payables'?"

---

## 5. Qualitative Discussion (10 min)
- **Feasibility:** "Can a 30-account core cover the majority of SME transactions in India? What about the 'MSME' specific disclosures?"
- **Ind AS vs. AS:** "For non-Ind AS companies, are the mappings equally valid?"

---

## 6. Closing (5 min)
(Standard closure)
