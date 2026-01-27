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
