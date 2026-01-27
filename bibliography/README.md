# Kontablo Bibliography

## Citation Standard
All references follow **APA 7th Edition** format.

## Source Classification

### Primary Sources (`/primary_sources`)
Official regulatory documents:
- IFRS Foundation standards (PDF + metadata)
- Local GAAP official publications
- Government tax codes
- XBRL taxonomy files

### Secondary Sources (`/secondary_sources`)
Academic papers, books, industry reports:
- Peer-reviewed journals
- CPA association publications
- Big 4 accounting firm whitepapers

### Standards (`/standards`)
Technical specifications:
- XBRL specification documents
- ISO 20022 documentation
- OpenAPI/JSON Schema specs

### Regulations (`/regulations`)
Country-specific legal requirements:
- Tax codes
- Mandatory reporting formats
- E-invoicing specifications

## Metadata Format

Each source must have a companion `.meta.yaml` file:
````yaml
source_id: "ifrs_2023_full"
type: "primary_standard"
title: "IFRS Standards 2023 (Full Set)"
author: "IFRS Foundation"
publication_date: "2023-01-01"
url: "https://www.ifrs.org/issued-standards/"
access_date: "2025-01-27"
license: "Proprietary - Reference permitted"
file_hash_sha256: "abc123..."
relevance: "Core foundation for ontology"
citation: |
  IFRS Foundation. (2023). IFRS Standards 2023. 
  https://www.ifrs.org/issued-standards/
````
