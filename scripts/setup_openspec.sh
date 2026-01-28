#!/bin/bash

# ============================================
# OpenSpec Setup (Fission AI)
# Spec-driven development workflow
# ============================================

echo "📋 Setting up OpenSpec for Kontablo..."

# -----------------
# 1. Install OpenSpec CLI
# -----------------

if ! command -v opsx &> /dev/null; then
    echo "📦 Installing OpenSpec CLI..."
    npm install -g @fission-codes/openspec
else
    echo "✅ OpenSpec CLI already installed"
fi

# -----------------
# 2. Initialize OpenSpec in project
# -----------------

echo ""
echo "📁 Initializing OpenSpec structure..."

mkdir -p openspec/{changes,archive}

cat > openspec/README.md << 'OPENSPEC_README'
# OpenSpec for Kontablo

Spec-driven development for all major features and decisions.

## Workflow
```bash
# 1. Start a new change
opsx:new extract-ifrs-taxonomy

# 2. Fast-forward (generate all specs)
opsx:ff

# 3. Review generated docs:
#    - proposal.md (why)
#    - specs/ (what)
#    - design.md (how)
#    - tasks.md (steps)

# 4. Implement (manually or with AI)
opsx:apply

# 5. Archive when done
opsx:archive
```

## Active Changes

[None yet]

## Archived Changes

See `/openspec/archive/`

OPENSPEC_README

# -----------------
# 3. OpenSpec Alias Setup
# -----------------

cat >> ~/.zshrc << 'ALIASES'

# OpenSpec aliases
alias opsx:new='openspec new'
alias opsx:ff='openspec fast-forward'
alias opsx:apply='openspec apply'
alias opsx:archive='openspec archive'

ALIASES

echo "✅ Added aliases to ~/.zshrc"
echo "   Run: source ~/.zshrc"

# -----------------
# 4. Create Template for Kontablo Changes
# -----------------

mkdir -p openspec/templates

cat > openspec/templates/research-task.md << 'TEMPLATE'
# {{TITLE}}

## Type
- [ ] Research Task
- [ ] Feature Implementation
- [ ] Infrastructure Change
- [ ] Documentation

## Context

[Why are we doing this?]

## Scope

### In Scope
- What will be researched/built

### Out of Scope
- What we're explicitly NOT doing

## Success Criteria

- [ ] Criterion 1
- [ ] Criterion 2

## Dependencies

- Blocked by: [Issue #X]
- Blocks: [Issue #Y]

## Timeline

**Estimated:** X days  
**Due:** YYYY-MM-DD

## Resources

- [Link to relevant docs]
- [Related ADRs]

TEMPLATE

echo "✅ Created OpenSpec templates"

echo ""
echo "🎉 OpenSpec setup complete!"
echo ""
echo "📋 Usage:"
echo "   opsx:new task-name    # Start new spec"
echo "   opsx:ff               # Generate all docs"
echo "   opsx:apply            # Implement"
echo "   opsx:archive          # Archive when done"
echo ""

