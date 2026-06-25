# Changelog

All notable changes to Kontablo are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

Full release notes live in `docs/strategy/release-notes-*.md`.

## [0.2.0] — 2026-06-25

The agent-native layer the preprint describes becomes real in code. No headline
numbers changed (195 / 60 / 56; 75 entities / 68 jurisdictions / 97.3%).

### Added
- **MCP server** (`api/mcp/`) — five deterministic agent tools (`resolve_account`,
  `get_account`, `validate_balance_sheet`, `consolidate_trial_balances`,
  `list_jurisdictions`) over the same engine as REST/gRPC, stdio transport, plus
  a runnable demo and full README. Tier-3/LLM fallback deliberately not exposed.
- **Shared input invariants** (`core/harness/validation.py`) backing REST, gRPC,
  and MCP: finite amounts, `> 0` finite manual FX rates, overflow handling.
- REST `/consolidation` now reports `balanced` / `balance_difference` / totals
  (parity with gRPC and MCP).
- `api/README.md` (three-faces overview + robustness/error model); project
  website and overview-essay links in `README.md`.

### Fixed
- Malformed-but-parseable requests (NaN/±Inf amounts, non-positive FX rates,
  finite-sum overflow) now fail cleanly — REST `422`/`400` (a validation handler
  scrubs non-finite values so the error body serializes instead of turning into a
  `500`), gRPC `INVALID_ARGUMENT`, MCP `ToolError` — instead of silently
  corrupting a consolidation or crashing serialization.

### Notes
- A2A and AP2 remain asserted-but-unimplemented; MCP is the only agent-native
  face with a real deterministic core.

## [0.1.1] — 2026-06-18
- Public release hardening: Zenodo concept-DOI consistency across citable
  surfaces, paper CC BY 4.0 licensing, ResearchGate channel, world-coverage map,
  status → Published. See the v0.1.0 notes for the substantive feature set.

## [0.1.0] — 2026-06-18
- Initial public release: ontology (30-account Level-3 core, 195 jurisdictions),
  FastAPI reference implementation, ERPNext/Frappe connector, preprint, and the
  reproducible mass-consolidation validation. Full notes:
  `docs/strategy/release-notes-v0.1.0.md`.

[0.2.0]: https://github.com/ChristianLuciani/accounting-esperanto/releases/tag/v0.2.0
[0.1.1]: https://github.com/ChristianLuciani/accounting-esperanto/releases/tag/v0.1.1
[0.1.0]: https://github.com/ChristianLuciani/accounting-esperanto/releases/tag/v0.1.0
