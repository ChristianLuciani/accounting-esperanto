#!/bin/bash

cd accounting-esperanto  # o renombrar a "kontablo"

# Crear estructura de investigación académica
mkdir -p bibliography/{primary_sources,secondary_sources,standards,regulations}
mkdir -p research/{comparative_analysis,field_studies,validation}
mkdir -p docs/papers/{drafts,published}

# -----------------
# BIBLIOGRAFÍA: Sistema de Referencias
# -----------------

cat << 'EOF' > bibliography/README.md
# Kontablo Bibliography

## Citation Standard
All references follow **APA 7th Edition** format.

## Source Classification

### Primary Sources (`/primary_sources`)
Official regulatory documents:
- IFRS Foundation standards (PDF + metadata)
- Local GAAP official publications
- Government tax codes
- XBRL taxonomy files

### Secondary Sources (`/secondary_sources`)
Academic papers, books, industry reports:
- Peer-reviewed journals
- CPA association publications
- Big 4 accounting firm whitepapers

### Standards (`/standards`)
Technical specifications:
- XBRL specification documents
- ISO 20022 documentation
- OpenAPI/JSON Schema specs

### Regulations (`/regulations`)
Country-specific legal requirements:
- Tax codes
- Mandatory reporting formats
- E-invoicing specifications

## Metadata Format

Each source must have a companion `.meta.yaml` file:
````yaml
source_id: "ifrs_2023_full"
type: "primary_standard"
title: "IFRS Standards 2023 (Full Set)"
author: "IFRS Foundation"
publication_date: "2023-01-01"
url: "https://www.ifrs.org/issued-standards/"
access_date: "2025-01-27"
license: "Proprietary - Reference permitted"
file_hash_sha256: "abc123..."
relevance: "Core foundation for ontology"
citation: |
  IFRS Foundation. (2023). IFRS Standards 2023. 
  https://www.ifrs.org/issued-standards/
````
EOF

cat << 'EOF' > bibliography/primary_sources/.gitkeep
# Primary Sources

Store official documents here:
- IFRS_2023_consolidated.pdf
- XBRL_taxonomy_2024.zip
- Mexico_SAT_catalog_2024.pdf
- etc.

Each file MUST have a corresponding .meta.yaml
EOF

# -----------------
# METODOLOGÍA DE INVESTIGACIÓN
# -----------------

cat << 'EOF' > research/RESEARCH_METHODOLOGY.md
# Research Methodology: Kontablo Ontology Development

**Version:** 1.0  
**Status:** Active  
**Last Updated:** 2025-01-27

## 1. Research Objectives

### Primary Objective
Develop a universally valid accounting ontology that:
1. Maps to IFRS/XBRL with 95%+ coverage
2. Supports 15+ national GAAPs with documented mappings
3. Enables AI-based classification with >85% accuracy
4. Passes peer review in accounting/information systems journals

### Research Questions
1. **RQ1:** What is the minimal set of accounts that covers 80% of transactions across industries?
2. **RQ2:** How do local GAAPs diverge from IFRS, and what aggregation rules resolve these?
3. **RQ3:** Can a graph-based ontology outperform tree-based structures in multi-dimensional reporting?
4. **RQ4:** What metadata is necessary for AI agents to classify transactions autonomously?

## 2. Research Design

### 2.1 Methodology Type
**Mixed Methods:**
- **Quantitative:** Comparative analysis of account structures (frequencies, mappings)
- **Qualitative:** Expert interviews, case studies

### 2.2 Data Collection

#### Phase A: Standards Inventory (Weeks 1-4)
**Objective:** Systematic collection of all relevant standards.

**Sources:**
1. **International Standards**
   - IFRS Foundation (primary)
   - US GAAP (FASB)
   - XBRL International taxonomy

2. **Regional Standards** (Latin America priority)
   - Mexico: SAT Código Agrupador
   - Colombia: PUC (Plan Único de Cuentas)
   - Panama: DGI/SMV guidelines
   - Peru: PCGE
   - Argentina: Plan General Contable
   - Brazil: Plano de Contas (SPED)
   - Ecuador: Superintendencia de Compañías
   - Venezuela: Federation of CPAs guidelines
   - Chile: FECU (Financial statement standard)

3. **Industry Extensions**
   - Financial services (Basel III, COREP)
   - Healthcare (HIPAA accounting)
   - Agriculture (IAS 41 biological assets)
   - Technology (SaaS revenue recognition)

**Data Collection Protocol:**
````
For each standard:
1. Download official PDF/XML
2. Create .meta.yaml with citation
3. Calculate SHA-256 hash
4. Extract account list to CSV
5. Document in research/standards/[country_code]/
````

#### Phase B: Comparative Analysis (Weeks 5-8)
**Objective:** Identify commonalities and divergences.

**Method:** Cross-tabulation matrix

| Account Concept | IFRS Code | US GAAP | MX SAT | CO PUC | PA Common | Mapping Type |
|-----------------|-----------|---------|--------|--------|-----------|--------------|
| Cash & Equivalents | ifrs-full:Cash... | ASC 305 | 101-103 | 1105 | 1101-1102 | N:1 aggregation |

**Tools:**
- Excel/Google Sheets for initial analysis
- Python (pandas) for statistical analysis
- Jupyter notebooks for reproducibility

#### Phase C: Expert Validation (Weeks 9-10)
**Objective:** Validate findings with practitioners.

**Sample:**
- 10+ CPAs from different countries
- 3+ Big 4 auditors
- 2+ ERP implementation consultants
- 1+ XBRL expert

**Method:**
- Semi-structured interviews (30-45 min)
- Survey on proposed ontology (Likert scale)
- Case study: "Map your company's COA to Kontablo"

**Documentation:**
- Transcripts (anonymized)
- Coded responses (thematic analysis)
- Stored in `research/validation/expert_interviews/`

### 2.3 Data Analysis

#### Quantitative Analysis
1. **Coverage Analysis:**
   - % of standard accounts mapped to Kontablo
   - % of transactions classifiable automatically

2. **Mapping Complexity:**
   - Distribution of mapping types (1:1, N:1, 1:N)
   - Confidence scores per mapping

3. **Statistical Validation:**
   - Inter-rater reliability (Cohen's kappa) for AI classifications
   - Precision/Recall of AI classifier

#### Qualitative Analysis
1. **Thematic Coding:**
   - Expert feedback on edge cases
   - Cultural accounting practices

2. **Case Study Analysis:**
   - Real company migrations to Kontablo
   - Documented in `research/field_studies/`

## 3. Quality Assurance

### 3.1 Traceability
Every claim in the paper must cite:
- Source document (with SHA-256 hash)
- Analysis script (Jupyter notebook)
- Expert validation (interview ID)

### 3.2 Reproducibility
All analysis code in `research/analysis/`:
````python
# Example: coverage_analysis.ipynb
# Input: bibliography/primary_sources/ifrs_2023.pdf
# Output: research/analysis/results/ifrs_coverage.csv
# Hash: abc123...
````

### 3.3 Version Control
- Git commits for every change
- Tagged releases (v0.1-research-findings)
- Zenodo DOI for dataset snapshots

## 4. Ethical Considerations

### 4.1 Data Privacy
- No real company financial data published
- Case studies anonymized
- Expert interviews require consent

### 4.2 Conflicts of Interest
- Disclosed in paper
- No funding from ERP vendors (to maintain neutrality)

## 5. Timeline

| Week | Activity | Deliverable |
|------|----------|-------------|
| 1-4 | Standards collection | Bibliography complete |
| 5-8 | Comparative analysis | Mapping matrix |
| 9-10 | Expert validation | Interview transcripts |
| 11-12 | Ontology refinement | Core v0.1 |
| 13-14 | AI classifier training | Benchmark results |
| 15-16 | White paper writing | Draft for review |
| 17-18 | Peer review iteration | Final version |
| 19-20 | Publication submission | Submitted to journal |

## 6. Target Journals

### Tier 1 (Ideal)
- **Journal of Information Systems** (AIS)
- **MIS Quarterly** (if AI angle strong)
- **Accounting Horizons** (AICPA)

### Tier 2 (Backup)
- **International Journal of Accounting Information Systems**
- **Journal of Emerging Technologies in Accounting**

### Preprint
- SSRN (Social Science Research Network)
- arXiv (cs.AI or cs.DB)

## 7. Success Criteria

- [ ] 15+ national standards documented
- [ ] 95%+ IFRS coverage
- [ ] 10+ expert validations
- [ ] 85%+ AI classification accuracy
- [ ] Accepted in peer-reviewed journal
- [ ] 3+ real-world implementations

---

**Principal Investigator:** [Your Name]  
**Institution:** Kontablo Research Initiative  
**Contact:** [Email]
EOF

# -----------------
# HERRAMIENTAS DE INVESTIGACIÓN RECURSIVA
# -----------------

cat << 'EOF' > research/tools/recursive_research.md
# Recursive AI Research Tools

## Problem
We need to systematically research 15+ accounting standards with:
- Source verification (no hallucinations)
- Citation tracking
- Automated comparative analysis

## Proposed Solutions

### Option 1: Perplexity AI Pro (RECOMMENDED for Phase A)
**Why:**
- ✅ Cites sources automatically
- ✅ Access to academic databases
- ✅ Can process PDFs
- ✅ API available for automation

**Workflow:**
````
1. Upload official standard PDF to Perplexity
2. Query: "Extract all account codes from this document in CSV format"
3. Query: "What is the hierarchical structure?"
4. Download citations → Add to bibliography/
````

**Cost:** ~$20/month (Pro plan)

### Option 2: Elicit.org (For Literature Review)
**Why:**
- ✅ Specifically for academic research
- ✅ Extracts data from papers
- ✅ Builds evidence tables

**Use case:**
- Find existing papers on "accounting ontologies"
- Extract methodologies from similar research

**Cost:** Free for basic, $10/month Pro

### Option 3: Custom RAG Pipeline (For Later)
**Why:**
- ✅ Complete control
- ✅ Reproducible
- ✅ Can cite exact paragraphs

**Stack:**
````python
# Tools:
- LangChain (orchestration)
- ChromaDB (vector storage)
- Claude API (reasoning)
- PyMuPDF (PDF parsing)

# Workflow:
1. Ingest PDFs → Extract text + metadata
2. Chunk documents → Embed with citations
3. Query: "What accounts are mandatory in Mexico SAT?"
4. Response includes: Answer + Source PDF + Page number
````

**Cost:** Development time + API costs (~$50/month)

### Option 4: Notebook LM (Google - NEW)
**Why:**
- ✅ Upload multiple sources
- ✅ Automatically synthesizes
- ✅ Cites which source each claim comes from

**Status:** Free (beta), but limited control

---

## RECOMMENDED APPROACH (Hybrid)

### Phase A (Weeks 1-4): Manual + Perplexity
1. Download official PDFs manually (ensures authenticity)
2. Use Perplexity to extract structured data
3. Verify with manual spot-checks
4. Store in `bibliography/primary_sources/`

### Phase B (Weeks 5-8): Elicit + Excel
1. Use Elicit for literature review
2. Excel/Python for comparative analysis
3. Jupyter notebooks for reproducibility

### Phase C (Weeks 9+): Custom RAG (Optional)
Only if we need to query across all sources simultaneously.

---

## Quality Checklist

For every source:
- [ ] Original PDF downloaded
- [ ] SHA-256 hash recorded
- [ ] .meta.yaml created
- [ ] Citation in APA format
- [ ] Extraction verified by human
- [ ] Data stored in version control

EOF

# -----------------
# TEMPLATE: Extracción de Datos de Estándares
# -----------------

cat << 'EOF' > research/tools/standard_extraction_template.md
# Standard Extraction Protocol

## For Each Country/Standard

### Step 1: Metadata Collection
````yaml
source_id: "mx_sat_2024"
type: "government_regulation"
country: "MX"
authority: "SAT"
title: "Código Agrupador del SAT 2024"
url: "http://omawww.sat.gob.mx/..."
download_date: "2025-01-27"
file_path: "bibliography/primary_sources/mx_sat_2024.pdf"
file_hash: "sha256:abc123..."
````

### Step 2: Structure Analysis
Document:
- Number of hierarchical levels
- Coding format (regex pattern)
- Total number of accounts
- Mandatory vs. optional accounts

### Step 3: Account Extraction
Extract to CSV:
````csv
local_code,local_label_es,local_label_en,nature,category,notes
101,"Caja","Cash",debit,current_asset,"General cash account"
102,"Bancos","Banks",debit,current_asset,"Bank accounts"
...
````

### Step 4: Mapping Hypotheses
For each extracted account, propose Kontablo mapping:
````yaml
- local_code: "101"
  local_label: "Caja"
  proposed_kontablo_uuid: "cash-uuid-here"
  proposed_kontablo_code: "1.1.01"
  mapping_type: "direct" # or "aggregate", "split"
  confidence: "high" # high, medium, low
  notes: "Direct equivalent to Cash and Cash Equivalents"
````

### Step 5: Validation Notes
Document edge cases:
- Accounts that don't map cleanly
- Cultural/legal differences
- Special tax treatment

---

## Automation Script (Perplexity-Assisted)
````python
# research/tools/extract_with_ai.py

import anthropic
import hashlib
from pathlib import Path

def extract_accounts_from_pdf(pdf_path: Path, country_code: str):
    """
    Uses Claude to extract account structure from PDF.
    """
    client = anthropic.Anthropic(api_key="your-key")
    
    # Read PDF (simplified - use PyMuPDF in production)
    with open(pdf_path, 'rb') as f:
        pdf_hash = hashlib.sha256(f.read()).hexdigest()
    
    prompt = f"""
    You are an accounting researcher analyzing the official chart of accounts 
    for {country_code}.
    
    Extract the following from the attached PDF:
    1. Hierarchical structure (how many levels?)
    2. Coding format (pattern)
    3. All accounts in CSV format: code, label, nature
    
    Cite the page number for each extracted account.
    
    Output format:
    ## Structure
    [Your analysis]
    
    ## Accounts CSV
```csv
    code,label,nature,page
    ...
```
    """
    
    # Call Claude with PDF
    response = client.messages.create(
        model="claude-3-5-sonnet-20241022",
        messages=[{
            "role": "user",
            "content": prompt
        }]
    )
    
    # Save response with citation
    output_file = f"research/standards/{country_code}/extracted_accounts.md"
    with open(output_file, 'w') as f:
        f.write(f"# Extracted from {pdf_path}\n")
        f.write(f"File hash: {pdf_hash}\n\n")
        f.write(response.content)
    
    print(f"✅ Extracted to {output_file}")

# Usage
extract_accounts_from_pdf(
    Path("bibliography/primary_sources/mx_sat_2024.pdf"),
    "mx"
)
````
EOF

# -----------------
# JUPYTER NOTEBOOK TEMPLATE
# -----------------

cat << 'EOF' > research/analysis/.gitkeep
# Analysis Notebooks

All quantitative analysis must be:
1. Reproducible (environment.yml included)
2. Documented (markdown cells)
3. Version controlled

Example notebooks:
- coverage_analysis.ipynb
- mapping_complexity.ipynb
- ai_benchmark_results.ipynb
EOF

cat << 'EOF' > research/analysis/environment.yml
name: kontablo-research
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - pandas
  - numpy
  - matplotlib
  - seaborn
  - jupyter
  - openpyxl
  - pyyaml
  - pip
  - pip:
    - anthropic
    - langchain
    - jsonschema
EOF

# -----------------
# GIT COMMIT
# -----------------

git add .
git commit -m "research: Add academic methodology framework

- Bibliography structure with APA citations
- Research methodology document
- Extraction protocol for standards
- Tools evaluation (Perplexity, Elicit, RAG)
- Jupyter environment for reproducibility

Ready for systematic data collection Phase A."

echo ""
echo "✅ Research methodology structure created!"
echo ""
echo "📁 Key additions:"
echo "   /bibliography      - Source documents + metadata"
echo "   /research/tools    - Extraction protocols"
echo "   /research/analysis - Jupyter notebooks"
echo ""
echo "📚 Next steps:"
echo "   1. Review research/RESEARCH_METHODOLOGY.md"
echo "   2. Set up Perplexity Pro account"
echo "   3. Download first official standard (IFRS PDF)"
echo "   4. Run extraction protocol"
echo ""