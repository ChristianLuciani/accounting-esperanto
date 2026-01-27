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
