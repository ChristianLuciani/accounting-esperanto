# OpenSpec: Multi-Language (i18n) Specification

**Change ID:** multi-language-specification  
**Status:** Proposal  
**Date:** January 27, 2026  
**Phase:** Phase 0 (Foundation), Full Implementation Phase 1+

---

## 📋 Proposal: Support Spanish, Portuguese, French Translations

### Problem
- Phase 0 has English only (label_en)
- Cannot use in Latin America without Spanish/Portuguese
- Will need translations eventually

### Solution
- **Phase 0:** Create translation structure (not full translations)
- **Phase 1:** Add Spanish for Mexico, Colombia, Panama
- **Phase 2:** Add Portuguese for Brazil
- **Phase 3+:** Add French, other languages as needed

### Current Scope: Phase 0 (Structure Only)

---

## 🎯 Design: i18n Architecture

### Account Label Structure

```yaml
account:
  uuid: "550e8400-e29b-41d4-a716-446655440000"
  code: "1.1.01"
  
  # Phase 0: All languages defined
  labels:
    en: "Cash and Cash Equivalents"
    es: "Efectivo y Equivalentes de Efectivo"  # Spanish
    pt: "Caixa e Equivalentes de Caixa"        # Portuguese
    fr: "Trésorerie et Équivalents de Trésorerie"  # French (future)
  
  # Accounting terminology (critical for accuracy)
  accounting_terms:
    en: "Cash"
    es: "Efectivo"
    pt: "Caixa"
    fr: "Trésorerie"
  
  # Alternative names (in each language)
  synonyms:
    en: ["Cash", "Bank Account", "Liquid Assets"]
    es: ["Efectivo", "Bancos", "Activos Líquidos"]
    pt: ["Caixa", "Bancos", "Ativos Líquidos"]

# Translation attributes
translation_metadata:
  primary_language: "en"  # Source for all translations
  
  translations:
    - language: "es"
      status: "complete"
      translator: "native_spanish_speaker"
      reviewed_by: "eva"
      review_date: "2026-02-15"
      confidence: 0.99
    
    - language: "pt"
      status: "complete"
      translator: "native_portuguese_speaker"
      reviewed_by: "eva"
      review_date: "2026-02-16"
      confidence: 0.98
    
    - language: "fr"
      status: "planned"
      translator: "TBD"
      review_date: null
      confidence: null
```

---

## 🌍 Language Priorities

### Phase 0-1: Foundation (Spanish + Portuguese)

```yaml
language_roadmap:
  
  phase_1_spanish:
    scope: "All 80+ Level 3 accounts + Mexico/Colombia terminology"
    due: "Week 5-8"
    translations_needed: 80
    regional_variations:
      mexico: "SAT standard terminology"
      colombia: "PUC standard terminology"
      panama: "DGI standard terminology"
    
    example_regional_variation:
      account: "1.1.01"
      label_en: "Cash and Cash Equivalents"
      
      label_es_mx: "Bancos/Caja (Mexico SAT)"
      label_es_co: "Disponibilidades (Colombia PUC)"
      label_es_pa: "Caja y Bancos (Panama DGI)"
  
  phase_1_portuguese:
    scope: "All 80+ Level 3 accounts + Brazil compatibility"
    due: "Week 5-8"
    translations_needed: 80
    regional_variations:
      brazil: "IFRS standards"
      portugal: "European standards"
  
  phase_2_french:
    scope: "All accounts"
    due: "Quarter 2, 2026"
    note: "For French-speaking African countries + Canada"
```

---

## 📊 Translation Process

### How translations get created

```yaml
translation_workflow:
  
  step_1_source:
    input: "label_en (English label)"
    example: "Cash and Cash Equivalents"
  
  step_2_native_translator:
    action: "Translate to target language"
    requirements:
      - native_speaker: true
      - accounting_background: true
      - familiar_with_standards: "IFRS/GAAP/Local standards"
    
    output:
      translation: "Efectivo y Equivalentes de Efectivo"
      rationale: "Direct translation following IFRS Spanish terminology"
      alternative_translations:
        - "Disponibilidades (Colombia)"
        - "Bancos/Caja (Mexico)"
  
  step_3_eva_review:
    action: "Domain expert review"
    criteria:
      - accounting_correctness: true
      - local_regulatory_compliance: true
      - regional_appropriateness: true
    
    approval_options:
      - approved: "Use this translation"
      - needs_revision: "Request changes"
      - use_regional: "Use regional variation"
    
  step_4_qa_check:
    action: "Quality assurance"
    checks:
      - length_reasonable: "Not too long/short"
      - special_characters: "Accents, tildes correct"
      - consistency: "Same terms used consistently"
    
  step_5_publish:
    action: "Add to specification"
    version_bump: "MINOR"  # New feature = minor bump
    changelog_entry: "Added Spanish translations"
```

---

## 💾 Data Structure: i18n Keys

### Use Translation Keys Instead of Literal Labels

```yaml
# Phase 0: Define keys
account:
  uuid: "550e8400-e29b-41d4-a716-446655440000"
  code: "1.1.01"
  
  # Keys reference translation system
  label_key: "account.1_1_01.label"
  description_key: "account.1_1_01.description"
  synonym_keys:
    - "account.1_1_01.synonym_1"
    - "account.1_1_01.synonym_2"

# Translation file: translations/es.json
{
  "account": {
    "1_1_01": {
      "label": "Efectivo y Equivalentes de Efectivo",
      "description": "Dinero en efectivo y en cuentas bancarias...",
      "synonym_1": "Efectivo",
      "synonym_2": "Bancos"
    },
    "1_1_02": {
      "label": "Inversiones a Corto Plazo",
      ...
    }
  }
}

# Translation file: translations/pt.json
{
  "account": {
    "1_1_01": {
      "label": "Caixa e Equivalentes de Caixa",
      "description": "Dinheiro em caixa e em contas bancárias...",
      "synonym_1": "Caixa",
      "synonym_2": "Bancos"
    }
  }
}
```

---

## 🔄 Maintaining Consistency Across Languages

### Translation Memory (Glossary)

```yaml
# accounting_glossary.yaml
accounting_glossary:
  
  english_term: "Cash and Cash Equivalents"
  
  translations:
    spanish:
      term: "Efectivo y Equivalentes de Efectivo"
      ifrs_standard: "IAS 7"
      used_in_accounts: [1.1.01, 1.1.02]
      regional_variants:
        mexico: "Bancos/Caja"
        colombia: "Disponibilidades"
        panama: "Caja y Bancos"
    
    portuguese:
      term: "Caixa e Equivalentes de Caixa"
      ifrs_standard: "IAS 7"
      used_in_accounts: [1.1.01, 1.1.02]
      regional_variants:
        brazil: "Caixa e Equivalentes de Caixa"
        portugal: "Caixa e Equivalentes de Caixa"

# This glossary ensures:
# - Same English term = same translation
# - Consistency across all 80+ accounts
# - Regional variations captured
# - Standards referenced
```

---

## 🔧 Implementation Tasks (Phase 0)

- [x] Design i18n architecture (this document)
- [x] Define translation keys format
- [x] Create accounting glossary structure
- [x] Document translation process
- [x] Plan Phase 1 Spanish translations

### Phase 1 Tasks

- [ ] Hire Spanish native translators (accountant background)
- [ ] Translate all 80+ accounts to Spanish
- [ ] Regional variation testing (Mexico/Colombia/Panama)
- [ ] Eva review & approval
- [ ] Integrate into spec

### Phase 2 Tasks

- [ ] Add Portuguese (Brazil)
- [ ] Add Portuguese (Portugal)

---

## ✅ Success Criteria (Phase 0)

- [x] i18n architecture documented
- [x] Translation keys defined
- [x] Glossary template created
- [x] Translation workflow documented
- [x] Regional variation handling planned

---

## 📅 Timeline

- **Week 1-4:** Phase 0 (this document)
- **Week 5-8:** Phase 1 Spanish translations
- **Month 3:** Phase 2 Portuguese

---

## 📦 Languages by Use Case

| Language | Use Case | Priority | Timeline |
|----------|----------|----------|----------|
| **English** | Technical reference | ✅ Done | Phase 0 |
| **Spanish** | Mexico, Colombia, Panama | 🔴 High | Phase 1 |
| **Portuguese** | Brazil | 🟡 Medium | Phase 2 |
| **French** | African countries, Canada | 🟢 Low | Phase 3+ |

