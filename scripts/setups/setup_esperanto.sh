#!/bin/bash

# ============================================
# ACCOUNTING ESPERANTO v3.0
# Synthesis of AI-native + z.ai robustness
# ============================================

REPO_NAME="accounting-esperanto"

echo "🌍 Creating Accounting Esperanto - Production-Ready Structure"
echo ""

# Create directory structure
mkdir -p $REPO_NAME/{docs,research/{standards/{international,local,industry},analysis},spec/{human,machine},core/{translations,schemas},logic/{mapping_rules,validators},localizations,api/{rest,grpc},blockchain,ai-training/{datasets,prompts},tooling,tests/{schema_validation,mapping_accuracy},examples,.github/ISSUE_TEMPLATE}

# -----------------
# ROOT README
# -----------------

cat << 'EOF' > $REPO_NAME/README.md
# 🌍 Accounting Esperanto

> The protocol layer for AI-native, multi-jurisdictional accounting

[![Status](https://img.shields.io/badge/status-research-yellow)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()
[![AI-Ready](https://img.shields.io/badge/AI-ready-purple)]()

## 🎯 Vision

A universal accounting ontology that serves as the "Rosetta Stone" between:
- 🌐 International standards (IFRS, XBRL)
- 🏛️ Local regulations (SAT, PUC, PCGE, etc.)
- 🤖 AI agent economy
- ⛓️ Blockchain/DeFi protocols

## 🏗️ Design Principles

1. **Graph, not Tree** - Accounts exist in multiple dimensions simultaneously
2. **UUID as Truth** - Codes are visual; UUIDs are canonical
3. **Logic-Based Mapping** - No 1:1 assumptions; aggregation via scripts
4. **API-First** - Designed for machine consumption
5. **Immutable Versioning** - Blockchain-anchored version hashes

## 📊 Current Phase: Research (Phase 0)

We are **not building software yet**. We are:

- [x] Defining ontological principles
- [ ] Analyzing 15+ local standards
- [ ] Mapping XBRL taxonomy
- [ ] Documenting AI/blockchain requirements
- [ ] Validating with accounting professionals

## 🗂️ Repository Structure
```
/docs           - Principles, strategy, decisions
/research       - Comparative analysis, raw data
/spec           - THE standard (human + machine readable)
/core           - Implementation schemas
/logic          - Mapping rules, validators (Phase 2)
/api            - REST/gRPC specs (Phase 2)
/ai-training    - Datasets, prompts
/localizations  - Country-specific mappings
```

## 🤝 Contributing

This project needs:
- 👔 **Accountants** - Validate mappings
- 🔬 **Researchers** - Analyze standards
- 💻 **Developers** - Build tooling (later)
- 🤖 **AI Engineers** - Train classifiers

See [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 License

MIT License - See [LICENSE](LICENSE)

---

⚠️ **Alpha Stage** - Not production-ready
EOF

# -----------------
# CORE PRINCIPLES
# -----------------

cat << 'EOF' > $REPO_NAME/docs/PRINCIPLES.md
# Ontological Principles

## 1. The Graph Model (Not a Tree)

**Problem with trees:**
```
Assets
└── Depreciation  ❌ Wrong - also affects P&L
```

**Graph solution:**
```yaml
- uuid: "depr-001"
  code: "1.2.99"
  label_en: "Accumulated Depreciation"
  classifications:
    statement_type: ["balance_sheet", "income_statement"]
    affects_cashflow: true
  relations:
    parent_uuid: "fixed-assets-uuid"
    impacts: ["net_income", "asset_value"]
```

## 2. UUID as Source of Truth

- **Code** (`1.1.01`) - Display only, can change
- **UUID** (`550e8400-...`) - Immutable, never changes
- **label_en** - For humans
- **label_key** - For i18n systems

## 3. Multi-Dimensional Classification

Every account belongs to:
- Statement type (Balance/P&L/CashFlow)
- Liquidity (Current/Non-Current)
- Nature (Debit/Credit)
- Industry (optional filters)

## 4. Aggregation Logic

Local standards → Global standard requires **code**, not just mapping.

Example:
```python
# mx_sat: 101, 102, 103 → Esperanto: Cash
def aggregate_cash_accounts(local_codes):
    return {
        "target_uuid": "cash-uuid",
        "method": "sum",
        "preserves_nature": True
    }
```

## 5. Immutability & Versioning

- UUIDs never deleted (only deprecated)
- Standard versions are blockchain-anchored
- Breaking changes require MAJOR version bump

---
Version: 1.0  
Last Updated: 2025-01-27
EOF

# -----------------
# ENHANCED SCHEMA
# -----------------

cat << 'EOF' > $REPO_NAME/core/schemas/account.schema.json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "$id": "https://accounting-esperanto.org/schemas/account.json",
  "title": "Accounting Esperanto Account",
  "description": "Universal account definition with multi-dimensional classification",
  "type": "object",
  "required": ["uuid", "standard_code", "label_en", "nature", "classifications"],
  "properties": {
    "uuid": {
      "type": "string",
      "format": "uuid",
      "description": "Immutable global identifier (primary key)"
    },
    "standard_code": {
      "type": "string",
      "pattern": "^\\d\\.\\d\\.\\d{2}(\\.\\d{3})?$",
      "description": "Human-readable hierarchical code (display only)",
      "examples": ["1.1.01", "5.2.15.002"]
    },
    "label_en": {
      "type": "string",
      "minLength": 1,
      "description": "English canonical label"
    },
    "label_key": {
      "type": "string",
      "description": "i18n key for translation systems",
      "pattern": "^[a-z_]+$",
      "examples": ["cash_and_equivalents", "software_subscriptions"]
    },
    "synonyms": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Alternative names for AI semantic matching"
    },
    "nature": {
      "type": "string",
      "enum": ["debit", "credit"],
      "description": "Fundamental accounting nature (never changes)"
    },
    "classifications": {
      "type": "object",
      "required": ["statement_type", "liquidity"],
      "properties": {
        "statement_type": {
          "type": "array",
          "items": {
            "type": "string",
            "enum": ["balance_sheet", "income_statement", "cash_flow", "retained_earnings"]
          },
          "minItems": 1,
          "description": "Which financial statement(s) this account appears on"
        },
        "liquidity": {
          "type": "string",
          "enum": ["current", "non_current", "not_applicable"],
          "description": "For balance sheet accounts"
        },
        "functional_category": {
          "type": "string",
          "enum": ["operating", "investing", "financing", "not_applicable"],
          "description": "For cash flow classification"
        }
      }
    },
    "relations": {
      "type": "object",
      "description": "Graph relationships to other accounts",
      "properties": {
        "parent_uuid": {
          "type": "string",
          "format": "uuid",
          "description": "Primary parent for rollup"
        },
        "also_rolls_up_to": {
          "type": "array",
          "items": {"type": "string", "format": "uuid"},
          "description": "Additional rollup parents (for multi-dimensional reporting)"
        },
        "contra_account_of": {
          "type": "string",
          "format": "uuid",
          "description": "If this is a contra account (e.g., Accumulated Depreciation)"
        }
      }
    },
    "xbrl_mapping": {
      "type": "object",
      "properties": {
        "primary_tag": {
          "type": "string",
          "pattern": "^[a-z-]+:[A-Z][a-zA-Z]+$",
          "examples": ["ifrs-full:CashAndCashEquivalents"]
        },
        "dimensions": {
          "type": "array",
          "items": {
            "type": "object",
            "properties": {
              "dimension": {"type": "string"},
              "member": {"type": "string"}
            }
          },
          "description": "XBRL dimensional metadata (advanced)"
        }
      }
    },
    "metadata": {
      "type": "object",
      "properties": {
        "is_monetary": {
          "type": "boolean",
          "description": "Requires currency revaluation"
        },
        "requires_depreciation": {
          "type": "boolean"
        },
        "status": {
          "type": "string",
          "enum": ["active", "deprecated", "experimental"],
          "default": "active"
        },
        "deprecated_date": {
          "type": "string",
          "format": "date"
        },
        "effective_date": {
          "type": "string",
          "format": "date",
          "description": "When this account became valid"
        }
      }
    },
    "agent_hints": {
      "type": "object",
      "description": "Metadata for AI classification",
      "properties": {
        "vendor_patterns": {
          "type": "array",
          "items": {"type": "string"},
          "examples": [["aws.amazon.com", "cloud.google.com"]]
        },
        "amount_ranges": {
          "type": "object",
          "properties": {
            "typical_min": {"type": "number"},
            "typical_max": {"type": "number"}
          }
        },
        "frequency": {
          "type": "string",
          "enum": ["one-time", "monthly", "quarterly", "annual", "varies"]
        }
      }
    },
    "blockchain": {
      "type": "object",
      "properties": {
        "supports_smart_contracts": {"type": "boolean"},
        "evm_compatible": {"type": "boolean"}
      }
    }
  }
}
EOF

# -----------------
# EXAMPLE ACCOUNT (Flat Structure)
# -----------------

cat << 'EOF' > $REPO_NAME/spec/machine/nodes.json
[
  {
    "uuid": "00000000-0000-4000-8000-000000000001",
    "standard_code": "1",
    "label_en": "Assets",
    "label_key": "assets",
    "nature": "debit",
    "classifications": {
      "statement_type": ["balance_sheet"],
      "liquidity": "not_applicable"
    },
    "relations": {
      "parent_uuid": null
    },
    "xbrl_mapping": {
      "primary_tag": "ifrs-full:Assets"
    },
    "metadata": {
      "status": "active",
      "is_monetary": false
    }
  },
  {
    "uuid": "00000000-0000-4000-8000-000000000011",
    "standard_code": "1.1",
    "label_en": "Current Assets",
    "label_key": "current_assets",
    "nature": "debit",
    "classifications": {
      "statement_type": ["balance_sheet"],
      "liquidity": "current"
    },
    "relations": {
      "parent_uuid": "00000000-0000-4000-8000-000000000001"
    },
    "xbrl_mapping": {
      "primary_tag": "ifrs-full:CurrentAssets"
    },
    "metadata": {
      "status": "active"
    }
  },
  {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "standard_code": "1.1.01",
    "label_en": "Cash and Cash Equivalents",
    "label_key": "cash_and_equivalents",
    "synonyms": ["Cash", "Caja", "Efectivo", "Bancos"],
    "nature": "debit",
    "classifications": {
      "statement_type": ["balance_sheet", "cash_flow"],
      "liquidity": "current",
      "functional_category": "operating"
    },
    "relations": {
      "parent_uuid": "00000000-0000-4000-8000-000000000011"
    },
    "xbrl_mapping": {
      "primary_tag": "ifrs-full:CashAndCashEquivalents"
    },
    "metadata": {
      "is_monetary": true,
      "status": "active"
    },
    "agent_hints": {
      "vendor_patterns": ["bank*", "paypal.com", "stripe.com"],
      "frequency": "varies"
    }
  }
]
EOF

# -----------------
# HUMAN-READABLE SPEC (For Documentation)
# -----------------

cat << 'EOF' > $REPO_NAME/spec/human/master.yaml
# Accounting Esperanto - Human-Readable Specification
# This format is for DOCUMENTATION and REVIEW
# For machine processing, use /spec/machine/nodes.json

version: "0.1.0"
last_updated: "2025-01-27"

elements:
  - uuid: "00000000-0000-4000-8000-000000000001"
    code: "1"
    label: "Assets"
    nature: debit
    xbrl: "ifrs-full:Assets"
    
    groups:
      - uuid: "00000000-0000-4000-8000-000000000011"
        code: "1.1"
        label: "Current Assets"
        liquidity: current
        
        categories:
          - uuid: "550e8400-e29b-41d4-a716-446655440000"
            code: "1.1.01"
            label: "Cash and Cash Equivalents"
            synonyms: ["Cash", "Caja", "Efectivo"]
            appears_on: ["Balance Sheet", "Cash Flow Statement"]
            
          # More accounts here...

  # More elements...
EOF

# -----------------
# TRANSLATIONS
# -----------------

cat << 'EOF' > $REPO_NAME/core/translations/en.json
{
  "assets": "Assets",
  "current_assets": "Current Assets",
  "cash_and_equivalents": "Cash and Cash Equivalents",
  "accounts_receivable": "Accounts Receivable",
  "inventory": "Inventory"
}
EOF

cat << 'EOF' > $REPO_NAME/core/translations/es.json
{
  "assets": "Activos",
  "current_assets": "Activos Corrientes",
  "cash_and_equivalents": "Efectivo y Equivalentes",
  "accounts_receivable": "Cuentas por Cobrar",
  "inventory": "Inventarios"
}
EOF

# -----------------
# LOGIC (Placeholders for Phase 2)
# -----------------

cat << 'EOF' > $REPO_NAME/logic/README.md
# Mapping Logic

**Status:** To be implemented in Phase 2

This directory will contain:

## `/mapping_rules`
Python/JavaScript functions that define how local accounts aggregate to global accounts.

Example:
```python
def mx_sat_to_esperanto(local_code):
    # Multiple local codes → One global UUID
    cash_codes = ["101", "102", "103"]
    if local_code in cash_codes:
        return {
            "uuid": "550e8400-...",
            "aggregation": "sum",
            "confidence": 1.0
        }
```

## `/validators`
Functions that ensure data integrity:
- Nature validation (assets are debit)
- Parent-child consistency
- XBRL tag validity

---
These will be implemented once the spec stabilizes.
EOF

cat << 'EOF' > $REPO_NAME/logic/mapping_rules/example_aggregation.py
"""
Example: How multiple local accounts map to one global account

This is a PLACEHOLDER - To be implemented in Phase 2
"""

def aggregate_local_to_global(local_accounts: list[dict]) -> dict:
    """
    Aggregates multiple local accounts to a single Esperanto account.
    
    Args:
        local_accounts: List of {code, balance, currency}
    
    Returns:
        {uuid, total_balance, currency, source_codes}
    """
    # Example logic (not production-ready)
    cash_codes = ["101", "102", "103"]  # From MX SAT
    
    total = sum(
        acc["balance"] 
        for acc in local_accounts 
        if acc["code"] in cash_codes
    )
    
    return {
        "target_uuid": "550e8400-e29b-41d4-a716-446655440000",
        "total_balance": total,
        "source_codes": cash_codes,
        "confidence": 1.0,
        "method": "direct_sum"
    }

# Future: Machine learning-based classification
# Future: Fuzzy matching for unknown accounts
EOF

# -----------------
# LOCALIZATION EXAMPLE
# -----------------

mkdir -p $REPO_NAME/localizations/mx_sat

cat << 'EOF' > $REPO_NAME/localizations/mx_sat/README.md
# Mexico - SAT (Servicio de Administración Tributaria)

## Authority
- **Country:** Mexico
- **Regulator:** SAT
- **Standard:** Código Agrupador del SAT
- **Digital Format:** XML
- **Last Updated:** 2024

## Mapping Strategy

### Aggregation (Many local → One global)
```
SAT 101 (Caja) ────┐
SAT 102 (Bancos)───┼──→ Esperanto 1.1.01 (Cash)
SAT 103 (Inversiones)─┘
```

### Disaggregation (One global → Many local)
```
Esperanto 4.1.01 (Revenue) ──┬──→ SAT 401 (Ventas Nacionales)
                             └──→ SAT 402 (Ventas Exportación)
```

## Files
- `catalog.json` - Official SAT chart of accounts
- `mapping.yaml` - Esperanto mappings with aggregation rules
EOF

cat << 'EOF' > $REPO_NAME/localizations/mx_sat/mapping.yaml
# Mexico SAT → Accounting Esperanto Mappings

mappings:
  # Cash accounts (aggregation example)
  - local_codes: ["101", "102", "103"]
    esperanto_uuid: "550e8400-e29b-41d4-a716-446655440000"
    esperanto_code: "1.1.01"
    aggregation_rule: "sum"
    confidence: 1.0
    notes: "Multiple cash accounts aggregate to one global account"
    
  # Revenue disaggregation example
  - local_codes: ["401", "402", "403"]
    esperanto_uuid: "revenue-operating-uuid"
    esperanto_code: "4.1.01"
    aggregation_rule: "sum"
    confidence: 1.0
    disaggregation_dimension: "geography"  # National vs Export
    notes: "Revenue splits by geography in SAT"

validation_rules:
  - rule: "101 must be debit balance"
    enforcement: "error"
  - rule: "401 must be credit balance"
    enforcement: "error"
EOF

# -----------------
# TOOLING
# -----------------

cat << 'EOF' > $REPO_NAME/tooling/format_converter.py
#!/usr/bin/env python3
"""
Convert between human-readable (YAML) and machine-readable (JSON) formats.

Usage:
    python format_converter.py human_to_machine spec/human/master.yaml spec/machine/nodes.json
    python format_converter.py machine_to_human spec/machine/nodes.json spec/human/master.yaml
"""

import sys
import json
import yaml
from pathlib import Path
from typing import List, Dict

def human_to_machine(yaml_file: Path, json_file: Path):
    """Convert nested YAML to flat JSON."""
    with open(yaml_file) as f:
        data = yaml.safe_load(f)
    
    flat_accounts = []
    
    def flatten(items, parent_uuid=None):
        for item in items:
            account = {
                "uuid": item["uuid"],
                "standard_code": item["code"],
                "label_en": item["label"],
                "nature": item["nature"],
                "relations": {
                    "parent_uuid": parent_uuid
                }
            }
            flat_accounts.append(account)
            
            if "groups" in item:
                flatten(item["groups"], item["uuid"])
            if "categories" in item:
                flatten(item["categories"], item["uuid"])
    
    flatten(data.get("elements", []))
    
    with open(json_file, 'w') as f:
        json.dump(flat_accounts, f, indent=2)
    
    print(f"✅ Converted {yaml_file} → {json_file}")

def machine_to_human(json_file: Path, yaml_file: Path):
    """Convert flat JSON to nested YAML."""
    with open(json_file) as f:
        accounts = json.load(f)
    
    # Build hierarchy
    # (Simplified - production version would handle full nesting)
    roots = [a for a in accounts if a["relations"].get("parent_uuid") is None]
    
    output = {"elements": roots}
    
    with open(yaml_file, 'w') as f:
        yaml.dump(output, f, default_flow_style=False, allow_unicode=True)
    
    print(f"✅ Converted {json_file} → {yaml_file}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)
    
    mode = sys.argv[1]
    input_file = Path(sys.argv[2])
    output_file = Path(sys.argv[3])
    
    if mode == "human_to_machine":
        human_to_machine(input_file, output_file)
    elif mode == "machine_to_human":
        machine_to_human(input_file, output_file)
    else:
        print("Error: Mode must be 'human_to_machine' or 'machine_to_human'")
        sys.exit(1)
EOF

chmod +x $REPO_NAME/tooling/format_converter.py

# -----------------
# TESTS
# -----------------

cat << 'EOF' > $REPO_NAME/tests/schema_validation/test_accounts.py
"""
Schema validation tests

Run: pytest tests/
"""

import json
from pathlib import Path
from jsonschema import validate, ValidationError
import pytest

SCHEMA_PATH = Path("core/schemas/account.schema.json")
ACCOUNTS_PATH = Path("spec/machine/nodes.json")

def load_schema():
    with open(SCHEMA_PATH) as f:
        return json.load(f)

def load_accounts():
    with open(ACCOUNTS_PATH) as f:
        return json.load(f)

def test_schema_exists():
    """Ensure schema file exists"""
    assert SCHEMA_PATH.exists()

def test_accounts_valid():
    """All accounts must pass schema validation"""
    schema = load_schema()
    accounts = load_accounts()
    
    for account in accounts:
        try:
            validate(instance=account, schema=schema)
        except ValidationError as e:
            pytest.fail(f"Account {account.get('uuid')} failed validation: {e.message}")

def test_unique_uuids():
    """UUIDs must be unique"""
    accounts = load_accounts()
    uuids = [a["uuid"] for a in accounts]
    assert len(uuids) == len(set(uuids)), "Duplicate UUIDs found"

def test_nature_consistency():
    """Assets (code 1.*) must be debit, Liabilities (2.*) must be credit"""
    accounts = load_accounts()
    
    for account in accounts:
        code = account["standard_code"]
        nature = account["nature"]
        
        if code.startswith("1") or code.startswith("5"):
            assert nature == "debit", f"{code} should be debit"
        elif code.startswith("2") or code.startswith("3") or code.startswith("4"):
            assert nature == "credit", f"{code} should be credit"

def test_parent_exists():
    """If parent_uuid is specified, it must exist"""
    accounts = load_accounts()
    all_uuids = {a["uuid"] for a in accounts}
    
    for account in accounts:
        parent = account.get("relations", {}).get("parent_uuid")
        if parent:
            assert parent in all_uuids, f"Parent {parent} not found for {account['uuid']}"
EOF

# -----------------
# RESEARCH TEMPLATES
# -----------------

cat << 'EOF' > $REPO_NAME/research/standards/TEMPLATE.md
# [Standard Name]

## Metadata
- **Country/Region:**
- **Authority:**
- **Official URL:**
- **Last Updated:**
- **Digital Format:** (XML/JSON/PDF/Paper)
- **Mandatory:** Yes/No

## Structure

### Hierarchical Levels
1. Level 1: [e.g., Element - Asset/Liability]
2. Level 2: [e.g., Group - Current/Non-Current]
3. Level 3: [e.g., Category - Cash/Receivables]
4. ...

### Coding Convention
- **Format:** X.XX.XXX or XXX-XX or other
- **Separator:** `.` `-` `_`
- **Character Set:** Numeric / Alphanumeric / Mixed

## Sample Accounts

| Local Code | Local Label | Nature | Esperanto Equivalent | Mapping Type |
|------------|-------------|--------|---------------------|--------------|
| 101 | Cash | Debit | 1.1.01 | 1:1 |
| 102 | Bank | Debit | 1.1.01 | N:1 (aggregates) |

## Validation Rules

- [ ] Assets must have debit balance
- [ ] Revenue must have credit balance
- [ ] Custom rule 1
- [ ] Custom rule 2

## Unique Characteristics

What makes this standard different?

## Mapping Challenges

Potential difficulties:
- Aggregation issues
- Missing concepts
- Cultural differences

## References

- Official documentation
- Related regulations

---
**Analyzed by:** [Your Name]  
**Date:** [YYYY-MM-DD]  
**Confidence:** High/Medium/Low
EOF

# -----------------
# GOVERNANCE
# -----------------

cat << 'EOF' > $REPO_NAME/governance/CHARTER.md
# Project Charter

## Mission

Create an open, AI-ready, universal accounting ontology that enables:
1. Multi-jurisdictional consolidation
2. Automated classification by AI agents
3. Blockchain/DeFi integration
4. Seamless ERP migration

## Principles

### 1. Graph-Based, Not Tree-Based
Accounts exist in multiple dimensions (Balance/P&L/CashFlow) simultaneously.

### 2. UUID Immutability
UUIDs are permanent. Codes can change.

### 3. Logic-Based Mapping
No naive 1:1 assumptions. Aggregation requires code.

### 4. Open Governance
- Decisions documented publicly
- Community input required
- No single vendor control

## Decision-Making

### Roles
- **Maintainers:** Can merge PRs (earned)
- **Advisory Board:** Domain experts
- **Community:** Anyone can propose

### Process
1. Proposal (GitHub Issue)
2. Research & Discussion (minimum 14 days)
3. Peer Review
4. Vote (maintainers)
5. Implementation

## Conflicts of Interest

All maintainers must disclose:
- Employer
- Consulting relationships
- Financial interests

---
Version: 1.0  
Last Updated: 2025-01-27
EOF

# -----------------
# GIT
# -----------------

cat << 'EOF' > $REPO_NAME/.gitignore
# Python
__pycache__/
*.py[cod]
.pytest_cache/
.venv/
venv/

# IDEs
.vscode/
.idea/
*.swp

# OS
.DS_Store
Thumbs.db

# Large files
research/raw_data/*.pdf
research/raw_data/*.xlsx
*.zip

# Generated
coverage.html
dist/
build/
EOF

# -----------------
# FINAL SETUP
# -----------------

cd $REPO_NAME
git init
git add .
git commit -m "feat: Initialize Accounting Esperanto v3.0

Architecture synthesis combining:
- Graph-based account model (z.ai peer review)
- AI-native design (blockchain, agent economy)
- Robust mapping logic (aggregation/disaggregation)
- Multi-dimensional classification
- Immutable UUID system

Structure:
- /spec: Human (YAML) + Machine (JSON) formats
- /core: Enhanced schemas with XBRL support
- /logic: Mapping rules (Phase 2 ready)
- /localizations: Country-specific with aggregation
- /api: REST/gRPC specs (AI agent ready)

Status: Phase 0 (Research)
Next: Standards inventory and comparative analysis"

echo ""
echo "✅ Accounting Esperanto v3.0 created successfully!"
echo ""
echo "📁 Key Directories:"
echo "   /spec/human   - For documentation (nested YAML)"
echo "   /spec/machine - For code (flat JSON)"
echo "   /logic        - Mapping rules (Phase 2)"
echo "   /localizations - Country mappings"
echo ""
echo "🎯 Next Steps:"
echo "   1. Review docs/PRINCIPLES.md (graph model)"
echo "   2. Fill research/standards/TEMPLATE.md (PA, EC, VE)"
echo "   3. Run: pytest tests/ (validate structure)"
echo "   4. Convert formats: python tooling/format_converter.py"
echo ""
echo "🤖 AI-Ready Features:"
echo "   - agent_hints in schema"
echo "   - Blockchain metadata"
echo "   - Semantic synonyms for matching"
echo ""
