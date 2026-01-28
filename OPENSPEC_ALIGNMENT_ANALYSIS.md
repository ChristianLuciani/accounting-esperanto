# 📋 OpenSpec Alignment Analysis for Kontablo

**Date:** January 27, 2026  
**Reviewed By:** AI Assistant  
**Status:** ✅ Analysis Complete

---

## 🎯 Executive Summary

**Current OpenSpec State:** Basic setup only  
**Project Goals Coverage:** **30% - Needs expansion**  
**Recommendation:** **Complete Phase 0 specifications before Week 2**

---

## 📊 Project Goals vs. Spec Status

### Core Vision: "Universal Accounting Ontology"

| Goal | Status | OpenSpec Coverage | Gap |
|------|--------|-------------------|-----|
| **Graph Model (not tree)** | Defined | ❌ Not specified | Need spec for multi-dimensional classification |
| **UUID as truth source** | Defined | ⚠️ Partial | UUID strategy exists in nodes.json but not formally documented |
| **Multi-jurisdictional mapping** | Defined | ❌ Not specified | Need spec for country-specific mappings |
| **AI-ready format** | Defined | ⚠️ Partial | JSON structure exists, no AI training spec |
| **Blockchain anchoring** | Defined | ❌ Not specified | No immutability/versioning spec |
| **Logic-based aggregation** | Defined | ❌ Not specified | No aggregation rules spec |

---

## 🔍 Detailed Gap Analysis

### What EXISTS in OpenSpec Today

1. **Directory Structure** ✅
   - `/openspec/README.md` - Workflow documented
   - `/openspec/templates/research-task.md` - Template exists
   - `/spec/human/master.yaml` - Human-readable spec started
   - `/spec/machine/nodes.json` - Machine-readable schema started

2. **Account Hierarchy** ✅
   - Level 1: Assets, Liabilities, Equity, Revenue, Expenses
   - Level 2: Current/Non-Current, sub-categories
   - Level 3: Partial (only Cash example)

### What's MISSING

1. **Account Level 3-4 Specification** ❌
   - Currently: Only 1-2 account levels with ~20 entries
   - Needed: 80-100 complete Level 3 accounts (per Week 1 extraction showing 14 IFRS types)
   - Impact: Cannot map countries without this

2. **Country Mapping Specification** ❌
   - Currently: No spec for MX SAT, CO PUC, PA DGI/SMV
   - Needed: Formal spec for how countries' codes map to Kontablo UUIDs
   - Example missing:
     ```yaml
     # Should exist but doesn't
     mappings:
       mx_sat:
         code: "101"
         kontablo_uuid: "550e8400-..."
         aggregation_rule: "sum"
     ```

3. **Aggregation Logic Specification** ❌
   - Currently: No formal spec for combining accounts
   - Needed: Rules engine definition for consolidation
   - Example from PRINCIPLES.md but not in spec:
     ```python
     def aggregate_cash_accounts(local_codes):
         return {"target_uuid": "...", "method": "sum"}
     ```

4. **AI Training Dataset Specification** ❌
   - Currently: No spec for AI classifier training
   - Needed: Document structure for transaction classification dataset
   - Related: `/ai-training/datasets/` exists but empty

5. **Validation Rules Specification** ❌
   - Currently: No formal spec for integrity checks
   - Needed: Rules for valid account combinations, debit/credit balancing, etc.

6. **Versioning & Immutability Specification** ❌
   - Currently: Version "0.1.0" exists but no change protocol
   - Needed: Formal blockchain-anchoring spec per PRINCIPLES.md
   - Include: UUID deprecation rules, version bump procedures

7. **Multi-Language (i18n) Specification** ❌
   - Currently: Only English labels
   - Needed: Spec for Spanish, Portuguese, French translations
   - Related: `/localizations/` folder exists but empty

---

## 🗂️ Current Spec Completeness

```
Spec Coverage Analysis:
=====================

Level 1 Accounts:    ████████░░  80% (5 main categories)
Level 2 Accounts:    ████████░░  70% (sub-categories partial)
Level 3 Accounts:    ██░░░░░░░░  20% (only Cash example)
Country Mappings:    ░░░░░░░░░░   0% (completely missing)
Aggregation Rules:   ░░░░░░░░░░   0% (completely missing)
AI Training Spec:    ░░░░░░░░░░   0% (completely missing)
Validation Rules:    ░░░░░░░░░░   0% (completely missing)
Versioning/Immutab:  ░░░░░░░░░░   0% (completely missing)
i18n Support:        ░░░░░░░░░░   0% (completely missing)

OVERALL COMPLETENESS: ~25%
```

---

## 🚀 Recommendations for Phase 0 Completion

### CRITICAL (Must complete before Week 2)

**1. Expand Level 3 Accounts → Use OpenSpec**
```bash
opsx:new expand-level3-accounts

# This should generate:
# - proposal.md: Why Level 3 is needed for consolidation
# - specs/level3_structure.yaml: Full account list (80+)
# - design.md: How accounts map to XBRL
# - tasks.md: AI extraction tasks
```

**2. Document Country Mapping Strategy → Use OpenSpec**
```bash
opsx:new country-mappings-specification

# This should generate:
# - proposal.md: Why multi-jurisdictional mapping is key
# - specs/mx_mapping.yaml: Mexico SAT codes → Kontablo UUIDs
# - specs/co_mapping.yaml: Colombia PUC → Kontablo UUIDs
# - specs/pa_mapping.yaml: Panama DGI/SMV → Kontablo UUIDs
# - design.md: Aggregation rules for each country
```

**3. Define Aggregation Logic → Use OpenSpec**
```bash
opsx:new aggregation-rules-specification

# This should generate:
# - proposal.md: Why logic-based (not 1:1) aggregation
# - specs/aggregation_rules.yaml: Rules engine structure
# - design.md: Python implementation of rules
# - examples.md: Real consolidation examples
```

### HIGH PRIORITY (Before end of Phase 0)

**4. Versioning & Immutability Spec**
```bash
opsx:new versioning-immutability-spec

# Formalize blockchain anchoring per PRINCIPLES.md
# - UUID never deleted (only deprecated)
# - Version hashes are blockchain-anchored
# - Breaking changes require MAJOR bump
```

**5. AI Training Dataset Spec**
```bash
opsx:new ai-training-dataset-spec

# For fine-tuning classifiers in Phase 2
# - Transaction classification format
# - Training/test set split
# - Label schemes
```

**6. Validation Rules Spec**
```bash
opsx:new validation-rules-specification

# For data quality checks
# - Debit/credit balance validation
# - Statement balancing rules
# - Country-specific validations
```

---

## ❓ Questions for You

**Before I complete these specs, I need clarification on:**

### Q1: Scope of Level 3 Accounts
- **Current:** 14 IFRS primary accounts extracted
- **Question:** How many Level 3 accounts do you want in Phase 0?
  - Option A: 80-100 (comprehensive, supports most transactions)
  - Option B: 40-50 (MVP, core accounts only)
  - Option C: Based on your IFRS extraction + countries analyzed

### Q2: Country Priority for Mappings
- **Current:** Plan includes Mexico (SAT), Colombia (PUC), Panama (DGI/SMV)
- **Question:** In what order should I create the specs?
  - Most important first? (You mentioned Panama is your specialty)
  - Complexity order? (Simplest → hardest)
  - Your preferred order?

### Q3: Aggregation Rule Complexity
- **Current:** Principles mention "no 1:1 assumptions"
- **Question:** How complex should aggregation rules be?
  - Simple: Just sum/average/weighted-sum
  - Moderate: Include conditional rules (e.g., "if revenue > X, then...")
  - Advanced: Include blockchain state checks for immutability?

### Q4: AI Training Dataset Scope
- **Current:** `/ai-training/datasets/` is empty
- **Question:** For Phase 0, do you want:
  - Just the spec (ready for Phase 2)?
  - Sample dataset (100-500 example transactions)?
  - Full dataset (1000+ real transactions)?

### Q5: Multi-Language Support
- **Current:** Only English labels (`label_en`)
- **Question:** Should Phase 0 specs include:
  - Spanish translation of all accounts?
  - Portuguese support (for Brazil/Portugal)?
  - All major accounting-software languages?

### Q6: Blockchain Immutability
- **Current:** Mentioned in PRINCIPLES but not formalized
- **Question:** For Phase 0, should the spec include:
  - Just the concept (blockchain-ready but not implemented)?
  - Integration specs for Ethereum/Polygon?
  - Smart contract examples?

---

## 📋 Proposed Action Plan for Spec Completion

### Phase 0 Extension: OpenSpec Formalization (This Week)

**Day 1-2: Critical Specs**
```bash
opsx:new expand-level3-accounts
opsx:new country-mappings-specification
opsx:ff  # Generate all specs
```

**Day 3: Aggregation + Versioning**
```bash
opsx:new aggregation-rules-specification
opsx:new versioning-immutability-spec
opsx:ff
```

**Day 4-5: Review + Refinement**
```bash
# Review all specs
# Answer the 6 questions above
# Apply changes with opsx:apply
```

**Then: Week 2 Research (Multi-Country Analysis)**
- Specs provide the "target" structure
- Extractions fill in the data
- No guessing or ad-hoc format changes

---

## 🎯 Success Criteria

OpenSpec will be complete when:

- ✅ Level 3 accounts defined (80+ accounts with UUIDs)
- ✅ Country mappings specified (MX, CO, PA with aggregation rules)
- ✅ Aggregation logic formalized (rules engine spec)
- ✅ Versioning protocol established (immutability rules)
- ✅ AI training format specified (for Phase 2)
- ✅ Validation rules documented (data quality checks)
- ✅ All specs have `opsx:apply` applied
- ✅ Specs can serve as "contract" between research and implementation

---

## 🔗 Related Documents

- [PRINCIPLES.md](../docs/PRINCIPLES.md) - Ontological foundation
- [ACTION_PLAN.md](../docs/ACTION_PLAN.md) - Execution timeline
- [spec/human/master.yaml](../spec/human/master.yaml) - Current account structure
- [spec/machine/nodes.json](../spec/machine/nodes.json) - Machine schema

---

**Next Step:** Please answer the 6 questions above, and I'll complete the Phase 0 specs using OpenSpec. This ensures research and implementation are aligned.

