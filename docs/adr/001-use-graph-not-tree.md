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
