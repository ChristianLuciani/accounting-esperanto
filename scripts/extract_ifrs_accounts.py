#!/usr/bin/env python3
"""
Extract IFRS accounts using Gemini and create Kontablo mapping.
This is Week 1, Days 2-5 of the action plan.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.ai_router import router
import json
from datetime import datetime

def extract_ifrs_accounts():
    """Extract IFRS taxonomy accounts and create initial mapping."""
    
    print("🚀 Week 1, Days 2-5: IFRS Extraction")
    print("=" * 60)
    
    # Step 1: Extract primary account structure
    print("\n📋 Step 1: Extract IFRS primary accounts...")
    
    ifrs_extraction = router.complete(
        prompt="""
You are analyzing the IFRS (International Financial Reporting Standards) taxonomy.

Extract the primary account structure:

1. **Balance Sheet Assets:**
   - Current Assets (Cash, Receivables, Inventory)
   - Non-Current Assets (PP&E, Intangibles, Investments)

2. **Balance Sheet Liabilities:**
   - Current Liabilities (Payables, Short-term Debt)
   - Non-Current Liabilities (Long-term Debt, Deferred Tax)

3. **Equity:**
   - Share Capital
   - Retained Earnings
   - Reserves

4. **Income Statement:**
   - Revenue
   - Cost of Sales
   - Operating Expenses
   - Financial Income/Expenses
   - Tax Expense

5. **Cash Flow:**
   - Operating Activities
   - Investing Activities
   - Financing Activities

For each primary account, provide:
- IFRS name (en)
- XBRL tag (e.g., ifrs-full:Assets)
- Nature (Debit/Credit)
- Statement (Balance Sheet/P&L/Cash Flow)
- Typical sub-accounts (3-5 examples)

Output as CSV with columns:
xbrl_tag,label_en,nature,statement_type,typical_subs

Output ONLY the CSV, no other text.
""",
        task_type="extraction",
        priority="quality",
        max_tokens=8000
    )
    
    # Save extraction
    os.makedirs('research/standards/international', exist_ok=True)
    with open('research/standards/international/ifrs_primary_accounts.csv', 'w') as f:
        f.write(ifrs_extraction['content'])
    
    print(f"✅ Extracted {ifrs_extraction['content'].count(chr(10))} IFRS accounts")
    
    # Step 2: Create Kontablo mapping
    print("\n🔗 Step 2: Create Kontablo Level 1-2 mapping...")
    
    kontablo_mapping = router.complete(
        prompt=f"""
Based on these IFRS accounts:

{ifrs_extraction['content']}

Design Kontablo Level 1-2 ontology that:

1. Maps every IFRS account to Kontablo
2. Creates UUIDs (use Python uuid4 format)
3. Defines aggregation rules

Output as YAML with this structure:

```yaml
kontablo_level_1:
  - id: assets
    uuid: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
    label_en: Assets
    ifrs_root: Assets
    level_2_accounts:
      - id: assets.current
        uuid: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        label_en: Current Assets
        ifrs_mappings:
          - ifrs-full:CurrentAssets
        accounts:
          - code: 1010
            label: Cash and Cash Equivalents
            ifrs_tag: ifrs-full:CashAndCashEquivalents
```

Be thorough and complete for all levels.
""",
        task_type="research",
        priority="quality",
        max_tokens=16000
    )
    
    # Save mapping
    with open('core/kontablo_v0_1_mapping.yaml', 'w') as f:
        f.write(kontablo_mapping['content'])
    
    print(f"✅ Created Kontablo Level 1-2 mapping")
    
    # Step 3: Create metadata
    print("\n📝 Step 3: Create extraction metadata...")
    
    metadata = {
        "extraction_date": datetime.now().isoformat(),
        "phase": "Phase 0, Week 1",
        "source": "IFRS Foundation Taxonomy",
        "standard": "IFRS 2024",
        "accounts_extracted": ifrs_extraction['content'].count('\n') - 1,
        "ai_model": ifrs_extraction.get('model', 'gemini-2.5-flash'),
        "tokens_used": ifrs_extraction.get('tokens', 0),
        "latency_seconds": ifrs_extraction.get('latency', 0),
        "files_created": [
            "research/standards/international/ifrs_primary_accounts.csv",
            "core/kontablo_v0_1_mapping.yaml",
            "research/standards/international/extraction_metadata.json"
        ]
    }
    
    with open('research/standards/international/extraction_metadata.json', 'w') as f:
        json.dump(metadata, f, indent=2)
    
    # Step 4: Summary
    print("\n" + "=" * 60)
    print("✅ Week 1 Days 2-5: IFRS Extraction Complete")
    print("=" * 60)
    print(f"\n📊 Summary:")
    print(f"  • Accounts extracted: {metadata['accounts_extracted']}")
    print(f"  • Model used: {metadata['ai_model']}")
    print(f"  • Tokens used: {metadata['tokens_used']}")
    print(f"  • Latency: {metadata['latency_seconds']:.2f}s")
    print(f"\n📁 Files created:")
    for file in metadata['files_created']:
        print(f"  • {file}")
    
    print("\n🚀 Next: Week 1, Day 1 - Set up additional API keys")
    print("\nTo continue with Week 2 (Mexico SAT, Colombia PUC):")
    print("  python scripts/extract_country_standards.py mx co pa")

if __name__ == '__main__':
    extract_ifrs_accounts()
