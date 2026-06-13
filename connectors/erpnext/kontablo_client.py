import requests
import json
from typing import List, Dict

class ERPNextKontabloConnector:
    """
    Connector to bridge ERPNext (Frappe) and the Kontablo API.
    """
    def __init__(self, erpnext_url: str, api_key: str, api_secret: str, kontablo_url: str = "http://localhost:8000"):
        self.erpnext_url = erpnext_url
        self.headers = {
            "Authorization": f"token {api_key}:{api_secret}",
            "Content-Type": "application/json"
        }
        self.kontablo_url = kontablo_url

    def get_chart_of_accounts(self, company: str) -> List[Dict]:
        """
        Fetches the Chart of Accounts from ERPNext.
        """
        params = {
            "fields": json.dumps(["name", "account_name", "parent_account", "is_group", "root_type", "account_type", "account_currency"]),
            "filters": json.dumps([["company", "=", company]]),
            "limit_page_length": 0
        }
        response = requests.get(f"{self.erpnext_url}/api/resource/Account", headers=self.headers, params=params, timeout=30)
        response.raise_for_status()
        return response.json().get("data", [])

    def sync_to_kontablo(self, company: str, jurisdiction: str):
        """
        Extracts CoA from ERPNext and sends it to Kontablo for mapping.
        """
        erp_accounts = self.get_chart_of_accounts(company)
        
        kontablo_payload = {
            "company_id": company,
            "jurisdiction": jurisdiction,
            "accounts": [
                {
                    "local_code": acc["name"],
                    "local_name": acc["account_name"],
                    "jurisdiction": jurisdiction
                } for acc in erp_accounts
            ]
        }
        
        response = requests.post(f"{self.kontablo_url}/mapping/batch", json=kontablo_payload, timeout=30)
        response.raise_for_status()
        return response.json()

    def write_back_mappings(self, mappings: List[Dict], custom_field: str = "kontablo_uuid") -> List[Dict]:
        """
        Writes the resolved Kontablo mapping back onto each ERPNext Account.

        This is the "write-back" leg of the round-trip: ERPNext chart of accounts
        → Kontablo mapping → annotate the ERP. It PUTs the kontablo_id / uuid /
        confidence into a custom field on each Account so the mapping is visible
        and auditable inside ERPNext (mirroring the Frappe 'Kontablo Mapping'
        DocType for the REST-only deployment path).

        `mappings` is the `mappings` list returned by Kontablo `/mapping/batch`.
        Returns the list of write-back results (one per account).
        """
        results = []
        for m in mappings:
            account_name = m.get("local_code")
            if not account_name:
                continue
            payload = {
                custom_field: m.get("kontablo_uuid") or m.get("kontablo_id"),
                "kontablo_id": m.get("kontablo_id"),
                "kontablo_confidence": m.get("confidence_score"),
            }
            response = requests.put(
                f"{self.erpnext_url}/api/resource/Account/{account_name}",
                headers=self.headers,
                json=payload,
                timeout=30,
            )
            response.raise_for_status()
            results.append({"account": account_name, "written": payload})
        return results

    def get_trial_balance(self, company: str, to_date: str) -> Dict:
        """
        Executes the Trial Balance report in ERPNext.
        """
        params = {
            "company": company,
            "to_date": to_date
        }
        # In ERPNext, Trial Balance is a report, often accessed via an RPC-like call
        response = requests.get(
            f"{self.erpnext_url}/api/method/erpnext.accounts.report.trial_balance.trial_balance.execute",
            headers=self.headers,
            params=params,
            timeout=30,
        )
        response.raise_for_status()
        # ERPNext reports usually return [columns, data]
        return response.json().get("message", [])

    def consolidate_in_kontablo(self, company: str, to_date: str, jurisdiction: str, currency: str):
        """
        Fetches TB from ERPNext and sends it to Kontablo for consolidation.
        """
        tb_data = self.get_trial_balance(company, to_date)
        # Process ERPNext TB into Kontablo format
        # ERPNext TB rows usually have: account, debit, credit
        entries = []
        for row in tb_data[1]: # data part of [columns, data]
            if row.get("account") and (row.get("debit") or row.get("credit")):
                entries.append({
                    "local_code": row["account"],
                    "local_name": row.get("account_name") or row["account"],
                    "debit": row.get("debit", 0.0),
                    "credit": row.get("credit", 0.0)
                })
        
        payload = {
            "target_currency": currency,
            "trial_balances": [
                {
                    "subsidiary_id": company,
                    "jurisdiction": jurisdiction,
                    "currency": currency, # Should get from ERPNext
                    "reporting_date": to_date,
                    "entries": entries
                }
            ]
        }
        
        response = requests.post(f"{self.kontablo_url}/consolidation", json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
