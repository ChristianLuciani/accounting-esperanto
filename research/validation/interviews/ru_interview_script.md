# Kontablo Expert Validation: Russia Interview Script (RU)

## Overview
- **Interviewer:** [Name]
- **Participant ID:** [RV-RU-XXX]
- **Jurisdiction:** Russia
- **Date:** [YYYY-MM-DD]
- **Duration:** 45-60 minutes

---

## 1. Introduction (5 min)
(Standard introduction)

---

## 2. Professional Profile (5 min)
- "Could you briefly describe your experience with **PBU (Pravila Bukhgalterskogo Ucheta)** and IFRS reconciliation in a Russian corporate context?"
- "Do you work primarily in 1C or on global ERPs like SAP R/3 or Microsoft Dynamics?"

---

## 3. Core Mapping Review (20 min)
(Review standard PBU/Local codes to Kontablo mapping)

| Kontablo ID | PBU Code | Label (RU/Cyrillic) | Confidence (1-5) | Comments/Corrections |
|-------------|----------|---------------------|------------------|----------------------|
| asset.current.cash | 50/51 | Касса / Расчетные счета | | |
| asset.current.receivables| 62 | Расчеты с покупателями | | |
| asset.current.vat_input| 19 | НДС по приобретенным ценностям | | |
| asset.current.inventory | 10/41 | Материалы / Товары | | |
| liability.current.payables| 60 | Расчеты с поставщиками | | |
| liability.current.vat_output| 68-nds | НДС (Налог на добавленную стоимость) | | |
| liability.current.salaries| 70 | Расчеты с персоналом по оплате труда | | |
| revenue.operating | 90 | Продажи | | |
| expense.cogs | 90-2 | Себестоимость продаж | | |
| expense.admin | 26 | Общехозяйственные расходы | | |

---

## 4. Russia-Specific Questions (15 min)
- **Local Standard (PBU):** "Russian PBU has very specific numeric account codes. Does Kontablo's semantic approach (e.g. mapping 62 to 'asset.current.receivables') lose critical data required for statutory 'Bukhgaltersky Balans' reporting?"
- **Cyrillic Semantic Parsing:** "Do you believe our AI can extract the semantic nuance of 'Уставный капитал' (Share Capital) vs 'Нераспределенная прибыль' (Retained Earnings) effectively?"

---

## 5. Co-responsibility & AI Governance (5 min)
- "The 'Inconsistency Flag' mechanism triggers when a human accountant maps a PBU code 51 (Bank) to a non-current asset node. How useful is this for preventing internal data entry errors in a heavy-compliance environment like 1C?"

---

## 6. Closing (5 min)
(Standard closure)
