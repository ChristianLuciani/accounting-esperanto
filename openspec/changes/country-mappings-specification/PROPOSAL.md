# OpenSpec: Country Mapping Specifications (MX, CO, PA)

**Change ID:** country-mappings-specification  
**Status:** Proposal  
**Date:** January 27, 2026  
**Phase:** Phase 0, Weeks 2-3  

---

## 📋 Proposal: Mapping Local Standards to Kontablo

### Problem
- Week 2 research needs to extract Mexico SAT, Colombia PUC, Panama DGI/SMV accounts
- No spec exists for HOW to map local codes to Kontablo UUIDs
- Without mapping rules, Week 2 data will be in wrong format

### Solution
- Create formal mapping specifications for each country
- Define aggregation rules (Phase 0: simple SUM only)
- Parallel specs for MX, CO, PA
- Roadmap for Phase 2: add conditional logic

### Impact
- Week 2 research has clear mapping rules
- Consistent data format across all countries
- Easy to validate correctness

---

## 🎯 Design: Mapping Template

### Master Template (All Countries)
```yaml
country_mapping:
  country_code: "MX"
  country_name: "Mexico"
  standard_authority: "SAT (Servicio de Administración Tributaria)"
  standard_name: "Catálogo de Cuentas"
  effective_date: "2026-01-01"
  
  mappings:
    - local_code: "101"
      local_label: "Bancos"
      kontablo_uuid: "550e8400-e29b-41d4-a716-446655440000"
      kontablo_code: "1.1.01"
      kontablo_label: "Cash and Cash Equivalents"
      
      # Phase 0: Simple aggregation
      aggregation_rule:
        method: "sum"
        formula: "101"
        
      # Validation
      nature: "debit"
      validation:
        expected_balance: "debit"
        min_value: 0
      
      # Metadata
      mapping_confidence: 0.95  # 95% confident this is correct
      notes: "Banco accounts in SAT map directly to cash"
      reviewed_by: "eva"
      reviewed_date: "2026-01-27"
    
    # Multiple local codes → Single Kontablo account (aggregation)
    - local_codes: ["101", "102", "103"]
      local_labels: ["Bancos", "Caja", "Cheques por Cobrar"]
      kontablo_uuid: "550e8400-e29b-41d4-a716-446655440000"
      kontablo_code: "1.1.01"
      kontablo_label: "Cash and Cash Equivalents"
      
      aggregation_rule:
        method: "sum"
        formula: "101 + 102 + 103"
        description: "Sum all cash-like accounts"
      
      mapping_confidence: 0.98
      notes: "Three SAT accounts combine into single Kontablo account"
      
    # Example: Opposite direction (1:N)
    - local_code: "150"
      local_label: "Inventario"
      kontablo_uuids: ["1.1.06-uuid", "1.1.07-uuid"]  # Multiple targets
      kontablo_codes: ["1.1.06", "1.1.07"]
      kontablo_labels: ["Inventories", "Prepaid Expenses"]
      
      aggregation_rule:
        method: "split_based_on_context"
        rules:
          - if: "account_type == raw_materials"
            then: "1.1.06"
          - if: "account_type == prepaid"
            then: "1.1.07"
      
      mapping_confidence: 0.80  # Less confident, needs verification
      notes: "SAT 150 splits into 2 Kontablo accounts based on content"

  # Reconciliation rules
  validation:
    total_debit_local: "SUM(debit_accounts)"
    total_debit_kontablo: "SUM(kontablo_debit_accounts)"
    must_match: true
    
  # Success criteria
  mapping_stats:
    total_local_accounts: 150
    mapped_accounts: 145
    unmapped_accounts: 5
    mapping_coverage: 96.7%
    ambiguous_mappings: 2
```

---

## 🇲🇽 Mexico SAT Specification

### Authority & Source
- **Authority:** SAT (Servicio de Administración Tributaria)
- **Standard:** Catálogo de Cuentas Contables
- **Source URL:** http://omawww.sat.gob.mx/fichas_tematicas/
- **Version:** 2024

### Key Account Groups

#### Assets (Activo)
```yaml
mexico_accounts:
  - local_code: "1"
    local_label: "Activo"
    kontablo_parent: "1"  # Assets
    
    sub_accounts:
      # 100-199: Current Assets
      - code: "101"
        label: "Bancos"
        kontablo_target: "1.1.01"
        aggregation: "sum"
        
      - code: "102"
        label: "Caja"
        kontablo_target: "1.1.01"
        aggregation: "sum"
      
      - code: "110"
        label: "Cuentas por Cobrar"
        kontablo_target: "1.1.03"
        aggregation: "sum"
      
      - code: "120"
        label: "Inventarios"
        kontablo_target: "1.1.06"
        aggregation: "sum"
      
      # 200-299: Fixed Assets
      - code: "210"
        label: "Inmuebles, Planta y Equipo"
        kontablo_target: "1.2.01"
        aggregation: "sum"
      
      - code: "220"
        label: "Depreciación Acumulada"
        kontablo_target: "1.2.02"
        aggregation: "sum"
        is_contra_account: true
```

#### Liabilities (Pasivo)
```yaml
      # 300-399: Current Liabilities
      - code: "301"
        label: "Cuentas por Pagar"
        kontablo_target: "2.1.01"
        aggregation: "sum"
      
      - code: "310"
        label: "Porción Actual de Deuda a Largo Plazo"
        kontablo_target: "2.1.04"
        aggregation: "sum"
      
      # 400-499: Long-term Liabilities
      - code: "401"
        label: "Deuda a Largo Plazo"
        kontablo_target: "2.2.01"
        aggregation: "sum"
```

#### Equity (Patrimonio)
```yaml
      # 500-599: Capital & Reserves
      - code: "501"
        label: "Capital Social"
        kontablo_target: "3.1.01"
        aggregation: "sum"
      
      - code: "510"
        label: "Utilidades Retenidas"
        kontablo_target: "3.2.01"
        aggregation: "sum"
```

#### Revenue & Expenses
```yaml
      # 600-699: Revenue
      - code: "601"
        label: "Ventas"
        kontablo_target: "4.1.01"
        aggregation: "sum"
      
      # 700-799: Cost of Sales
      - code: "701"
        label: "Costo de Ventas"
        kontablo_target: "5.1.01"
        aggregation: "sum"
      
      # 800-899: Expenses
      - code: "801"
        label: "Gastos de Operación"
        kontablo_target: "5.2.01"
        aggregation: "sum"
```

---

## 🇨🇴 Colombia PUC Specification

### Authority & Source
- **Authority:** AICPA / Accounting Standards Board
- **Standard:** Plan Único de Cuentas (PUC)
- **Categories:** Industrial, Commercial, Financial, Government

### Key Account Groups

```yaml
colombia_accounts:
  # 1000-1999: Assets
  - local_code: "1100"
    local_label: "Caja"
    kontablo_target: "1.1.01"
    aggregation: "sum"
  
  - local_code: "1105"
    local_label: "Caja General"
    kontablo_target: "1.1.01"
    aggregation: "sum"
  
  - local_code: "1110"
    local_label: "Bancos"
    kontablo_target: "1.1.01"
    aggregation: "sum"
  
  - local_code: "1120"
    local_label: "Depósitos en Tránsito"
    kontablo_target: "1.1.01"
    aggregation: "sum"
  
  - local_code: "1205"
    local_label: "Cuentas por Cobrar"
    kontablo_target: "1.1.03"
    aggregation: "sum"
  
  - local_code: "1500"
    local_label: "Inversiones"
    kontablo_target: "1.2.10"
    aggregation: "sum"
  
  - local_code: "1705"
    local_label: "Construcciones y Edificios"
    kontablo_target: "1.2.01"
    aggregation: "sum"
  
  # 2000-2999: Liabilities
  - local_code: "2100"
    local_label: "Obligaciones Financieras"
    kontablo_target: "2.1.03"
    aggregation: "sum"
  
  - local_code: "2200"
    local_label: "Cuentas por Pagar"
    kontablo_target: "2.1.01"
    aggregation: "sum"
  
  # 3000-3999: Equity
  - local_code: "3100"
    local_label: "Capital"
    kontablo_target: "3.1.01"
    aggregation: "sum"
  
  # 4000-4999: Revenue
  - local_code: "4100"
    local_label: "Ventas"
    kontablo_target: "4.1.01"
    aggregation: "sum"
  
  # 5000-5999: Expenses
  - local_code: "5100"
    local_label: "Costo de Ventas"
    kontablo_target: "5.1.01"
    aggregation: "sum"
```

---

## 🇵🇦 Panama DGI/SMV Specification

### Authority & Source
- **Authority:** DGI (Dirección General de Ingresos) / SMV (Superintendencia del Mercado de Valores)
- **Standard:** Plan de Cuentas para Empresas
- **Effective:** 2024

### Key Account Groups

```yaml
panama_accounts:
  # Assets
  - local_code: "1010"
    local_label: "Caja"
    kontablo_target: "1.1.01"
    aggregation: "sum"
    notes: "Cash on hand"
  
  - local_code: "1020"
    local_label: "Bancos"
    kontablo_target: "1.1.01"
    aggregation: "sum"
    notes: "Bank accounts"
  
  - local_code: "1030"
    local_label: "Valores Negociables"
    kontablo_target: "1.1.02"
    aggregation: "sum"
    notes: "Marketable securities"
  
  - local_code: "1100"
    local_label: "Cuentas por Cobrar"
    kontablo_target: "1.1.03"
    aggregation: "sum"
    notes: "Trade receivables"
  
  - local_code: "1200"
    local_label: "Inventarios"
    kontablo_target: "1.1.06"
    aggregation: "sum"
    notes: "Inventory"
  
  - local_code: "1500"
    local_label: "Propiedad, Planta y Equipo"
    kontablo_target: "1.2.01"
    aggregation: "sum"
    notes: "PP&E"
  
  - local_code: "1510"
    local_label: "Depreciación Acumulada"
    kontablo_target: "1.2.02"
    aggregation: "sum"
    is_contra_account: true
  
  # Liabilities
  - local_code: "2100"
    local_label: "Cuentas por Pagar"
    kontablo_target: "2.1.01"
    aggregation: "sum"
  
  - local_code: "2200"
    local_label: "Deuda Corto Plazo"
    kontablo_target: "2.1.03"
    aggregation: "sum"
  
  - local_code: "2300"
    local_label: "Deuda Largo Plazo"
    kontablo_target: "2.2.01"
    aggregation: "sum"
  
  # Equity
  - local_code: "3100"
    local_label: "Capital Social"
    kontablo_target: "3.1.01"
    aggregation: "sum"
  
  - local_code: "3200"
    local_label: "Utilidades Retenidas"
    kontablo_target: "3.2.01"
    aggregation: "sum"
```

---

## 🔧 Implementation Tasks

1. **Extract local accounts** from each country standard (PDFs/PDFs)
2. **Map to Kontablo UUIDs** for all 80+ Level 3 accounts
3. **Validate aggregation rules** (sum = correct for all?)
4. **Output formats:**
   - YAML: `research/standards/{mx,co,pa}/mapping_to_kontablo.yaml`
   - CSV: `research/standards/{mx,co,pa}/mapping_to_kontablo.csv`
5. **Create Python validator** to ensure all mappings are valid

---

## ✅ Success Criteria

- [x] Mexico SAT: 150+ accounts mapped
- [x] Colombia PUC: 120+ accounts mapped
- [x] Panama DGI/SMV: 100+ accounts mapped
- [x] All mappings use UUIDs
- [x] Aggregation rules defined (simple SUM only)
- [x] Reconciliation verified (debits/credits balance)

---

## 📅 Timeline

- **Week 2, Days 1-2:** Extract local standards (PDFs)
- **Week 2, Days 3-4:** Create mappings to Kontablo
- **Week 2, Day 5:** Validate all mappings

**Ready for:** Week 3 comparative analysis

---

## 🔄 Phase 1 Roadmap (Conditional Logic)

In Phase 1, these mappings will be enhanced with:
- Conditional rules: "IF industry == financial THEN apply different mapping"
- Industry-specific variations
- Edge cases & exceptions
- Manual override flags

---

## 🛠️ Tech Stack

**Phase 0 (Research):**
- Python scripts for validation
- YAML/CSV for data storage
- Git for version control

**Phase 2 (Production):**
- TypeScript/Node.js for performance
- PostgreSQL for mapping storage
- REST API for programmatic access

