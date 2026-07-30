# arXiv submission metadata (T9)

Staged, ready to paste into the arXiv submission form. Every policy statement
below is sourced to arXiv's own documentation via
[`research/dr5_arxiv_submission.md`](research/dr5_arxiv_submission.md); where
DR5 could not confirm something from a primary source, this file says so rather
than filling the gap.

**Read the blocker first (§5). arXiv is not the first publication channel for
this paper, and should not be treated as one.**

---

## 1. Title

```
Deterministic Auditability Invariants for Autonomous Financial Agents:
The Loss Ledger and Pre-Transaction Fiber Query
```

## 2. Authors

```
Christian Luciani
```

Affiliation as published elsewhere for this project — keep identical to
`CITATION.cff` and `.zenodo.json`: Independent Researcher, Cuenca, Ecuador
(Praxia, the initiative's planned entity, in incorporation).
ORCID `0000-0002-6955-5384`.

## 3. Abstract

Paste the paper's abstract as plain text. It is **1887 characters** against
arXiv's 1920-character limit — **33 characters of headroom**, so **re-measure
after any abstract edit**. The abstract has already been trimmed once to make
room for the co-responsibility clause; there is no slack left for another
addition without a compensating cut:

```bash
python3 - <<'PY'
import re
s = open('main.tex', encoding='utf-8').read()
ab = s.split(r'\begin{abstract}')[1].split(r'\medskip')[0]
ab = re.sub(r'\\[a-zA-Z]+\{([^}]*)\}', r'\1', ab)
ab = re.sub(r'\s+', ' ', ab.replace('\\noindent','').replace('}','').replace('$','').replace('\\','')).strip()
print(len(ab))
PY
```

Replace the LaTeX em-dashes (`---`) with a plain em-dash or ` - ` before
pasting; leave the `(I1)` / `(I2)` / `(I3)` markers intact, since they carry the
paper's coined vocabulary.

## 4. Categories

| Field | Value |
|---|---|
| **Primary** | `cs.MA` — Multiagent Systems |
| **Cross-list** | `cs.CE` — Computational Engineering, Finance, and Science |

**One cross-list, not three.** `TASKS.md` originally named three candidates
(`cs.AI`, `cs.CE`, `q-fin.GN`). DR5 changed that, on primary-source grounds:

- arXiv's own cross-listing page states *"it is rarely appropriate to add more
  than one or two cross-lists"* and *"Bad cross-lists will be removed."*
  Requesting three invites exactly the outcome we are trying to avoid.
- **`cs.AI` is out.** The arXiv category taxonomy's own description of `cs.AI`
  says it *"Covers all areas of AI except Vision, Robotics, Machine Learning,
  **Multiagent Systems**, and Computation and Language."* Cross-listing a
  multi-agent paper into a category that textually excludes multi-agent systems
  is a bad cross-list by arXiv's own definition.
- **`cs.CE` is in.** Taxonomy text: *"Covers applications of computer science to
  the mathematical modeling of complex systems in the fields of science,
  engineering, and **finance**. Papers here are interdisciplinary and
  applications-oriented."* That is this paper.
- **`q-fin.GN` is out.** *"Development of general quantitative methodologies with
  applications in finance"* — this contribution is an ontology/systems result,
  not a quantitative methodology in the q-fin sense. A thin fit, and the second
  cross-list slot is better spent on nothing than on a weak claim.

**Unverified (DR5 could not close from a primary source):** whether a
cross-listed category requires its own endorsement, and whether cross-lists can
be requested in the same submission session or only afterward from the user
page. Do not assume either way — handle it interactively at submission time.

## 5. License

**CC BY 4.0** — Creative Commons Attribution 4.0 International.

DR5 confirmed against `info.arxiv.org/help/license/` that CC BY 4.0 is
selectable with no disqualifying condition, described by arXiv as allowing
reusers to *"distribute, remix, adapt, and build upon the material in any medium
or format, so long as attribution is given"* and that *"The license allows for
commercial use."* This matches `docs/papers/LICENSE` and what the project
already uses on Zenodo, SSRN and ResearchGate — no divergence to reconcile.

Two arXiv governance facts that matter operationally:

- **The license choice is irrevocable per version.** arXiv: *"The license chosen
  is irrevocable and cannot be changed."* A later version can carry a different
  license, but v1 cannot be re-licensed. Choose deliberately at v1.
- **Metadata is CC0 regardless.** *"A Creative Commons CC0 1.0 Universal Public
  Domain Dedication will apply to all metadata"* whatever the article license.
  This is standard across repositories (Zenodo included), not arXiv-specific.

## 6. Comments field

```
19 pages, 2 figures, 1 table. Companion spoke paper to the Kontablo
specification (Zenodo concept DOI 10.5281/zenodo.20738795). All quantitative
claims regenerate from committed commands in the public repository;
reproducibility section lists them. Validation dataset is synthetic trial
balances, not real ledger exports.
```

The synthetic-data sentence is **not optional**. It is the project's standing
data-honesty guardrail, and the comments field is the first thing a moderator
reads.

## 7. Journal-ref / DOI fields

Leave `journal-ref` empty. Once the Zenodo deposit exists (see §8), add its DOI
to the arXiv **DOI field** so the two records resolve to each other.

---

## 8. The blocker: endorsement, and why arXiv is not first

**arXiv `cs.MA` requires endorsement, and this project has already hit that
wall** — the hub paper was refused in `cs.*` with "not endorsed for this
archive."

DR5 found the barrier has since become *harder*, not easier: as of
**2026-01-21** arXiv stopped accepting an institutional email address alone as
sufficient for auto-endorsement, institution-wide. For an unaffiliated submitter
with no prior arXiv-published co-authorship in the target category, the only
remaining path is a **personal endorsement from an existing arXiv author in that
domain** — with no service-level agreement and no guaranteed timeline.

Therefore the publication order is:

1. **Zenodo first — now, and not contingent on anything.** A new, separate
   Zenodo deposit for this spoke (its own DOI, related to the hub's concept DOI
   per `HUB_UPDATE.md` item 5). Zero endorsement gate; already proven to work
   for this project three times.
2. **Pursue endorsement in parallel, non-blocking.** Publication does not wait
   on it.
3. **Submit to arXiv the moment endorsement lands**, using the metadata above.
4. **Layer a workshop slot afterwards** if one fits. DR5 §(h) lists candidates
   beyond DR3's original venue survey, with fit assessed honestly rather than
   optimistically.

**Moderation risk, separately:** DR5 read arXiv's moderation policy in full and
found **no clause** naming software-system or product papers as a decline
category — the diffuse worry is not supported by the policy text. The one
concrete, dated risk is a **2025-10-31** CS-specific tightening that requires
prior peer review for *review* and *position* papers. That is very likely
inapplicable here: this paper reports an empirical result (the round-trip audit)
against a committed implementation, not a survey or an opinion piece. Keeping
§4's result and §6's limitations prominent is the cheapest insurance.

---

## 9. Pre-submission checklist

- [ ] `pdflatex` + `bibtex` + 2 passes: 0 undefined refs, 0 undefined citations,
      0 bibtex warnings (last verified in `REPRO_CHECK.md`).
- [ ] Abstract re-measured under 1920 characters after any edit.
- [ ] Every claims-evidence command re-run and still matching (`REPRO_CHECK.md`
      §"Results, command by command").
- [ ] Dataset described as **synthetic** everywhere, including the comments
      field.
- [ ] The human is described as the legal principal everywhere; the agent is
      never described as deciding alone.
- [ ] Zenodo deposit created and its DOI available for the arXiv DOI field.
- [ ] `HUB_UPDATE.md` item 1 cut, so the hub and this paper do not contradict
      each other on MCP implementation status in public.
