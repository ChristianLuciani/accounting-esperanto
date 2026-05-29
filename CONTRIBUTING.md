# Contributing to Kontablo

Thank you for your interest in contributing. Please read this document before
opening issues or submitting pull requests.

---

## Contributor License Agreement (CLA)

Kontablo is licensed under **BSL 1.1**, which includes a commercial reservation.
To allow contributions to be incorporated into both the open and commercial layers,
**all contributors must sign a Contributor License Agreement** before their first
pull request is merged.

The CLA grants Praxia (and its predecessor entity, Christian Luciani) the right to
use your contribution under any license, including commercial ones, while you retain
copyright over your contribution.

To sign the CLA, email **cluciani@gmail.com** with the subject line
`CLA — Kontablo — [your GitHub username]`. A template will be provided on request.

This requirement does not apply to the ERPNext/Frappe connector
(`connectors/erpnext/`), which is Apache 2.0 and does not require a CLA.

---

## What contributions are welcome

- **Jurisdiction mappings** — new or corrected chart-of-accounts entries in `/localizations/`
- **Ontology corrections** — errors in UUID assignments or account classifications in `/core/`
- **Specification improvements** — clarity, precision, or completeness in `/spec/` or `/openspec/`
- **Bug reports** — API service, connector, or validator bugs with a reproducible case
- **Documentation** — corrections to factual errors in any document

**Not in scope for external contributions at this time:**
- Changes to the co-responsibility governance model (ADR 008) — architectural decisions
  require author review
- New ERP connectors for proprietary systems (NetSuite, SAP) — these are commercial layer
- Changes to the BSL license parameters

---

## Branch naming

| Work type | Branch prefix | Example |
|---|---|---|
| Claude Code sessions | `claude/[topic]` | `claude/jurisdiction-mapping-turkey` |
| Cursor IDE sessions | `cursor/[topic]` | `cursor/api-validation-fix` |
| External contributors | `contrib/[github-username]/[topic]` | `contrib/jsmith/fix-fr-pcg-512000` |

Never commit directly to `main`. All changes go through pull requests.

---

## Commit format

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]
```

Types: `feat`, `fix`, `docs`, `chore`, `refactor`, `test`

Scope (optional, use when relevant): `api`, `core`, `spec`, `connector`, `adr`,
`readme`, `license`, `preprint`

Examples:
```
feat(core): add KZ-KAS (Kazakhstan) jurisdiction mapping
fix(api): correct confidence threshold for tier-2 disambiguation
docs(adr): add ADR-015 for gRPC versioning strategy
```

---

## Pull request process

1. Open an issue first for any change larger than a typo fix. Discuss before coding.
2. Fork the repository and create your branch from `main`.
3. Keep PRs focused — one logical change per PR.
4. Include a description of **why**, not just what.
5. All PRs require review by a maintainer before merge.
6. If your PR adds or modifies a jurisdiction mapping, include a primary source
   reference (official standards document or government publication).

---

## Epistemic standards

Kontablo's documentation follows a strict epistemic protocol inherited from the
project's academic context:

- **Explicit uncertainty.** If you are not certain of a claim, say so. "I believe"
  or "this may need verification" is correct. Confident-sounding errors are worse
  than hedged ones.
- **Primary source citations.** Every claim about a jurisdiction standard, protocol
  specification, or regulatory requirement needs a link to the original source.
  Wikipedia is acceptable as a pointer, not as evidence.
- **Verifiability.** Indicate how a claim can be independently verified.

PRs that introduce undocumented claims about jurisdiction standards will be returned
for sourcing.

---

## Development setup

```bash
# Python environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Frontend
cd frontend && npm install && npm run dev

# API service
cd api/src && uvicorn main:app --reload
```

Tests:
```bash
pytest tests/
```

---

## Questions

Open a [GitHub Discussion](https://github.com/ChristianLuciani/accounting-esperanto/discussions)
or email cluciani@gmail.com.
