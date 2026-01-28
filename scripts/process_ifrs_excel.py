#!/usr/bin/env python3
"""
Process IFRS taxonomy Excel file into Kontablo format.

Usage:
    python scripts/process_ifrs_excel.py path/to/ifrs.xlsx
"""

import sys
import pandas as pd
from pathlib import Path
import yaml
import uuid

def process_ifrs_excel(excel_path: Path):
    """Convert IFRS Excel to Kontablo YAML."""
    
    print(f"📊 Processing: {excel_path}")
    
    # Read Excel
    df = pd.read_excel(excel_path, sheet_name=0)
    
    print(f"✅ Loaded {len(df)} rows")
    print(f"📋 Columns: {list(df.columns)}")
    
    # Determine structure
    # (Adjust based on actual columns in your file)
    
    accounts = []
    
    for idx, row in df.iterrows():
        # Example mapping (adjust based on your Excel structure)
        account = {
            'uuid': str(uuid.uuid4()),
            'xbrl_tag': row.get('Element', ''),
            'label_en': row.get('Label', ''),
            'nature': 'debit' if 'Asset' in str(row.get('Type', '')) else 'credit',
            'status': 'active'
        }
        
        accounts.append(account)
    
    # Save to YAML
    output_path = Path('research/standards/international/ifrs_from_excel.yaml')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        yaml.dump({'accounts': accounts}, f, default_flow_style=False)
    
    print(f"✅ Saved to: {output_path}")
    print(f"📊 Extracted {len(accounts)} accounts")
    
    # Create summary
    summary_path = output_path.with_suffix('.md')
    with open(summary_path, 'w') as f:
        f.write(f"""# IFRS Taxonomy Extraction

**Source:** {excel_path}  
**Date:** {pd.Timestamp.now().strftime('%Y-%m-%d')}  
**Rows processed:** {len(df)}  
**Accounts extracted:** {len(accounts)}

## Structure

{df.describe()}

## Sample Accounts

{df.head(10).to_markdown()}
""")
    
    print(f"✅ Summary: {summary_path}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    
    excel_path = Path(sys.argv[1])
    
    if not excel_path.exists():
        print(f"❌ File not found: {excel_path}")
        sys.exit(1)
    
    process_ifrs_excel(excel_path)
