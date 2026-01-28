#!/bin/bash

# ============================================
# Bulk Download Official Standards
# Uses Antigravity to find and download
# ============================================

echo "📥 Downloading official accounting standards..."

# Countries to download
COUNTRIES=(
    "mx:Mexico:SAT:http://omawww.sat.gob.mx/"
    "co:Colombia:PUC:https://www.supersociedades.gov.co/"
    "pa:Panama:DGI:https://www.dgi.gob.pa/"
    "pe:Peru:PCGE:https://www.mef.gob.pe/"
    "ar:Argentina:FACPCE:https://www.facpce.org.ar/"
    "br:Brazil:CFC:https://cfc.org.br/"
)

mkdir -p bibliography/primary_sources

for entry in "${COUNTRIES[@]}"; do
    IFS=: read -r code country authority url <<< "$entry"
    
    echo ""
    echo "🌍 $country ($code)"
    echo "   Authority: $authority"
    echo "   URL: $url"
    echo ""
    
    # Use Antigravity to find the official document
    python - <<PYTHON_INLINE
import google.generativeai as genai
import os

# Get API key
api_key = os.popen('infisical secrets get GOOGLE_AI_API_KEY --plain').read().strip()
genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-2.0-flash-exp')

prompt = """Find the official chart of accounts PDF for $country.

Authority: $authority
Website: $url

Provide:
1. Direct download URL (if available)
2. Page where it can be found
3. Document title
4. Year/version

If no direct PDF, explain how to access it.
"""

response = model.generate_content(prompt)
print(response.text)
PYTHON_INLINE
    
    read -p "Download manually? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📂 Save to: bibliography/primary_sources/${code}_official.pdf"
        echo "   Then run: python scripts/research/antigravity_extract.py bibliography/primary_sources/${code}_official.pdf $code"
    fi
done

echo ""
echo "✅ Download guide complete"
echo "📁 PDFs should be in: bibliography/primary_sources/"
