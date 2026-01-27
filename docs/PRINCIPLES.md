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
