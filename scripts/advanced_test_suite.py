import asyncio
import httpx
import json
import os
import sys

API_URL = "http://127.0.0.1:8000"

async def test_mapping_quality():
    print("🧠 Phase 1: Testing Semantic AI Mapping Quality...")
    async with httpx.AsyncClient() as client:
        # Mexican obscure account
        payload = {
            "local_code": "999.01",
            "local_name": "Provision por obsolescencia de inventarios estrategicos",
            "jurisdiction": "mx"
        }
        print(f"  > Mapping obscure account: '{payload['local_name']}'...")
        r = await client.post(f"{API_URL}/mapping/account", json=payload)
        if r.status_code == 200:
            data = r.json()
            print(f"  ✅ Result: {data['kontablo_id']} (Score: {data['confidence_score']})")
            print(f"  📝 Justification: {data['justification']}")
        else:
            print(f"  ❌ Error: {r.status_code}")

async def test_full_consolidation():
    print("\n🏢 Phase 2: Simulating Multi-Entity Global Consolidation...")
    
    consolidation_query = {
        "target_currency": "USD",
        "trial_balances": [
            {
                "subsidiary_id": "MEX-01",
                "jurisdiction": "mx",
                "currency": "MXN",
                "reporting_date": "2026-03-31",
                "entries": [
                    {"local_code": "101.01", "local_name": "Caja y efectivo", "debit": 50000.0, "credit": 0.0},
                    {"local_code": "105.01", "local_name": "Clientes nacionales", "debit": 150000.0, "credit": 0.0}
                ]
            },
            {
                "subsidiary_id": "BRA-02",
                "jurisdiction": "br",
                "currency": "BRL",
                "reporting_date": "2026-03-31",
                "entries": [
                    {"local_code": "1.01.01.01", "local_name": "Caixa Geral", "debit": 30000.0, "credit": 0.0},
                    {"local_code": "1.01.03.01", "local_name": "Duplicatas a Receber", "debit": 95000.0, "credit": 0.0}
                ]
            },
            {
                "subsidiary_id": "FRA-03",
                "jurisdiction": "fr",
                "currency": "EUR",
                "reporting_date": "2026-03-31",
                "entries": [
                    {"local_code": "512", "local_name": "Banque de France", "debit": 35000.0, "credit": 0.0},
                    {"local_code": "411", "local_name": "Clients de l'exercice", "debit": 95000.0, "credit": 0.0}
                ]
            },
            {
                "subsidiary_id": "PAN-04",
                "jurisdiction": "pa",
                "currency": "USD",
                "reporting_date": "2026-03-31",
                "entries": [
                    {"local_code": "1101", "local_name": "Caja Chucha", "debit": 15000.0, "credit": 0.0},
                    {"local_code": "1102", "local_name": "Banco General Panama", "debit": 120000.0, "credit": 0.0}
                ]
            },
            {
                "subsidiary_id": "ECU-05",
                "jurisdiction": "ec",
                "currency": "USD",
                "reporting_date": "2026-03-31",
                "entries": [
                    {"local_code": "10101", "local_name": "Caja Principal Ecuador", "debit": 8000.0, "credit": 0.0}
                ]
            },
            {
                "subsidiary_id": "VEN-06-OFFICIAL",
                "jurisdiction": "ve",
                "currency": "VES",
                "reporting_date": "2026-03-31",
                "entries": [
                    {"local_code": "1.1.01.01", "local_name": "Caja Principal", "debit": 100000.0, "credit": 0.0}
                ]
            },
            {
                "subsidiary_id": "VEN-07-PARALLEL",
                "jurisdiction": "ve",
                "currency": "VES",
                "reporting_date": "2026-03-31",
                "exchange_rate": 0.02, # Override: Parallel market rate (we value Bolivares less)
                "entries": [
                    {"local_code": "1.1.01.01", "local_name": "Caja Principal", "debit": 100000.0, "credit": 0.0}
                ]
            }
        ]
    }
    
    async with httpx.AsyncClient() as client:
        print("  > Sending consolidation request for MXN and BRL subsidiaries...")
        r = await client.post(f"{API_URL}/consolidation", json=consolidation_query, timeout=30.0)
        
        if r.status_code == 200:
            res = r.json()
            print(f"  ✅ Consolidated {res['entities_consolidated']} entities into {res['target_currency']}.")
            
            print("\n  --- CONSOLIDATED RESULTS ---")
            print(f"  {'Kontablo ID':<30} | {'Balance (USD)':>12}")
            print("  " + "-" * 45)
            
            for item in res['results']:
                balance = item['debit'] - item['credit']
                print(f"  {item['kontablo_id']:<30} | {balance:>12,.2f}")
        else:
            print(f"  ❌ Error: {r.status_code} - {r.text}")

async def main():
    print("🛡️ KONTABLO ADVANCED TEST SUITE")
    print("================================")
    
    # Check if server is up
    try:
        async with httpx.AsyncClient() as client:
            await client.get(API_URL)
    except:
        print("❌ CRITICAL: API Server is not running at http://127.0.0.1:8000")
        print("💡 Please run 'uvicorn api.src.main:app --reload' in another terminal first.")
        return

    await test_mapping_quality()
    await test_full_consolidation()
    
    print("\n🏁 Advanced test suite completed.")

if __name__ == "__main__":
    asyncio.run(main())
