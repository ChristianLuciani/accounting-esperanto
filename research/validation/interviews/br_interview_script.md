# Kontablo Expert Validation: Brazil Interview Script (BR)

## Overview
- **Interviewer:** [Name]
- **Participant ID:** [RV-XXX]
- **Jurisdiction:** Brazil
- **Date:** [YYYY-MM-DD]
- **Duration:** 45-60 minutes

---

## 1. Introduction (5 min)
(Standard introduction)

---

## 2. Professional Profile (5 min)
- "Briefly describe your experience with **CPC (Comitê de Pronunciamentos Contábeis)** and **SPED (ECD/ECF)** compliance?"
- "What is your experience with indirect tax calculations (ICMS/PIS/COFINS/ISS)?"

---

## 3. Core Mapping Review (20 min)
(Review standard Plano Referencial codes to Kontablo mapping)

| Kontablo ID | Plano Referencial | Label (PT-BR) | Confidence (1-5) | Comments/Corrections |
|-------------|-------------------|---------------|------------------|----------------------|
| asset.current.cash | 1.01.01 | Caixa e Equivalentes | | |
| asset.current.receivables| 1.01.03 | Contas a Receber | | |
| asset.current.vat_input| 1.01.04 | Tributos a Recuperar | | |
| asset.current.inventory | 1.01.02 | Estoques | | |
| asset.noncurrent.ppe | 1.02.04 | Imobilizado | | |
| liability.current.payables| 2.01.02 | Fornecedores | | |
| liability.current.vat_output| 2.01.05 | Obrigações Tributárias| | |
| liability.current.tax | 2.01.05.06 | IRPJ e CSLL a Pagar | | |
| revenue.operating | 4.01.01 | Venda de Mercadorias | | |
| expense.cogs | 5.01 | Custo das Mercadorias | | |
| expense.admin | 5.02.02 | Despesas Adm | | |

---

## 4. Brazil-Specific Questions (15 min)
- **Tax Complexity:** "Brazil has five major tax contributions (ICMS, PIS, COFINS, ISS, IPI). How do you typically structure these in your chart of accounts? Does Kontablo's single 'vat_output' and 'vat_input' oversimplify?"
- **SPED Integration:** "Can Kontablo coexist with SPED requirements, or does the abstraction create mapping gaps (e.g., related to 'registros' like the 0150 or I150)?"
- **Accounting Reconciliation:** "Most companies keep separate accounts for 'Credit at harvest' vs 'Credit on sales'. Is this distinction handled adequately?"

---

## 5. Qualitative Discussion (10 min)
- **Feasibility:** "Does a 30-account taxonomy cover most Routine operations for a company in Brazil (Lucro Real or Lucro Presumido)?"
- **Inflationary Adjustments:** "While not currently used, do you see value in the 'historical-cost vs constant-currency' mapping?"

---

## 6. Closing (5 min)
(Standard closure)
