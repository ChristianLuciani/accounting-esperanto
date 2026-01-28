# Kontablo Tooling Stack (100% Free)

## Core Tools

### 1. Secrets Management
**Tool:** Infisical (Free tier)  
**Purpose:** Store API keys, tokens  
**Setup:** `./scripts/setup_secrets.sh`

### 2. Spec-Driven Development
**Tool:** OpenSpec (Fission AI)  
**Purpose:** Structured feature planning  
**Setup:** `./scripts/setup_openspec.sh`

### 3. AI Research Assistant
**Tool:** Google AI Studio (Antigravity)  
**Model:** Gemini 2.0 Flash  
**Cost:** FREE (15 RPM, 1M tokens/day)  
**Setup:** `./scripts/setup_antigravity.sh`

### 4. Version Control
**Tool:** Git + GitHub  
**Purpose:** Code, docs, issues  
**Cost:** FREE

### 5. IDE
**Tool:** VS Code (free) + Continue extension  
**Alt:** Zed editor (free, fast)  
**Purpose:** Code editing with AI assist

## AI Assistants

### Primary: Google AI Studio (Antigravity)
- ✅ FREE tier (generous limits)
- ✅ Multimodal (PDFs, images)
- ✅ 1M context window
- ✅ API access
- 🔗 https://aistudio.google.com/

**Use for:**
- PDF extraction
- Standards analysis
- Literature search

### Secondary: Claude Code (if available)
- ✅ Deep reasoning
- ✅ Long context
- ⚠️ Requires Pro subscription (but you may have access)

**Use for:**
- Ontology design decisions
- Paper writing
- Complex analysis

### Tertiary: GitHub Copilot (free for OSS)
- ✅ Free for public repos
- ✅ Code completion
- 🔗 https://github.com/features/copilot

## Research Tools (Free)

### 1. Google Scholar
**Purpose:** Find academic papers  
**Cost:** FREE  
**URL:** https://scholar.google.com/

### 2. Semantic Scholar
**Purpose:** AI-powered paper search  
**Cost:** FREE  
**URL:** https://www.semanticscholar.org/

### 3. arXiv
**Purpose:** Preprints (CS, econ)  
**Cost:** FREE  
**URL:** https://arxiv.org/

### 4. SSRN
**Purpose:** Business/accounting papers  
**Cost:** FREE (reading)  
**URL:** https://www.ssrn.com/

## Data Processing

### 1. Python + Pandas
**Purpose:** CSV/Excel analysis  
**Cost:** FREE  
**Install:** `pip install pandas openpyxl`

### 2. Jupyter Notebooks
**Purpose:** Reproducible analysis  
**Cost:** FREE  
**Install:** `pip install jupyter`

### 3. DuckDB
**Purpose:** SQL on CSV files  
**Cost:** FREE  
**Install:** `pip install duckdb`

## Documentation

### 1. Markdown + Mermaid
**Purpose:** Docs with diagrams  
**Cost:** FREE  
**Render:** GitHub natively supports

### 2. Docusaurus (later)
**Purpose:** Documentation site  
**Cost:** FREE  
**Deploy:** GitHub Pages (free)

## Project Management

### 1. GitHub Issues
**Purpose:** Task tracking  
**Cost:** FREE

### 2. GitHub Projects
**Purpose:** Kanban board  
**Cost:** FREE

### 3. ADRs (this repo)
**Purpose:** Decision tracking  
**Cost:** FREE

## Limitations & Workarounds

### No Perplexity Pro?
**Workaround:** Google AI Studio + manual verification

### No Cursor paid?
**Workaround:** VS Code + Continue extension (free)

### No OpenAI API?
**Workaround:** Google AI Studio (Gemini)

### No compute budget?
**Workaround:** Google Colab (free GPU for notebooks)

## Budget: $0/month ✅

All tools are either:
- Completely free (GitHub, VS Code, Python)
- Free tier sufficient (Infisical, Google AI)
- Open source (Continue, DuckDB)

---

**Next:** Run setup scripts in order:
1. `./scripts/setup_secrets.sh`
2. `./scripts/setup_openspec.sh`
3. `./scripts/setup_antigravity.sh`
