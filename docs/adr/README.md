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
| [011](011-client-specific-determinism-agent.md) | Client-Specific Determinism Agent | Proposed | 2026-05-28 |
| [012](012-mathematical-foundations-and-prior-art.md) | Mathematical Foundations and Prior-Art Positioning | Proposed | 2026-05-29 |
| [013](013-erp-tree-to-graph-compatibility.md) | Tree-to-Graph Compatibility Protocol for ERP Integration | Proposed | 2026-03-13 |
| [014](014-postgresql.md) | PostgreSQL | Proposed | 2026-01-27 |
| [015](015-core-node-admission-and-growth-policy.md) | Core-Node Admission Policy — when the ontology grows and when it must not | Proposed | 2026-06-11 |

> ⚠️ **Header/filename mismatch (renumbering debt):** files `013-erp-tree-to-graph-compatibility.md`
> and `014-postgresql.md` still carry their pre-renumbering internal headers (`013` reads
> "ADR-008", `014` reads "ADR 005"). This is why `docs/papers/.../ontology.tex` cites "ADR-008"
> for the tree-to-graph protocol. Reconcile filenames and internal headers in a single dedicated
> session — do not fix ad hoc, as other documents reference the current filenames.

> ⚠️ **Known debt:** ADR numbers 005 and 008 each have two files (collision). Resolve by renumbering in a dedicated session before public release — do not renumber ad hoc, as other documents may reference the current filenames.

## How to Create a New ADR

```bash
./scripts/new-adr.sh "Your Decision Title"
```
