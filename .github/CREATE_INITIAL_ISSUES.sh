#!/bin/bash

# Create initial issues via GitHub CLI
# Install: brew install gh
# Authenticate: gh auth login

echo "Creating initial issues..."

gh issue create \
  --title "[RESEARCH] Extract IFRS/XBRL Taxonomy" \
  --body "Extract all account concepts from IFRS Taxonomy 2024 into structured CSV.

## Tasks
- Download IFRS Taxonomy 2024
- Create bibliography entry
- Parse XSD files with Python
- Export to research/standards/international/ifrs_concepts.csv
- Verify 500+ concepts extracted

## Deliverables
- CSV with columns: xbrl_tag, label_en, statement_type
- Jupyter notebook documenting extraction

## Timeline
Due: Week 1" \
  --label "research,phase-0,week-1" \
  --assignee "@me" 2>/dev/null && echo "✅ Issue 1 created" || echo "⚠️  Could not create issue (gh CLI may not be authenticated)"

echo "✅ Done!"
echo ""
echo "To create more issues:"
echo "  1. Install GitHub CLI: brew install gh"
echo "  2. Authenticate: gh auth login"
echo "  3. Run: ./.github/CREATE_INITIAL_ISSUES.sh"
