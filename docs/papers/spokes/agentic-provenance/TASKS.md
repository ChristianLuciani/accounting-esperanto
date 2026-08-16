# Spoke 1 — Task backlog & deep-research prompts

Prioritized path from the adopted **v0.1 draft** to a **publication-ready**
arXiv cs.MA spoke. Each task is sized to be one **atomic PR** onto
`claude/spoke1-agentic-provenance` (see `WORKFLOW.md`). Suggested branch names in
`code`.

Status legend: ☐ todo · ◐ in progress · ☑ done
Draft baseline: v0.1 (adopted 2026-07-24), compiles, anchored on the round-trip
audit, honest on implementation status. **Content is strong; the gaps are
scholarly apparatus (citations, figures, positioning) and publication mechanics.**

---

## P0 — Blockers to a credible cs.MA submission

### ☑ T1 — Related Work + populate `references.bib`  ·  `claude/spoke1-related-work`
**DONE 2026-07-24.** `\section{Related work: where these invariants sit}`
(label `sec:related`) with four subsections plus positioning, replacing the old
thin "Positioning" section. **32 references, all cited, all with resolvable
URLs** (acceptance bar was ≥12). Compiles clean: 0 bibtex warnings, 0 undefined
citations, 12 pp.

Two research findings materially **changed** the paper's claims rather than
decorating them:
- **Granularity is not our gap** (DR4). XBRL GL, AICPA ADS and OECD SAF-T
  already reach journal-entry granularity. Leading with "the only entry-level
  standard" would have been rebutted on sight. The claim now rests on the
  *combination*: agent-callable pre-transaction query + cross-jurisdiction
  unification + per-entry lineage + typed zero-silent-loss.
- **I1 is not literally "constrained decoding"** (DR2). That literature
  constrains a model's own decoding; Tier-1/Tier-2 involve no model at all.
  Related work now states this explicitly — it is a *stricter* instance — and
  preempts the "constraining reasoning hurts reasoning" critique
  (`tam2024letmespeak`, `banerjee2025crane`) instead of leaving it to a reviewer.

Also handled: AuditFlow (`wang2026auditflow`) is **discussed, not merely cited**
(DR3 flagged it as the biggest related-work risk — detection on filed reports
vs. prevention at posting time); absence-of-evidence is scoped to "within a
bounded survey", never "nobody has done this".

**Residual TODOs** (carried into T2/T9, not blockers): pin COLM 2024 proceedings
for `koo2024automata`; confirm ICML 2025 acceptance for `luo2024gcr` before
citing a venue; re-verify ISO 20022 metadata manually (iso.org 403s); confirm
whether XBRL GL 2015 is still the latest Recommendation.

**Excluded on purpose** (do not reintroduce without fresh verification): two
post-cutoff single-author preprints quarantined by DR2; Mastercard Agent Pay
(403, snippet-only); the "100M+ x402 transactions" and Visa "IOUs" claims.

### ☑ T2 — Claim/code audit pass  ·  `claude/spoke1-claim-audit`
Every file path and behavioral claim in `main.tex` must match current `main`
code (epistemic rule + claims–evidence rule). Already verified this session:
6 MCP tools ✓, round-trip numbers ✓, `clapps.cls` clean-room ✓. **Still to
confirm and pin:** the `rule_id` string formats (`tier1:<jur>:<code>` /
`tier2:<node>:<keyword>`) against `core/harness/provenance.py`; that REST
`GET /accounts/{id}/fiber` and MCP `get_node_fiber` exist as described; that
`MappingQuote` carries the listed fields; that the "97.3% / 4 escalations" cross
-reference is consistent with the loss-ledger "4 escalated entries."
**Acceptance:** a short `CLAIMS_AUDIT.md` mapping each in-text claim → file:line
or command; zero unverifiable claims remain.

### ☑ T3 — Figures (≥1, ≤2)  ·  `claude/spoke1-figures`
The draft is figure-less. Add, following the hub's reproducible convention
(`.py`→`.png` or TikZ `.tex` committed):
- **Fig 1 (required):** the agent→layer decision flow — agent calls an MCP
  deterministic tool → ontology-as-constraint guardrail → *either* a resolved
  `MappingQuote` *or* a typed loss-ledger record that escalates (I1+I2), showing
  the Tier-3/LLM path deliberately **outside** the tool surface.
- **Fig 2 (optional):** the I3 fiber query — one universal node, its per-
  jurisdiction preimage (fiber) with preserved local structure, queried
  *before* the transaction.
**Acceptance:** figure(s) compile in `main.pdf`; generator committed and
regenerable; referenced from the text.

---

## P1 — Materially raises acceptance odds

### ☑ T4 — Adversarial-agent threat model  ·  `claude/spoke1-threat-model`
cs.MA reviewers will ask: *can a malicious or buggy agent defeat I1/I2/I3?* Add a
short subsection: it can escalate-spam or submit garbage, but it **cannot** emit
a non-existent UUID (I1), **cannot** cause a silent loss (I2 — the worst case is
a *counted* escalation), and **cannot** hide the preimage (I3). State the residual
attack surface honestly (e.g., a wrong-but-existing UUID is still reachable; that
is a semantic-correctness problem I1 bounds but does not eliminate).
**Acceptance:** one tight subsection; claims consistent with I1's "bounded, not
eliminated" wording.

### ☑ T5 — Inference-cost / resource-economy framing  ·  `claude/spoke1-inference-cost`
Make principle #5's *consequence* concrete (as a consequence, never a banner):
~0.9% escalation rate (4/441) ⇒ ~99% of resolutions are graph lookups that avoid
an LLM call — token, latency, and energy cost not incurred, and no stochastic
error to contaminate downstream steps. **Acceptance:** a short paragraph with the
number sourced to `results.json`; framed as economy+determinism, not marketing.

### ☑ T6 — Sharpen I3 novelty & math tie-in  ·  `claude/spoke1-i3-sharpen`
"Pre-transaction fiber query" is the most novel-sounding term and must be
airtight. Tie the fiber to the preimage / H¹-obstruction language of the hub's
`mathematical_foundations.tex` at a level cs.MA accepts, without importing the
full category-theory apparatus (that is **Spoke 2**'s job — cite it as
forthcoming, do not pre-empt it). **Acceptance:** I3 reads as a systems result
with a clean pointer to the math spoke; no overlap that invites salami critique.

### ☑ T7 — Abstract/intro GEO/AEO polish  ·  `claude/spoke1-geo-polish`
Already has "Kontablo is…" once ✓. Light pass: first-100-words direct answer,
question-as-heading (mostly done), quantified claims traceable. Confirm keywords
line matches venue taxonomy. **Acceptance:** GEO checklist (hub CLAUDE.md §
"AI Discoverability") satisfied.

---

## P2 — Polish & publication mechanics

### ☑ T8 — Modularization decision  ·  (decision, likely *no PR*)
**DECIDED 2026-07-29: keep monolithic.** `main.tex` stays a single file; it is
not split into `sections/` like the 65 pp hub.

Rationale, on the state as of this decision: the paper is **16 pp compiled**, of
which ~13 pp is body text and ~3 pp is front matter plus the 34-entry
bibliography. That is at the trigger threshold the original guidance named, but
the threshold was a proxy for *diff pain*, and the diff pain has not
materialized: every atomic PR from T3 through T7 touched one or two contiguous
regions of the file and reviewed cleanly. Splitting now would buy nothing and
would cost a rename of every `\input` path plus a build-instruction change in
the README, on a paper that is about to freeze for submission.

Revisit only if the paper grows past ~24 pp (e.g. if a reviewer round adds a
full evaluation section), or if two tasks ever need to edit genuinely
independent regions in parallel. Neither has happened.

### ☑ T9 — License header + arXiv metadata  ·  `claude/spoke1-license-meta`
**DONE 2026-07-29.** CC BY 4.0 stated in-paper (new License section, drawing
the paper-vs-implementation boundary explicitly), and the submission metadata is
staged in [`ARXIV_METADATA.md`](ARXIV_METADATA.md).

Note: `docs/strategy/arxiv-submission.md` — named in the original task as the
file to mirror — **does not exist** in the repo. `ARXIV_METADATA.md` is
therefore self-contained and lives beside the paper it describes.

Two things DR5 changed relative to the original plan:

- **One cross-list, not three.** arXiv's own page says *"it is rarely
  appropriate to add more than one or two cross-lists"* and *"Bad cross-lists
  will be removed."* `cs.AI` is dropped because the arXiv taxonomy's own
  description of `cs.AI` explicitly **excludes** Multiagent Systems; `q-fin.GN`
  is dropped as a thin fit (this is an ontology/systems result, not a
  quantitative methodology). Final: primary `cs.MA`, cross-list `cs.CE` only.
- **arXiv is not the first channel.** `cs.MA` requires endorsement, the project
  has already hit that wall once, and DR5 found the barrier got *harder* on
  2026-01-21 (institutional email alone no longer suffices for auto-endorsement).
  Publication order is Zenodo first and unconditional, endorsement pursued in
  parallel and non-blocking, arXiv when it lands. See `ARXIV_METADATA.md` §8.

CC BY 4.0 is confirmed selectable on arXiv, with the license irrevocable per
version and metadata CC0 regardless — both sourced to `info.arxiv.org`.

### ☑ T10 — Hub↔spoke cross-link wiring  ·  `claude/spoke1-crosslink`
**DONE 2026-07-29 — staged, not applied.** See
[`HUB_UPDATE.md`](HUB_UPDATE.md): seven items with exact file, line and
replacement text, plus the ordering for publication day.

Beyond the cross-link cosmetics the task asked for, the pass surfaced one item
that is **not** cosmetic and should be cut whether or not the spoke ever gets a
DOI: `docs/papers/drafts/sections/agentic_economy.tex:29` still says the MCP
server "is specified but not yet implemented, and is tracked as roadmap work."
That was true when the hub froze and is now false — `api/mcp/server.py`
registers six deterministic tools. The spoke's anti-salami argument (README gate
1) rests on the MCP core having shipped *after* the hub froze, so the two
documents must not contradict each other in public. `HUB_UPDATE.md` item 1.

### ☑ T11 — Fresh-checkout reproducibility check  ·  `claude/spoke1-repro-check`
**DONE 2026-07-29 — PASS.** Full log in [`REPRO_CHECK.md`](REPRO_CHECK.md).
Fresh `git clone` of `c45a28f` outside the working tree; every Reproducibility
command run in order and the tree diffed against the committed artifacts.

All five commands exit 0. Both claims-evidence artifacts
(`roundtrip_audit/results.json`, `consolidation_v2/results.json`) and the
generated `figures/fig_fiber_query.tex` regenerate **byte-for-byte identical**.
Paper builds clean from the clone: 16 pp, 0 undefined refs, 0 undefined
citations, 0 bibtex warnings. `pyyaml` is the only third-party dependency any
claim-generating script needs.

One low-severity defect found: `consolidation_v2/per_entry.csv` is not
byte-stable — the writer emits CRLF (correct for the `csv` module) while the
committed copy is LF, so a repro run always leaves the tree dirty. Content is
identical; no published number is affected. Fix is hub-side
(`lineterminator="\n"` on the `DictWriter`), so it is **not** applied in this
spoke per `WORKFLOW.md` rule 3 — filed separately.

---

## Deep-research prompts (run via the `deep-research` skill)

Each is self-contained; paste as the research question. Outputs land in
`docs/internal/` (working notes, gitignored) and feed the tasks noted.

**DR1 — Agent payment & interoperation protocols, and what they do *not* specify.**
> Survey the current (2025–2026) state of machine-to-machine agent payment and
> interoperation protocols: Google's Agent Payments Protocol (AP2) and Agent2Agent
> (A2A), Anthropic's Model Context Protocol (MCP), and adjacent efforts (x402,
> ERC-8004, Coinbase/Skyfire/Visa agent-payment initiatives). For each: spec
> maturity, what auditability/settlement guarantee it makes, and — critically —
> whether it says anything about the *accounting-semantic correctness* of the
> value moved (i.e., that the transaction is booked to the right concept). Cite
> primary specs. Goal: substantiate the paper's "these are settlement/interop
> layers; accounting-semantic auditability is a distinct layer beneath them."
> *Feeds T1, positioning §5.*

**DR2 — Ontology/constraint as a guardrail against LLM hallucination.**
> Survey 2023–2026 work on preventing LLM hallucination by *constraining the
> output space* rather than post-hoc checking: constrained/grammar/JSON-schema-
> guided decoding, retrieval- or ontology-bounded generation, tool-use where the
> callable surface is a fixed vocabulary, and any formal "the model cannot emit
> a token/identifier outside the allowed set" results. Distinguish statistical
> mitigation from constructive (unreachable-by-design) guarantees. Goal: place
> the paper's I1 "ontology-as-constraint" in the literature and defend the
> "a whole class of malformed bookings is unreachable, not merely unlikely" claim.
> *Feeds T1, I1 (§3.1), T4.*

**DR3 — Auditable autonomous action in multi-agent systems (venue mapping).**
> Who publishes, and where, on autonomous-agent economies, machine-to-machine
> financial infrastructure, and provenance/accountability for agent actions —
> AAMAS and its workshops, AAAI, IJCAI, NeurIPS/ICML agent tracks, and dedicated
> agentic-AI / agent-economy workshops in 2025–2026? Identify 8–15 representative
> papers and the 3–5 best open venues for a systems-flavored cs.MA result.
> Goal: Related Work grounding + venue shortlist for the playbook.
> *Feeds T1 and the venue decision (playbook).*

**DR4 — Financial ontologies/standards for machines, and the gap.**
> Compare the machine-facing financial semantics standards — FIBO (EDM Council),
> XBRL / iXBRL / ESEF, ISO 20022, GL/audit taxonomies — on: what semantics they
> encode for machines, granularity, whether any addresses *autonomous-agent
> posting* or per-entry provenance/lineage, and their treatment of cross-
> jurisdiction chart mapping. Goal: position Kontablo's UUID-graph + loss-ledger
> as complementary and identify precisely the gap it fills (per-entry, reconstruc-
> tible, agent-native). Cite primary standards pages. *Feeds T1, positioning §5.*

**DR5 — arXiv cs.MA submission & endorsement, and the de-risked open-venue path.** ☑ DONE 2026-07-29 — [`research/dr5_arxiv_submission.md`](research/dr5_arxiv_submission.md).
> Document the exact mechanics for submitting to arXiv **cs.MA** as an independent
> researcher: endorsement requirements and how to obtain an endorser, moderation
> risk, license options (confirm CC BY 4.0 compatibility), cross-listing rules,
> and timelines. NOTE the prior context: the Kontablo hub hit the arXiv
> "not endorsed for this archive" wall in cs.*. Produce a de-risked plan: which
> open platform to publish on *first* so publication never blocks on endorsement
> (Zenodo already integrated), and how arXiv + a workshop slot to layer on after.
> Goal: the venue section of the local playbook. *Feeds the playbook + T9.*

**DR6 (optional) — Provenance & lineage models to frame I2/I3 rigorously.**
> Summarize provenance/lineage models from data systems (W3C PROV, database
> why-/where-/how-provenance, lineage in data pipelines) at a level that lets the
> paper describe the loss ledger (I2) and fiber query (I3) in the field's own
> vocabulary. Goal: one or two precise citations that make I2/I3 legible to
> reviewers who know provenance theory. *Feeds T1, I2/I3 (§3).*

---

## Suggested landing order

`T1 → T2 → T3` (P0, unblock a submittable draft) → `T4, T5, T6` (P1, strengthen)
→ `T7, T9, T10, T11` (polish/mechanics). `T8` is a one-line decision up front.
Run **DR1–DR4 early** (they gate T1, the critical-path task); **DR5** before the
playbook's venue lock; **DR6** is optional depth.
