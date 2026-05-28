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
| [005](005-manifesto-principles.md) | Manifesto Principles | Accepted | 2025 |
| [005](005-postgresql.md) | PostgreSQL ⚠️ NUMBER COLLISION with manifesto-principles | Accepted | 2025 |
| [006](006-mx-sat-alignment.md) | MX-SAT Alignment | Accepted | 2025 |
| [007](007-hiperinflation-standard.md) | Hyperinflation Standard | Accepted | 2025 |
| [008](008-erp-tree-to-graph-compatibility.md) | ERP Tree-to-Graph Compatibility | Accepted | 2025 |
| [008](008_co_responsibility_governance.md) | Co-Responsibility Governance ⚠️ NUMBER COLLISION with erp-tree-to-graph | Accepted | 2026 |
| [009](009-determinism-over-stochasticity.md) | Determinism Over Stochasticity (Code Over Inference) | Accepted | 2026-05-28 |
| [010](010-agent-native-and-connector-licensing.md) | Agent-Native Access Layer & Connector Licensing | Accepted | 2026-05-28 |

> ⚠️ **Known debt:** ADR numbers 005 and 008 each have two files (collision). Resolve by renumbering in a dedicated session before public release — do not renumber ad hoc, as other documents may reference the current filenames.

## How to Create a New ADR

```bash
./scripts/new-adr.sh "Your Decision Title"
```
