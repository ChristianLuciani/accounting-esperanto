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

**Principal Investigator:** Christian Luciani  
**Institution:** Kontablo Research Initiative  
**Contact:** cluciani@gmail.com
