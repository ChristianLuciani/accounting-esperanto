#!/bin/bash

# ============================================
# KONTABLO: GitHub Project Structure Setup
# ============================================

cd "$(dirname "$0")/../../" || exit 1

# -----------------
# 1. ADR (Architecture Decision Records)
# -----------------

mkdir -p docs/adr

cat << 'EOF' > docs/adr/README.md
# Architecture Decision Records (ADR)

## What is an ADR?

A document that captures an important architectural decision made along with its context and consequences.

## Format

Each ADR follows this structure:
- **Title**: Short noun phrase
- **Status**: Proposed | Accepted | Deprecated | Superseded
- **Context**: What forces are at play?
- **Decision**: What did we decide?
- **Consequences**: What becomes easier/harder?

## Index

| # | Title | Status | Date |
|---|-------|--------|------|
| [001](001-use-graph-not-tree.md) | Use Graph Model Instead of Tree | Accepted | 2025-01-27 |
| [002](002-uuid-as-primary-key.md) | UUID as Immutable Primary Key | Accepted | 2025-01-27 |
| [003](003-kontablo-naming.md) | Project Naming: Kontablo | Accepted | 2025-01-27 |
| [004](004-research-first-approach.md) | Research-First Before Implementation | Accepted | 2025-01-27 |

## How to Create a New ADR

```bash
./scripts/new-adr.sh "Your Decision Title"
```
EOF

# ADR Template Script
mkdir -p scripts

cat << 'EOF' > scripts/new-adr.sh
#!/bin/bash

# Get next ADR number
LAST_ADR=$(ls docs/adr/*.md 2>/dev/null | grep -E '^docs/adr/[0-9]+' | tail -1 | sed 's/.*\/0*\([0-9]*\).*/\1/')
NEXT_NUM=$(printf "%03d" $((LAST_ADR + 1)))

TITLE="$1"
if [ -z "$TITLE" ]; then
    echo "Usage: ./scripts/new-adr.sh 'Your Decision Title'"
    exit 1
fi

FILENAME="docs/adr/${NEXT_NUM}-$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | tr ' ' '-').md"

cat > "$FILENAME" << TEMPLATE
# ADR ${NEXT_NUM}: ${TITLE}

**Status:** Proposed
**Date:** $(date +%Y-%m-%d)
**Deciders:** [Names]

## Context

What is the issue that we're seeing that is motivating this decision or change?

## Decision

What is the change that we're proposing and/or doing?

## Consequences

### Positive
- What becomes easier?

### Negative
- What becomes harder?

### Neutral
- What is affected but neither good nor bad?

## References
- Related ADRs
- External resources
TEMPLATE

echo "✅ Created: $FILENAME"
echo "Edit it and change status to 'Accepted' when ready."
EOF

chmod +x scripts/new-adr.sh

# Create initial ADRs

cat << 'EOF' > docs/adr/001-use-graph-not-tree.md
# ADR 001: Use Graph Model Instead of Tree

**Status:** Accepted
**Date:** 2025-01-27
**Deciders:** Core team

## Context

Initial design used nested YAML (tree structure) where each account has one parent via `children` arrays. However, accounting concepts exist in multiple dimensions.

## Decision

Adopt a **graph-based model** where accounts reference parents via `parent_uuid`.

## Consequences

### Positive
- Supports multi-dimensional reporting
- Easier to query (flat structure)
- No artificial constraints

### Negative
- More complex to visualize
- Requires both human and machine specs

## References
- z.ai peer review (2025-01-27)
EOF

cat << 'EOF' > docs/adr/002-uuid-as-primary-key.md
# ADR 002: UUID as Immutable Primary Key

**Status:** Accepted
**Date:** 2025-01-27
**Deciders:** Core team

## Context

Accounts need immutable identifiers that don't change with standards updates.

## Decision

Use **UUIDs as the canonical identifier** (primary key).

## Consequences

### Positive
- Immutability: UUIDs never change
- Global uniqueness: No collision risk
- Database-friendly: Perfect for foreign keys

### Negative
- Not human-readable (need display layer)

## References
- RFC 4122 (UUID specification)
EOF

cat << 'EOF' > docs/adr/003-kontablo-naming.md
# ADR 003: Project Naming - Kontablo

**Status:** Accepted
**Date:** 2025-01-27
**Deciders:** Core team

## Context

Need a meaningful name that relates to accounting and has international appeal.

## Decision

**Kontablo** (from Esperanto "Kontableco" = Accounting)

## Consequences

### Positive
- Strong brand identity
- Works across languages
- Easy to pronounce in multiple languages

### Neutral
- Need to register domain and GitHub org
EOF

cat << 'EOF' > docs/adr/004-research-first-approach.md
# ADR 004: Research-First Before Implementation

**Status:** Accepted
**Date:** 2025-01-27
**Deciders:** Core team

## Context

Two possible approaches: Build MVP vs. Systematic research first.

## Decision

**Phase 0 (Research) before Phase 1 (Implementation)**

## Consequences

### Positive
- Credibility: Peer-reviewed publication = legitimacy
- Avoids mistakes: Research prevents costly pivots

### Negative
- Slower time to market
- Risk of scope creep
EOF

# -----------------
# 2. GitHub Issues Templates
# -----------------

mkdir -p .github/ISSUE_TEMPLATE

cat << 'EOF' > .github/ISSUE_TEMPLATE/research-task.md
---
name: Research Task
about: Track a specific research deliverable
title: '[RESEARCH] '
labels: research, phase-0
assignees: ''
---

## Research Objective

[What are we trying to learn/document?]

## Deliverables

- [ ] Data collected
- [ ] Analysis completed
- [ ] Documented
- [ ] Cited in bibliography

## Data Sources

- [ ] Source 1: [URL]
- [ ] Source 2: [URL]

## Timeline

**Due:** [Date]

## Related ADRs

- ADR-XXX
EOF

cat << 'EOF' > .github/ISSUE_TEMPLATE/adr-proposal.md
---
name: ADR Proposal
about: Propose an architectural decision
title: '[ADR] '
labels: decision, needs-review
assignees: ''
---

## Decision Title

[Short, clear description]

## Context

[What problem are we solving?]

## Proposed Decision

[What should we do?]

## Alternatives Considered

1. **Option A:** [Description]
2. **Option B:** [Description]

## Recommendation

[Which option and why?]

## Discussion Period

**Open for feedback until:** [Date, minimum 7 days]
EOF

cat << 'EOF' > .github/ISSUE_TEMPLATE/standard-analysis.md
---
name: Standard Analysis
about: Track analysis of a national/industry standard
title: '[STANDARD] Country/Standard Name'
labels: research, standard-analysis
assignees: ''
---

## Standard Information

- **Country:** [e.g., Mexico]
- **Authority:** [e.g., SAT]
- **Type:** [National GAAP / Industry-specific]

## Tasks

- [ ] Download official document
- [ ] Create metadata
- [ ] Extract account structure
- [ ] Document in research/standards
- [ ] Propose Kontablo mappings
- [ ] Expert validation

## Key Findings

[To be filled after analysis]
EOF

# -----------------
# 3. Project Automation Workflow
# -----------------

mkdir -p .github/workflows

cat << 'EOF' > .github/workflows/project-automation.yml
name: Project Automation

on:
  issues:
    types: [opened, labeled]
  pull_request:
    types: [opened, labeled]

jobs:
  add-to-project:
    runs-on: ubuntu-latest
    steps:
      - name: Add to Phase 0 Research Project
        uses: actions/add-to-project@v0.5.0
        with:
          project-url: https://github.com/orgs/kontablo/projects/1
          github-token: ${{ secrets.GITHUB_TOKEN }}
          labeled: research, phase-0
EOF

# -----------------
# 4. Project Roadmap
# -----------------

cat << 'EOF' > docs/ROADMAP.md
# Kontablo Roadmap

**Status:** Phase 0 (Research)
**Started:** 2025-01-27
**Target Completion:** 2025-06-30 (Phase 2)

## Phase 0: Research & Validation (Weeks 1-12)

**Goal:** Peer-reviewed white paper validating ontology

### Week 1-4: Standards Inventory
- IFRS/XBRL taxonomy extraction
- Mexico (SAT) analysis
- Colombia (PUC) analysis
- Panama (DGI/SMV) analysis
- Peru (PCGE) analysis
- US GAAP overview

### Week 5-8: Comparative Analysis
- Cross-tabulation matrix
- Frequency analysis
- Mapping complexity study
- Industry extensions

### Week 9-10: Expert Validation
- Recruit 10 CPAs (5 countries)
- Semi-structured interviews
- Survey on ontology
- Case study: Real company migration

### Week 11-12: Ontology Refinement
- Core v0.1 finalization
- Validation rules
- AI training dataset

## Phase 1: Specification (Weeks 13-16)

**Goal:** Published white paper

- Draft paper (Methodology, Results)
- Submit to Journal of Information Systems
- Preprint on SSRN

## Phase 2: Implementation (Weeks 17-24)

**Goal:** Working API + ERPNext module

- REST API
- AI classifier
- ERPNext module
- SDK (Python, JavaScript)

---

**Track progress:** https://github.com/kontablo/kontablo-core/projects/1
EOF

# -----------------
# 5. Decision Log
# -----------------

cat << 'EOF' > docs/DECISIONS.md
# Decision Log

Quick reference for all major decisions. See `/docs/adr/` for full context.

| Date | Decision | Status | ADR |
|------|----------|--------|-----|
| 2025-01-27 | Use graph model (not tree) | ✅ Accepted | [ADR-001](adr/001-use-graph-not-tree.md) |
| 2025-01-27 | UUID as primary key | ✅ Accepted | [ADR-002](adr/002-uuid-as-primary-key.md) |
| 2025-01-27 | Name project "Kontablo" | ✅ Accepted | [ADR-003](adr/003-kontablo-naming.md) |
| 2025-01-27 | Research-first approach | ✅ Accepted | [ADR-004](adr/004-research-first-approach.md) |

## Pending Decisions

- [ ] Which JSON Schema version? (draft-07 vs 2020-12)
- [ ] Use Protobuf for gRPC? (vs JSON)
- [ ] PostgreSQL vs MongoDB?
EOF

# -----------------
# 6. Initial GitHub Issues Script
# -----------------

cat << 'EOF' > .github/CREATE_INITIAL_ISSUES.sh
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
EOF

chmod +x .github/CREATE_INITIAL_ISSUES.sh

# -----------------
# 7. Git Commit
# -----------------

if [ -d .git ]; then
    git add -A
    git commit -m "infra: Add project management infrastructure

- ADR system with 4 initial decisions
- GitHub issue templates
- Project automation workflows
- Roadmap document
- Decision log for quick reference
- Script to create initial issues via gh CLI

All decisions tracked and documented." 2>/dev/null || true
fi

# -----------------
# 8. Summary
# -----------------

echo ""
echo "=========================================="
echo "✅ Project infrastructure created!"
echo "=========================================="
echo ""
echo "📋 What was created:"
echo "   docs/adr/              - Architecture Decision Records"
echo "   docs/ROADMAP.md        - 3-phase plan"
echo "   docs/DECISIONS.md      - Decision log"
echo "   .github/ISSUE_TEMPLATE/ - Issue templates"
echo "   .github/CREATE_INITIAL_ISSUES.sh - Issue generator"
echo "   scripts/new-adr.sh     - ADR generator"
echo ""
echo "🚀 Next steps:"
echo ""
echo "1. View the roadmap:"
echo "   cat docs/ROADMAP.md"
echo ""
echo "2. View the decisions:"
echo "   cat docs/DECISIONS.md"
echo ""
echo "3. Create a new ADR when needed:"
echo "   ./scripts/new-adr.sh 'Your Decision Title'"
echo ""
echo "4. Create initial GitHub issues:"
echo "   ./.github/CREATE_INITIAL_ISSUES.sh"
echo ""
