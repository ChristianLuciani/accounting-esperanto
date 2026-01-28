#!/bin/bash

# ============================================
# Investigación en Vivo: APIs Gratuitas LLM
# ============================================

echo "🔍 Investigando APIs gratuitas de LLMs..."
echo "=========================================="
echo ""

# Create research directory
mkdir -p research/api_providers

# Function to research a provider
research_provider() {
    local provider=$1
    local url=$2
    
    echo "📡 Researching: $provider"
    echo "   URL: $url"
    
    # Use Antigravity to research via infisical
    infisical run -- /opt/anaconda3/bin/python3 << PYTHON
import google.generativeai as genai
import os
import sys
from datetime import datetime

# Get API key from Infisical (already injected by infisical run)
api_key = os.getenv('GOOGLE_AI_API_KEY')
if not api_key:
    print("⚠️  No GOOGLE_AI_API_KEY found. Skipping.")
    sys.exit(0)

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

provider_name = "$provider"
provider_url = "$url"

prompt = f"""You are researching FREE LLM API providers as of TODAY.

For the following provider, find:

1. **Free Tier Details:**
   - Is it "always free with limits" or "free credits that run out"?
   - What are the rate limits? (RPM, TPM, daily caps)
   - Does it require credit card?

2. **Available Models (as of today):**
   - List ALL models available in free tier
   - For each model: name, context window, speed tier

3. **API Documentation:**
   - Base URL
   - Authentication method
   - Example curl command

4. **Reliability:**
   - Uptime history (if available)
   - Community feedback

5. **Best Use Case for Kontablo:**
   - Which model is best for: PDF extraction, research, coding

Be SPECIFIC with model names and versions. Check the official docs.

PROVIDER: {provider_name}
URL: {provider_url}

IMPORTANT: Visit the actual website and check TODAY's offerings. Provide CURRENT information."""

print(f"🤖 Querying Gemini about {provider_name}...")

try:
    response = model.generate_content(prompt)
    
    # Save response
    safe_name = provider_name.lower().replace(" ", "_").replace(".", "")
    output_file = f'research/api_providers/{safe_name}.md'
    with open(output_file, 'w') as f:
        f.write(f"""# {provider_name} - Free Tier Research

**Research Date:** {datetime.now().strftime('%Y-%m-%d')}
**Researcher:** Gemini 2.5 Flash (Antigravity)
**Official URL:** {provider_url}

---

{response.text}

---

**Verification Status:** ⏳ Pending manual verification
**Next:** Test API with actual key
""")
    
    print(f"✅ Saved: {output_file}")
    
except Exception as e:
    print(f"❌ Error researching {provider_name}: {e}")
    sys.exit(1)

PYTHON
    
    echo ""
}

# List of providers to research
echo "🎯 Target Providers:"
echo ""

providers=(
    "Groq:https://groq.com"
    "Together AI:https://together.ai"
    "Cerebras:https://cerebras.ai"
    "OpenRouter:https://openrouter.ai"
    "Hugging Face:https://huggingface.co/inference-api"
    "Poe:https://poe.com/api"
    "Fireworks AI:https://fireworks.ai"
    "Replicate:https://replicate.com"
    "Anyscale:https://anyscale.com"
    "DeepInfra:https://deepinfra.com"
    "Mistral AI:https://mistral.ai"
    "Cohere:https://cohere.com"
)

for entry in "${providers[@]}"; do
    IFS=: read -r provider url <<< "$entry"
    echo "  - $provider"
done

echo ""
read -p "Research all providers? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    for entry in "${providers[@]}"; do
        IFS=: read -r provider url <<< "$entry"
        research_provider "$provider" "$url"
        sleep 2  # Rate limit courtesy
    done
    
    echo ""
    echo "✅ Research complete!"
    echo "📁 Results in: research/api_providers/"
    echo ""
    echo "🔍 To review results:"
    echo "   ls -lh research/api_providers/"
    echo "   cat research/api_providers/*.md | head -50"
    echo ""
    echo "💡 Next: Review each file and verify manually"
else
    echo "⏭️  Skipped automated research"
    echo "💡 Run again when ready, or research manually"
fi

