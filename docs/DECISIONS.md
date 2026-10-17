# Decision Log

Quick reference for all major decisions. See `/docs/adr/` for full context.

> **Alcance declarado** (`agos` §Convenciones):
> Cubre: las decisiones mayores **listadas en la tabla de abajo** (4 filas al 2026-10-16) · No cubre: el registro completo de ADR — `docs/adr/` tiene 19 y **ése** es el ledger canónico; una decisión sin fila acá no es por eso menor ni inexistente · as_of: 2026-10-16
> Si una pieza no aparece, no asumas que no existe: reportá el hueco.

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
