# Hub-side updates to cut on publication day (T10)

**Status: staged, not applied.** Nothing in this file has been landed on `main`.
It is the exact list of hub-side edits to make **once this spoke has its own
DOI**, cut as a *separate* PR to `main` (`WORKFLOW.md` rule 3 — the spoke never
edits the hub's citable surfaces from the integration branch).

Two of these are **not** cross-link cosmetics: item 1 corrects a hub statement
that this spoke's own existence falsifies, and item 6 is the honesty check that
must pass before the rest ship. **Item 1 has already been cut** (PR #102) rather
than waiting for the DOI, which is what it said to do.

Placeholders below: `<SPOKE_DOI>` = the spoke's Zenodo version DOI,
`<SPOKE_URL>` = its resolved landing page, `<PUB_DATE>` = the publication date.

---

## 1. `docs/papers/drafts/sections/agentic_economy.tex` — a stale hub claim

**☑ CUT 2026-07-29 as PR #102 to `main`, independently of the DOI** (preprint
v1.9.3). Kept below as the record of what was changed and why. Everything from
item 2 down is still staged and unapplied.

The hub stated the opposite of what shipped.

Line 29 reads:

> \[the\] MCP server is specified but not yet implemented, and is tracked as
> roadmap work

That was true when the hub froze. It is now false: `api/mcp/server.py` registers
six deterministic tools (`resolve_account`, `get_account`,
`validate_balance_sheet`, `consolidate_trial_balances`, `get_node_fiber`,
`list_jurisdictions`), none of which calls a language model, and
`tests/mcp/test_mcp_server.py` covers them hermetically. The spoke's
anti-salami argument (README gate 1) rests on this having shipped *after* the
hub froze, so the hub text and the spoke text must not contradict each other in
public.

Replace with the honesty-bar wording the project already uses for gRPC:
**"deterministic core implemented, Tier-3/LLM tools planned"** — explicitly not
full feature parity with REST. Keep the surrounding scope-boundary paragraph
(Kontablo is a mapping and validation layer, not a book of record) unchanged;
it is still correct.

This edit moves a *qualitative* claim, not a number, so no claims-evidence
surface has to move with it.

---

## 2. `README.md` — companion-paper pointer

The README has no "spoke" or "companion" mention today. Add a row to the
identity table near line 28, immediately after the existing **Preprint** row:

```markdown
| **Companion paper** | *Deterministic Auditability Invariants for Autonomous Financial Agents: The Loss Ledger and Pre-Transaction Fiber Query* — [DOI <SPOKE_DOI>](<SPOKE_URL>) · `docs/papers/spokes/agentic-provenance/` |
```

Keep it a *pointer*, not a summary. The hub stays the specification of record;
the spoke is the community-facing result.

---

## 3. `README.md` — claims-evidence row

Add to the claims → evidence table:

| Claim | Generating command |
|---|---|
| 0 silent losses over 441 entries; every local trial balance reconstructs byte-for-byte from lineage alone; 6 deterministic MCP tools, none invoking an LLM | `python scripts/roundtrip_audit.py` → `research/experiments/roundtrip_audit/results.json`; `grep -c "@server.tool(" api/mcp/server.py` → 6 |

**Check before adding:** the root `CLAUDE.md` claims table already carries a
round-trip row ("0 silent losses / exact entry-level reconstruction (441
entries, 75 entities, 68 jurisdictions)"). If `README.md` already mirrors it by
the time this is cut, add only the **MCP tool-count** half and do not duplicate
the round-trip half. One number, one row.

---

## 4. `CITATION.cff` — related identifier

The `identifiers:` block (line 30 onward) already lists the concept DOI, three
version DOIs, SSRN and ResearchGate. Append:

```yaml
  - type: doi
    value: "<SPOKE_DOI>"
    description: "Companion spoke paper (cs.MA): Deterministic Auditability Invariants for Autonomous Financial Agents"
```

Do **not** change the top-level `doi:` field — that stays the hub's concept DOI.

---

## 5. `.zenodo.json` — related identifier

Append to `related_identifiers`:

```json
{
  "relation": "isSupplementedBy",
  "identifier": "<SPOKE_DOI>",
  "resource_type": "publication-preprint"
}
```

`isSupplementedBy` is the correct DataCite relation here: the hub is the
specification of record and the spoke supplements it with a community-facing
result. It is **not** `isIdenticalTo` (used for the SSRN and ResearchGate
mirrors of the *same* document) and **not** `isPartOf` (the spoke is a separate
work, not a component of the hub).

---

## 6. Honesty check before any of the above ships

Run these and confirm they still hold at the commit being published. If any
fails, fix the code or the wording — never the assertion.

```bash
python scripts/roundtrip_audit.py            # exit 0, silent_losses == 0
python scripts/mass_consolidation_v2.py      # 97.3%, 75 entities, 68 jurisdictions
grep -c "@server.tool(" api/mcp/server.py    # -> 6
pytest tests/ connectors/                    # CI command; claims-evidence gate
```

Then confirm, by reading rather than grepping:

- The hub and the spoke agree on MCP implementation status (item 1 applied).
- Neither describes the 75-entity / 441-entry dataset as anything other than
  **synthetic**.
- Neither describes the agent as deciding alone; the human remains the legal
  principal in both.

---

## 7. Not to be done

- **Do not** merge the spoke's paper text into the hub preprint. They are
  separate works with separate DOIs; that is the whole point of the
  hub-and-spoke program.
- **Do not** update the hub's abstract, `CITATION.cff` title, or `.zenodo.json`
  title/description to mention the spoke's contribution. The four citable
  surfaces move only when a *hub* number moves.
- **Do not** commit the publication playbook. It stays in the gitignored
  `docs/internal/`.

---

## Ordering on the day

1. Merge `claude/spoke1-agentic-provenance` → `main` (the spoke itself).
2. Publish; obtain `<SPOKE_DOI>`.
3. Cut a **separate** PR to `main` applying items 2–5 (item 1 already cut as
   PR #102), with item 6 run first.
4. Commit the built `main.pdf` (gitignored during development — `WORKFLOW.md`
   rule 4 releases it only at the publication merge).

Item 1 was cut earlier and independently, as anticipated — it is a correction,
not a cross-link, and it did not depend on `<SPOKE_DOI>`. **PR #102, merged or
pending, is the record.** On publication day, verify it landed before running the
§6 honesty check, since that check asks whether the hub and the spoke agree on
MCP implementation status.
