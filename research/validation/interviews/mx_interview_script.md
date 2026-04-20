# Kontablo Expert Validation: Mexico Interview Script (MX)

## Overview
- **Interviewer:** [Name]
- **Participant ID:** [RV-XXX]
- **Jurisdiction:** Mexico
- **Date:** [YYYY-MM-DD]
- **Duration:** 45-60 minutes

---

## 1. Introduction (5 min)
(Standard introduction as per generic script)

---

## 2. Professional Profile (5 min)
- "Could you briefly describe your experience with **NIF (Normas de Información Financiera)** and **SAT** compliance?"
- "Do you work with CFDI accounting XMLs for electronic accounting (Contabilidad Electrónica)?"

---

## 3. Core Mapping Review (20 min)
(Review standard SAT-compliant codes to Kontablo mapping)

| Kontablo ID | SAT Agrupador | Label (ES) | Confidence (1-5) | Comments/Corrections |
|-------------|---------------|------------|------------------|----------------------|
| asset.current.cash | 101/102 | Caja / Bancos | | |
| asset.current.receivables| 105 | Clientes | | |
| asset.current.vat_input| 118/119 | IVA Acreditable / Pendiente | | |
| asset.current.inventory | 115 | Inventarios | | |
| asset.noncurrent.ppe | 151-176 | Activo Fijo (Maquinaria/Escritorio)| | |
| liability.current.payables| 201 | Proveedores | | |
| liability.current.vat_output| 208/209 | IVA Trasladado / Pendiente | | |
| liability.current.tax | 213 | Impuestos por Pagar | | |
| revenue.operating | 401 | Ventas y/o Servicios | | |
| expense.cogs | 501 | Costo de Ventas | | |
| expense.admin | 601 | Gastos de Administración | | |

---

## 4. Co-responsibility & AI Governance (10 min)
- **Concept Presentation:** "In Kontablo, we use a 'Co-responsibility Architecture'. If an AI proposes a mapping that violates deterministic rules (e.g. mapping cash to a non-current asset), the system allows the human to override it but leaves an 'Inconsistency Flag' and an audit note. What is your opinion on this approach for reducing ledger corruption?"
- **Trust:** "Does having an AI 'monitor' human entries for logical consistency increase your confidence in the resulting financial statements, or do you feel it undermines the accountant's authority?"
- **Audit Value:** "For a tax audit by the SAT, do you think having these 'AI warnings' documented on problematic entries would be beneficial or harmful for the company?"

---

## 5. Agentic Economy & M2M (10 min)
- **M2M Transactions:** "Are you seeing any rise in autonomous or high-frequency digital transactions (API-driven payments)? How would you record 10,000 micro-transactions per day if they were executed by an autonomous AI agent?"
- **Kontablo ID as Subledger:** "Kontablo proposes a universal ID (`asset.current.cash`) as the target for these AI agents, bypassing local tax codes in the initial booking. Does this separation between 'Agentic Execution' and 'Statutory Reporting' make sense for your workflow?"

---

## 6. Qualitative Discussion & Future Work (5 min)
- **Feasibility:** "Does a 30-account taxonomy cover most Routine operations for an SME in Mexico?"
- **Inflation Accounting:** "Although currently low, do you see a need for inflation adjustments (B-10) in this mapping standard?"

---

## 7. Closing (5 min)
(Standard closure)
