# Kontablo Expert Validation: France Interview Script (FR)

## Overview
- **Interviewer:** [Name]
- **Participant ID:** [RV-XXX]
- **Jurisdiction:** France
- **Date:** [YYYY-MM-DD]
- **Duration:** 45-60 minutes

---

## 1. Introduction (5 min)
(Standard introduction)

---

## 2. Professional Profile (5 min)
- "Could you briefly describe your experience with **PCG (Plan Comptable Général)** and **FEC (Fichier des Écritures Comptables)** compliance?"
- "What is your primary industry sector in France?"

---

## 3. Core Mapping Review (20 min)
(Review PCG classes to Kontablo mapping)

| Kontablo ID | PCG Code | Label (FR) | Confidence (1-5) | Comments/Corrections |
|-------------|----------|------------|------------------|----------------------|
| asset.current.cash | 512/53 | Banque / Caisse | | |
| asset.current.receivables| 411 | Clients | | |
| asset.current.vat_input| 44566 | TVA Déductible | | |
| asset.current.inventory | 37 | Stocks | | |
| asset.noncurrent.ppe | 215/218 | Installations / Immos | | |
| liability.current.payables| 401 | Fournisseurs | | |
| liability.current.vat_output| 44571 | TVA Collectée | | |
| liability.current.tax | 444 | Impôts sur les bénéfices| | |
| revenue.operating | 707 | Ventes de marchandises | | |
| expense.cogs | 607 | Achats de marchandises | | |
| expense.admin | 641 | Rémunérations | | |

---

## 4. France-Specific Questions (15 min)
- **FEC Compliance:** "France requires the FEC (Audit File). Does Kontablo's high-level mapping create any challenges for future FEC audits?"
- **Social Charges:** "France has complex social security charges (*Charges sociales*). Is '641' + '43' enough, or should we break down social charges further in Kontablo for French entities?"
- **Chart of Accounts Rigidity:** "French accounting is very standardized via the PCG. How easy is it to map your typical SME's chart of accounts to the Kontablo 'Level 3' taxonomy?"

---

## 5. Qualitative Discussion (10 min)
- **Feasibility:** "Does a 30-account core cover most routine transactions for a French TPE/PME?"

---

## 6. Closing (5 min)
(Standard closure)
