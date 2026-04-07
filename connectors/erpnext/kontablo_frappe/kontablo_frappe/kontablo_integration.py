import frappe
import requests
import json

@frappe.whitelist()
def sync_chart_of_accounts(company: str, jurisdiction: str):
    """
    Whitelisted method to sync Frappe accounts to the Kontablo mapping service.
    """
    accounts = frappe.get_all("Account", 
        fields=["name", "account_name", "parent_account", "is_group", "root_type", "account_type", "account_currency"],
        filters={"company": company}
    )
    
    # Use the local FastAPI URL (this would be configurable in a Settings doctype in a real app)
    kontablo_url = "http://localhost:8000"
    
    payload = {
        "company_id": company,
        "jurisdiction": jurisdiction,
        "accounts": [
            {
                "local_code": acc["name"],
                "local_name": acc["account_name"],
                "jurisdiction": jurisdiction
            } for acc in accounts
        ]
    }
    
    try:
        response = requests.post(f"{kontablo_url}/mapping/batch", json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"Kontablo Sync Error: {str(e)}", "Kontablo Integration")
        return {"error": str(e)}

@frappe.whitelist()
def sync_trial_balance(company: str, to_date: str, jurisdiction: str, currency: str):
    """
    Pulls Trial Balance from Frappe and sends it to Kontablo for consolidation.
    """
    from erpnext.accounts.report.trial_balance.trial_balance import execute
    
    # Execute the core ERPNext report
    filters = {"company": company, "to_date": to_date}
    _, data = execute(filters)
    
    entries = []
    for row in data:
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
                "currency": currency,
                "reporting_date": to_date,
                "entries": entries
            }
        ]
    }
    
    kontablo_url = "http://localhost:8000"
    try:
        response = requests.post(f"{kontablo_url}/consolidation", json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"Kontablo Consolidation Error: {str(e)}", "Kontablo Integration")
        return {"error": str(e)}
