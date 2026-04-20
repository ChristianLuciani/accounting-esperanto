# Kontablo Expert Validation: Vietnam Interview Script (VN)

## Overview
- **Interviewer:** [Name]
- **Participant ID:** [RV-VN-XXX]
- **Jurisdiction:** Vietnam
- **Date:** [YYYY-MM-DD]
- **Duration:** 45-60 minutes

---

## 1. Introduction (5 min)
(Standard introduction about Kontablo as a universal subledger for the M2M economy)

---

## 2. Professional Profile (5 min)
- "Could you briefly describe your experience with **VAS (Vietnamese Accounting Standards)** and local tax compliance?"
- "Do you work with non-Latin accounting software or systems that use the Vietnamese language?"

---

## 3. Core Mapping Review (20 min)
(Review standard VAS-compliant codes to Kontablo mapping)

| Kontablo ID | VAS Code | Label (VN) | Confidence (1-5) | Comments/Corrections |
|-------------|----------|------------|------------------|----------------------|
| asset.current.cash | 111 | Tiền mặt | | |
| asset.current.bank | 112 | Tiền gửi ngân hàng | | |
| asset.current.receivables| 131 | Phải thu của khách hàng | | |
| asset.current.vat_input| 133 | Thuế GTGT được khấu trừ | | |
| asset.current.inventory | 152/156 | Nguyên liệu / Hàng hóa | | |
| liability.current.payables| 331 | Phải trả cho người bán | | |
| liability.current.vat_output| 3331 | Thuế GTGT phải nộp | | |
| revenue.operating | 511 | Doanh thu bán hàng và CCDV | | |
| expense.cogs | 632 | Giá vốn hàng bán | | |

---

## 4. Vietnam-Specific Questions (10 min)
- **Non-Latin Mapping:** "Does Kontablo's AI engine accurately capture the semantic meaning of Vietnamese account names (e.g., 'Phải thu' vs 'Phải trả')?"
- **VAT Settlement:** "In Vietnam, VAT (GTGT) settlement is highly ritualized. Does our asset/liability split for VAT cover your monthly settlement needs?"

---

## 5. Co-responsibility & AI Governance (10 min)
- "In the 'Co-responsibility' model, if a human accountant overrides a mapping for 'Tiền mặt' into an incorrect node, the system flags it as an inconsistency for the audit report. Does this help your internal controls, or is it seen as too disruptive?"

---

## 6. Closing (5 min)
(Standard closure)
