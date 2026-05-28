# Architecture Decision Record: ADR-008
# Title: Tree-to-Graph Compatibility Protocol for ERP Integration
# Date: 2026-03-13
# Status: PROPOSED

# Context
# =======
# All major ERPs (ERPNext, Zoho Books, QuickBooks, SAP B1, Odoo) store accounts as TREES:
# - One parent per account
# - Linear hierarchy (e.g., Assets > Current Assets > Cash)
# - Cannot express multi-dimensional membership
#
# Kontablo is a GRAPH:
# - Accounts can belong to multiple dimensions simultaneously
# - Example: "Cash" is simultaneously: [Balance Sheet], [Current Asset], [Liquidity Level 1]
# - This multi-dimensional property is Kontablo's key competitive advantage

# Decision
# ========
# Accept controlled information loss when importing FROM tree-based ERPs into Kontablo.
# Apply a three-tier resolution strategy.

resolution_strategy:
  tier_1_exact:
    description: "Direct account_type → UUID mapping (high confidence ≥ 0.95)"
    applies_when: "account_type unambiguously maps to a single Kontablo UUID"
    examples:
      - erpnext_type: "Cash" → uuid: "00000000-0000-4000-8000-000000000101"
      - erpnext_type: "Receivable" → uuid: "00000000-0000-4000-8000-000000000104"
      - zoho_type: "accounts_payable" → uuid: "00000000-0000-4000-8000-000000000201"

  tier_2_disambiguation:
    description: "account_type + account_name pattern matching (medium confidence 0.70-0.94)"
    applies_when: "account_type is ambiguous (e.g., 'Other Current Asset')"
    mechanism: "Regex/keyword rules in ERP bridge scripts"
    examples:
      - zoho_type: "other_current_liability" + name_contains: "VAT" → uuid: "...000000000203"
      - zoho_type: "other_current_liability" + name_contains: "Deferred Revenue" → uuid: "...000000000207"

  tier_3_semantic_ai:
    description: "Semantic Matcher AI (variable confidence 0.50-0.85)"
    applies_when: "Tiers 1 and 2 fail to produce a match"
    mechanism: "SemanticMatcherAgent with full account context (name + type + code + description)"
    flag: "Result flagged for human review if confidence < 0.80"

information_loss_protocol:
  acceptable_losses:
    - "Multi-dimensional graph edges are collapsed to primary dimension"
    - "ERP account codes are preserved as metadata; not as primary identifier"
    - "Group accounts (is_group=True in ERPNext) are excluded from mapping"
  unacceptable_losses:
    - "Incorrect UUID assignment (prefer 'UNMAPPED' over wrong UUID)"
    - "Loss of debit/credit nature information"
    - "Loss of local code (must be stored as mapping provenance)"

export_direction:
  kontablo_to_erp:
    description: "When EXPORTING from Kontablo to an ERP, the graph must be LINEARIZED."
    algorithm: "Choose the primary dimension edge (Balance Sheet classification)"
    risk: "LOW - Primary dimension is always defined in Kontablo core"
  erp_to_kontablo:
    description: "When IMPORTING from ERP to Kontablo (the MicroSaaS use case)"
    algorithm: "Apply three-tier resolution above"
    risk: "MEDIUM - Requires AI fallback for complex cases"

implementation_artifacts:
  - "research/erp_compatibility/erpnext_account_types.yaml"
  - "research/erp_compatibility/zoho_books_types.yaml"
  - "scripts/erp_bridges/erpnext_kontablo_bridge.py (TODO)"
  - "scripts/erp_bridges/zoho_kontablo_bridge.py (TODO)"

consequences:
  positive:
    - "Kontablo can accept data from any major ERP without requiring ERP customization"
    - "The three-tier system maximizes automation while preserving human oversight"
    - "Confidence scores allow progressive automation as AI improves"
  negative:
    - "Some accounts will map to 'generic' UUIDs temporarily"
    - "Tier 3 (AI) requires LLM API calls (cost + latency)"
    - "Human review queue will exist for Tier 3 mappings"
