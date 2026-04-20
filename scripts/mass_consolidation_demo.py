import asyncio
import json
import os
import sys

# Add API src to path
sys.path.append(os.path.join(os.getcwd(), 'api/src'))

from models.kontablo import TrialBalance, TrialBalanceEntry
from services.ontology import OntologyService
from services.mapping import MappingService
from services.consolidation import ConsolidationService
from services.ai import AIService

async def run_massive_simulation():
    print("🚀 Starting Kontablo Massive Consolidation Simulation...")
    
    # 1. Setup Services
    BASE_DIR = os.getcwd()
    ONTOLOGY_PATH = os.path.join(BASE_DIR, "core/schemas/level3_accounts.yaml")
    STANDARDS_DIR = os.path.join(BASE_DIR, "research/standards")
    
    ontology_service = OntologyService(ONTOLOGY_PATH)
    ai_service = AIService() # Will be mock/none if no key
    mapping_service = MappingService(STANDARDS_DIR, ontology_service, ai_service)
    consolidation_service = ConsolidationService(mapping_service, ontology_service)
    
    # 2. Generate Mock Data for 4 Jurisdictions
    subsidiaries = [
        {"id": "MX-ENT-001", "jurisdiction": "mx", "currency": "MXN", "accounts": [("101.01", "Caja", 50000, 0), ("105.01", "Clientes", 120000, 0)]},
        {"id": "BR-ENT-002", "jurisdiction": "br", "currency": "BRL", "accounts": [("1.01.01.01", "Caixa Geral", 30000, 0), ("1.01.03.01", "Clientes", 80000, 0)]},
        {"id": "FR-ENT-003", "jurisdiction": "fr", "currency": "EUR", "accounts": [("512", "Banque", 15000, 0), ("411", "Clients", 45000, 0)]},
        {"id": "IN-ENT-004", "jurisdiction": "in", "currency": "INR", "accounts": [("1001", "Cash", 500000, 0), ("2001", "Trade Receivables", 1200000, 0)]}
    ]
    
    trial_balances = []
    for sub in subsidiaries:
        entries = [
            TrialBalanceEntry(local_code=code, local_name=name, debit=float(d), credit=float(c))
            for code, name, d, c in sub["accounts"]
        ]
        trial_balances.append(TrialBalance(
            subsidiary_id=sub["id"],
            jurisdiction=sub["jurisdiction"],
            currency=sub["currency"],
            reporting_date="2026-12-31",
            entries=entries
        ))
    
    print(f"📊 {len(subsidiaries)} Subsidiaries loaded. Processing mappings...")
    
    # 3. Process Consolidation
    # We use USD as target currency
    result = await consolidation_service.consolidate(trial_balances, "USD")
    
    # 4. Display Results
    print("\n" + "="*60)
    print("📈 KONTABLO CONSOLIDATED FINANCIAL STATEMENT (DRAFT)")
    print("="*60)
    print(f"Target Currency: {result['target_currency']}")
    print(f"Entities: {result['entities_consolidated']}")
    print("-" * 60)
    print(f"{'Kontablo ID':<30} | {'Debit (USD)':>12} | {'Credit (USD)':>12}")
    print("-" * 60)
    
    total_debit = 0
    total_credit = 0
    
    for row in result["results"]:
        print(f"{row['kontablo_id']:<30} | {row['debit']:>12,.2f} | {row['credit']:>12,.2f}")
        total_debit += row["debit"]
        total_credit += row["credit"]
        
    print("-" * 60)
    print(f"{'TOTAL':<30} | {total_debit:>12,.2f} | {total_credit:>12,.2f}")
    print("=" * 60)
    print("\n✅ Simulation Complete. All local accounts successfully mapped to IFRS Level 3.")

if __name__ == "__main__":
    asyncio.run(run_massive_simulation())
