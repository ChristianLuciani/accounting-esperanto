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
