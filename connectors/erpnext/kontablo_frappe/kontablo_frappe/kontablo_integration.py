import frappe
import requests
import json

@frappe.whitelist()
def sync_chart_of_accounts(company: str, jurisdiction: str):
    """
    Syncs Frappe accounts to Kontablo and STORES the results in 'Kontablo Mapping' DocType.
    This implements the 'AI Proposes' side of Co-responsibility.
    """
    # 1. Get Settings
    settings = frappe.get_single("Kontablo Settings")
    if not settings.is_active:
        frappe.throw("Kontablo integration is not active in Settings.")
        
    kontablo_url = settings.api_url
    api_key = settings.get_password("api_key")
    
    # 2. Extract local accounts
    accounts = frappe.get_all("Account", 
        fields=["name", "account_name"],
        filters={"company": company, "is_group": 0}
    )
    
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
    
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        response = requests.post(f"{kontablo_url}/mapping/batch", json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # 3. Store results in ERPNext for human review (The 'Human Disposes' part)
        for mapping in data.get("mappings", []):
            if not frappe.db.exists("Kontablo Mapping", mapping["local_code"]):
                doc = frappe.new_doc("Kontablo Mapping")
                doc.erp_account = mapping["local_code"]
                doc.kontablo_id = mapping["kontablo_id"]
                doc.confidence_score = mapping["confidence_score"] * 100
                doc.status = "Suggested"
                doc.inconsistency_flag = mapping.get("inconsistency_flag", False)
                doc.audit_note = mapping.get("inconsistency_note") or mapping.get("justification")
                doc.insert()
            else:
                doc = frappe.get_doc("Kontablo Mapping", mapping["local_code"])
                # We only update if status is still 'Suggested' to avoid overwriting human work
                if doc.status == "Suggested":
                    doc.kontablo_id = mapping["kontablo_id"]
                    doc.confidence_score = mapping["confidence_score"] * 100
                    doc.inconsistency_flag = mapping.get("inconsistency_flag", False)
                    doc.audit_note = mapping.get("inconsistency_note") or mapping.get("justification")
                    doc.save()
                    
        return {"status": "success", "mapped": data["mapped_count"]}
        
    except Exception as e:
        frappe.log_error(f"Kontablo Sync Error: {str(e)}", "Kontablo Integration")
        return {"error": str(e)}

@frappe.whitelist()
def sync_trial_balance(company: str, to_date: str, jurisdiction: str, currency: str):
    """
    Pulls Trial Balance from Frappe and sends it to Kontablo for global consolidation.
    """
    from erpnext.accounts.report.trial_balance.trial_balance import execute
    
    settings = frappe.get_single("Kontablo Settings")
    kontablo_url = settings.api_url
    api_key = settings.get_password("api_key")
    
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
    
    headers = {"Authorization": f"Bearer {api_key}"}
    try:
        response = requests.post(f"{kontablo_url}/consolidation", json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        frappe.log_error(f"Kontablo Consolidation Error: {str(e)}", "Kontablo Integration")
        return {"error": str(e)}
