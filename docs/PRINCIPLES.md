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

## 6. Casos de Estudio e Implementaciones Locales

- **Panamá (DGI/SMV):**
  - [Propuesta de Estandarización](papers/panama_standardization_proposal.md): Análisis estratégico de la adopción ante la falta de un catálogo agrupador único.
  - [Guía de Mapeo para el CPA](manuals/panama_accountant_guide.md): Manual táctico de integración.

- **Ecuador (SuperCias/SRI):**
  - [Mapeo SuperCias](../localizations/ec/supercias_mapping.yaml): Mapeo directo del estándar obligatorio.
  - [Default Tree Ecuador](../localizations/ec/default_tree_ec.yaml): Plantilla de configuración rápida para nuevos ERPs.

- **Colombia (Supersociedades/Dian):**
  - [Mapeo PUC](../localizations/co/puc_mapping.yaml): Mapeo del Plan Único de Cuentas (D2650) a Kontablo.
  - [Default Tree Colombia](../localizations/co/default_tree_co.yaml): Estructura referencial 2650 con UUIDs universales.

- **Perú (SUNAT/CNC):**
  - [Mapeo PCGE](../localizations/pe/pcge_mapping.yaml): Mapeo del Plan Contable General Empresarial 2019.
  - [Default Tree Perú](../localizations/pe/default_tree_pe.yaml): Modelo de 2 a 3 dígitos para configuración de nuevos ERPs.

- **Chile (SII/CMF):**
  - [Mapeo FECU](../localizations/cl/fecu_mapping.yaml): Mapeo de la Ficha Estadística Codificada Uniforme (IFRS Chile).
  - [Default Tree Chile](../localizations/cl/default_tree_cl.yaml): Estándar basado en reportes CMF.

- **Argentina (FACPCE):**
  - [Mapeo RT 10](../localizations/ar/rt10_mapping.yaml): Mapeo basado en Normas Contables Profesionales Argentinas.
  - [Default Tree Argentina](../localizations/ar/default_tree_ar.yaml): Estructura para reporte de balances y estados de resultados.

- **Venezuela (FCCPV/SENIAT):**
  - [Mapeo VEN-NIF](../localizations/ve/ven_nif_mapping.yaml): Mapeo con taxonomía de reexpresión (NIC 29).
  - [ADR 007 Hyperinflation](../docs/adr/007-hiperinflation-standard.md): Principios para el manejo de economías con alta inflación.

- **Brasil (RFB/SPED):**
  - [Mapeo SPED](../localizations/br/sped_mapping.yaml): Mapeamento baseado no Plano de Contas Referencial da Receita Federal.
  - [Default Tree Brasil](../localizations/br/default_tree_br.yaml): Modelo voltado para o SPED (ECD/ECF).

- **USA & Canada (FASB/CPA Canada):**
  - [Mapeo US/CA](../localizations/us/us_ca_mapping.yaml): Mapeo basado en prácticas comunes de ERPs (QuickBooks/Xero/NetSuite).
  - [Default Tree NorthAmerica](../localizations/us/default_tree_us_ca.yaml): Estructura numérica estándar (1xxx-5xxx).

- **España (ICAC):**
  - [Mapeo PGC](../localizations/es/pgc_mapping.yaml): Mapeo del Plan General de Contabilidad (España).
  - [Default Tree España](../localizations/es/default_tree_es.yaml): Estructura de grupos 1-7 clásica.

- **China (MoF/ASBE):**
  - [Mapeo ASBE](../localizations/cn/asbe_mapping.yaml): Mapeo de las Normas Contables para Empresas (PRC).
  - [Default Tree China](../localizations/cn/default_tree_cn.yaml): Estructura de 4 dígitos (CAS).

- **Alemania (DATEV/HGB):**
  - [Mapeo SKR 04](../localizations/de/skr04_mapping.yaml): Estructura rígida de 4 dígitos (Abschlussgliederungsprinzip).
  - Stress Test: Rigidez de procesos y cumplimiento de ley comercial HGB.

- **India (ICAI/GST):**
  - [Mapeo GST](../localizations/in/ind_as_gst_mapping.yaml): Manejo de impuestos indirectos multi-slab (GST 5/12/18/28%).
  - Stress Test: Complejidad masiva en impuestos indirectos paralelos.

- **Reino Unido (FRC/FRS 102):**
  - [Mapeo FRS 102](../localizations/uk/frs102_mapping.yaml): Terminología específica (Debtors/Creditors).
  - Stress Test: Integración de IFRS-lite para PYMES británicas.

- **Emiratos Árabes Unidos (FTA):**
  - [Mapeo UAE Tax](../localizations/ae/uae_tax_mapping.yaml): Impuesto de sociedades (9%) y zonas francas exentas.
  - Stress Test: Manejo de jurisdicciones con baja carga impositiva y zonas económicas especiales.

- **Japón (ASBJ/J-GAAP):**
  - [Mapeo J-GAAP](../localizations/jp/jgaap_mapping.yaml): Enfoque en matching ingreso-gasto (Revenue-Expense approach).
  - Stress Test: Estructuras contables bilingües y lógica antagonista al balance-sheet approach de IFRS.

- **Rusia (MinFin/RAS):**
  - [Mapeo RAS](../localizations/ru/ras_mapping.yaml): Plan Schetov (99 cuentas principales).
  - Stress Test: Sistema de dos dígitos obligatorio con lógica post-soviética.

- **Israel (IASB/Israeli GAAP):**
  - [Mapeo Israel](../localizations/il/israel_gaap_mapping.yaml): Bilingüismo Hebreo/Inglés y convergencia IFRS.
  - Stress Test: Adaptación semántica a alfabetos no latinos.

- **Francia (ANC/PCG) - El Reto Definitivo:**
  - [Mapeo PCG](../localizations/fr/pcg_mapping.yaml): Estructura rígida de 8 clases. Padre de todos los sistemas codificados.
  - Stress Test: Si Kontablo puede con el Plan Comptable Général, puede con cualquier sistema del mundo.

---
Version: 1.0  
Last Updated: 2025-01-27
