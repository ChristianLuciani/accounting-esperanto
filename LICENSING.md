# Licensing

## Why BSL 1.1?

Kontablo is an open-core project. The core ontology, specifications, mapping methodology,
and reference implementation are publicly available. The commercial layer — validated
production connectors for proprietary ERPs (NetSuite, SAP S/4HANA), implementation
services, and validated mapping artifacts — is reserved for Praxia.

The **Business Source License 1.1 (BSL 1.1)** preserves this structure:

- All source code is publicly readable and auditable from day one.
- Non-commercial and internal business use requires no license or payment.
- The Additional Use Grant permits open-source ERP integrations and academic use.
- Commercial products that compete directly with Kontablo's core offering require
  a separate commercial license from the Licensor.
- After **June 18, 2030** (four years from first public release), the entire codebase
  converts automatically to **Apache License 2.0** — no action required.

This model is used by MariaDB, HashiCorp (pre-BSL), and other infrastructure projects
that need to sustain development while remaining open to the ecosystem.

## What the Additional Use Grant permits

You may use Kontablo in production for:

- Internal accounting, reporting, or financial consolidation within your organization.
- Academic research, student projects, and educational curricula.
- Integration testing and evaluation.
- Building open-source integrations with ERPs such as ERPNext, Odoo, GnuCash, or similar.
- Forking and contributing back to the project.

You may **not** use Kontablo to build and sell a commercial multi-jurisdictional
accounting mapping or consolidation service to third parties without a commercial license.
If in doubt, contact the Licensor.

## Per-submodule license exceptions

Connectors for open-source ERP and accounting projects use **Apache License 2.0**,
not BSL 1.1. This applies to:

| Connector | Location | License |
|-----------|----------|---------|
| ERPNext / Frappe | `connectors/erpnext/` | Apache 2.0 |
| Odoo | `connectors/odoo/` | Apache 2.0 |

Rationale: open-source ERP communities will not adopt connectors under non-OSI licenses.
Apache 2.0 maximizes adoption in these ecosystems. The protectable commercial assets are
the validated ontology, implementation services, and connectors to proprietary ERPs —
those remain BSL or proprietary. See the strategic posture section of `CLAUDE.md` for
the full reasoning.

Connectors for proprietary ERPs (NetSuite, SAP S/4HANA), when developed, will be
distributed under a separate commercial license.

## General principle

Open the interface — grow the ecosystem.
Protect the validated implementation behind it.

The real moat is first-mover citability, 195-jurisdiction depth (60 statutory-chart overlays), hyperinflation expertise,
and execution speed — not the license text.

## Commercial licensing

To obtain a commercial license, contact: Christian Luciani — cluciani@gmail.com

## IP assignment

The Licensor is Christian Luciani. IP is scheduled for assignment to **Praxia S.A.S.**
(Cuenca, Ecuador) upon incorporation. The license terms are unaffected by this assignment.
