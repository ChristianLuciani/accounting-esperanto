# Kontablo Expert Validation: Germany Interview Script (DE)

## Overview
- **Interviewer:** [Name]
- **Participant ID:** [RV-XXX]
- **Jurisdiction:** Germany
- **Date:** [YYYY-MM-DD]
- **Duration:** 45-60 minutes

---

## 1. Introduction (5 min)
(Standard introduction)

---

## 2. Professional Profile (5 min)
- "Could you briefly describe your experience with **HGB (Handelsgesetzbuch)** and **IFRS** in Germany?"
- "Do you work with **SKR03** or **SKR04** standard charts of accounts?"

---

## 3. Core Mapping Review (20 min)
(Review SKR / HGB accounts to Kontablo mapping)

| Kontablo ID | SKR03 / HGB Account | Label (DE) | Confidence (1-5) | Comments/Corrections |
|-------------|---------------------|------------|------------------|----------------------|
| asset.current.cash | 1000/1200 | Kasse / Bank | | |
| asset.current.receivables| 1400 | Forderungen a.L.u.L.| | |
| asset.current.vat_input| 1571/1576 | Vorsteuer | | |
| asset.current.inventory | 3980 | Warenbestände | | |
| asset.noncurrent.ppe | 0400 | BGA (Betriebs- und Geschäftsausstattung)| | |
| liability.current.payables| 1600 | Verbindlichkeiten a.L.u.L.| | |
| liability.current.vat_output| 1771/1776 | Umsatzsteuer | | |
| liability.current.tax | 1810 | Körperschaftsteuer | | |
| revenue.operating | 8400 | Erlöse | | |
| expense.cogs | 3400 | Wareneingang | | |
| expense.admin | 4100 | Personalkosten | | |

---

## 4. Germany-Specific Questions (15 min)
- **HGB vs. IFRS:** "HGB emphasizes prudence (Prudence Principle), while Kontablo is IFRS-anchored. How do you handle deferred items (*Rechnungsabgrenzungsposten*)? Does the Kontablo mapping work effectively for them?"
- **SKR Consistency:** "Most German companies use SKR03 or SKR04. Is it feasible to provide a 1:1 mapping from SKR standard accounts to Kontablo L3 elements?"
- **E-Bilanz Compliance:** "Does the Kontablo mapping create any conflicts for the digital financial statement (*E-Bilanz*) required by the German tax authorities?"

---

## 5. Qualitative Discussion (10 min)
- **Feasibility:** "Does a 30-account core cover most routine bookkeeping for a German SME (*Mittelstand*)?"

---

## 6. Closing (5 min)
(Standard closure)
