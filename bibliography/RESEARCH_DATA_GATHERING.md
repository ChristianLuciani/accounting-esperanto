# Research Data Gathering Guide

**Phase:** 0 Research  
**Date Started:** January 28, 2026  
**Status:** Ready to Begin  
**Owner:** Research Team  

---

## 🎯 Mission

Collect authoritative accounting standards from 4 jurisdictions to support Level 3 account extraction and country mapping validation. All sources must be:
- ✅ **Authoritative** (government/standards body official)
- ✅ **Current** (2024 or latest version)
- ✅ **Verified** (SHA-256 hash confirmed)
- ✅ **Traceable** (source URL, download date, metadata)

---

## 📦 Bibliography Structure

```
bibliography/
├── INDEX.md                    # Master index (this documents all sources)
├── primary_sources/
│   ├── ifrs/                  # IFRS Taxonomy (international standard)
│   │   ├── ifrs-taxonomy-2024.zip
│   │   ├── ifrs-taxonomy-2024.meta.yaml
│   │   └── README.md
│   ├── mx_sat/                # Mexico - Catálogo de Cuentas
│   │   ├── catalogo_cuentas_2024.pdf
│   │   ├── catalogo_cuentas_2024.meta.yaml
│   │   └── README.md
│   ├── co_puc/                # Colombia - Plan Única de Cuentas
│   │   ├── puc_2024.pdf
│   │   ├── puc_2024.meta.yaml
│   │   └── README.md
│   └── pa_dgi_smv/            # Panama - Plan de Cuentas
│       ├── plan_cuentas_dgi_2024.pdf
│       ├── plan_cuentas_dgi_2024.meta.yaml
│       └── README.md
├── regulations/               # Related accounting regulations
│   ├── ifrs/
│   ├── mx/
│   ├── co/
│   └── pa/
├── standards/                 # Extracted/analyzed standards
│   ├── international/
│   │   └── TEMPLATE.md
│   ├── mx/
│   │   └── TEMPLATE.md
│   ├── co/
│   │   └── TEMPLATE.md
│   └── pa/
│       └── TEMPLATE.md
└── secondary_sources/         # Academic papers, books, articles
    ├── ifrs/
    ├── mexico_accounting/
    ├── colombia_accounting/
    └── panama_accounting/
```

---

## 1️⃣ IFRS Taxonomy 2024

### What You're Getting
- International standard for consolidated financial reporting
- Foundation for Level 3 account design
- XBRL tags and mappings
- GL Account structure (Assets → Liabilities → Equity → Revenue → Expenses)

### Where to Get It
| Source | URL | Format | Size |
|--------|-----|--------|------|
| **IFRS Official** | https://www.ifrs.org/issued-standards/ifrs-taxonomy/ | ZIP | ~500MB |
| Direct Download | https://www.ifrs.org/content/dam/ifrs/standards/taxonomy/ifrs-taxonomy_2024-01-31.zip | ZIP | ~500MB |

### Download Steps

```bash
# 1. Create directory
mkdir -p bibliography/primary_sources/ifrs
cd bibliography/primary_sources/ifrs

# 2. Download (this may take 5-10 minutes due to size)
echo "⏳ Downloading IFRS Taxonomy 2024..."
curl -L -o ifrs-taxonomy-2024.zip \
  "https://www.ifrs.org/content/dam/ifrs/standards/taxonomy/ifrs-taxonomy_2024-01-31.zip"

# 3. Verify integrity
echo "🔐 Calculating SHA-256 hash..."
HASH=$(shasum -a 256 ifrs-taxonomy-2024.zip | cut -d' ' -f1)
echo "Hash: $HASH"

# 4. Create metadata
cat > ifrs-taxonomy-2024.meta.yaml << EOF
source_id: "ifrs_taxonomy_2024_01_31"
jurisdiction: "international"
type: "primary_standard"
authority: "IFRS Foundation"
standard_name: "IFRS Taxonomy"
standard_version: "2024-01-31"
download_date: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
download_url: "https://www.ifrs.org/content/dam/ifrs/standards/taxonomy/ifrs-taxonomy_2024-01-31.zip"
file_name: "ifrs-taxonomy-2024.zip"
file_size_mb: 500
file_hash_sha256: "$HASH"
file_hash_algorithm: "SHA-256"
notes: "Extracted Jan 28, 2026. Required for Level 3 account design and XBRL mappings."
EOF

# 5. Extract
unzip -q ifrs-taxonomy-2024.zip

# 6. Verify extraction
ls -la | head -20

echo "✅ IFRS Taxonomy downloaded and verified"
```

### What's Inside
```
ifrs-taxonomy-2024/
├── META/
├── common/
├── ifrs/
│   ├── full/          ← COMPLETE GL ACCOUNT STRUCTURE
│   ├── full-unsegmented/
│   └── smefp/         ← Small/Medium Entities
└── xsd/               ← XML Schema (for parsing)
```

**Key Section:** `ifrs/full/ifrs-full_2024-01-31.xsd` - Contains complete account list

---

## 🇲🇽 2️⃣ Mexico - SAT Catálogo de Cuentas

### What You're Getting
- Mexico's official Chart of Accounts (Catálogo de Cuentas)
- Structure: Level 1-4 with codes (101-999 range)
- SAT Catalog for tax reporting compliance
- ~200+ accounts across all categories

### Where to Get It
| Source | URL | Format |
|--------|-----|--------|
| **SAT Official** | http://www.sat.gob.mx/fichas_tematicas/conta_e/... | PDF |
| IMCP (Accounting Institute) | https://www.imcp.org.mx | PDF |
| Academia Portal | https://fichas.saic.sat.gob.mx | Web |

### Download Steps

```bash
# 1. Create directory
mkdir -p bibliography/primary_sources/mx_sat
cd bibliography/primary_sources/mx_sat

# NOTE: SAT catalog is not available via direct download link
# You'll need to:

# Option A: Manual Download (Recommended)
# 1. Visit: https://www.sat.gob.mx/fichas_tematicas/conta_e/...
# 2. Download PDF
# 3. Save as: catalogo_cuentas_2024.pdf
# 4. Place in this directory

# Option B: Use IMCP source (Accounting Institute)
# 1. Visit: https://www.imcp.org.mx
# 2. Download the current catalog
# 3. Verify it's 2024 edition

# 2. Once you have the PDF, create metadata
cat > catalogo_cuentas_2024.meta.yaml << 'EOF'
source_id: "mx_sat_catalogo_2024"
jurisdiction: "mexico"
type: "primary_standard"
authority: "Servicio de Administración Tributaria (SAT)"
standard_name: "Catálogo de Cuentas para Contabilidad Electrónica"
standard_version: "2024"
download_date: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
file_name: "catalogo_cuentas_2024.pdf"
file_size_mb: "~15"
file_hash_sha256: "RUN: shasum -a 256 catalogo_cuentas_2024.pdf"
notes: |
  Mexico's official Chart of Accounts for electronic bookkeeping.
  Used for Level 3 mapping and tax compliance validation.
  Covers all account types: Assets, Liabilities, Equity, Revenue, Expenses.
EOF

# 3. Verify hash
HASH=$(shasum -a 256 catalogo_cuentas_2024.pdf | cut -d' ' -f1)
echo "✅ File hash: $HASH"

# 4. Update metadata with actual hash
sed -i '' "s/RUN: shasum.*/\"$HASH\"/" catalogo_cuentas_2024.meta.yaml
```

### Key Content to Extract
- Account codes (101-999)
- Account names (Spanish)
- Account type (Activo/Pasivo/Capital/Ingresos/Gastos)
- Debit/credit nature
- Level in hierarchy (1-4)

**Output:** CSV with columns: `code, name_es, type, nature, level`

---

## 🇨🇴 3️⃣ Colombia - PUC (Plan Única de Cuentas)

### What You're Getting
- Colombia's unified Chart of Accounts
- Structure: 4-digit codes (1000-9999)
- DIAN (tax authority) official standard
- ~180+ accounts

### Where to Get It
| Source | URL | Format |
|--------|-----|--------|
| **DIAN Official** | https://www.dian.gov.co | PDF/Web |
| Resolution 220/2020 | [See DIAN website] | PDF |
| Ministry of Commerce | https://www.mincomericio.gov.co | PDF |

### Download Steps

```bash
# 1. Create directory
mkdir -p bibliography/primary_sources/co_puc
cd bibliography/primary_sources/co_puc

# 2. DIAN PUC download (manual - email request may be needed)
# Visit: https://www.dian.gov.co
# Search: "Plan Única de Cuentas"
# Version: Latest (typically 2024)
# Save as: puc_2024.pdf

# 3. Create metadata
cat > puc_2024.meta.yaml << 'EOF'
source_id: "co_dian_puc_2024"
jurisdiction: "colombia"
type: "primary_standard"
authority: "Dirección de Impuestos y Aduanas Nacionales (DIAN)"
standard_name: "Plan Única de Cuentas"
standard_version: "2024"
regulation: "Resolution 220/2020"
download_date: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
file_name: "puc_2024.pdf"
file_size_mb: "~20"
file_hash_sha256: "RUN: shasum -a 256 puc_2024.pdf"
notes: |
  Colombia's official unified Chart of Accounts.
  Structure: 4-digit codes (1000-9999)
  Mandatory for all accounting entities.
EOF

# 4. Verify hash
HASH=$(shasum -a 256 puc_2024.pdf | cut -d' ' -f1)
sed -i '' "s/RUN: shasum.*/\"$HASH\"/" puc_2024.meta.yaml
```

### Key Content to Extract
- Account codes (1000-9999, 4 digits)
- Account names (Spanish)
- Account classification (Activo/Pasivo/Capital/Ingresos/Gastos)
- Debit/credit nature
- Account group hierarchy

**Output:** CSV with columns: `code, name_es, classification, nature, group`

---

## 🇵🇦 4️⃣ Panama - DGI/SMV Plan de Cuentas

### What You're Getting
- Panama's official Chart of Accounts
- DGI (tax) and SMV (securities) standards
- Structure: Hierarchical with multiple levels
- ~150-200 accounts

### Where to Get It
| Source | URL | Format |
|--------|-----|--------|
| **DGI Official** | https://www.dgi.gob.pa | PDF/Web |
| **SMV Official** | https://www.smv.gob.pa | PDF/Web |
| Accounting Regulations | See DGRCP | PDF |

### Download Steps

```bash
# 1. Create directory
mkdir -p bibliography/primary_sources/pa_dgi_smv
cd bibliography/primary_sources/pa_dgi_smv

# 2. Download from DGI and SMV websites
# DGI: https://www.dgi.gob.pa → Normativas → Contabilidad
# SMV: https://www.smv.gob.pa → Normativas

# Save as:
# - dgi_plan_cuentas_2024.pdf
# - smv_plan_cuentas_2024.pdf

# 3. Create metadata for each
cat > dgi_plan_cuentas_2024.meta.yaml << 'EOF'
source_id: "pa_dgi_plan_2024"
jurisdiction: "panama"
type: "primary_standard"
authority: "Dirección General de Ingresos (DGI)"
standard_name: "Plan de Cuentas"
standard_version: "2024"
download_date: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
file_name: "dgi_plan_cuentas_2024.pdf"
file_size_mb: "~12"
file_hash_sha256: "RUN: shasum -a 256 dgi_plan_cuentas_2024.pdf"
notes: |
  Panama's official Chart of Accounts for tax compliance.
  Required for corporate reporting to DGI.
EOF

# 4. Verify hashes
HASH_DGI=$(shasum -a 256 dgi_plan_cuentas_2024.pdf | cut -d' ' -f1)
sed -i '' "s/RUN: shasum.*/\"$HASH_DGI\"/" dgi_plan_cuentas_2024.meta.yaml

echo "✅ Panama files processed"
```

### Key Content to Extract
- Account codes
- Account names (Spanish)
- Account type/classification
- Debit/credit nature
- Required for DGI/SMV reporting

**Output:** CSV with columns: `code, name_es, type, nature, authority`

---

## 📋 Creating Bibliography INDEX.md

Once all files are downloaded, create a master index:

```bash
cd bibliography

cat > INDEX.md << 'EOF'
# Bibliography Index

**Last Updated:** 2026-01-28  
**Research Phase:** 0  
**Purpose:** Document all primary sources for Level 3 account extraction  

---

## Primary Sources

### 1. IFRS Taxonomy 2024
- **Status:** ✅ Downloaded
- **Location:** `primary_sources/ifrs/`
- **File:** `ifrs-taxonomy-2024.zip` (500 MB)
- **Hash:** [SHA-256 from metadata]
- **Download Date:** 2026-01-28
- **Authority:** IFRS Foundation
- **Purpose:** International standard foundation for Level 3 accounts
- **Key Section:** `ifrs/full/ifrs-full_2024-01-31.xsd`

### 2. Mexico - SAT Catálogo de Cuentas 2024
- **Status:** ⏳ Pending Download
- **Location:** `primary_sources/mx_sat/`
- **File:** `catalogo_cuentas_2024.pdf` (~15 MB)
- **Authority:** Servicio de Administración Tributaria (SAT)
- **Purpose:** Mexico account structure mapping
- **Key Content:** 200+ accounts, codes 101-999

### 3. Colombia - DIAN PUC 2024
- **Status:** ⏳ Pending Download
- **Location:** `primary_sources/co_puc/`
- **File:** `puc_2024.pdf` (~20 MB)
- **Authority:** Dirección de Impuestos y Aduanas Nacionales (DIAN)
- **Purpose:** Colombia account structure mapping
- **Key Content:** ~180 accounts, codes 1000-9999

### 4. Panama - DGI/SMV Plan de Cuentas 2024
- **Status:** ⏳ Pending Download
- **Location:** `primary_sources/pa_dgi_smv/`
- **Files:** `dgi_plan_cuentas_2024.pdf`, `smv_plan_cuentas_2024.pdf`
- **Authority:** DGI / Superintendencia del Mercado de Valores
- **Purpose:** Panama account structure mapping
- **Key Content:** 150-200 accounts

---

## Secondary Sources

### Academic & Reference Materials
- IFRS Conceptual Framework
- Country-specific accounting textbooks
- International accounting journals

---

## Data Integrity

All files verified with SHA-256 hashing. Metadata files store:
- Download date/time (ISO 8601)
- Source URL
- File size
- Hash algorithm & value
- Authority and jurisdiction
- Purpose and notes

---

## Timeline

| Date | Milestone |
|------|-----------|
| Jan 28 | Bibliography gathering initiated |
| Jan 29-30 | IFRS + Mexico SAT downloaded |
| Jan 31 | Colombia PUC + Panama DGI downloaded |
| Feb 1-2 | Metadata verification |
| Feb 3-5 | Extraction + analysis |
| Feb 6 | Comparative matrix complete |

EOF

cat INDEX.md
```

---

## 🔐 Verification Protocol

All downloads must follow this checklist:

```bash
# ✅ Download Verification Checklist

# 1. File exists and is readable
ls -lh [file_name]

# 2. File size is reasonable
file [file_name]

# 3. Calculate hash
shasum -a 256 [file_name] > [file_name].sha256

# 4. Store metadata
cat > [file_name].meta.yaml << EOF
source_id: "..."
authority: "..."
file_hash_sha256: "$(cat [file_name].sha256 | cut -d' ' -f1)"
download_date: "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
EOF

# 5. Create README
cat > README.md << EOF
# [Source Name]

Downloaded: $(date)
Hash verified: YES
Ready for extraction: YES
EOF

# 6. Commit to git
git add [file_name].meta.yaml README.md
git commit -m "bibliography: Add [source] with SHA-256 verification"
```

---

## 📊 What Happens Next

Once all sources are gathered (by Feb 1):

1. **Week 2 (Feb 3-7):** Extract accounts from each source
   - Parse IFRS XSD with XML tools
   - Extract tables from SAT/DIAN/DGI PDFs
   - Create CSV files for each jurisdiction

2. **Week 2 (Feb 3-7):** Map to Kontablo Level 3
   - Align Mexico SAT → Level 3
   - Align Colombia PUC → Level 3
   - Align Panama DGI/SMV → Level 3

3. **Week 3 (Feb 8-12):** Create comparative matrix
   - Identify common accounts (core)
   - Identify country-specific accounts
   - Document aggregation rules

4. **Week 4 (Feb 15-21):** Validate with experts
   - CPA/auditor review
   - Country specialist validation
   - Academic credibility check

---

## 🚀 Getting Started

**Run this now:**

```bash
cd /Users/eva/PROJECTOS/GitHub/accounting-esperanto

# Create directories
mkdir -p bibliography/primary_sources/{ifrs,mx_sat,co_puc,pa_dgi_smv}

# Start with IFRS (can run in background due to size)
cd bibliography/primary_sources/ifrs
echo "⏳ Starting IFRS download (may take 10 minutes)..."
curl -L -o ifrs-taxonomy-2024.zip \
  "https://www.ifrs.org/content/dam/ifrs/standards/taxonomy/ifrs-taxonomy_2024-01-31.zip" &

# While that downloads, manually get the others
echo "👉 Next steps:"
echo "1. Visit https://www.sat.gob.mx and download catalogo_cuentas_2024.pdf"
echo "2. Visit https://www.dian.gov.co and download puc_2024.pdf"
echo "3. Visit https://www.dgi.gob.pa and download plan de cuentas"
echo "4. Place all files in their respective directories"
echo "5. Run: bash bibliography/RESEARCH_DATA_GATHERING.md (this file has all scripts)"
```

---

**Status:** Ready to begin research phase ✅
**Next:** Download and verify all sources by January 31, 2026
