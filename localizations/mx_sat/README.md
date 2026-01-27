# Mexico - SAT (Servicio de Administración Tributaria)

## Authority
- **Country:** Mexico
- **Regulator:** SAT
- **Standard:** Código Agrupador del SAT
- **Digital Format:** XML
- **Last Updated:** 2024

## Mapping Strategy

### Aggregation (Many local → One global)
```
SAT 101 (Caja) ────┐
SAT 102 (Bancos)───┼──→ Esperanto 1.1.01 (Cash)
SAT 103 (Inversiones)─┘
```

### Disaggregation (One global → Many local)
```
Esperanto 4.1.01 (Revenue) ──┬──→ SAT 401 (Ventas Nacionales)
                             └──→ SAT 402 (Ventas Exportación)
```

## Files
- `catalog.json` - Official SAT chart of accounts
- `mapping.yaml` - Esperanto mappings with aggregation rules
