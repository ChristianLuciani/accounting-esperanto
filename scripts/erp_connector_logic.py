"""
Kontablo ERP Universal Connector Logic Prototype
Demonstrates mapping two different ERP structures to the Kontablo Graph.

1. ERP-A (Hierarchical): SAP/Oracle Style 
   - 1000 Assets
     - 1100 Current Assets
       - 1101 Cash at Bank
2. ERP-B (Analytical/Flat): Xero/Quickbooks/SaaS Style
   - Account Name: "USD Operating Account"
   - Category: "BankAccount"
"""

from typing import List, Dict
import json

# Kontablo Graph Target Nodes (Sample)
KONTABLO_GRAPH = {
    "asset.current.cash": {"labels": ["Cash", "Bancos", "Tien mat"], "level": 3},
    "asset.current.receivables": {"labels": ["Receivables", "Clientes"], "level": 3}
}

class ERPConnector:
    def __init__(self, erp_type: str):
        self.erp_type = erp_type

    def normalize_account_data(self, raw_data: Dict) -> Dict:
        """
        Normalizes disparate ERP structures into a Kontablo-compatible flat schema.
        """
        if self.erp_type == "hierarchical":
            # Extract path: 1000 -> 1100 -> 1101
            return {
                "local_code": raw_data.get("code"),
                "local_name": raw_data.get("name"),
                "context": f"Path: {raw_data.get('parent_name')} > {raw_data.get('name')}"
            }
        elif self.erp_type == "analytical":
            return {
                "local_code": raw_data.get("id"),
                "local_name": raw_data.get("name"),
                "context": f"Type: {raw_data.get('category')}"
            }
        return raw_data

def run_demo():
    # Example 1: SAP-style hierarchical data
    sap_data = {"code": "1101", "name": "Cash - HSBC USD", "parent_name": "Current Assets"}
    
    # Example 2: Xero-style analytical data
    xero_data = {"id": "acc-998", "name": "Main Operating Account", "category": "BankAccount"}

    connectors = {
        "hierarchical": ERPConnector("hierarchical"),
        "analytical": ERPConnector("analytical")
    }

    print("--- KONTABLO ERP NORMALIZATION DEMO ---")
    
    norm_sap = connectors["hierarchical"].normalize_account_data(sap_data)
    norm_xero = connectors["analytical"].normalize_account_data(xero_data)

    print(f"SAP Normalized: {json.dumps(norm_sap, indent=2)}")
    print(f"Xero Normalized: {json.dumps(norm_xero, indent=2)}")

    print("\n--- NEXT STEP: AI Semantic Mapping ---")
    print("AI would take 'Context: Path: Current Assets > Cash' and Map to 'asset.current.cash'")
    print("AI would take 'Context: Type: BankAccount' and Map to 'asset.current.cash'")
    print("RESULT: Unified corporate ledger achieved despite different ERP logic.")

if __name__ == "__main__":
    run_demo()
