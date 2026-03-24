# ADR-006: Mapeo y Alineación con el Catálogo de Cuentas del SAT (México)

**Date**: 2026-03-09  
**Status**: Propuesto  
**Context**: El Anexo 24 de México define una jerarquía estricta de cuentas (Catálogo de Cuentas) de uso obligatorio fiscal. Kontablo utiliza una ontología de grafo (ADR-001) para representar la multi-dimensionalidad financiera. Debemos establecer cómo se resuelven las divergencias entre el árbol fiscal mexicano y el grafo universal de Kontablo.

## Decisión

1. **Uso de Cuentas Contra-Activo como Agregación de Resta (`subtract`)**:
   El SAT incluye las estimaciones por cuentas incobrables de clientes dentro del rubro de Activo a Corto Plazo. Kontablo vincula explícitamente estas "contra-cuentas" al UUID del activo que disminuyen agregando la regla de "subtract" en su campo `aggregation_rules`.
   * **Ejemplo**: La cuenta SAT `106` (Estimación de cuentas incobrables) se mapea al UUID de Trade Receivables (`00000000-0000-4000-8000-000000000104`) con la regla `subtract`.

2. **Diferenciación de Impuestos Trasladados y Retenidos (Nivel 3 Kontablo)**:
   El SAT divide los pasivos de impuestos entre trasladados (IVA) y retenidos (ISR). Kontablo agrupaba todos los "Current Tax Liabilities" en Nivel 2. Por tanto, se han creado dos UUIDs de Nivel 3 en el Core (`kontablo_v0_1_mapping.yaml`) para soportar esta granularidad:
   * `00000000-0000-4000-8000-000000000203`: Current Tax Liabilities (Translated) - IVA
   * `00000000-0000-4000-8000-000000000204`: Current Tax Liabilities (Withheld) - ISR Retenciones

3. **Mapeo N:1 (Varios Códigos de SAT a 1 UUID de Kontablo)**:
   En los casos donde el modelo SAT sea innecesariamente detallado desde una perspectiva global de consolidación, múltiples códigos SAT mapearán al mismo UUID de Kontablo, sumando automáticamente sus saldos.

## Consecuencias Positivas
- Kontablo gana capacidad real de ingestar Balanzas de Comprobación electrónicas de México de forma automatizada.
- Las empresas multinacionales podrán ver la provisión por cuentas incobrables de México ya consolidada en sus Cuentas por Cobrar Netas a nivel IFRS.
- Mantiene la premisa de "Graph, not Tree", usando reglas de agregación dinámicas en un esquema inmutable.

## Consecuencias Negativas / Riesgos
- Si el mapeo a Nivel 1 carece de la resolución a cuentas Nivel 2 del SAT (por ejemplo desgloses de impuestos regionales específicos), podríamos perder información impositiva relevante de México en el consolidado. Se solventa mapeando todas las cuentas de Nivel 2 SAT a "Custom UUIDs" en el futuro.

## Implementación
El archivo de mapeo oficial para México reside en `localizations/mx/sat_mapping.yaml` y la expansión de Nivel 3 en `core/kontablo_v0_1_mapping.yaml`.
