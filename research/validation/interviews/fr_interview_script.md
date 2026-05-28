# Kontablo Expert Validation: France Interview Script (FR)

## Overview
- **Interviewer:** [Name]
- **Participant ID:** [RV-FR-XXX]
- **Jurisdiction:** France
- **Date:** [YYYY-MM-DD]
- **Duration:** 45-60 minutes

---

## 1. Introduction (5 min)
(Standard introduction)

---

## 2. Professional Profile (5 min)
- "Could you briefly describe your experience with **PCG (Plan Comptable Général)** and the standard FEC (Fichier des Écritures Comptables) for audits?"
- "What ERPs are you most familiar with in the French market (Sage 100, Cegid, SAP Business One, ERPNext)?"

---

## 3. Core Mapping Review (20 min)
(Review standard PCG codes to Kontablo mapping)

| Kontablo ID | PCG Code | Label (FR) | {line_number}: {original_line} | Comments/Corrections |
|-------------|----------|------------|---------------------------------|----------------------|
| asset.current.cash | 512 | Banques | | |
| asset.current.receivables| 411 | Clients | | |
| asset.current.vat_input| 44566 | TVA déductible sur ABS | | |
| asset.current.inventory | 31-37 | Stocks et en-cours | | |
| liability.current.payables| 401 | Fournisseurs | | |
| liability.current.vat_output| 44571 | TVA collectée | | |
| revenue.operating | 701-707 | Ventes de produits/services | | |
| expense.cogs | 601-607 | Achats stockés | | |
| expense.admin | 61-62 | Services extérieurs | | |

---

## 4. France-Specific Questions (15 min)
- **FEC Audit Standard:** "The French FEC is one of the most rigorous audit file formats in Europe. Does our graph-based approach to mapping (Level 3 Minimum Core) risk missing granular data points required for a FEC audit?"
- **Chart of Accounts Rigidity:** "The French PCG is very rigid. Do you think French CAs (Experts-Comptables) would trust an AI-driven mapping from PCG to a universal ontology, or would they prefer an 'Exact Lookup' table only?"

---

## 5. Co-responsibility & AI Governance (5 min)
- "The 'Co-responsibility' architecture ensures that if a human deviates from PCG-IFRS logic, it is flagged. In a context of potential tax avoidance audits (DGFIP), do you see this as an asset to the accountant's professional defense?"

---

## 6. Closing (5 min)
(Standard closure)
