# 📚 Research Phase Execution Plan

**Phase:** 0 Research  
**Timeline:** January 28 - February 12, 2026  
**Status:** Starting Bibliography Gathering  
**Owner:** EVA  

---

## 🎯 Phase 0 Research Goals

1. ✅ **Complete OpenSpec Specifications** (DONE - committed Jan 28)
2. 📥 **Gather All Bibliography Sources** (IN PROGRESS)
3. 📊 **Extract Account Structures** (Pending Feb 3)
4. 🗺️ **Create Country Mappings** (Pending Feb 6)
5. 📈 **Build Comparative Analysis** (Pending Feb 9)
6. ✍️ **Validate with Experts** (Pending Feb 12)

---

## 📦 Week 1: Bibliography Gathering (Jan 28 - Feb 1)

### Day 1 (Jan 28) - ✅ COMPLETE
- [x] Finalize and commit 6 OpenSpec specifications (Level 3, Countries, Aggregation, Versioning, i18n, AI Training)
- [x] Create RESEARCH_DATA_GATHERING.md with download instructions
- [x] Create verify_bibliography.py verification script
- [x] Set up directory structure for all 4 sources

### Day 2-3 (Jan 29-30) - 📥 IN PROGRESS
**Task:** Download IFRS Taxonomy + Mexico SAT

#### IFRS Taxonomy 2024
```bash
cd bibliography/primary_sources/ifrs

# 1. Download (large file, may take 10+ min)
curl -L -o ifrs-taxonomy-2024.zip \
  "https://www.ifrs.org/content/dam/ifrs/standards/taxonomy/ifrs-taxonomy_2024-01-31.zip"

# 2. Calculate hash
shasum -a 256 ifrs-taxonomy-2024.zip

# 3. Create metadata
python ../../../scripts/research/verify_bibliography.py \
  --create-metadata ifrs

# 4. Extract
unzip -q ifrs-taxonomy-2024.zip

# 5. Verify
ls -la ifrs-taxonomy-2024/ifrs/full/
```

**Expected Result:**
- File: `ifrs-taxonomy-2024.zip` (500 MB)
- Extracted: ~500 files in ifrs-taxonomy-2024/
- Key file: `ifrs-taxonomy-2024/ifrs/full/ifrs-full_2024-01-31.xsd`
- Metadata: `ifrs-taxonomy-2024.meta.yaml` with SHA-256

---

#### Mexico SAT Catálogo de Cuentas 2024
**MANUAL DOWNLOAD REQUIRED:**

1. Visit: https://www.sat.gob.mx
2. Navigate: Fichas Temáticas → Contabilidad Electrónica → Catálogo de Cuentas
3. Download latest PDF (2024 version)
4. Save as: `bibliography/primary_sources/mx_sat/catalogo_cuentas_2024.pdf`

Once downloaded:
```bash
cd bibliography/primary_sources/mx_sat

# Create metadata
python ../../../scripts/research/verify_bibliography.py \
  --create-metadata mx_sat

# Verify
python ../../../scripts/research/verify_bibliography.py --verify mx_sat
```

**Expected Result:**
- File: `catalogo_cuentas_2024.pdf` (~15 MB)
- Metadata: `catalogo_cuentas_2024.meta.yaml`
- Status: ✅ VERIFIED

---

### Day 4-5 (Jan 31 - Feb 1) - ⏳ PENDING
**Task:** Download Colombia PUC + Panama DGI/SMV

#### Colombia DIAN PUC 2024
**MANUAL DOWNLOAD REQUIRED:**

1. Visit: https://www.dian.gov.co
2. Navigate: Normativas → Contabilidad → Plan Única de Cuentas
3. Download latest version (2024)
4. Save as: `bibliography/primary_sources/co_puc/puc_2024.pdf`

Once downloaded:
```bash
cd bibliography/primary_sources/co_puc

python ../../../scripts/research/verify_bibliography.py \
  --create-metadata co_puc

python ../../../scripts/research/verify_bibliography.py --verify co_puc
```

---

#### Panama DGI Plan de Cuentas 2024
**MANUAL DOWNLOAD REQUIRED:**

1. Visit: https://www.dgi.gob.pa
2. Navigate: Normativas → Contabilidad → Plan de Cuentas
3. Download latest version (2024)
4. Save as: `bibliography/primary_sources/pa_dgi_smv/plan_cuentas_2024.pdf`

Once downloaded:
```bash
cd bibliography/primary_sources/pa_dgi_smv

python ../../../scripts/research/verify_bibliography.py \
  --create-metadata pa_dgi_smv

python ../../../scripts/research/verify_bibliography.py --verify pa_dgi_smv
```

---

### Bibliography Verification Checklist
Once all files are downloaded:

```bash
cd /Users/eva/PROJECTOS/GitHub/accounting-esperanto

# Verify all sources
python scripts/research/verify_bibliography.py

# Expected output:
# ✅ IFRS (ifrs-taxonomy-2024.zip) - 500 MB
#    ✓ Hash verified: ...
# ✅ MEXICO SAT (catalogo_cuentas_2024.pdf) - 15 MB
#    ✓ Hash verified: ...
# ✅ COLOMBIA DIAN (puc_2024.pdf) - 20 MB
#    ✓ Hash verified: ...
# ✅ PANAMA DGI (plan_cuentas_2024.pdf) - 12 MB
#    ✓ Hash verified: ...
# 
# Summary: 4 ✅ | 0 ❌ | 0 ⚠️

# Commit to git
git add -A bibliography/primary_sources/
git commit -m "bibliography: Add all primary sources with SHA-256 verification

- IFRS Taxonomy 2024 (500 MB)
- Mexico SAT Catálogo de Cuentas 2024
- Colombia DIAN PUC 2024
- Panama DGI Plan de Cuentas 2024

All files verified with SHA-256 hashing and metadata tracking."
```

---

## 📊 Week 2: Account Extraction (Feb 3 - Feb 7)

Once all sources are downloaded and verified:

### Day 6-7 (Feb 3-4): Extract IFRS Structure

```bash
# Create extraction workspace
mkdir -p research/standards/international
mkdir -p research/analysis/extractions

# Extract IFRS with XML parsing
python << 'PYTHON'
import xml.etree.ElementTree as ET
from pathlib import Path
import csv

# Parse IFRS taxonomy
ifrs_xsd = Path("bibliography/primary_sources/ifrs/ifrs-taxonomy-2024/ifrs/full/ifrs-full_2024-01-31.xsd")
tree = ET.parse(ifrs_xsd)
root = tree.getroot()

# Extract concepts (GL accounts)
accounts = []

# Parse namespace
ns = {
    'xs': 'http://www.w3.org/2001/XMLSchema',
    'xsd': 'http://www.w3.org/2001/XMLSchema'
}

# Find all elements (simplified approach)
# In production: use sophisticated XML parsing for XBRL

# Save as CSV
with open('research/standards/international/ifrs_accounts.csv', 'w', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['xbrl_tag', 'label_en', 'type', 'balance_type', 'statement'])
    # Write extracted accounts

print("✅ IFRS extraction complete")
PYTHON
```

**Output Files:**
- `research/standards/international/ifrs_accounts.csv`
- `research/standards/international/EXTRACTED_DATA.md`

---

### Day 8-9 (Feb 5-6): Extract Mexico SAT + Colombia PUC

```bash
# Extract Mexico SAT using Antigravity
python scripts/research/antigravity_extract.py \
    bibliography/primary_sources/mx_sat/catalogo_cuentas_2024.pdf \
    --output research/standards/mx/

# Extract Colombia DIAN PUC
python scripts/research/antigravity_extract.py \
    bibliography/primary_sources/co_puc/puc_2024.pdf \
    --output research/standards/co/

# Extract Panama DGI
python scripts/research/antigravity_extract.py \
    bibliography/primary_sources/pa_dgi_smv/plan_cuentas_2024.pdf \
    --output research/standards/pa/
```

**Output Files per Country:**
- `research/standards/{mx,co,pa}/accounts.csv`
- `research/standards/{mx,co,pa}/EXTRACTED_DATA.md`

---

### Day 10 (Feb 7): Create Comparative Matrix

```bash
# Load all extracted accounts and create comparison
python << 'PYTHON'
import pandas as pd
from pathlib import Path

# Load all data
ifrs = pd.read_csv('research/standards/international/ifrs_accounts.csv')
mexico = pd.read_csv('research/standards/mx/accounts.csv')
colombia = pd.read_csv('research/standards/co/accounts.csv')
panama = pd.read_csv('research/standards/pa/accounts.csv')

# Create comparative analysis
# - Common accounts (exist in all jurisdictions)
# - Jurisdiction-specific accounts
# - Mapping complexity

# Save analysis
with open('research/analysis/comparative_matrix.md', 'w') as f:
    f.write("""
# Comparative Analysis Matrix

## Common Core Accounts (All Jurisdictions)
[Analysis results]

## Jurisdiction-Specific Accounts
[Analysis results]

## Mapping Complexity by Country
[Scoring and analysis]
""")

print("✅ Comparative analysis complete")
PYTHON
```

---

## 🗺️ Week 3: Kontablo Mapping (Feb 8 - Feb 12)

### Day 11-12 (Feb 8-9): Map Countries to Level 3

Using the [expand-level3-accounts specification](../../openspec/changes/expand-level3-accounts/PROPOSAL.md):

```bash
# Map Mexico SAT → Level 3
python << 'PYTHON'
import pandas as pd

# Load Level 3 spec
level3 = pd.read_csv('core/schemas/level3_accounts.csv')

# Load Mexico extracted accounts
mexico = pd.read_csv('research/standards/mx/accounts.csv')

# Create mapping (manual review + AI assistance)
# Output: mapping CSV with local_code → kontablo_uuid

# Save mapping
mapping.to_csv('research/mappings/mx_sat_to_kontablo.csv', index=False)
PYTHON

# Repeat for Colombia and Panama
```

**Output Files:**
- `research/mappings/mx_sat_to_kontablo.csv`
- `research/mappings/co_puc_to_kontablo.csv`
- `research/mappings/pa_dgi_smv_to_kontablo.csv`

---

### Day 13-14 (Feb 10-12): Validation + Expert Review

```bash
# Validate mappings
python << 'PYTHON'
# Check:
# - No duplicate mappings
# - All local accounts mapped
# - No orphaned Kontablo accounts
# - Aggregation rules make sense

# Generate validation report
PYTHON

# Expert validation (by CFO/CPA)
echo "📧 Sending for expert review..."
mail -s "Mapping validation" cpa@kontablo.mx
```

---

## 📋 Resource Tracking

### Required Sources
| Source | Status | Size | File | Verified |
|--------|--------|------|------|----------|
| IFRS Taxonomy 2024 | ⏳ In Progress | 500 MB | `ifrs-taxonomy-2024.zip` | Pending |
| Mexico SAT | ⏳ Manual Download | 15 MB | `catalogo_cuentas_2024.pdf` | Pending |
| Colombia DIAN | ⏳ Manual Download | 20 MB | `puc_2024.pdf` | Pending |
| Panama DGI | ⏳ Manual Download | 12 MB | `plan_cuentas_2024.pdf` | Pending |

### Verification Command
```bash
python scripts/research/verify_bibliography.py
```

---

## 🚀 Getting Started RIGHT NOW

```bash
cd /Users/eva/PROJECTOS/GitHub/accounting-esperanto

# 1. Start IFRS download (large, run in background)
cd bibliography/primary_sources/ifrs
curl -L -o ifrs-taxonomy-2024.zip \
  "https://www.ifrs.org/content/dam/ifrs/standards/taxonomy/ifrs-taxonomy_2024-01-31.zip" &

# 2. Create directories for other sources
mkdir -p ../mx_sat ../co_puc ../pa_dgi_smv

# 3. Update todo list
cd /Users/eva/PROJECTOS/GitHub/accounting-esperanto
echo "📥 Bibliography gathering initiated"

# 4. Check progress
python scripts/research/verify_bibliography.py

# 5. Once IFRS downloads, create metadata
# (Check back when complete)
```

---

## 📌 Success Criteria

### By Feb 1 (End of Week 1)
- [ ] IFRS Taxonomy 2024 downloaded and verified
- [ ] Mexico SAT PDF obtained and verified
- [ ] Colombia PUC PDF obtained and verified
- [ ] Panama DGI PDF obtained and verified
- [ ] All metadata YAML files created with SHA-256 hashes
- [ ] All sources committed to git

### By Feb 7 (End of Week 2)
- [ ] IFRS accounts extracted as CSV (~100 accounts)
- [ ] Mexico SAT accounts extracted (~200 accounts)
- [ ] Colombia PUC accounts extracted (~180 accounts)
- [ ] Panama DGI accounts extracted (~150 accounts)
- [ ] Comparative matrix created showing overlaps/differences
- [ ] All extraction code documented

### By Feb 12 (End of Week 3)
- [ ] Mexico → Level 3 mappings complete (95%+ coverage)
- [ ] Colombia → Level 3 mappings complete (95%+ coverage)
- [ ] Panama → Level 3 mappings complete (95%+ coverage)
- [ ] Aggregation rules defined (Phase 0 simple SUM rules)
- [ ] Validation report generated
- [ ] Expert review completed

---

**Status:** Ready to begin bibliography gathering  
**Next Step:** Follow the download instructions above  
**Timeline:** Complete by February 12, 2026
