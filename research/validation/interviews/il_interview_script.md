# Kontablo Expert Validation: Israel Interview Script (IL)

## Overview
- **Interviewer:** [Name]
- **Participant ID:** [RV-IL-XXX]
- **Jurisdiction:** Israel
- **Date:** [YYYY-MM-DD]
- **Duration:** 45-60 minutes

---

## 2. Professional Profile (5 min)
- "Could you briefly describe your experience with **Israeli Income Tax** and the local reporting requirement (PCN 874)?"
- "Do you use local ERPs like Hashavshevet or global ones like SAP Business One/Oracle?"

---

## 3. Core Mapping Review (20 min)
(Review standard Israeli practices (NIIF/GAAP hybrid with local nuances))

| Kontablo ID | Label (HE/EN) | Confidence (1-5) | Comments/Corrections |
|-------------|---------------|------------------|----------------------|
| asset.current.cash | מזומנים ושווי מזומנים / Cash & Cash Equiv | | |
| asset.current.receivables| לקוחות / Customers | | |
| asset.current.vat_input| מע"מ תשומות / Input VAT | | |
| liability.current.payables| ספקים / Suppliers | | |
| liability.current.vat_output| מע"מ עסקאות / Output VAT | | |
| liability.current.provisions| הפרשות לחופשה והבראה / Vacation/Recuperation Provisions| | |
| revenue.operating | הכנסות / Revenue | | |
| expense.cogs | עלות המכר / COGS | | |
| expense.admin | הוצאות הנהלה וכלליות / Admin Expenses | | |

---

## 4. Israel-Specific Questions (15 min)
- **Dual Currency:** "Many Israeli companies (especially high-tech) maintain books in both NIS (local) and USD (reporting). How do you manage this in your ERP? Should Kontablo's ontology include specific nodes for currency revaluation?"
- **Vacation/Recuperation (Severance):** "Israel has specific mandatory social provisions (Recuperation/Havara). Does Kontablo's 'liability.noncurrent.provisions_personnel' capture the complexity of the Severance Pay Act (Pitzuim)?"

---

## 5. Co-responsibility & AI Governance (5 min)
- "The Israeli Tax Authority (ITA) is digitizing (e-invoicing 'Israel Invoices'). Do you think an AI-driven 'audit witness' (Inconsistency Flag) adds value for tax safety within the Israeli high-tech corporate governance?"

---

## 6. Closing (5 min)
(Standard closure)
