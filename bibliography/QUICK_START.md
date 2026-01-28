# 🚀 Quick Start: Bibliography Gathering

**Start Date:** January 28, 2026  
**Deadline:** February 1, 2026  
**Goal:** Collect all authoritative accounting standards

---

## 📥 What You Need to Download

4 files total, ~547 MB:

| # | Source | Size | Type | Download |
|---|--------|------|------|----------|
| 1 | **IFRS Taxonomy 2024** | 500 MB | ZIP (auto) | ✅ Script below |
| 2 | **Mexico SAT** | 15 MB | PDF (manual) | 👉 Visit SAT website |
| 3 | **Colombia DIAN** | 20 MB | PDF (manual) | 👉 Visit DIAN website |
| 4 | **Panama DGI** | 12 MB | PDF (manual) | 👉 Visit DGI website |

---

## ⚡ Step 1: Download IFRS (Automatic)

Run this command in terminal (will take ~5-10 minutes):

```bash
cd /Users/eva/PROJECTOS/GitHub/accounting-esperanto/bibliography/primary_sources/ifrs

curl -L -o ifrs-taxonomy-2024.zip \
  "https://www.ifrs.org/content/dam/ifrs/standards/taxonomy/ifrs-taxonomy_2024-01-31.zip"

# Wait for download to complete...
```

**While that downloads**, do the manual downloads below.

---

## 👉 Step 2: Download Mexico SAT (Manual)

1. Open browser → https://www.sat.gob.mx
2. Navigate: **Fichas Temáticas** → **Contabilidad Electrónica** → **Catálogo de Cuentas**
3. Download **latest PDF** (2024 version)
4. Save to: `/Users/eva/PROJECTOS/GitHub/accounting-esperanto/bibliography/primary_sources/mx_sat/`
5. Name it: `catalogo_cuentas_2024.pdf`

**Alternative sources:**
- IMCP (Mexican Accounting Institute): https://www.imcp.org.mx
- SAT Portal: https://fichas.saic.sat.gob.mx

---

## 👉 Step 3: Download Colombia DIAN (Manual)

1. Open browser → https://www.dian.gov.co
2. Navigate: **Normativas** → **Contabilidad** → **Plan Única de Cuentas**
3. Download **latest PDF** (2024 version)
4. Save to: `/Users/eva/PROJECTOS/GitHub/accounting-esperanto/bibliography/primary_sources/co_puc/`
5. Name it: `puc_2024.pdf`

**Note:** May need to email DIAN for direct link

---

## 👉 Step 4: Download Panama DGI (Manual)

1. Open browser → https://www.dgi.gob.pa
2. Navigate: **Normativas** → **Contabilidad** → **Plan de Cuentas**
3. Download **latest PDF** (2024 version)
4. Save to: `/Users/eva/PROJECTOS/GitHub/accounting-esperanto/bibliography/primary_sources/pa_dgi_smv/`
5. Name it: `plan_cuentas_2024.pdf`

---

## ✅ Step 5: Verify Everything

Once all files are downloaded:

```bash
cd /Users/eva/PROJECTOS/GitHub/accounting-esperanto

# Run verification script
python scripts/research/verify_bibliography.py

# Expected output:
# ✅ IFRS (ifrs-taxonomy-2024.zip) - 500 MB
#    ✓ Hash verified: [hash]
# ✅ MEXICO SAT (catalogo_cuentas_2024.pdf) - 15 MB
#    ✓ Hash verified: [hash]
# ✅ COLOMBIA DIAN (puc_2024.pdf) - 20 MB
#    ✓ Hash verified: [hash]
# ✅ PANAMA DGI (plan_cuentas_2024.pdf) - 12 MB
#    ✓ Hash verified: [hash]
#
# Summary: 4 ✅ | 0 ❌ | 0 ⚠️
```

---

## 📦 Step 6: Extract IFRS (Auto)

After IFRS download is complete:

```bash
cd bibliography/primary_sources/ifrs

# Extract ZIP
unzip -q ifrs-taxonomy-2024.zip

# Verify extraction
ls -la ifrs-taxonomy-2024/ifrs/full/ | head -10
```

---

## 🔐 Step 7: Commit to Git

```bash
cd /Users/eva/PROJECTOS/GitHub/accounting-esperanto

git add bibliography/primary_sources/
git commit -m "bibliography: Add all primary sources"
```

---

## 🎯 Success Checklist

- [ ] IFRS Taxonomy 2024 downloaded (500 MB)
- [ ] Mexico SAT PDF downloaded (15 MB)
- [ ] Colombia DIAN PDF downloaded (20 MB)
- [ ] Panama DGI PDF downloaded (12 MB)
- [ ] All verification hashes match
- [ ] IFRS extracted to 500+ files
- [ ] All files committed to git
- [ ] `verify_bibliography.py` shows 4 ✅

---

## 📚 Next Phase (Feb 3)

Once all sources are verified:
- Extract account lists from each source
- Create comparative analysis
- Map to Kontablo Level 3

See [RESEARCH_EXECUTION_PLAN.md](../research/RESEARCH_EXECUTION_PLAN.md) for full timeline.

---

**Estimated Time:** 20-30 minutes of actual work (+ 10 min download time)  
**Deadline:** January 31, 2026  
**Start Now:** Step 1 ↑
