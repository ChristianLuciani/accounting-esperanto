# Kontablo Expert Validation: Turkey Interview Script (TR)

## Overview
- **Interviewer:** [Name]
- **Participant ID:** [RV-TR-XXX]
- **Jurisdiction:** Turkey
- **Date:** [YYYY-MM-DD]
- **Duration:** 45-60 minutes

---

## 2. Professional Profile (5 min)
- "Could you briefly describe your experience with **TDHP (Tek Düzen Hesap Planı)** and Turkish tax compliance?"
- "Do you work with global ERPs in Turkey (SAP R/3, Dynamics NAV) or local ones like Logo or Micro?"

---

## 3. Core Mapping Review (20 min)
(Review standard Turkish TDHP codes to Kontablo mapping)

| Kontablo ID | TDHP Code | Label (TR) | Confidence (1-5) | Comments/Corrections |
|-------------|-----------|------------|------------------|----------------------|
| asset.current.cash | 100/102 | Kasa / Bankalar | | |
| asset.current.receivables| 120 | Alıcılar | | |
| asset.current.vat_input| 191 | İndirilecek KDV | | |
| asset.current.inventory | 153/154 | Ticari Mallar / Mamuller | | |
| liability.current.payables| 320 | Satıcılar | | |
| liability.current.vat_output| 391 | Hesaplanan KDV | | |
| liability.current.tax_liab| 360-361 | Ödenecek Vergi ve Fonlar | | |
| revenue.operating | 600 | Yurtiçi Satışlar | | |
| expense.cogs | 621 | Satılan Ticari Mallar Maliyeti | | |
| expense.admin | 770 | Genel Yönetim Giderleri | | |

---

## 4. Turkey-Specific Questions (15 min)
- **Inflation Accounting:** "Turkey recently implemented inflation adjustments (TAS 29). How is this handled in your ledger? Do you believe Kontablo's graph should have a dedicated node for 'Inflation Correction Surplus/Deficit'?"
- **VAT Disparity:** "Turkish VAT rates are highly variable (1%, 8%, 18%). Does Kontablo's high-level 'asset.current.vat_input' node lose information that you need for your BAS-style tax filing?"

---

## 5. Co-responsibility & AI Governance (5 min)
- "The 'Inconsistency Note' is an audit comment left by the AI when a human makes an incoherent mapping (e.g. mapping 100-Kasa to a non-current asset). Given the high level of tax scrutiny in Turkey, do you think this feature helps avoid audit penalties?"

---

## 6. Closing (5 min)
(Standard closure)
