# Security Policy

## Scope

This policy applies to the Kontablo repository (`accounting-esperanto`) and all
artifacts produced from it: ontology schemas, API service, reference dashboard,
ERP connectors, and specifications.

---

## Threat Model

Kontablo handles financial data with multi-decade retention requirements. The threat
model explicitly includes **harvest-now-decrypt-later (HNDL) attacks**: an adversary
captures encrypted financial records today and decrypts them once quantum computing
becomes practical. Quantum-resistant computation at commercially relevant scale is
projected before 2030 (IBM, Google, IonQ public roadmaps).

Three threat categories are in scope:

| Category | Description |
|---|---|
| **HNDL** | Long-lived financial records encrypted today, decrypted by future quantum adversary |
| **Ontology tampering** | Unauthorized modification of UUID-to-account mappings, producing silent mis-classification |
| **Audit trail integrity** | Deletion or alteration of transaction records, undermining the zero-corruption guarantee |

Out of scope for this repository: social engineering, physical access, supply-chain
attacks on dependencies. These are addressed at the deployment level by the integrating
organization.

---

## Post-Quantum Cryptography Roadmap

**Standard:** [NIST Post-Quantum Cryptography](https://csrc.nist.gov/projects/post-quantum-cryptography),
finalized August 2024.

| Algorithm | FIPS | Role in Kontablo |
|---|---|---|
| **ML-KEM** (from Kyber) | [FIPS 203](https://csrc.nist.gov/pubs/fips/203/final) | Key encapsulation for data at rest and in transit |
| **ML-DSA** (from Dilithium) | [FIPS 204](https://csrc.nist.gov/pubs/fips/204/final) | Digital signatures on spec version hashes |
| **SLH-DSA** (from SPHINCS+) | [FIPS 205](https://csrc.nist.gov/pubs/fips/205/final) | Hash-based signature alternative (conservative fallback) |

**Important distinction:** Kontablo implements **PQC (Post-Quantum Cryptography)** —
classical algorithms resistant to quantum attacks, implementable in standard software.
This is distinct from **QKD (Quantum Key Distribution, e.g. BB84)**, which requires
photonic hardware and is not applicable to Kontablo's software architecture.

**Implementation status:** not started. Target: hybrid classical + PQC signatures on
spec version hashes by Phase 3 (post-publication). Implementation will use
[Open Quantum Safe / liboqs](https://openquantumsafe.org/) or `pyca/cryptography`
once PQC primitives are merged upstream.

---

## Auditability and Zero-Corruption Design Goal

Every transaction processed through Kontablo must produce an immutable audit record
containing: the agent decision, the confidence score, the UUID assigned, the human
approval mode (auto / co-signature / escalation), and the identity of the human
principal. This record cannot be deleted — only annotated with corrections that
themselves become part of the audit trail.

Zero-corruption is an explicit design goal. Kontablo implements everything technically
possible to make financial flows observable, traceable, and verifiable. This is not a
marketing claim — it is a design constraint that governs implementation decisions.

---

## Reporting a Vulnerability

**Do not open a public GitHub issue for security vulnerabilities.**

Report privately to:

**Christian Luciani** — cluciani@gmail.com

Include in your report:
- Description of the vulnerability
- Steps to reproduce
- Affected component (ontology, API, connector, spec)
- Your assessment of impact and exploitability

**Response commitment:**
- Acknowledgement within 5 business days
- Status update within 14 business days
- Public disclosure coordinated with the reporter after a fix is available

There is no bug bounty program at this time.

---

## Supported Versions

| Version | Supported |
|---|---|
| `main` branch | Yes |
| Tagged releases | Yes (current release only) |
| Older releases | No |

---

## Security-Relevant Architecture Decisions

| ADR | Decision |
|---|---|
| [ADR 001](docs/adr/001-use-graph-not-tree.md) | Graph model prevents implicit account collisions |
| [ADR 002](docs/adr/002-uuid-as-primary-key.md) | UUID as canonical identity — codes are metadata |
| [ADR 008](docs/adr/008-co-responsibility-governance.md) | Human veto power and full auditability as non-negotiable properties |
| [ADR 009](docs/adr/009-determinism-over-stochasticity.md) | Determinism over stochasticity — reduces attack surface of inference errors |
