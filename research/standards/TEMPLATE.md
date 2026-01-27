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
