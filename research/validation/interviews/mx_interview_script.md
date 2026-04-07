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

## 4. Mexico-Specific Questions (15 min)
- **VAT Distinction:** "How do you handle the distinction between **IVA trasladado** (output VAT) and **IVA acreditable** (input VAT) in your chart of accounts? Does Kontablo's simple 'asset' vs 'liability' split handle the cash-basis VAT requirement in Mexico?"
- **CFDI Compliance:** "The SAT requires CFDI electronic invoicing with specific code grouping. Does Kontablo's high-level abstraction layer (e.g., 'asset.current.receivables') lose critical information required for SAT reporting?"
- **Chart of Accounts Grouping:** "Most ERPs in Mexico use the 'Código Agrupador del SAT'. Is mapping from this agrupador to Kontablo feasible for automated reporting?"

---

## 5. Qualitative Discussion (10 min)
- **Feasibility:** "Does a 30-account taxonomy cover most Routine operations for an SME in Mexico?"
- **Inflation Accounting:** "Although currently low, do you see a need for inflation adjustments (B-10) in this mapping standard?"

---

## 6. Closing (5 min)
(Standard closure)
