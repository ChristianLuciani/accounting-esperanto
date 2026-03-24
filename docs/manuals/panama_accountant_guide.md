# Guía de Mapeo Kontablo para el CPA Panameño: De Su Catálogo Actual a los Reportes DGI Sin Complicaciones

**Tipo:** Manual Práctico / Tutorial Paso a Paso
**Versión:** 0.1.0-draft
**Fecha:** Marzo 2026
**Para:** Contadores Públicos Autorizados (CPA) y asistentes contables que trabajan con Sage 50 (Peachtree), QuickBooks u otras herramientas en Panamá.

---

## Bienvenida: Por Qué Existe Esta Guía

Si usted trabaja como contador en Panamá, probablemente conoce de memoria este ciclo:

1. El año fiscal cierra. Usted exporta la balanza de comprobación de Peachtree o QuickBooks a Excel.
2. Abre el formulario de la DGI en paralelo.
3. Durante días — o semanas — traslada cifras de una columna a otra, recordando qué cuenta interna corresponde a qué línea del formulario de renta, cuánto del "ITBMS por Pagar" es al 7% y cuánto es retención de agentes, cuáles gastos son deducibles y cuáles no lo son bajo el régimen territorial.
4. Al terminar, rezar para que los totales cuadren a la primera.

Este proceso no es culpa de usted. Es une consecuencia estructural de que **en Panamá no existe un plan de cuentas estándar** que conecte directamente su software de contabilidad con los formularios de la DGI y la SMV. Usted lleva años construyendo ese puente de forma manual, con todo el conocimiento en su cabeza y en sus hojas de Excel.

**Kontablo es ese puente, hecho oficial y transferible.** Esta guía le enseña, paso a paso, cómo asignar un identificador universal a cada cuenta de su catálogo actual — sin cambiar ningún nombre, sin migrar ningún dato, sin afectar ningún proceso de cierre. Una vez hecho este trabajo de una sola vez, sus reportes tributarios podrán generarse automáticamente, y su conocimiento dejará de estar solo en su memoria para estar documentado en el sistema.

---

## Antes de Empezar: Conceptos Clave en 3 Minutos

Antes del primer paso práctico, necesita entender tres conceptos. Son simples.

### ¿Qué es un UUID?

Un UUID (Identificador Único Universal) es simplemente un número de identificación que **nunca cambia** y **no depende del nombre** que usted le haya puesto a su cuenta. Piénselo como el número de cédula de sus cuentas contables.

Su cliente puede llamar a su cuenta de ventas locales: *"4-01-01 Ventas Locales"* o *"Revenue - Sales Panama"* o *"Income - Local Q1"*. El nombre no importa para el sistema tributario, pero el concepto sí: son ingresos de fuente panameña sujetos a ISR. El UUID de Kontablo para ese concepto es siempre el mismo:

```
00000000-0000-4000-8000-000000000301
```

Cuando su sistema ve ese UUID, sabe automáticamente que esa cifra va al renglón de "Ingresos Gravables de Fuente Panameña" en la declaración de renta.

### ¿Tengo que cambiar mis cuentas en Peachtree?

**No.** Usted no toca nada en su ERP. El mapeo vive fuera del sistema: es una tabla de equivalencias (puede ser un Excel, un YAML, o un campo adicional en su base de datos) que dice: *"Cuando aparezca el código 4-01-01 en la balanza, su UUID es 000...-0301"*.

### ¿Es esto un software nuevo que debo instalar?

No es un software. Kontablo es un **estándar abierto** (como el IBAN bancario, o como el código de aeropuerto IATA). Usted puede adoptarlo con Excel si quiere, o integrarlo en herramientas más avanzadas después.

---

## Sección 1: El Mapa de Sus Cuentas — Preparación del Catálogo

### Paso 1.1: Exportar Su Catálogo de Cuentas Actual

En **Sage 50 / Peachtree**, vaya a:
`Listas → Plan de Cuentas → Exportar a Excel`

En **QuickBooks**, vaya a:
`Reportes → Contabilidad → Plan de Cuentas (Lista) → Exportar a XLS`

El resultado es una hoja de Excel con al menos tres columnas: **Código**, **Nombre de Cuenta**, y **Tipo** (Activo, Pasivo, etc.).

### Paso 1.2: Añadir la Columna UUID

Añada una nueva columna en esa hoja llamada `kontablo_uuid`. Al final de esta guía encontrará la tabla de mapeo completa. Su tarea es rellenar esa columna usando la tabla de equivalencias de la Sección 5.

**Ejemplo después de completar el mapeo:**

| Código | Nombre (Peachtree) | Tipo | kontablo_uuid |
|---|---|---|---|
| 1-01-01 | Caja General | Activo | 00000000-0000-4000-8000-000000000101 |
| 1-02-01 | Bancos - Cuenta BAC USD | Activo | 00000000-0000-4000-8000-000000000102 |
| 2-05-01 | ITBMS por Pagar 7% | Pasivo | 00000000-0000-4000-8000-000000000203 |
| 4-01-01 | Ventas Locales Gravadas | Ingresos | 00000000-0000-4000-8000-000000000301 |
| 4-02-01 | Ingresos Zona Libre | Ingresos | 10000000-0000-4000-8000-000000000302 |

---

## Sección 2: Ingresos — La Diferencia que Define su Renta

La distinción más crítica en la declaración de renta panameña es la **territorialidad del ingreso**. Esta sección le explica cómo mapearla correctamente.

### 2.1 Ingresos de Fuente Panameña (Gravables)

Son los ingresos que provienen de actividades económicas realizadas dentro del territorio de la República de Panamá. Ejemplos:

- Ventas de productos al consumidor final dentro de Panamá.
- Prestación de servicios a clientes con domicilio o actividad en Panamá.
- Arrendamientos de bienes inmuebles ubicados en Panamá.
- Intereses de préstamos otorgados a personas o empresas con actividad en Panamá.

**UUID Kontablo:** `00000000-0000-4000-8000-000000000301` → "Domestic Revenue (Subject to territorial tax)"

> ⚠️ **Atención práctica:** Muchos contadores colocan en esta categoría los honorarios cobrados por servicios de asesoría a un cliente extranjero cuando el *servicio* se prestó físicamente en Panamá. En ese caso, el ingreso sí es de fuente panameña aunque el cliente esté en otro país. La DGI ha sostenido este criterio en múltiples resoluciones de consulta.

### 2.2 Ingresos de Fuente Extranjera (Exentos de ISR)

Son los ingresos que provienen de actividades fuera del territorio panameño. Bajo el principio de territorialidad del Código Fiscal panameño, estos ingresos **no pagan ISR en Panamá** aunque la empresa esté domiciliada aquí.

Ejemplos comunes en empresas panameñas:
- Dividendos provenientes de acciones de empresas extranjeras.
- Intereses de inversiones en el exterior.
- Ganancias de capital por venta de activos en el exterior.
- Ingresos de SEM/EMMA por servicios prestados a entidades fuera de Panamá.

**UUID Kontablo:** `10000000-0000-4000-8000-000000000302` → "Foreign/Offshore Revenue (Non-territorial)"

> ⚠️ **El riesgo de confundirlos:** Si ingresos exentos se incluyen en la base gravable, la empresa paga impuesto que no debe (error favorable a la DGI, pero no es eficiencia). Más grave: si gastos vinculados a ingresos exentos se incluyen como deducibles, la empresa reduce su base indebidamente y está expuesta a ajustes, multas, e intereses en una auditoría.

### 2.3 Regla Práctica: La Pregunta del Nexo

Cuando no sepa si un ingreso es de fuente panameña o extranjera, hágase esta pregunta: **¿El servicio o bien que generó este ingreso se entregó, realizó, o consumió en el territorio de la República de Panamá?**

- Si la respuesta es **Sí** → UUID `...000301` (gravable)
- Si la respuesta es **No** → UUID `...000302` (exento)

---

## Sección 3: El ITBMS — Tres Tasas, Un Sistema

El ITBMS es el impuesto de consumo panameño (similar al IVA de otros países). Su característica principal es que existe en **tres tasas diferenciadas** que deben reportarse por separado en el Formulario 430 mensual.

### 3.1 Mapa de Tasas y UUIDs

| Tasa | Aplica a | UUID Pasivo (trasladado) | UUID Activo (acreditable) |
|---|---|---|---|
| **7%** | Bienes y servicios en general | `00000000-...0203` | `10000000-...0001` |
| **10%** | Bienes de lujo (joyas, yates, vehículos >$60,000) | *(UUID en desarrollo)* | *(UUID en desarrollo)* |
| **15%** | Bebidas alcohólicas y tabaco | *(UUID en desarrollo)* | *(UUID en desarrollo)* |
| **Retención 50%** | Pagos a proveedores no domiciliados | `00000000-...0204` | — |

> 📌 **Recomendación inmediata:** Si actualmente tiene una sola cuenta de "ITBMS por Pagar" en su ERP, esto es el momento de dividirla en sub-cuentas por tasa. El trabajo de clasificación que usted hace hoy en Excel cada mes se vuelve automático cuando las cuentas tienen UUIDs distintos por tasa.

### 3.2 El Agente de Retención: Qué Contabilizar y Cómo

Si su empresa está designada como Agente de Retención de ITBMS (aplica a empresas grandes o a quienes contratan servicios de no domiciliados), al pagar a un proveedor que no está domiciliado en Panamá debe:

1. **Retener el 50%** del ITBMS de la factura.
2. **Registrar el pasivo** de esa retención separado del ITBMS que usted misma genera.
3. **Remitir la retención** a la DGI mensualmente.

**Contabilización correcta (con UUIDs):**

```
Débito:  Cuentas por Pagar Proveedor        [UUID: ...000206]  $1,000.00
Débito:  ITBMS Acreditable 7%               [UUID: ...000001]  $    35.00  (50% del ITBMS)
 Crédito: Banco                                                 $1,035.00
 Crédito: Retención ITBMS a Remitir         [UUID: ...000204]  $    35.00
```

---

## Sección 4: Gastos — La Clave de la Declaración de Renta

La clasificación correcta de los gastos es el factor que más frecuentemente genera ajustes en las auditorías de la DGI. La diferencia entre un gasto "deducible" y uno "no deducible" puede representar miles de dólares en impuesto.

### 4.1 ¿Qué Hace Deducible a un Gasto? La Regla General

El Código Fiscal panameño (Artículo 694) establece que son deducibles los gastos que sean:
1. **Necesarios** para producir la renta gravable.
2. **Causados** durante el año fiscal (independientemente de si se pagaron en efectivo).
3. **Debidamente documentados** con factura o comprobante válido.

Resumiendo: si el gasto existe y es necesario para que la empresa genere los ingresos gravables, es deducible. Si el gasto está vinculado a la generación de ingresos *exentos*, no es deducible frente a la renta territorial.

**UUID para gastos deducibles:** `00000000-0000-4000-8000-000000000501`
**UUID para gastos no deducibles:** `10000000-0000-4000-8000-000000000502`

### 4.2 Gastos Comunes y su Clasificación

| Tipo de Gasto | Deducible | No Deducible | Nota |
|---|---|---|---|
| Sueldos y salarios del personal en Panamá | ✅ | — | Siempre y cuando estén vinculados a la actividad gravable |
| Cuotas de seguro social patronal (CSS) | ✅ | — | Obligatoria, siempre deducible |
| Alquiler de oficina en Panamá | ✅ | — | Debe existir contrato registrado |
| Gastos de representación | ✅ (con límite) | ⚠️ (exceso) | Deducible hasta el 1% de los ingresos brutos |
| Gastos de viaje al exterior | ✅ (parcial) | ⚠️ | Solo la porción vinculada a la actividad gravable |
| Multas y sanciones de la DGI | — | ✅ | Nunca deducibles |
| Dividendos pagados | — | ✅ | No son gasto, son distribución de utilidades |
| Depreciación de activos usados en actividad gravable | ✅ | — | Según tabla de la DGI |
| Intereses de préstamos para inversión en el exterior | ⚠️ | ✅ (mayoritariamente) | El destino del préstamo determina la deducibilidad |

### 4.3 El Workpaper del Contador: Usando UUIDs para Automatizar el Análisis

Con los UUIDs correctamente asignados, al fin de año usted puede generar automáticamente este resumen:

```
RESUMEN FISCAL - EJERCICIO 202X
================================
Ingresos Gravables (UUID ...0301):          $850,000.00
Ingresos Exentos   (UUID ...0302):          $150,000.00
Total Ingresos:                           $1,000,000.00

Gastos Deducibles  (UUID ...0501):          $320,000.00
Gastos No Deducibles (UUID ...0502):         $15,000.00
------
Renta Neta Gravable:                        $530,000.00
ISR Estimado (25%):                         $132,500.00
```

Este resumen, que hoy le toma días construir desde su balanza, se genera en minutos cuando cada cuenta tiene su UUID.

---

## Sección 5: Tabla de Mapeo — Su Hoja de Referencia

Esta es la tabla que usará para completar la columna `kontablo_uuid` en su catálogo exportado (Paso 1.2).

### Activos

| Concepto de Cuenta | UUID Kontablo | UUID (formato corto) |
|---|---|---|
| Caja (billetes y monedas) | `00000000-0000-4000-8000-000000000101` | `...0101` |
| Bancos (cuentas corrientes y de ahorro) | `00000000-0000-4000-8000-000000000102` | `...0102` |
| Inversiones a corto plazo | `00000000-0000-4000-8000-000000000103` | `...0103` |
| Cuentas por Cobrar Clientes | `00000000-0000-4000-8000-000000000104` | `...0104` |
| Otras Cuentas por Cobrar | `00000000-0000-4000-8000-000000000105` | `...0105` |
| Créditos Fiscales DGI (ITBMS Acreditable) | `10000000-0000-4000-8000-000000000001` | `10...001` |
| Inventarios | `00000000-0000-4000-8000-000000000106` | `...0106` |
| Gastos Prepagados | `00000000-0000-4000-8000-000000000108` | `...0108` |

### Pasivos

| Concepto de Cuenta | UUID Kontablo | UUID (formato corto) |
|---|---|---|
| Proveedores (por pagar comerciales) | `00000000-0000-4000-8000-000000000201` | `...0201` |
| Préstamos Bancarios a Corto Plazo | `00000000-0000-4000-8000-000000000202` | `...0202` |
| ITBMS Trasladado por Pagar (7%, 10%, 15%) | `00000000-0000-4000-8000-000000000203` | `...0203` |
| Retenciones ITBMS a Remitir (Agente) | `00000000-0000-4000-8000-000000000204` | `...0204` |

### Ingresos

| Concepto de Cuenta | UUID Kontablo | UUID (formato corto) |
|---|---|---|
| Ingresos Locales Gravables (fuente panameña) | `00000000-0000-4000-8000-000000000301` | `...0301` |
| Ingresos Exentos / Offshore / Extranjeros | `10000000-0000-4000-8000-000000000302` | `10...302` |
| Ingresos Financieros (intereses locales) | `00000000-0000-4000-8000-000000000402` | `...0402` |

### Gastos

| Concepto de Cuenta | UUID Kontablo | UUID (formato corto) |
|---|---|---|
| Gastos Deducibles de Renta Territorial | `00000000-0000-4000-8000-000000000501` | `...0501` |
| Gastos No Deducibles | `10000000-0000-4000-8000-000000000502` | `10...502` |
| Costos de Ventas / Costo de Servicio | `00000000-0000-4000-8000-000000000404` | `...0404` |

---

## Sección 6: Validación Final — Antes de Declarar

Una vez complete el mapeo de su catálogo, recomendamos ejecutar esta lista de verificación antes de presentar cualquier declaración:

### ✅ Lista de Verificación (Checklist)

- [ ] **Todos los ingresos tienen UUID asignado.** Ninguna cuenta de ingreso debe quedar sin mapear.
- [ ] **Los ingresos exentos suman con el UUID correcto (10...302).** Verifique que no haya ingresos gravables clasificados como exentos o viceversa.
- [ ] **El saldo de ITBMS por Pagar cuadra con el libro auxiliar de facturas emitidas.** Compare la suma de todos los UUIDs de ITBMS pasivo contra las facturas del período.
- [ ] **Los créditos fiscales de ITBMS (UUID 10...001) corresponden a facturas de compra con ITBMS.** Solo aplica cuando el gasto es deducible y está vinculado a la actividad gravable.
- [ ] **No hay gastos con UUID de "No Deducibles" (10...502) incluidos en la renta gravable.** Esta es la causa más común de ajustes en auditorías.
- [ ] **La suma de todos los UUIDs de ingresos coincide con el total de ingresos de la balanza.** Sin fugas ni duplicados.

---

## Glosario Rápido

| Término | Definición rápida |
|---|---|
| **UUID** | Identificador Único Universal. El "número de cédula" de una cuenta contable. Nunca cambia. |
| **Territorialidad** | Principio fiscal panameño: solo pagan ISR los ingresos de *fuente panameña*. |
| **ITBMS** | Impuesto de Transferencia de Bienes Corporales Muebles y Prestación de Servicios. El "IVA" panameño, a tasa del 7%, 10%, o 15%. |
| **Agente de Retención** | Empresa designada por la DGI que debe retener parte del impuesto al pagar a ciertos proveedores. |
| **UUID Kontablo** | Un UUID estándar asignado por la ontología Kontablo a un concepto contable universal. |
| **Crédito Fiscal** | Saldo de ITBMS pagado en compras que puede descontarse del ITBMS cobrado en ventas. |
| **Grafo Contable** | Estructura donde una cuenta puede pertenecer a múltiples categorías simultáneamente, a diferencia del árbol jerárquico tradicional. |

---

## Preguntas Frecuentes

**P: ¿Qué hago si mi empresa tiene actividad mixta (gravable y exenta)?**
R: Debe prorratear los costos y gastos compartidos. La DGI acepta el prorrateo por ingreso (gastos deducibles = gastos totales × ingresos gravables / ingresos totales). Con el mapeo de UUIDs, este cálculo se hace automáticamente.

**P: ¿Puedo usar esta guía si estoy en QuickBooks en vez de Peachtree?**
R: Sí. El mapeo de UUIDs es independiente del software. El proceso de exportar el catálogo a Excel y agregar la columna UUID funciona igual en cualquier ERP.

**P: ¿Qué pasa si abro una cuenta nueva a mitad de año?**
R: Al crear la cuenta nueva en su ERP, asigne inmediatamente su UUID usando la tabla de esta guía. No hay que esperar al cierre del año.

**P: ¿El CPA ha presentado estas UUIDs ante la DGI?**
R: Los UUIDs son internos a su sistema contable y a cualquier herramienta de reporte que use. No se presentan directamente ante la DGI. Son una herramienta de organización interna que facilita la preparación de los formularios que sí se presentan.

---

*Manual producido en el marco del proyecto Accounting Esperanto / Kontablo v0.1.0. Licencia MIT. Para reportar errores o sugerir mejoras, abrir un Issue en el repositorio del proyecto.*
