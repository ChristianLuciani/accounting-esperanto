# El Problema de los Mil Catálogos: Una Propuesta de Estandarización Contable para Panamá

**Tipo:** Documento de Análisis y Propuesta Técnica
**Versión:** 0.1.0-draft
**Fecha:** Marzo 2026
**Estado:** Borrador para Revisión
**Dirigido a:** Contadores Públicos Autorizados (CPA), Firmas de Auditoría, Directores Financieros (CFOs), y la Superintendencia del Mercado de Valores (SMV) de Panamá.

---

## Resumen Ejecutivo

Panamá tiene una paradoja contable: es una de las plazas financieras más sofisticadas de América Latina —con zonas libres, banca offshore, holding companies y un sector de servicios financieros internacionales de primer nivel— pero no dispone de un catálogo de cuentas estándar que unifique cómo se clasifica la información contable a lo largo de sus miles de empresas.

El resultado es predecible: cada firma construye su propio "idioma contable". Un mismo concepto —digamos, los ingresos de una exportación libre de impuesto de renta— puede llamarse "Ventas Externas", "Ingresos Off-Shore", "Exportaciones Netas" o "Revenue Foreign" dependiendo de quién configuró el ERP hace diez años. Cuando ese mismo dato debe reportarse ante la DGI en la Declaración Jurada de Renta, o ante la SMV en los estados financieros auditados, el contador asume la carga de hacer una "traducción" manual, cada año, propensa a errores, y que consume semanas de trabajo.

**Kontablo** es una propuesta de ontología contable abierta que resuelve este problema sin obligar a ninguna empresa a cambiar su catálogo de cuentas interno. Funciona como una capa de traducción universal: cada cuenta —sin importar su nombre local— recibe un identificador único e inmutable (UUID) que permite a cualquier sistema leer, consolidar, y reportar la información sin ambigüedad. Para el contador, esto significa menos horas de conciliación, menos errores en las declaraciones, y más tiempo para el análisis que realmente agrega valor a sus clientes.

---

## 1. El Contexto Contable Panameño: Fortalezas y Vacíos

### 1.1 Una Economía que Opera en Múltiples Regímenes

Panamá es el único país de la región que alberga simultáneamente:

- **Régimen Territorial de Renta:** Solo tributan los ingresos de *fuente panameña*. Los ingresos de fuente extranjera están exentos del Impuesto sobre la Renta (ISR).
- **Zona Libre de Colón (ZLC):** Operaciones de importación-reexportación con tratamiento fiscal especial.
- **Centros de Coordinación y Servicios Multinacionales (SEM/EMMA):** Empresas multinacionales con incentivos fiscales diferenciados.
- **Sector Bancario Internacional:** Sujeto a las normas prudenciales de la Superintendencia de Bancos (SBP) y a los estándares internacionales de auditoría.
- **Empresas Offshore Holding:** Constitución legal sin actividad territorial, cuya contabilidad debe mantener trazabilidad para due diligence y reportes de UIF (Unidad de Inteligencia Financiera).

Esta riqueza de regímenes es una fortaleza competitiva de Panamá, pero exige que el sistema contable sea **multi-dimensional**: el mismo activo o ingreso puede tener una naturaleza diferente dependiendo del lente fiscal bajo el que se observe.

### 1.2 Las Normas Vigentes: NIIF y PCGA en Convivencia

La legislación panameña, a través del Decreto 32 de 2011 (reformado) y las resoluciones de la Junta Técnica de Contabilidad, establece la adopción obligatoria de las **Normas Internacionales de Información Financiera (NIIF / IFRS)** para las entidades de interés público (cotizadas, bancos, aseguradoras). Las PYMES y empresas privadas no cotizadas pueden optar por las **NIIF para PYMES** o los Principios de Contabilidad Generalmente Aceptados de Panamá (PCGA-PA).

Lo que **no existe** en Panamá es un equivalente al *Código Agrupador del SAT* de México (Anexo 24), al *Plan Único de Cuentas (PUC)* de Colombia, o al *PCGE* del Perú: un catálogo de cuentas numerado que el ente regulador exija adoptar como estructura base para todas las empresas.

### 1.3 El Resultado: El Ecosistema de los Mil Catálogos

Sin un catálogo estándar, el mercado panameño ha desarrollado espontáneamente decenas de variantes. Las firmas de contabilidad tienen sus propias plantillas en Peachtree (Sage 50), QuickBooks, o SAP. Los bancos usan estructuras del Comité de Basilea. Las empresas del sector libre usan catálogos heredados de sus matrices en EE.UU., España, o Colombia.

La consecuencia directa para el profesional contable es que **el mapeo entre el catálogo interno y el formato de reporte regulatorio es un trabajo manual, artesanal, y no transferible**: cuando el contador renuncia, el conocimiento de "cómo traducir estas cuentas al formulario de la DGI" se va con él.

---

## 2. Los Desafíos que Enfrenta el Profesional Contable en Panamá

Este capítulo describe los problemas concretos del día a día que son consecuencia directa de la ausencia de estandarización. No son problemas de regulación ni de tecnología: son problemas de la **profesión contable** que impactan la calidad del trabajo y la carga sobre los profesionales.

### 2.1 La Declaración Jurada de Renta: El Mapa No Coincide con el Territorio

El formulario de Declaración Jurada de Renta (Formulario 930 y sus variantes) que exige la DGI organiza los ingresos y gastos en categorías específicas:
- Ingresos gravables de fuente panameña
- Ingresos exentos
- Costos y gastos deducibles
- Gastos no deducibles
- Créditos fiscales (ITBMS)

Sin embargo, la balanza de comprobación exportada del ERP de una empresa típica listaría cientos de cuentas con nombres internos como "Sales - Local Q1", "Revenue - Export ZLC", "Admin Expenses - MX HQ Recharged", o "Professional Fees - Retainer". La tarea del contador es mapear manualmente cada línea a la categoría correcta del formulario. **Este proceso, repetido para cada cliente y cada año fiscal, consume entre el 30% y el 50% del tiempo total de cierre.**

### 2.2 El ITBMS: Tres Tasas, Infinitas Interpretaciones

El Impuesto de Transferencia de Bienes Corporales Muebles y la Prestación de Servicios (ITBMS) se aplica en tres tasas diferenciadas:

| Categoría | Tasa |
|---|---|
| Tasa General (bienes y servicios generales) | 7% |
| Bienes de Lujo (joyas, autos de lujo, yates) | 10% |
| Bebidas Alcohólicas y Tabaco | 15% |

Además, ciertos contribuyentes son **agentes de retención**, obligados a retener el 50% del ITBMS que pagan a proveedores no domiciliados, y a remitir ese monto directamente a la DGI.

El problema: en la mayoría de los ERPs configurados en Panamá, las tres tasas del ITBMS y las retenciones comparten una sola cuenta contable —o a veces dos. En el momento de preparar la declaración mensual de ITBMS, el contador debe desagregar manualmente los saldos, usando notas en Excel, para identificar qué porción corresponde al 7%, cuál al 10%, y qué monto fue retenido a proveedores del exterior.

### 2.3 La Territorialidad: El Riesgo Silencioso

El principio de renta territorial es la joya fiscal de Panamá para las empresas multinacionales. Pero también es su mayor fuente de riesgo en una auditoría de la DGI.

El error más común: **incluir ingresos de fuente extranjera en la base gravable local** (pagando impuesto de más) o, peor, **incluir gastos vinculados a ingresos exentos como deducibles** (pagando menos de lo correcto y quedando expuesto a sanciones). Ambos errores son difíciles de detectar cuando la información vive en un único árbol de cuentas donde "ingresos" es "ingresos" sin distinción de territorialidad.

### 2.4 La Consolidación Regional: Cuando el Cliente Tiene Filiales en Tres Países

Para los grupos empresariales que operan en Panamá, México, y Colombia simultáneamente, el problema se multiplica. El CFO del holding quiere un estado financiero consolidado en IFRS. El contador panameño tiene una balanza en Sage 50 con nombres en inglés. El contador mexicano tiene una balanza del SAT en español. El contador colombiano tiene el PUC en su propia estructura.

Consolidar estas tres fuentes requiere hoy semanas de trabajo en Excel, con el riesgo de que una columna copiada incorrectamente distorsione el resultado. En muchos grupos, este proceso se terceriza a firmas de Big Four con costos de miles de dólares por cierre trimestral.

---

## 3. La Solución Kontablo: Una Capa de Traducción Sin Romper Nada

Kontablo no propone que las empresas panameñas desechen sus catálogos actuales. No sugiere que la DGI emita un decreto imponiendo nuevas cuentas. Su propuesta es más sutil y más poderosa: **añadir una columna invisible que lo une todo.**

### 3.1 El UUID: El Traductor Universal

Un UUID (Identificador Único Universal) es un código inmutable, de 36 caracteres, que identifica un concepto contable sin importar cómo se llame en ningún sistema en particular. Es como el número de cédula de una persona: no importa si le dicen "Carlos", "Carlitos", o "Mr. García" —su cédula es siempre la misma y lo identifica de manera única.

```
Tu cuenta en Sage 50:  "4-01-01 Ventas Locales Gravadas"
UUID Kontablo:          00000000-0000-4000-8000-000000000301
Significado universal:  "Ingreso Doméstico Sujeto a Impuesto Territorial"
```

Cuando tu catálogo de cuentas tiene un UUID asignado a cada línea, cualquier sistema —un reporte, una declaración, o un análisis— puede leer ese UUID y saber exactamente de qué tipo de ingreso se trata, sin depender del nombre textual de la cuenta.

### 3.2 El Modelo de Grafo: Por Qué el Árbol Tradicional Falla

La contabilidad convencional organiza las cuentas en un árbol: Activo → Activo Corriente → Efectivo → Bancos → Cuenta Corriente BAC. Esta estructura es intuitiva pero **engañosamente rígida**: una cuenta de "Impuestos por Pagar" puede ser al mismo tiempo un Pasivo Corriente (en el Balance), un Gasto Deducible (en la Renta), y una Obligación Mensual de Reportar (en el ITBMS). En un árbol, existe en un solo lugar. En un grafo, existe en todos los contextos relevantes simultáneamente.

Kontablo usa una estructura de grafo donde cada cuenta tiene múltiples dimensiones:

| Dimensión | Ejemplo para "IVA/ITBMS Acreditable" |
|---|---|
| Tipo de Estado | Activo Corriente (Balance) |
| Naturaleza Fiscal | Crédito Fiscal ante DGI |
| Liquidez | Corriente |
| Territorialidad | Local / Par con ingreso gravable |

El contador no tiene que recordar estas reglas: están codificadas en el UUID. El sistema las aplica automáticamente.

### 3.3 El Mapeo No Obliga: La Regla de la Adición

Kontablo es **aditivo, no sustitutivo**. Una empresa panameña que adopta Kontablo no debe cambiar ningún nombre de cuenta en su ERP, no debe migrar su base de datos, no debe afectar ningún proceso de cierre existente. Solo debe:

1. Descargar la capa de mapeo correspondiente (`localizations/pa/dgi_mapping.yaml`).
2. Asignar el UUID correcto a cada código de cuenta de su catálogo interno (una vez, en una hoja de Excel o mediante un script).
3. A partir de ese momento, cualquier exportación de balanza puede ser automáticamente "traducida" hacia los formatos DGI, SMV, o IFRS sin intervención manual adicional.

---

## 4. Casos de Uso Frecuentes para el Contexto Panameño

### 4.1 Caso de Uso 1: Preparación de la Declaración Jurada de Renta

**Antes de Kontablo:**
El contador exporta la balanza de comprobación al cierre de diciembre. Abre el formulario de la DGI. Con el balance a la vista en una columna y el formulario en otra, va línea a línea asignando cada cuenta al renglón correcto. Para una empresa con 150 cuentas, este proceso toma entre 2 y 5 días de trabajo. Los errores en la clasificación de gastos deducibles son comunes y frecuentemente detectados en revisiones posteriores.

**Con Kontablo:**
Al cerrar el ejercicio, el sistema lee el UUID de cada cuenta. Suma automáticamente todos los saldos con el UUID de "Ingreso Territorial Gravable" y los asigna al Renglón A del formulario. Los gastos con UUID de "Gasto No Deducible" son tabulados por separado. El borrador de la declaración se genera en minutos. El contador dedica ese tiempo al análisis: ¿hay créditos fiscales no aplicados? ¿Se están deduciendo los gastos correctos?

### 4.2 Caso de Uso 2: Separación del ITBMS por Tasas

**Antes de Kontablo:**
Al preparar la declaración mensual de ITBMS (Formulario 430), el contador revisa el libro auxiliar de "ITBMS por Pagar" y clasifica manualmente las transacciones buscando el texto de la descripción para distinguir el 7%, el 10%, y el 15%. En empresas con alto volumen de transacciones, usa tablas pivot de Excel para hacer esta separación. Si el proveedor olvidó poner la descripción correcta al registrar la factura, la clasificación es un estimado.

**Con Kontablo:**
Al momento de registrar la factura, el UUID del pasivo de ITBMS indica la tasa exacta:
- UUID `00000000-...0203` → ITBMS 7% Trasladado
- Los de lujo → UUID distinto para 10%
- Las retenciones → UUID `00000000-...0204`

El "Formulario 430" se genera directamente desde el sistema, con los totales correctos por tasa. El error de clasificación es prácticamente imposible.

### 4.3 Caso de Uso 3: Separación de Territorialidad para el Holding Regional

**Antes de Kontablo:**
El CFO del holding solicita en enero el paquete de reporte consolidado de sus tres filiales (Panamá, México, Colombia). El equipo panameño entrega una balanza en Sage 50 exportada a XLS. El equipo de consolidación pasa tres semanas fusionando y recategorizando cuentas para que sean comparables. Se descubren diferencias de criterios que requieren ajustes.

**Con Kontablo:**
Cada filial entrega su balanza con los UUIDs mapeados. El sistema de consolidación lee tres archivos JSON con la misma estructura de UUIDs universales, suma los saldos en segundos, y entrega el estado  consolidado. Las diferencias de nomenclatura local han desaparecido porque el UUID de "Efectivo y Bancos" es el mismo independientemente de si en Panamá se llama "Caja y Bancos", en México "Bancos (SAT 102)", o en Colombia "Efectivo PUC 11".

---

## 5. Hoja de Ruta para la Adopción en Panamá

La adopción de Kontablo se propone como un proceso de tres etapas no invasivas, aplicables a firmas de contabilidad o equipos de finanzas corporativas:

### Etapa 1: Mapeo Interno (Semana 1-2)
- Exportar el catálogo de cuentas actual desde el ERP (Sage 50, QuickBooks, SAP) a Excel.
- Usar la tabla de mapeo `localizations/pa/dgi_mapping.yaml` para asignar un UUID a cada cuenta (proceso guiado en la *Guía del CPA Panameño*).
- Resultado: una "roseta de traducción" que permanece estática a menos que se creen nuevas cuentas.

### Etapa 2: Adopción del "Default Tree Panama Kontablo" (Mes 1.5):
  - Implementación de árboles de cuentas de referencia precargados con UUIDs para nuevas empresas o departamentos.
  - Uso de plantillas prediseñadas para Sage 50 y QuickBooks que ya vienen con el "gen" de Kontablo instalado.
### Etapa 3: Integración con MicroSaaS de Mapeo Asistido (Mes 3-4):
  - Uso de la API de Kontablo para reducir la carga manual de mapeo mediante agentes de IA.
  - Conexión nativa con ERPs locales para sincronización de balanzas en tiempo real.
### Etapa 4: Validación y Auditoría (Continuo):
  - Uso de los Default Trees como base para tests automatizados de integridad contable.
  - Facilitar el trabajo de la firma externa mediante el acceso a la capa de mapeo universal.

---

## 6. Referencias y Base Normativa

- **Decreto Ejecutivo N° 32** (Agosto 2021, Ministerio de Economía y Finanzas de Panamá) — Adopción de NIIF.
- **Código Fiscal de la República de Panamá**, Libro IV, Título I — Impuesto sobre la Renta, principio de territorialidad.
- **Ley 76 de 1976** (y reformas) — Impuesto de Transferencia de Bienes Corporales Muebles (ITBMS).
- **Resolución 201-3724** (DGI) — Sistema de Facturación Electrónica (SFEP).
- **IFRS Foundation (IASB)** — IFRS Taxonomy 2024.
- **XBRL International** — Taxonomía de Etiquetado Contable Extensible.
- **McCarthy, W. E.** (1982). *The REA Accounting Model: A Generalized Framework for Accounting Systems in a Shared Data Environment.* The Accounting Review, 57(3), 554–578.
- **Kontablo MANIFESTO.md** — Principios ontológicos del estándar universal.
- **Kontablo ADR-001** — Decisión de arquitectura: uso de grafo en lugar de árbol.

---

*Documento producido en el marco del proyecto de investigación Accounting Esperanto / Kontablo v0.1.0. Licencia MIT. Para sugerencias y correcciones, abrir un Issue en el repositorio del proyecto.*
