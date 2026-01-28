#!/bin/bash

# ============================================
# Kontablo: Complete Free Setup
# ============================================

set -e  # Exit on error

echo "🚀 Kontablo - Complete Free Setup"
echo "=================================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

commands=("git" "python3" "pip" "npm")
for cmd in "${commands[@]}"; do
    if ! command -v $cmd &> /dev/null; then
        echo "❌ $cmd not found. Please install first."
        exit 1
    fi
done

echo "✅ All prerequisites installed"
echo ""

# 1. Infisical
echo "🔐 Step 1/3: Secrets Management (Infisical)"
echo "==========================================="
./scripts/setup_secrets.sh
echo ""

# 2. OpenSpec
echo "📋 Step 2/3: Spec-Driven Development (OpenSpec)"
echo "================================================"
./scripts/setup_openspec.sh
echo ""

# 3. Antigravity
echo "🤖 Step 3/3: AI Research (Antigravity)"
echo "======================================"
./scripts/setup_antigravity.sh
echo ""

# Final instructions
cat << 'FINAL'

🎉 Setup Complete!

📋 Quick Start Guide:

1. Set your secrets:
   infisical secrets set GOOGLE_AI_API_KEY "AIza..."
   infisical secrets set GITHUB_TOKEN "ghp_..."

2. Start your first research task:
   opsx:new extract-ifrs-taxonomy

3. Download a standard:
   ./scripts/research/download_standards.sh

4. Extract with Antigravity:
   python scripts/research/antigravity_extract.py file.pdf mx

📚 Documentation:
   - Tooling: docs/TOOLING.md
   - ADRs: docs/adr/
   - Roadmap: docs/ROADMAP.md

💡 All tools are FREE. No payment required.

🚀 Ready to start research!

FINAL

