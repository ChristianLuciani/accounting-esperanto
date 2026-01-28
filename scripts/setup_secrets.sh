#!/bin/bash

# ============================================
# Infisical Setup for Kontablo
# All tokens/secrets stored securely
# ============================================

echo "🔐 Setting up Infisical for secrets management..."

# -----------------
# 1. Install Infisical CLI
# -----------------

if ! command -v infisical &> /dev/null; then
    echo "📦 Installing Infisical CLI..."
    
    # macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install infisical/get-cli/infisical
    # Linux
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        curl -1sLf 'https://dl.cloudsmith.io/public/infisical/infisical-cli/setup.deb.sh' | sudo -E bash
        sudo apt-get update && sudo apt-get install -y infisical
    else
        echo "❌ Unsupported OS. Install manually: https://infisical.com/docs/cli/overview"
        exit 1
    fi
else
    echo "✅ Infisical CLI already installed"
fi

# -----------------
# 2. Login to Infisical
# -----------------

echo ""
echo "🔑 Login to Infisical..."
echo "   If you don't have an account: https://app.infisical.com/signup"
echo ""

infisical login

# -----------------
# 3. Initialize Project
# -----------------

echo ""
echo "📁 Initializing Infisical project..."
echo ""

# This creates .infisical.json (add to .gitignore)
infisical init

# -----------------
# 4. Set Required Secrets
# -----------------

cat << 'SECRETS_GUIDE'

📝 Required Secrets for Kontablo:

Run these commands to set each secret:

# GitHub Token (for automation)
infisical secrets set GITHUB_TOKEN "ghp_your_token_here" --env=dev

# Google AI Studio API Key (Antigravity - FREE)
# Get it: https://aistudio.google.com/app/apikey
infisical secrets set GOOGLE_AI_API_KEY "AIza..." --env=dev

# Anthropic API Key (if you have Claude Code access)
# Get it: https://console.anthropic.com/
infisical secrets set ANTHROPIC_API_KEY "sk-ant-..." --env=dev

# GitHub Fine-Grained Token (for gh CLI)
# Create: https://github.com/settings/tokens?type=beta
# Permissions: repo (all), workflow, project
infisical secrets set GH_TOKEN "github_pat_..." --env=dev

---

To use secrets in scripts:
  infisical run -- your_command

To export to shell:
  export $(infisical export --format=dotenv)

To view secrets:
  infisical secrets

SECRETS_GUIDE

# -----------------
# 5. Update .gitignore
# -----------------

cat >> .gitignore << 'GITIGNORE'

# Infisical
.infisical.json
.env
.env.local

GITIGNORE

echo ""
echo "✅ Infisical setup complete!"
echo ""
echo "🔑 Next: Set your secrets (see instructions above)"
echo ""

