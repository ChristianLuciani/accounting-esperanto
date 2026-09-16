# Kontablo — Community Preparation & Open Source Maturation Roadmap

> **Creado:** Agosto 2026 · **Branch:** `claude/updated-roadmap`  
> **Propósito:** Hoja de ruta táctica para preparar a Kontablo para colaboración  
> externa genuina, con una estrategia de licenciamiento escalonado que protege  
> la capa comercial de Praxia mientras reduce la fricción para contribuidores.

---

## 🎯 Visión general

Kontablo ya está publicado (v0.3.0, DOI Zenodo, SSRN, GitHub público). El problema
no es "¿está listo para publicar?" — ya se publicó. El problema es **"¿está listo
para aceptar colaboración externa de forma fluida?"**

Este roadmap estructura el trabajo en **tres fases con un gate de licenciamiento**
al final: la licencia escala de BSL 1.1 → Apache 2.0 (o MIT) una vez que el
proyecto tenga comunidad, los spokes académicos estén publicados, y la atribución
al proyecto original esté garantizada.

---

## 🗺️ Fases

```
FASE 1                FASE 2                 FASE 3              🚀 GATE
Community Prep        Spokes Publication      Mature OSS          LICENSE
(infraestructura)     (credibilidad)          (adopción)           CHANGE
                                                                  BSL → Apache/MIT
    │                     │                      │                    │
    ▼                     ▼                      ▼                    ▼
┌─────────┐   ┌──────────────────────┐   ┌──────────────┐   ┌────────────────┐
│ Issues  │   │ Spoke 1: Agentic     │   │ PyPI package  │   │ Requisitos:    │
│ Discus. │   │ Provenance Paper     │   │ Docker image  │   │ ✅ Fase 1 done │
│ CLA bot │   │ Spoke 2: [TBD]       │   │ Website docs  │   │ ✅ Fase 2 done │
│ CODEOWN.│   │ ...                  │   │ Case studies  │   │ ✅ Citabilidad │
│ CI badg │   │                      │   │               │   │    asegurada   │
└─────────┘   └──────────────────────┘   └──────────────┘   └────────────────┘
```

---

## 📋 FASE 1: Community Preparation (Infraestructura)

> **Objetivo:** Que un desarrollador externo que llegue al repo sepa exactamente  
> cómo contribuir, qué issues están disponibles, y qué esperar del proceso.

### Bloque A: Infraestructura de colaboración en GitHub

| # | Tarea | Prioridad | Estado | Notas |
|---|-------|:---------:|:------:|-------|
| A1 | Crear `.github/ISSUE_TEMPLATE/bug_report.yml` | 🔴 Alta | ⬜ Pendiente | Formulario estructurado con pasos para reproducir, versión, componente afectado |
| A2 | Crear `.github/ISSUE_TEMPLATE/jurisdiction_mapping.yml` | 🔴 Alta | ⬜ Pendiente | Template específico para contribuciones de localización: país, fuente primaria, chart name, códigos |
| A3 | Crear `.github/ISSUE_TEMPLATE/feature_request.yml` | 🟡 Media | ⬜ Pendiente | Para sugerencias de API, conectores, herramientas |
| A4 | Configurar **GitHub Discussions** | 🔴 Alta | ⬜ Pendiente | Categorías: Announcements, Q&A, Ideas, Show & Tell, Jurisdictions |
| A5 | Agregar `CODEOWNERS` | 🔴 Alta | ⬜ Pendiente | `* @ChristianLuciani` como reviewer automático de PRs |
| A6 | Crear `SUPPORT.md` | 🟢 Baja | ⬜ Pendiente | Redirigir a Discussions + email para temas comerciales |

### Bloque B: Automatización del CLA

> **Problema actual:** El CLA se firma enviando email manual a `cluciani@gmail.com`.  
> Esto es dealbreaker para contribuidores casuales.

| # | Tarea | Prioridad | Estado | Notas |
|---|-------|:---------:|:------:|-------|
| B1 | Evaluar CLA Assistant (SAP) vs DCO bot | 🔴 Alta | ⬜ Pendiente | CLA Assistant: firma electrónica en PR. DCO: `Signed-off-by:` en commits |
| B2 | Implementar bot de CLA elegido | 🔴 Alta | ⬜ Pendiente | GitHub App o Action que chequee firma en cada PR |
| B3 | Redactar versión simplificada del CLA | 🔴 Alta | ⬜ Pendiente | Versión human-readable de lo que el contributor cede y retiene |
| B4 | Actualizar `CONTRIBUTING.md` con nuevo flujo | 🟡 Media | ⬜ Pendiente | Reflejar el bot, quitar instrucción de email manual |

### Bloque C: Señalización para newcomers

| # | Tarea | Prioridad | Estado | Notas |
|---|-------|:---------:|:------:|-------|
| C1 | Agregar badge de tests al README | 🟡 Media | ⬜ Pendiente | `![Tests](https://img.shields.io/badge/tests-198%20passed-success)` o dinámico vía CI |
| C2 | Agregar badge de coverage | 🟢 Baja | ⬜ Pendiente | Si se configura `coverage.py` + `pytest-cov` |
| C3 | Crear label `good first issue` en GitHub | 🔴 Alta | ⬜ Pendiente | Issues de baja fricción: traducciones, typos, agregar jurisdicción pequeña |
| C4 | Crear milestone `v0.4.0 — Community Ready` | 🟡 Media | ⬜ Pendiente | Agrupar issues de Fase 1 |
| C5 | Escribir `docs/community/ONBOARDING.md` | 🟡 Media | ⬜ Pendiente | Guía para nuevos contribuidores: setup, flujo, dónde empezar |

### Bloque D: Higiene del repositorio

| # | Tarea | Prioridad | Estado | Notas |
|---|-------|:---------:|:------:|-------|
| D1 | Consolidar worktrees de spoke1 activos (merge a `main` lo listo) | 🟡 Media | ⬜ Pendiente | 23 branches de spoke — decidir cuáles se mergean y cuáles se archivan |
| D2 | Mergear `claude/human-oversight-surface` a `main` | 🔴 Alta | ⬜ Pendiente | Contiene feat importante, es el branch actual |
| D3 | Limpiar worktrees obsoletos (cranky-keller, heuristic-khayyam, relaxed-merkle, pensive-snyder) | 🟢 Baja | ⬜ Pendiente | Worktrees detached HEAD que ya cumplieron su propósito |
| D4 | Agregar `CONTRIBUTORS.md` | 🟢 Baja | ⬜ Pendiente | Reconocimiento a contribuidores (vacío inicialmente, se llena solo) |

---

## 📝 FASE 2: Spokes Publication (Credibilidad académica)

> **Objetivo:** Publicar los artículos derivados (spokes) que profundizan aspectos  
> específicos de Kontablo. Esto construye el "moat" de citabilidad antes de  
> relajar la licencia.

### Spokes en preparación

| Spoke | Tema | Branch(es) activo(s) | Estado |
|-------|------|---------------------|--------|
| **Spoke 1** | Agentic Provenance & Audit Trail | `claude/spoke1-agentic-provenance`, `claude/spoke1-continuous-authority`, `claude/spoke1-related-work`, `claude/spoke1-claim-audit`, `claude/spoke1-coresponsibility`, `claude/spoke1-claim-closeout`, `claude/spoke1-crosslink`, `claude/spoke1-figures`, `claude/spoke1-geo-polish`, `claude/spoke1-i3-sharpen`, `claude/spoke1-inference-cost`, `claude/spoke1-license-meta`, `claude/spoke1-protocol-universality`, `claude/spoke1-repro-check`, `claude/spoke1-threat-model` | 🔧 15+ branches activos |
| **Spoke 2** | [Por definir] | — | 💡 Idea |
| **Spoke N** | [Por definir] | — | 💡 Idea |

### Tareas de publicación por spoke

| # | Tarea | Prioridad | Estado |
|---|-------|:---------:|:------:|
| S1 | Finalizar y mergear Spoke 1: Agentic Provenance | 🔴 Alta | ⬜ Pendiente |
| S2 | Publicar Spoke 1 en Zenodo/SSRN/ResearchGate | 🔴 Alta | ⬜ Pendiente |
| S3 | Publicar Spoke 1 como preprint en arXiv | 🟡 Media | ⬜ Pendiente |
| S4 | Definir temas para Spoke 2+ (posibles: Hyperinflation accounting, Multi-jurisdictional consolidation, PQC for financial audit, MCP/A2A/AP2 protocol convergence) | 🟢 Baja | ⬜ Pendiente |

---

## 🌍 FASE 3: Mature OSS & Adoption

> **Objetivo:** Kontablo como herramienta instalable, no solo como paper + repo.

| # | Tarea | Prioridad | Estado | Notas |
|---|-------|:---------:|:------:|-------|
| M1 | Publicar paquete en **PyPI** (`pip install kontablo`) | 🔴 Alta | ⬜ Pendiente | Exponer API + engine como librería instalable |
| M2 | Publicar **Docker image** de la API | 🔴 Alta | ⬜ Pendiente | `docker run -p 8000:8000 christianluciani/kontablo` |
| M3 | Publicar **GitHub Pages** mejorado (website + docs) | 🟡 Media | ⬜ Pendiente | Ya existe en `christianluciani.github.io/accounting-esperanto` |
| M4 | Escribir **casos de estudio** (real-data validation) | 🟡 Media | ⬜ Pendiente | Phase 4: EDGAR, ESEF, UK Companies House |
| M5 | **Anuncio público** (HackerNews, r/Accounting, r/opensource, Lobste.rs) | 🟡 Media | ⬜ Pendiente | Coordinar post-spokes |
| M6 | Buscar **early adopters** (ERPNext community, Odoo community) | 🟢 Baja | ⬜ Pendiente | Los conectores Apache 2.0 ya lo permiten |

---

## 🔑 FASE GATE: Cambio de Licencia

### Estrategia escalonada

Kontablo nace con **BSL 1.1** (Business Source License) con conversión automática a
Apache 2.0 el **18 de junio de 2030** (~4 años desde la primera publicación).
Esta estrategia protege la capa comercial de Praxia durante la fase inicial.

**Propuesta de aceleración condicional:** adelantar la conversión a **Apache 2.0**
(o **MIT**) cuando se cumplan **tres condiciones**:

```
┌─────────────────────────────────────────────────────────────┐
│           GATE DE CAMBIO DE LICENCIA                        │
│                                                             │
│  ✅ CONDICIÓN 1: FASE 1 COMPLETA                            │
│     Infraestructura de comunidad funcionando:               │
│     - Issues/PRs templates activos                          │
│     - CLA bot automatizado                                  │
│     - GitHub Discussions con actividad                      │
│     - CODEOWNERS funcionando                                │
│                                                             │
│  ✅ CONDICIÓN 2: SPOKES PUBLICADOS                          │
│     Al menos 2 spokes publicados en Zenodo/SSRN:            │
│     - Spoke 1: Agentic Provenance                           │
│     - Spoke 2: [Tema de alto impacto]                       │
│     Esto garantiza que el "moat" de citabilidad             │
│     está establecido antes de relajar la licencia.          │
│                                                             │
│  ✅ CONDICIÓN 3: ATRIBUCIÓN GARANTIZADA                     │
│     La licencia de destino (Apache 2.0 o MIT) debe          │
│     incluir un mecanismo que asegure:                       │
│     - Retención de atribución al proyecto original          │
│     - Citabilidad del paper en works derivados              │
│     - NOTICE file obligatorio mencionando a Kontablo        │
│     Ver sección "Atribución mínima" abajo.                  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  ▶ Al cumplirse las 3 condiciones, ejecutar:                │
│     1. PR que reemplaza LICENSE (BSL 1.1 → Apache 2.0/MIT) │
│     2. Actualizar LICENSING.md                              │
│     3. Actualizar README badges                             │
│     4. Announcement en Discussions + redes                  │
│     5. Tag release v1.0.0 con nueva licencia                │
└─────────────────────────────────────────────────────────────┘
```

### Atribución mínima requerida

Independientemente de si la licencia final es **Apache 2.0** o **MIT**, se debe
asegurar que todo uso y derivación mantenga visibilidad del proyecto original.
Estrategias (no mutuamente excluyentes):

| Mecanismo | Cómo funciona | Ventaja |
|-----------|--------------|---------|
| **NOTICE file** (Apache 2.0) | Apache 2.0 requiere que derivados conserven `NOTICE` con atribución | Estándar, legalmente vinculante |
| **CITATION.cff obligatorio** | Incluir en licencia que todo derivado debe preservar `CITATION.cff` intacto | Promueve citabilidad académica |
| **Branding clause suave** | "This product uses Kontablo™. When referencing the ontology in publications, cite: Luciani, C. (2026)..." | No restrictivo, estilo BSD+advertising |
| **Badge requerido en docs** | "Powered by Kontablo" badge con link al repo en documentación de derivados | Visibilidad sin carga legal |

**Recomendación:** Apache 2.0 con NOTICE file + CITATION.cff preservado. Es el camino
de menor fricción legal con máxima retención de atribución. MIT es más simple pero no
tiene mecanismo de NOTICE — requeriría una cláusula adicional.

---

## 📊 Timeline estimado

```
2026 Q3 (Ago-Sep)     FASE 1 — Community Prep
                      ████████████████░░░░░░░░░░░░░░░░░░░░

2026 Q3-Q4 (Sep-Dic)  FASE 2 — Spokes Publication
                      ░░░░░░░░░░░░░░░░████████████████░░░░

2027 Q1-Q2            FASE 3 — Mature OSS & Adoption
                      ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██████

2027 Q2-Q3            GATE — Cambio de Licencia
                      ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░██

2030 Jun 18           Fallback: conversión automática BSL → Apache 2.0
                      (si el gate condicional no se ejecutó antes)
```

---

## 📋 Checkpoint: ¿Qué está bloqueado por BSL+CLA hoy?

| Actividad | ¿Bloqueada por BSL+CLA? |
|-----------|:----------------------:|
| Leer el código | ❌ No |
| Usar internamente en una empresa | ❌ No (Additional Use Grant lo permite) |
| Forkear y experimentar | ❌ No |
| Contribuir jurisdiction mappings | ⚠️ Parcial (CLA requerido, proceso manual) |
| Contribuir código al core | ⚠️ Parcial (CLA + BSL = fricción) |
| Construir integración open-source (ERPNext, Odoo) | ❌ No (conectores son Apache 2.0) |
| Construir producto comercial competidor | 🔴 Sí (requiere licencia comercial) |
| Incluir en distribución Linux/paquete | 🔴 Sí (BSL no es OSI-approved) |

---

## 📝 Notas de sesión

- **Auditoría de madurez:** Agosto 2026, realizada por pi (AionUi coding agent).
- **Puntaje de madurez técnica:** 4.7/5 — excepcional.
- **Puntaje de preparación para comunidad:** 2.0/5 — infraestructura pendiente.
- **Spokes activos:** 23 branches, ~15 para Spoke 1.
- **Worktrees activos:** 19 total, 4 detached HEAD obsoletos.
- **Tests:** 198 passing, 1 skipped, CI claims–evidence gate funcionando.
- **Desacople de NEXOS:** Total — cero referencias a infraestructura local.

---

> **Próximo paso:** Empezar Fase 1, Bloque A — crear templates de issues y configurar  
> GitHub Discussions. Cada ítem de este roadmap debe convertirse en un issue con  
> el label correspondiente y asignarse al milestone `v0.4.0 — Community Ready`.
