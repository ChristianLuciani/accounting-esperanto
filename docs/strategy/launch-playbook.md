# Launch Playbook — Kontablo v0.1.0

> **STATUS: OPERATIVO.** Listo para ejecución. Release day target: a confirmar.
> Autor: Christian Luciani — cluciani@gmail.com — ORCID 0000-0002-6955-5384

---

## Secuencia del release day (orden estricto)

### T-0: Zenodo GitHub integration (una vez, antes del tag)
1. Ir a https://zenodo.org/account/settings/github/
2. Activar el toggle en `ChristianLuciani/accounting-esperanto`
3. Confirmar que aparece el webhook en la configuración del repo

### T+0: GitHub release (trigger de Zenodo)
```bash
gh release create v0.1.0 \
  --title "Kontablo v0.1.0 — Initial public release" \
  --notes-file docs/strategy/release-notes-v0.1.0.md \
  --latest
```
→ Zenodo asigna DOI automáticamente (~5 min).

### T+15min: Actualizar BibTeX y CITATION.cff con DOIs reales
- Abrir https://zenodo.org/deposit → copiar DOI asignado
- Editar `docs/papers/drafts/kontablo_preprint_modular.tex`: reemplazar `howpublished={Preprint v1.75}` por el DOI y URL de Zenodo
- Editar `CITATION.cff`: reemplazar `notes: "SSRN/Zenodo submission pending"` por el DOI real
- Recompilar PDF y hacer commit/push

### T+30min: SSRN upload
- Ir a https://papers.ssrn.com/sol3/SSRN_Submit.cfm
- Paper series: **Accounting** (o Information Systems para más alcance en IA)
- Subir `docs/papers/drafts/kontablo_preprint_modular.pdf`
- Abstract: copiar el texto limpio de `docs/papers/drafts/sections/abstract.tex` (245 palabras)
- Keywords: `accounting ontology, IFRS, multi-jurisdictional, agentic economy, MCP, graph database, UUID, ERP consolidation`
- Una vez aprobado (~24-48h hábiles), SSRN asigna número y URL permanente

### T+1h: Posts coordinados (ver sección 3)

---

## 1. Lista de notificación — 25 personas

> Regla: nota personalizada, específica, una por una. Sin copy-paste. Sin links a wall de posts.
> Hook: "tu trabajo en X conecta con esto porque Y."

### Tier 1 — Day-of (notificar el mismo día del release)

| # | Nombre | Contexto | Hook específico |
|---|--------|----------|-----------------|
| 1 | **Simon Willison** (@simonw) | Herramientas para LLMs, datasets, open data | Deterministic boundary library elimina clase entera de alucinaciones — conecta con su trabajo en tool-calling y verificación de outputs |
| 2 | **Swyx** (@swyx) | AI infra, latent space podcast | La harness architecture como marco de análisis de agentes — buen ángulo para Latent Space |
| 3 | **Lilian Weng** (@lilianweng, OpenAI) | LLM agents, tool use, hallucination | Co-responsibility Architecture como solución al problema de accountability en agentes financieros |
| 4 | **Yohei Nakajima** (@yoheinakajima) | Babyagi, agentic frameworks | AP2/A2A integration — cómo una ontología contable es infraestructura para agentes económicos |
| 5 | **Phil Wainewright** (@philww) | ERP/SaaS analyst, diginomica | 195 jurisdicciones soberanas, multi-estándar — exactamente el problema que cubre en análisis de ERP |
| 6 | **Dennis Howlett** (@dahowlett) | Accounting tech analyst, diginomica | Ángulo contable: "Accounting Babel" y la fragmentación de estándares nacionales |
| 7 | **Sebastien Bubeck** (Microsoft Research) | LLM reasoning, grounding | Determinism over stochasticity como principio de diseño — cierra con trabajo en grounding |
| 8 | **XBRL International** (cuenta oficial) | Estándares XBRL | Kontablo como capa semántica sobre XBRL — complementario, no competidor |

### Tier 2 — +24h (después de que haya algo de traction que señalar)

| # | Nombre | Contexto | Hook específico |
|---|--------|----------|-----------------|
| 9 | **Haomiao Huang** (Anthropic) | MCP spec | Kontablo como caso de uso financiero de MCP — cómo el protocolo necesita una capa semántica |
| 10 | **Ivan Mehta** (@ivan_mehta) | TC+ / fintech coverage | ERP consolidation + AI agents ángulo fintech |
| 11 | **Florian Ederer** (Yale SOM) | Economía de plataformas | Kontablo como protocolo estándar con externalidades de red — relevante para su trabajo |
| 12 | **Barr Moses** (@barrmoses) | Data observability, Monte Carlo | Deterministic validation en pipelines de datos financieros |
| 13 | **Santiago Valdarrama** (@svpino) | ML engineering, applied AI | Harness architecture y el determinism principle — ángulo pragmático de MLOps |
| 14 | **IASB / IFRS Foundation** (cuenta oficial) | Estándares IFRS | Validación empírica de 195 jurisdicciones soberanas — dato citable en sus análisis |
| 15 | **Andrej Karpathy** (@karpathy) | LLMs, agents | Solo si hay conexión genuina con un post/trabajo específico suyo |
| 16 | **Comunidad ERPNext/Frappe** (foro oficial) | Open-source ERP | Conector Apache 2.0 disponible — post técnico en su foro |

### Tier 3 — +7 días (para deep engagement)

| # | Nombre | Contexto | Hook específico |
|---|--------|----------|-----------------|
| 17 | **Investigador en accounting IS** (academia) | Investigación IS contable | Pedir feedback en el paper, no solo amplificación |
| 18 | **Latin American fintech Slack/Discord** | FinTech LATAM | Venezuela hyperinflation y VE mapping — caso único para la región |
| 19 | **Hacker News** | Comunidad técnica | Post propio en "Show HN" — no pedir a nadie que vote |
| 20 | **r/MachineLearning** + **r/accounting** | Reddit | Crossposts con ángulos distintos por audiencia |
| 21 | **arXiv cs.AI / econ.GN** | Repositorio académico | Crosspost del preprint si el scope es compatible |
| 22 | **OpenCFP / CFP.exchange** | Conferencias | Proponer talk en conferencias de accounting-tech y AI infra |
| 23 | **Odoo community** | Open-source ERP | Conector futuro — sembrar visibilidad |
| 24 | **FinDev Gateway** | Finanzas en desarrollo / LATAM | Venezuela + Ecuador + LATAM jurisdictions |
| 25 | **ACCA / ICAEW internacional** | Organismos contables | Validación de estándares internacionales |

---

## 2. Social media — borradores

### Twitter/X thread (15 posts)

```
[1/15]
Hoy publico Kontablo v0.1.0 — una ontología contable universal, graph-based,
validada en 195 jurisdicciones soberanas (cobertura global completa), con una capa nativa para el agentic economy.

HILO 🧵
[repo] [preprint DOI]

---

[2/15]
El problema: contabilidad es "Accounting Babel."
MX usa SAT. BR usa SPED. FR usa PCG. IL usa GAAP propio.
Venezuela agrega IAS 29 (hiperinflación).

Un agente que maneja dinero necesita entender TODOS sin ambigüedad.
No existe esa capa. Hasta ahora.

---

[3/15]
Kontablo no es un ERP. No es un SaaS. No es un framework.

Es un PROTOCOLO. Como ISO 20022 para mensajería de pagos,
pero para la semántica de las cuentas.
Un UUID por cada concepto contable universal. Inamovible.

---

[4/15]
El grafo tiene 30 cuentas core (Nivel 3).
Esas 30 cubren ~94% del volumen de transacciones rutinarias
(y ~99% con un núcleo extendido de 34 cuentas), según el benchmark
reproducible en `research/coverage_benchmark/`.

No es un número redondo — es el resultado de la validación empírica.

---

[5/15]
La innovación que me importa más: el Deterministic Boundary Library.

Un agente no puede proponer un UUID que no existe en el grafo.
Eso ELIMINA la clase clásica de alucinación contable al nivel del harness.

El error se reubica a los límites del coverage — problema de ingeniería, no de magia.

---

[6/15]
Three-Tier Resolution Strategy:

1. Exact-code lookup (determinista, sin LLM)
2. Regex disambiguation rules (determinista)
3. Semantic AI fallback con confidence score

Solo el Tier 3 toca inferencia estocástica.
Los Tiers 1-2 son puro grafo.

---

[7/15]
Co-responsibility Architecture (CRA):

Todo mapeo de AI tiene un pathway de revisión humana obligatoria
+ audit trail inmutable de inconsistencias.

La accountability legal descansa en el operador humano. Siempre.
No en el modelo.

---

[8/15]
El stress test más extremo: Venezuela.

IAS 29 (hiperinflación) requiere reexpresión continua de todos los activos.
El motor de consolidación lo maneja en tiempo real, con moneda dual.

Si funciona en Venezuela, funciona en cualquier lado.

---

[9/15]
Para el agentic economy:

Kontablo expone una capa agent-native vía MCP, A2A, y AP2.
Un agente de pagos puede consumir la ontología directamente,
sin parsear PDFs de estándares nacionales.

La lógica de agregación es determinista. El agente no adivina.

---

[10/15]
Licencia: Business Source License 1.1.
Conversión a Apache 2.0 en 4 años.

Los conectores a ERP open-source (ERPNext, Odoo) son Apache 2.0 hoy.
La ontología validada y los conectores NetSuite/SAP son comerciales.

Open-core: interfaz abierta, implementación protegida.

---

[11/15]
Lo que no es Kontablo:
❌ Un reemplazo de tu ERP
❌ Un software de contabilidad
❌ Un modelo de AI para contabilidad
❌ Una solución completa de compliance

Es la capa semántica que falta entre los estándares nacionales
y los sistemas que los consumen.

---

[12/15]
195 jurisdicciones soberanas mapeadas — cobertura global completa.
Contextos especiales: IAS 29 hiperinflación (VE, LB, ZW), finanzas islámicas (SA, QA, KW),
CIT distribución-solo (EE, LV, GE), SYSCOHADA (15 países OHADA).

---

[13/15]
Stack técnico:
- Python / FastAPI (API de referencia)
- YAML + UUID (ontología, machine-readable by design)
- React + Framer Motion (dashboard demo)
- ERPNext connector (Apache 2.0)
- PQC roadmap: ML-KEM, ML-DSA (NIST FIPS 203/204)

---

[14/15]
El preprint está en [Zenodo DOI] y [SSRN URL].
El repo está en github.com/ChristianLuciani/accounting-esperanto

Si tu trabajo toca ERP, XBRL, fintech, o AI agents que manejan dinero
— me interesa escuchar si el framework es útil o incompleto.

---

[15/15]
Construido en Cuenca, Ecuador.
Con datos de Venezuela, México, Brasil, Francia, Arabia Saudita, Vietnam, Nigeria, y 16 más.

Kontablo existe porque el mundo financiero no puede permitirse que los agentes adivinen.

[repo] [preprint] [ORCID: 0000-0002-6955-5384]
```

---

### LinkedIn post (~600 palabras, audiencia contable/ERP)

```
Hoy publico Kontablo — una ontología contable universal validada en 195 jurisdicciones soberanas.

El problema que resuelve es uno que todo contador internacional conoce:
México usa SAT, Brasil usa SPED, Francia usa PCG, Venezuela usa IAS 29 con hiperinflación.
Cada sistema tiene su propia lógica, sus propios códigos, su propia jerarquía.
Cuando una empresa multinacional necesita consolidar, alguien tiene que reconciliar esos mundos manualmente.
Eso cuesta tiempo, dinero, y errores.

Kontablo es la capa semántica que está faltando.

No es un ERP. No es un software de contabilidad. Es un protocolo —
como un diccionario universal que asigna un UUID inamovible a cada concepto contable,
independientemente de cómo lo llame cada jurisdicción.

La arquitectura core es un grafo de 30 cuentas universales (Nivel 3) que cubre
~94% del volumen de transacciones rutinarias (~99% con un núcleo extendido de 34 cuentas).
Sobre ese grafo, una lógica determinista de resolución en tres niveles:
primero busca por código exacto, luego por reglas de desambiguación,
y solo como último recurso usa un fallback semántico con IA.

¿Por qué minimizar la IA en el camino crítico?
Porque cada decisión que se puede mover de inferencia estocástica a lógica determinista
es una decisión que se vuelve verificable, reproducible, y libre del riesgo de alucinación.

El resultado: un agente no puede proponer una cuenta que no exista en el grafo.
Eso elimina la clase clásica de error de un sistema de contabilidad basado en IA.

Validamos el framework con un motor de consolidación en 10 entidades de 9 países,
incluyendo un stress test de hiperinflación bajo IAS 29 en Venezuela.
Si funciona ahí, funciona en cualquier lado.

Para profesionales contables: el preprint está en [SSRN URL].
Para equipos de ERP: el conector para ERPNext es Apache 2.0 y está disponible hoy.
Para desarrolladores: el repo está en github.com/ChristianLuciani/accounting-esperanto.

Busco feedback honesto — especialmente de personas que trabajan con consolidación multijurisdiccional.
Si el framework tiene huecos o casos no cubiertos, quiero saberlo antes de la validación académica formal.

Christian Luciani | ORCID 0000-0002-6955-5384 | Cuenca, Ecuador

#contabilidad #IFRS #ERP #fintech #AI #ontología #agenticeconomy
```

---

## 3. Long-form narrative — estructura (desarrollar en sesión separada)

**Título sugerido:** "Por qué los agentes de IA no pueden manejar dinero sin una ontología contable universal"

**Estructura (~2,500 palabras):**
1. La anécdota de Venezuela (IAS 29 — el caso extremo que diseñó el sistema)
2. El problema: Accounting Babel y por qué existe
3. Lo que intenté primero y por qué no alcanza (XBRL como solución parcial)
4. La arquitectura de Kontablo — el grafo, los UUIDs, el Deterministic Boundary Library
5. Por qué el agentic economy lo necesita hoy
6. El resultado: 195 jurisdicciones soberanas, ~94% coverage (~99% con núcleo extendido), stress test hiperinflación
7. Lo que Kontablo no es (gestión de expectativas)
8. Cómo contribuir / cómo usarlo

**Hosting recomendado:** GitHub Pages del repo primero (cero fricción, indexable de inmediato), Substack después para newsletter.

---

## 4. Release notes v0.1.0

> Archivo: `docs/strategy/release-notes-v0.1.0.md` — crear antes del tag.

### What's in this release

- **Ontology**: 30 universal accounts (Level 3 minimum-core), UUID-keyed, validated across 195 sovereign jurisdictions
- **API**: FastAPI reference implementation (`api/`) with mapping, batch consolidation, and transaction classification endpoints
- **Connectors**: ERPNext/Frappe connector (Apache 2.0 license)
- **Preprint**: Full academic paper at [DOI — to be filled post-deposit]
- **Localizations**: YAML mapping files for 195 sovereign jurisdictions

### Known limitations

- MX SAT local codes not yet wired into YAML ontology (tracked: xfail tests in `tests/api/test_endpoints.py`)
- AI semantic fallback requires external API key (Google Gemini — migration to `google.genai` pending)
- Post-quantum cryptography (ML-KEM/ML-DSA) scheduled for Phase 3

### License

Business Source License 1.1. Converts to Apache 2.0 on 2030-06-01.
ERPNext connector: Apache 2.0.

---

## 5. Checklist de ejecución

- [ ] Activar Zenodo GitHub integration: https://zenodo.org/account/settings/github/
- [ ] Confirmar que el repo es público en GitHub
- [ ] Crear `docs/strategy/release-notes-v0.1.0.md` (usar sección 4 arriba)
- [ ] Ejecutar `gh release create v0.1.0` (Claude Code puede hacer esto bajo confirmación)
- [ ] Copiar DOI de Zenodo y actualizar BibTeX + CITATION.cff
- [ ] Recompilar PDF y hacer commit final
- [ ] Subir PDF a SSRN (manual — web form)
- [ ] Publicar Twitter/X thread (T+1h del release)
- [ ] Publicar LinkedIn post (T+1h del release)
- [ ] Enviar DMs Tier 1 (mismo día)
- [ ] Enviar DMs Tier 2 (+24h)
- [ ] Post en Hacker News Show HN (+7 días)
