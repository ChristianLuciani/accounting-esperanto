#!/usr/bin/env python3
"""
Antigravity-powered document extraction.

Usage:
    python scripts/research/antigravity_extract.py path/to/document.pdf country_code
    
Features:
- Uploads PDFs to Google AI Studio (FREE)
- Extracts structured account data
- Saves with citations and hash verification
"""

import sys
import os
import hashlib
from pathlib import Path
import google.generativeai as genai

def get_api_key():
    """Get API key from Infisical or environment."""
    # First try Infisical
    try:
        import subprocess
        result = subprocess.run(
            ['infisical', 'secrets', 'get', 'GOOGLE_AI_API_KEY', '--plain'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except:
        pass
    
    # Fallback to environment
    return os.getenv('GOOGLE_AI_API_KEY')

def extract_accounts(pdf_path: Path, country_code: str):
    """Extract account structure using Gemini 2.0."""
    
    print(f"📄 Processing: {pdf_path}")
    
    # Calculate hash
    with open(pdf_path, 'rb') as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    
    print(f"🔐 SHA-256: {file_hash}")
    
    # Initialize Gemini
    api_key = get_api_key()
    if not api_key:
        print("❌ No API key found. Run: infisical secrets set GOOGLE_AI_API_KEY")
        sys.exit(1)
    
    genai.configure(api_key=api_key)
    
    # Upload file
    print("📤 Uploading to Google AI Studio...")
    uploaded_file = genai.upload_file(pdf_path)
    print(f"✅ Uploaded: {uploaded_file.uri}")
    
    # Create prompt
    prompt = f"""You are an accounting research assistant analyzing the official chart of accounts for {country_code.upper()}.

Extract the following information systematically:

## 1. STRUCTURE
- Number of hierarchical levels
- Coding format (provide regex pattern)
- Total estimated accounts
- Separator used (dot, dash, etc.)

## 2. ACCOUNT EXTRACTION
Extract ALL accounts into this CSV format:
```csv
code,label,nature,category,page_number
```

Rules:
- nature: "debit" or "credit"
- category: "asset", "liability", "equity", "revenue", "expense"
- Include page number for verification

## 3. KEY CHARACTERISTICS
- Mandatory vs optional accounts
- Unique features compared to IFRS
- Industry-specific sections

## 4. MAPPING CHALLENGES
- Accounts that don't map cleanly to IFRS
- Ambiguous classifications
- Cultural/legal specifics

## 5. VERIFICATION
File hash for verification: {file_hash}

Provide extremely detailed extraction. This is for academic research requiring 100% accuracy.
"""

    # Call Gemini 2.0 Flash (FREE, multimodal)
    model = genai.GenerativeModel('gemini-2.0-flash-exp')
    
    print("🤖 Extracting with Gemini 2.0 Flash...")
    response = model.generate_content([uploaded_file, prompt])
    
    # Save output
    output_dir = Path(f'research/standards/{country_code}')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'antigravity_extraction.md'
    
    with open(output_file, 'w') as f:
        f.write(f"""# {country_code.upper()} Chart of Accounts Extraction

**Source:** {pdf_path}  
**File Hash:** {file_hash}  
**Extraction Date:** {pd.Timestamp.now().strftime('%Y-%m-%d')}  
**Model:** Gemini 2.0 Flash (Antigravity)

---

{response.text}
""")
    
    print(f"✅ Saved to: {output_file}")
    
    # Extract CSV if present
    if '```csv' in response.text:
        csv_start = response.text.find('```csv') + 6
        csv_end = response.text.find('```', csv_start)
        csv_content = response.text[csv_start:csv_end].strip()
        
        csv_file = output_dir / 'accounts.csv'
        with open(csv_file, 'w') as f:
            f.write(csv_content)
        
        print(f"✅ Extracted CSV: {csv_file}")
    
    # Create metadata
    meta_file = output_dir / f'{pdf_path.stem}.meta.yaml'
    with open(meta_file, 'w') as f:
        f.write(f"""source_id: "{country_code}_{pdf_path.stem}"
type: "government_regulation"
country: "{country_code.upper()}"
title: "[To be filled]"
file_path: "{pdf_path}"
file_hash: "{file_hash}"
extraction_method: "Gemini 2.0 Flash (Antigravity)"
extraction_date: "{pd.Timestamp.now().strftime('%Y-%m-%d')}"
""")
    
    print(f"✅ Created metadata: {meta_file}")
    print("")
    print("🎉 Extraction complete!")
    print(f"📁 Review: {output_dir}/")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(1)
    
    pdf_path = Path(sys.argv[1])
    country_code = sys.argv[2]
    
    if not pdf_path.exists():
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)
    
    # Pandas for timestamp
    import pandas as pd
    
    extract_accounts(pdf_path, country_code)
