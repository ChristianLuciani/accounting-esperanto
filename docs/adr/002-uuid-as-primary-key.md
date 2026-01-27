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
