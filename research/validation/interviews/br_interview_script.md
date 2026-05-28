# Kontablo Expert Validation: Brazil Interview Script (BR)

## Overview
- **Interviewer:** [Name]
- **Participant ID:** [RV-BR-XXX]
- **Jurisdiction:** Brazil
- **Date:** [YYYY-MM-DD]
- **Duration:** 45-60 minutes

---

## 1. Introduction (5 min)
(Standard introduction)

---

## 2. Professional Profile (5 min)
- "Could you briefly describe your experience with **SPED (Sistema Público de Escrituração Digital)** and the Brazilian Reference Chart of Accounts (Plano de Contas Referencial)?"
- "What is your primary ERP for tax calculation in Brazil (Sankhya, TOTVS, SAP S/4HANA)?"

---

## 3. Core Mapping Review (20 min)
(Review standard Plano Referencial codes to Kontablo mapping)

| Kontablo ID | Label (PT) | Confidence (1-5) | Comments/Corrections |
|-------------|------------|------------------|----------------------|
| asset.current.cash | Caixa / Bancos | | |
| asset.current.receivables| Duplicatas a Receber | | |
| asset.current.tax_asset| Impostos a Recuperar (PIS/COFINS)| | |
| asset.current.inventory | Estoques | | |
| liability.current.payables| Fornecedores | | |
| liability.current.tax_liab| Impostos a Recolher (ICMS/ISS)| | |
| liability.current.labor | Salários e Encargos | | |
| revenue.operating | Receita Bruta de Vendas | | |
| expense.cogs | Custo das Mercadorias Vendidas (CMV)| | |

---

## 4. Brazil-Specific Questions (15 min)
- **Extreme Tax Complexity:** "In Brazil, PIS, COFINS, ICMS, and IPI have complex credit/debit logic. Does Kontablo's simple 'asset.current.tax_asset' vs 'liability.current.tax_liability' node capture enough detail for a Brazilian multinational, or is it too high-level?"
- **SPED ECF/ECD Reconciliation:** "Every year, companies must reconcile their corporate books with the SPED Reference Chart. Does Kontablo's ontology speed up this reconciliation process?"

---

## 5. Co-responsibility & AI Governance (5 min)
- "Brazil has one of the world's most advanced digital audit systems (SPED). Does a 'Co-responsibility' model (AI warning the accountant about inconsistencies) provide a useful second layer of protection before the submission of the SPED file?"

---

## 6. Closing (5 min)
(Standard closure)
