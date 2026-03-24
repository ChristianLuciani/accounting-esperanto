# ADR 007: Manejo de Economías Hiperinflacionarias (NIC 29)

## Contexto y Problema

En economías hiperinflacionarias (como el caso de Venezuela), la contabilidad histórica pierde su valor predictivo y de control. Según la NIC 29 (VEN-NIF en Venezuela), los estados financieros deben ser reexpresados usando un índice de precios (IPC/INPC) al cierre del periodo.

El desafío para Kontablo es:
1. ¿Cómo diferenciar partidas monetarias de no monetarias sin romper la estructura de grafo?
2. ¿Cómo manejar las cuentas de "ajuste por inflación" que suelen ser subcuentas en árboles tradicionales?
3. ¿Cómo soportar la dualidad (Histórico vs. Reexpresado) en una misma ontología?

## Decisión Proyectada

1. **Dimensionalidad de Monetariedad:** Añadiremos un campo booleano `is_monetary` al catálogo base. Esto permitirá aplicar algoritmos de reexpresión automáticos a nivel de UUID.
2. **Nodos de Reexpresión Separados:** En lugar de ver el ajuste por inflación como un "parche" de la cuenta padre, utilizaremos UUIDs dedicados para partidas de reexpresión (Serie `2000-0000...`). Esto permite al grafo sumar ambos nodos para obtener el valor reexpresado sin perder la trazabilidad del costo histórico.
3. **Manejo del REMA:** El Resultado por Exposición a la Inflación (o REMA/REPOMET) tendrá un UUID estable en el Nivel 3 para asegurar comparabilidad regional de la pérdida/ganancia por inflación.

## Consecuencias

- **Positivas:** Konsistencia regional para auditorías internacionales, facilidad para auditoría de reexpresión.
- **Negativas:** Mayor complejidad en el algoritmo de agregación regional si se comparan países con vs sin inflación.

---
Estado: Propuesto (Basado en caso Venezuela)
Fecha: 2026-03-11
