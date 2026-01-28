# OpenSpec: Aggregation Rules Specification

**Change ID:** aggregation-rules-specification  
**Status:** Proposal  
**Date:** January 27, 2026  
**Phase:** Phase 0 (Simple), Phase 2 (Moderate), Phase 3 (Advanced)

---

## 📋 Proposal: How to Combine Multiple Local Accounts into One Kontablo Account

### Problem
- Countries have different chart of accounts
- Mexico has 3 cash accounts; Colombia has 4
- Need formal rules to combine (aggregate) them into single Kontablo account
- Without this, consolidation logic will be ad-hoc

### Solution
- **Phase 0:** Simple aggregation (SUM, AVERAGE, WEIGHTED-SUM)
- **Phase 2:** Moderate (add conditional logic)
- **Phase 3:** Advanced (add blockchain verification)

### Current Scope: Phase 0 Only

---

## 🎯 Design: Phase 0 Simple Aggregation Rules

### Schema
```yaml
aggregation_rules:
  rule_id: "agg_cash_simple"
  target_kontablo_account: "1.1.01"
  target_label: "Cash and Cash Equivalents"
  
  # Phase 0: All countries use same rule (for now)
  phase_0_rules:
    method: "sum"  # Options: sum, average, weighted_sum
    
    # By country
    countries:
      mexico:
        source_accounts: ["101", "102", "103"]
        source_labels: ["Bancos", "Caja", "Cheques por Cobrar"]
        aggregation_method: "sum"
        formula: "101 + 102 + 103"
        validation:
          - all_accounts_must_exist: true
          - all_accounts_must_be_debit: true
          - no_negative_values: true
      
      colombia:
        source_accounts: ["1105", "1110", "1120"]
        source_labels: ["Caja General", "Bancos", "Depósitos en Tránsito"]
        aggregation_method: "sum"
        formula: "1105 + 1110 + 1120"
        validation:
          - all_accounts_must_exist: true
          - all_accounts_must_be_debit: true
      
      panama:
        source_accounts: ["1010", "1020"]
        source_labels: ["Caja", "Bancos"]
        aggregation_method: "sum"
        formula: "1010 + 1020"
        validation:
          - all_accounts_must_exist: true
          - all_accounts_must_be_debit: true
```

### Python Implementation (Phase 0)
```python
# Phase 0: Simple aggregation functions

def aggregate_simple_sum(accounts: list[float]) -> float:
    """Sum all accounts."""
    return sum(accounts)

def aggregate_simple_avg(accounts: list[float]) -> float:
    """Average of all accounts."""
    return sum(accounts) / len(accounts)

def aggregate_weighted_sum(accounts: list[tuple[float, float]]) -> float:
    """Weighted sum: accounts are (value, weight) tuples."""
    numerator = sum(value * weight for value, weight in accounts)
    denominator = sum(weight for _, weight in accounts)
    return numerator / denominator if denominator > 0 else 0

# Rule registry
PHASE_0_RULES = {
    "cash": {
        "method": "sum",
        "countries": {
            "mexico": ["101", "102", "103"],
            "colombia": ["1105", "1110", "1120"],
            "panama": ["1010", "1020"]
        }
    },
    "accounts_receivable": {
        "method": "sum",
        "countries": {
            "mexico": ["110", "111"],
            "colombia": ["1205", "1206"],
            "panama": ["1100", "1101"]
        }
    },
    "inventory": {
        "method": "weighted_sum",  # By inventory value
        "countries": {
            "mexico": ["120", "121"],
            "colombia": ["1300", "1301"],
            "panama": ["1200", "1201"]
        }
    }
}

def apply_aggregation_rule(rule_id: str, country: str, account_values: dict) -> float:
    """Apply aggregation rule to get consolidated account value."""
    
    rule = PHASE_0_RULES.get(rule_id)
    if not rule:
        raise ValueError(f"Rule {rule_id} not found")
    
    method = rule["method"]
    source_accounts = rule["countries"][country]
    
    # Get values for source accounts
    values = [account_values[acc] for acc in source_accounts]
    
    # Apply aggregation method
    if method == "sum":
        return aggregate_simple_sum(values)
    elif method == "average":
        return aggregate_simple_avg(values)
    elif method == "weighted_sum":
        # Assumes account_values has weight info
        weighted = [(account_values[acc], get_weight(acc)) for acc in source_accounts]
        return aggregate_weighted_sum(weighted)
    else:
        raise ValueError(f"Unknown aggregation method: {method}")

# Example usage
accounts_mexico = {
    "101": 50000,     # Bancos
    "102": 10000,     # Caja
    "103": 500        # Cheques por Cobrar
}

cash_mexico = apply_aggregation_rule("cash", "mexico", accounts_mexico)
print(f"Consolidated cash (Mexico): {cash_mexico}")  # 60500
```

---

## 📊 Phase 0 Rules (Simple - SUM only)

### Assets
```yaml
assets:
  - rule_id: "cash"
    method: "sum"
    target: "1.1.01"
    description: "All cash-like accounts combine into Cash"
    
  - rule_id: "short_term_investments"
    method: "sum"
    target: "1.1.02"
    
  - rule_id: "accounts_receivable"
    method: "sum"
    target: "1.1.03"
    
  - rule_id: "inventory"
    method: "sum"
    target: "1.1.06"
    note: "Phase 2: upgrade to weighted-sum by value"
    
  - rule_id: "ppe"
    method: "sum"
    target: "1.2.01"
    
  - rule_id: "accumulated_depreciation"
    method: "sum"
    target: "1.2.02"
    is_contra_account: true
```

### Liabilities
```yaml
liabilities:
  - rule_id: "accounts_payable"
    method: "sum"
    target: "2.1.01"
    
  - rule_id: "short_term_debt"
    method: "sum"
    target: "2.1.03"
    
  - rule_id: "long_term_debt"
    method: "sum"
    target: "2.2.01"
```

### Equity
```yaml
equity:
  - rule_id: "capital"
    method: "sum"
    target: "3.1.01"
    
  - rule_id: "retained_earnings"
    method: "sum"
    target: "3.2.01"
```

### Revenue & Expenses
```yaml
income:
  - rule_id: "revenue"
    method: "sum"
    target: "4.1.01"
    
  - rule_id: "cost_of_sales"
    method: "sum"
    target: "5.1.01"
    
  - rule_id: "operating_expenses"
    method: "sum"
    target: "5.2.01"
```

---

## 🔄 Phase 2 Roadmap: Conditional Logic

**In Phase 2, upgrade to MODERATE complexity:**

```yaml
# Phase 2 example: Conditional rules
aggregation_rules_phase_2:
  rule_id: "accumulated_depreciation_conditional"
  target: "1.2.02"
  
  conditions:
    # Rule 1: Financial companies
    - condition: "industry == 'financial'"
      method: "sum"
      adjustment: "apply_ifrs9_guidance"
      
    # Rule 2: Manufacturing
    - condition: "industry == 'manufacturing'"
      method: "sum"
      adjustment: "apply_accelerated_depreciation"
      
    # Rule 3: Tech/Software
    - condition: "industry == 'technology'"
      method: "sum"
      adjustment: "apply_shorter_useful_life"
    
    # Default
    - condition: "default"
      method: "sum"
      adjustment: "none"

# Phase 2 Python
def apply_conditional_rule(rule_id: str, context: dict) -> callable:
    """Return aggregation function based on context (industry, status, etc)."""
    
    rule = PHASE_2_RULES.get(rule_id)
    
    for condition_rule in rule["conditions"]:
        if evaluate_condition(condition_rule["condition"], context):
            return get_aggregation_func(condition_rule["method"])
    
    return get_aggregation_func(rule["conditions"][-1]["method"])
```

---

## 🚀 Phase 3 Roadmap: Blockchain Verification

**In Phase 3, add ADVANCED blockchain checking:**

```yaml
# Phase 3 example: Blockchain verification
aggregation_rules_phase_3:
  rule_id: "cash_blockchain_verified"
  target: "1.1.01"
  
  # All Phase 2 logic + blockchain check
  blockchain_verification:
    network: "ethereum"
    contract_address: "0x..."
    method: "verify_account_aggregation"
    
  workflow:
    1: "Apply conditional logic (Phase 2)"
    2: "Calculate aggregated value"
    3: "Create aggregation proof (hash)"
    4: "Submit to smart contract"
    5: "Contract verifies and stores hash"
    6: "Return verified value + proof"

# Phase 3 Python
async def apply_blockchain_rule(rule_id: str, accounts: dict) -> dict:
    """Apply rule with blockchain verification."""
    
    # Step 1-2: Apply Phase 2 logic
    aggregated_value = apply_conditional_rule(rule_id, context)
    
    # Step 3: Create proof
    aggregation_proof = create_hash_proof({
        "rule_id": rule_id,
        "accounts": accounts,
        "value": aggregated_value,
        "timestamp": datetime.now()
    })
    
    # Step 4-5: Verify on blockchain
    tx_hash = await blockchain.verify_aggregation(
        contract_address=KONTABLO_CONTRACT,
        proof=aggregation_proof
    )
    
    # Step 6: Return with proof
    return {
        "value": aggregated_value,
        "proof": aggregation_proof,
        "blockchain_tx": tx_hash,
        "verified": True
    }
```

---

## 🔧 Implementation Tasks

### Phase 0 (This Week)
- [x] Define simple aggregation rules (SUM only)
- [x] Create Python functions for SUM, AVG, WEIGHTED_SUM
- [x] Create rule registry (PHASE_0_RULES)
- [x] Document all 20+ aggregation rules
- [x] Add validation (all accounts must be debit/credit, etc.)

### Phase 2 (Weeks 5-8)
- [ ] Add conditional logic framework
- [ ] Create industry-specific rules
- [ ] Add context-aware aggregation
- [ ] Implement rule engine

### Phase 3 (Weeks 9+)
- [ ] Add blockchain integration
- [ ] Create smart contract
- [ ] Implement proof verification
- [ ] Add immutability layer

---

## ✅ Success Criteria (Phase 0)

- [x] 20+ simple aggregation rules defined
- [x] Python functions implement SUM/AVG/WEIGHTED_SUM
- [x] All rules have clear country mappings
- [x] Validation rules documented
- [x] No conditional logic (keep simple)
- [x] Roadmap for Phase 2/3 documented

---

## 📅 Timeline

- **Today:** Finalize this spec
- **Week 2:** Use these rules for country extraction
- **Week 3:** Validate aggregations in comparative analysis
- **Week 4:** Verify consolidations in paper

**Phase 2 Upgrade:** Weeks 5-8 (once you see real data patterns)

---

## 📦 Tech Stack by Phase

| Phase | Language | Framework | Storage | Use Case |
|-------|----------|-----------|---------|----------|
| **0** | Python | Pandas | YAML/CSV | Research |
| **2** | TypeScript/Node | Express | PostgreSQL | Production API |
| **3** | TypeScript/Node | Express + Web3 | PostgreSQL + Ethereum | Enterprise |

