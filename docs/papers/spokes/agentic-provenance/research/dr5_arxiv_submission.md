# DR5 — arXiv cs.MA submission mechanics, moderation risk, and the de-risked open-venue path

> Deep-research note for Spoke 1 ("Agentic Provenance"). Feeds the local
> publication playbook's venue section and `T9` (license header + arXiv
> metadata) in `TASKS.md`. Research date: 2026-07-29. All sources below were
> retrieved live via `WebFetch`/`WebSearch`/`curl` in this session — none are
> recalled from training data. This note is a **working research artifact,
> not a paper edit**: it does not touch `main.tex`, `references.bib`, or any
> other file. Where I fetched arXiv's own HTML directly with `curl` (bypassing
> `WebFetch`'s summarizing model) I quote the extracted plain text verbatim
> and say so; where I relied on `WebFetch`'s paraphrase I note that too, since
> the two have different fidelity. Companion note: `dr3_mas_venues_priorart.md`
> (2026-07-24) already surveyed AAMAS/AAAI/ICLR/ICML-family venues in depth —
> this note does not repeat that table, it cites it and adds what DR3 did not
> cover (NeurIPS/ACM-cycle venues, and the arXiv mechanics DR3 explicitly
> flagged as unverified).

---

## (a) Executive summary

- **Endorsement verdict: cs.MA requires endorsement, no exception exists for
  independent researchers, and the barrier got harder five months before this
  research date, not easier.** arXiv's own endorsement page states plainly:
  *"arXiv requires that users be endorsed before submitting their first paper
  to arXiv or a new category."* As of **2026-01-21**, arXiv stopped accepting
  an institutional email address alone as sufficient for automatic
  endorsement, institution-wide (not just the Math pilot that preceded it in
  December 2025) — a submitter now needs *both* an institutional email *and*
  prior claimed co-authorship on an already-accepted paper in the target
  endorsement domain, or must fall back to **personal endorsement from an
  established arXiv author** in that domain. Christian Luciani (independent
  researcher, no institutional email, no prior arXiv-published co-authorship
  in `cs.MA`) has exactly one path open: personal endorsement. This is fully
  consistent with, and explains, the "not endorsed for this archive" wall the
  Kontablo hub paper already hit — that wall is an endorsement-system
  response, not a moderation/content rejection, and it is *harder* to clear
  today than it would have been before 2026-01-21.
- **Moderation risk is real but diffuse — no primary-source clause singles
  out "papers about a software system or company product."** I read arXiv's
  full moderation policy (`info.arxiv.org/help/moderation/index.html`)
  end-to-end. It gives moderators broad discretion (*"arXiv, in its sole
  discretion, may decline to post works... This is not an exhaustive
  list"*) under headings **Scholarly Standards**, **Scholarly interest**
  (originality/novelty/significance; *"avoid extraneous personal or political
  statements"*), **Content types**, and **"On a topic not covered, or a
  community not currently served."** None of these name "software system,"
  "product," or "company" as a distinct decline category. The closest
  concrete, dated risk is a **2025-10-31 CS-specific policy change**: review
  articles and position papers submitted to arXiv's CS category now need
  prior peer-reviewed acceptance documentation or are *"likely to be
  rejected."* The Kontablo spoke paper is a systems/architecture paper with
  quantified empirical validation (round-trip audit, consolidation
  percentages), not a survey or a pure position paper, so this specific rule
  should not bite directly — but the paper's framing needs to keep reading as
  a research contribution with results, not as product documentation, to stay
  clearly on the safe side of "Scholarly interest."
- **License: CC BY 4.0 is confirmed selectable, with no restriction found.**
  arXiv's license page lists CC BY 4.0 first among available licenses and
  states plainly it *"allows for commercial use"* with attribution. This
  matches the license the project has already standardized on for the paper
  text across Zenodo, SSRN, and ResearchGate (`docs/papers/LICENSE`), so
  there is no license-compatibility problem to resolve before an eventual
  arXiv submission — `T9` can proceed as planned.
- **Cross-listing: requestable at submission time (per a secondary source),
  capped by etiquette not by hard rule, and — per a `WebSearch`-only
  synthesis I could not fully corroborate against a primary arXiv page —
  does not require separate endorsement.** arXiv's own `cross.html` page only
  documents adding cross-lists via *"the cross-list facility on your user
  page"* and does not state whether that facility is reachable during the
  initial submission flow or only afterward, nor whether endorsement is
  required per cross-listed category. A secondary source (a mathematician's
  personal, non-official notes on the submission workflow) describes
  cross-lists being offered at the **end** of the initial submission process,
  one at a time, capped at two. Treat the endorsement-not-required claim as
  **plausible but not primary-source-confirmed** (see Residual unknowns).
  The candidate cross-lists named in the task (`cs.AI`, `cs.CE`, `q-fin.GN`)
  are all real, live arXiv categories with descriptions that plausibly fit
  the paper (verified directly against `arxiv.org/category_taxonomy`).
- **Timelines are fast and predictable once a submission clears
  endorsement.** Five weekly announcement windows (Mon–Fri submission cutoffs
  at 14:00 ET, Sun–Thu 20:00 ET announcements, no Fri/Sat announcements);
  *"Quality assurance checks can take between one to four days to resolve,
  sometimes longer."* The bottleneck for this project is not arXiv's queue —
  it is obtaining the endorsement in the first place, which has no SLA at
  all (it depends on finding a willing endorser).
- **De-risked plan (the deliverable): publish on Zenodo first — already true
  today, no new work required — pursue arXiv endorsement in parallel as a
  non-blocking side quest, and use a 2026 non-archival or lightweight-archival
  workshop as the second, faster citable layer if a topically-fitting one has
  an open window.** Concretely: (1) the paper already has, or will get on
  submission, its own Zenodo deposit and concept DOI the same way the hub
  paper does (`10.5281/zenodo.20738795`, confirmed live, v0.3.0, CC BY 4.0
  paper license under a BSL-licensed-software umbrella) — this alone makes
  the paper permanently citable with a resolvable DOI, indexed, and
  versionable, with zero endorsement gate; (2) run the personal-endorsement
  search opportunistically (candidates: authors of recent `cs.MA` papers,
  authors DR1–DR4 already surfaced as citing or adjacent to this work, AAMAS
  workshop program committees) without letting it block publication; (3) if
  and when endorsement lands, submit to arXiv primary `cs.MA` with CC BY 4.0
  and the three cross-lists, which costs nothing extra given (1) is already
  done; (4) separately, DR3's AAMAS/AAAI/ICLR/ICML-family workshop shortlist
  and this note's own finding of a **currently-open, non-archival NeurIPS
  2026 workshop deadline (2026-08-22 AoE)** give a workshop-layer option that
  does not touch arXiv's endorsement system at all, on a schedule that could
  land before an arXiv endorsement does.

---

## (b) The arXiv endorsement system — verbatim mechanics

Source: `https://info.arxiv.org/help/endorsement.html`, fetched directly with
`curl` this session (bypassing the summarizing fetch model) so the quotes
below are the page's own text, not a paraphrase.

**Why it exists:** *"The endorsement system verifies that arXiv contributors
belong to the scientific community in a fair and sustainable way that can
scale with arXiv's growth."*

**When it applies:** *"arXiv requires that users be endorsed before
submitting their first paper to arXiv or a new category."* — this is
per-category, not per-paper: a submitter who is already endorsed in `cs.AI`
would still need a **separate** endorsement the first time they submit to
`cs.MA` as a primary category.

**The two paths, as currently documented (post the 2026-01-21 policy
tightening, since this is the live page):**

1. **Institutional-email path (no longer automatic on its own).** *"Your
   account may receive endorsement if: you have claimed ownership of a paper
   submitted by a co-author **and** your email address meets the
   institutional email criteria."* The page is explicit that institutional
   email alone is insufficient now: *"If you are the submitting author or
   have claimed papers but do not have an institutional email: you will need
   to update your email address to an institutional email."* — i.e. even
   *with* claimed papers, you still need the institutional email on top,
   confirming the January 2026 policy change described in §(f) below is
   already baked into this page's current wording.
2. **Personal-endorsement path.** *"Alternatively you can seek personal
   endorsement from an established arXiv author."* The page walks through
   the mechanics: start a submission and select the target category; arXiv
   emails an *"endorsement request email"* containing a shareable link; find
   a plausible endorser by locating a relevant recent arXiv paper and
   clicking *"Which authors of this paper are endorsers?"* at the bottom of
   its abstract page; contact them with the endorsement request email
   (*"it is inappropriate to email large numbers of potential endorsers at
   once, or to repeatedly email the same endorser"*); *"At least one positive
   endorsement is required per endorsement category to be considered
   endorsed for that category."*

**Who is eligible to endorse ("Who can endorse?"):** *"Endorsers must have
authored a certain number of papers within the endorsement domain of a
subject area. The number of papers depends on the particular subject area,
but has been set so that any active scientist who has been working in their
field for a few years should be able to endorse if their work has been
submitted to arXiv and if they are registered as an author of their papers."*
Only papers *"submitted between three months and five years ago"* count
toward an endorser's qualifying history. An endorser must also *"have an
active positive endorsement to that area yourself before you may endorse for
that subject classification"* — endorsement authority is itself
domain-scoped and non-transitive across unrelated subject areas.

**The endorsement code mechanism:** *"If an author asks you for endorsement,
they will send you a six-character alphanumeric endorsement code."* The
endorser enters it on arXiv's endorsement form and records a positive or
negative vote; a negative vote and any comments are private between the
endorser and arXiv administrators, never shown to the requester (*"this
information will not be shared with arXiv users or the person requesting
endorsement"*).

**What disqualifies a submitter, from the endorser's side ("What are my
responsibilities as an endorser?"):** *"You should not endorse the author if
the author is unfamiliar with the basic facts of the field, or if the work is
entirely disconnected with current work in the area."* Endorsers are told
explicitly the process *"is not peer review"* — they need not verify
correctness, only that the submitter looks like a legitimate member of the
field working on-topic material. arXiv separately reserves broader revocation
authority: *"arXiv reserves the right to revoke any submitter's endorsement
if that submitter has violated arXiv policies."*

**Endorsement domains — granularity is a genuine open question for `cs.MA`
specifically.** The page states: *"most high-level subject areas... are
currently endorsement domains, with the notable exception of physics, in
which individual subject classes... are endorsement domains."* This sentence
does not resolve cleanly whether, for the Computer Science archive, the
endorsement domain is the whole `cs` archive or each `cs.XX` subcategory
separately (both readings are grammatically possible from the page's own
wording, and I found no primary-source page that lists the domains
explicitly by name). A `WebSearch` synthesis asserted `cs.AI` and `cs.MA` are
"separate endorsement domains," but that synthesis cited no single
authoritative page for the claim and is not something I could independently
confirm — **flagged as unverified, see Residual unknowns.** Practically this
does not change the plan: either way, the concrete action is the same (find
one qualifying, willing endorser).

---

## (c) Moderation risk

Source: `https://info.arxiv.org/help/moderation/index.html` (full text
fetched via `curl`), `https://info.arxiv.org/help/policies/content-types.html`
(full text fetched via `curl`), and `https://blog.arxiv.org/2025/10/31/...`
(fetched via `WebFetch`, arXiv's own blog — official but a blog post, treated
as primary-but-secondary-format per this project's source hierarchy).

**What moderators check, verbatim from the primary policy page:**

- *"Submissions to arXiv must comply with appropriate standards of scholarly
  communication in form, including appropriate and carefully prepared
  sections, figures, tables, references, etc. Language standards require
  professional communication, and sufficiently neutral tone."* (Scholarly
  Standards)
- *"A submission may be declined if the moderators determine it lacks
  originality, novelty, significance, and/or contains falsified, plagiarized
  content or serious misrepresentations of data, affiliation, or content.
  Submissions should focus entirely on the scientific research and avoid
  extraneous personal or political statements."* (Scholarly interest)
- *"Submissions that do not contain original or substantive research,
  including course projects, research proposals, news, or information about
  political causes... may be declined. Submissions in need of significant
  review and revision may also be declined."*
- *"While arXiv serves a variety of scientific communities, not all subjects
  are currently covered. Submissions may be declined if they do not fit into
  our current classification scheme or we do not currently serve the
  community who is the intended audience."* (this is the closest primary
  wording to a formal "not appropriate for this archive" ground — it is
  about topical fit to the target category's community, not about a paper
  being "too product-like")
- Explicit discretion, stated twice in different words: *"arXiv, in its sole
  discretion, may decline to post works submitted to the platform. The
  following list includes example topics that could lead to a submission
  being declined. This is not an exhaustive list"* and *"arXiv reserves the
  right to decline or remove any content. arXiv may reclassify already
  announced papers if the moderators determine there is a more appropriate
  category."*

**On papers "primarily about a software system or company's product" — I
found no primary-source clause that names this as a decline category.** The
closest adjacent items in `content-types.html`'s explicit not-typically-accepted
list are narrower than a full systems paper: *"Abstract-only submissions,"*
*"Abstracts or extended abstracts of system demonstrations, conference
tutorials, or short courses,"* and *"Course projects."* A full research
article that happens to describe a system — with a methods section, a
validation section, and quantified results — is not the same content type as
a bare demo abstract, and the accepted-content-types list explicitly names
*"Articles"* (*"Research articles are the primary content type submitted to
arXiv. Articles should be complete final drafts"*) as the primary accepted
type with no carve-out excluding systems/architecture papers. **Net
assessment:** the risk here is real but comes from moderator *discretion*
under the general "scholarly interest / novelty / significance" standard, not
from a specific named rule — the mitigation is the same mitigation that makes
any paper stronger: lead with the empirical contribution (round-trip audit,
consolidation numbers) and the invariants (I1/I2/I3), keep vendor/product
framing (Kontablo-as-product, Praxia, licensing) out of the paper text
entirely, and cite the general standard's own language ("originality,
novelty, significance") as the bar the paper needs to visibly clear.

**A concrete, dated, CS-specific tightening worth naming even though it
likely does not apply directly:** on **2025-10-31** arXiv announced *"Updated
Practice for Review Articles and Position Papers in arXiv CS Category."*
Per that post: review/survey articles and position papers must now be
*"accepted at a journal or a conference"* with *"successful peer review"*
and *"peer reviewed journal reference and DOI metadata"* supplied at
submission, or they are *"likely to be rejected."* Stated reason: an
*"unmanageable influx of review articles and position papers"* to arXiv CS,
many *"little more than annotated bibliographies."* The post does not draw an
explicit line between this and an original-research systems paper with
empirical results, but by its own framing (survey/position content lacking
*"new research results"*) it targets a different genre than the Kontablo
spoke paper, which reports a specific empirical validation (round-trip audit
numbers, consolidation percentages) rather than surveying or advocating.
**Action item, not a finding:** make sure nothing in the paper's framing
(abstract, intro) reads as primarily a position/opinion piece about how
agentic accounting *should* work — keep the empirical results load-bearing
in the framing, which the paper's existing structure (per `TASKS.md` T1–T7,
already merged) appears to already do.

**Appeals exist but are a dead end if things go wrong, not a safety net to
rely on:** *"Please note that decisions upon appeal are final, and that no
feedback will be provided with the decision."* — do not plan around
appealing a decline; plan around not triggering one.

---

## (d) License options

Source: `https://info.arxiv.org/help/license/index.html`, full text fetched
via `curl`.

All licenses available, verbatim descriptions from the page:

| License | arXiv's description (verbatim) | Commercial reuse | Notes |
|---|---|---|---|
| **CC BY 4.0** | *"This license allows reusers to distribute, remix, adapt, and build upon the material in any medium or format, so long as attribution is given to the creator. The license allows for commercial use."* | Yes | Listed first; arXiv notes many journals accept preprints deposited under CC BY — *"Check directly with the journal to find out."* |
| **CC BY-SA 4.0** | Same reuse rights as CC BY, *"If you remix, adapt, or build upon the material, you must license the modified material under identical terms."* | Yes | ShareAlike obligation on derivatives. |
| **CC BY-NC-SA 4.0** | Distribute/remix/adapt *"for noncommercial purposes only,"* ShareAlike on derivatives. | No | |
| **CC BY-NC-ND 4.0** | *"copy and distribute the material in any medium or format in unadapted form only, for noncommercial purposes only."* | No | No derivatives permitted; arXiv notes this is common for publisher-embargoed *"accepted manuscripts."* |
| **arXiv.org perpetual, non-exclusive license 1.0** | *"This license gives limited rights to arXiv to distribute the article, and also limits re-use of any type from other entities or individuals."* | N/A (most restrictive re-use) | Accommodates funder/government requirements that forbid a more open license; author can still state a preferred license on the paper's first page. |
| **CC Zero (CC0)** | *"a public dedication tool, which allows creators to give up their copyright and put their works into the worldwide public domain... with no conditions."* | Yes (public domain) | *"If you choose this license, you will no longer control the article's copyright"* — arXiv explicitly flags this conflicts with most publishers' copyright-transfer requirements. |

Two governance facts worth carrying into `T9`: *"The license chosen is
irrevocable and cannot be changed"* per version, and *"different versions of
the work can have different licenses"* (so a v2 could in principle change
license even though a given version cannot). Separately, *"A Creative Commons
CC0 1.0 Universal Public Domain Dedication will apply to all metadata"*
regardless of which license is chosen for the article body — this is
standard across essentially all scholarly repositories (Zenodo does the
same, confirmed independently below) and not arXiv-specific.

**Verdict for this project:** CC BY 4.0 is confirmed available with no
disqualifying condition found, and it is already the license this project
uses for the paper text everywhere else it is distributed (Zenodo, SSRN,
ResearchGate — confirmed by reading `docs/papers/LICENSE` in this worktree,
which states CC BY 4.0 explicitly and gives the rationale for keeping the
code license, BSL 1.1, separate from the paper license). No conflict, no
extra work needed for `T9` beyond stating the same license arXiv-side.

---

## (e) Cross-listing rules

Source: `https://info.arxiv.org/help/cross.html` (full text via `curl`);
timing detail corroborated only by a secondary source (see below).

**What arXiv's own page says, verbatim, is the entire content of the primary
source on this topic:** *"You may feel that your article is of direct
interest to the readers of a category other than the one to which you
submitted your article. In such cases you may cross-list your article to the
other category so that your article appears in the regular listing for that
category (in the cross-list section)."* On volume: *"it is rarely
appropriate to add more than one or two cross-lists"* and *"Bad cross-lists
will be removed"* — advisory, not a hard numeric cap, but the guidance is
explicit that restraint is expected. Mechanism: *"You can cross-list an
article using the cross-list facility on your user page."*

**What the primary page does *not* say, and where I had to rely on a weaker
source:** whether that "cross-list facility" is reachable during the
original submission flow (same session) or only afterward via account
management, and whether endorsement is required separately per cross-listed
category. `info.arxiv.org/help/submit/index.html`'s own submission-guidelines
page references cross-listing only by a link, with no procedural detail. A
personal set of notes on the submission process (not an arXiv page —
`math.berkeley.edu/~gbergman/papers/arXiv.html`, explicitly labeled
secondary in this note) describes the mechanic as: *"At the end of the
submission process, they display your submission... and give you the
opportunity of adding one or more 'cross-listings'... You only get a chance
to add one cross-listing at a time; but once you submit the meta-data with
one cross-listing, the resulting page allows you to add another, and so
on"* — i.e. cross-lists **can** be requested in the same submission session,
one at a time, and by community convention (not a stated arXiv rule) up to
about two is the accepted norm. A `WebSearch` synthesis separately claimed
cross-listing does not require its own endorsement, reasoning that
endorsement is tied to a paper's *primary* category — this is plausible and
consistent with how the mechanism is generally described in secondhand
accounts, but **I could not find a single arXiv primary-source sentence that
states this explicitly**, so it is recorded here as inferred, not confirmed.

**The three candidate cross-lists, verified directly against
`https://arxiv.org/category_taxonomy`** (fetched raw via `curl`, exact
verbatim descriptions):

- **`cs.AI`** (Artificial Intelligence): *"Covers all areas of AI except
  Vision, Robotics, Machine Learning, Multiagent Systems, and Computation and
  Language (Natural Language Processing), which have separate subject
  areas. In particular, includes Expert Systems, Theorem Proving..., Knowledge
  Representation, Planning, and Uncertainty in AI."* Note the taxonomy text
  itself explicitly *excludes* Multiagent Systems from `cs.AI`'s scope,
  which is a mild argument for keeping `cs.MA` primary and `cs.AI` secondary
  (consistent with the plan already recorded in `TASKS.md` T9).
- **`cs.CE`** (Computational Engineering, Finance, and Science): *"Covers
  applications of computer science to the mathematical modeling of complex
  systems in the fields of science, engineering, and finance. Papers here
  are interdisciplinary and applications-oriented..."* Good topical fit for
  an accounting-ontology paper.
- **`q-fin.GN`** (General Finance): *"Development of general quantitative
  methodologies with applications in finance"* — the shortest category
  description of the three; a plausible but thin fit, since Kontablo's
  contribution is more an ontology/systems result than a "quantitative
  methodology" in the q-fin sense. Worth a one-line justification in the
  submission metadata if used.

---

## (f) Timelines

Source: `https://info.arxiv.org/help/availability.html`, full text via
`curl`.

**Announcement schedule (all times US Eastern):**

| Submission window | Announced | Mailed |
|---|---|---|
| Mon 14:00 – Tue 14:00 | Tue 20:00 | Tue night / Wed morning |
| Tue 14:00 – Wed 14:00 | Wed 20:00 | Wed night / Thu morning |
| Wed 14:00 – Thu 14:00 | Thu 20:00 | Thu night / Fri morning |
| Thu 14:00 – Fri 14:00 | Sun 20:00 | Sun night / Mon morning |
| Fri 14:00 – Mon 14:00 | Mon 20:00 | Mon night / Tue morning |

*"Submissions to arXiv are typically posted publicly Sunday through
Thursday, with no announcements Friday or Saturday."* Processing time:
*"Quality assurance checks can take between one to four days to resolve,
sometimes longer."* arXiv IDs are only assigned on announcement and *"cannot
be back-dated"* — the ID reflects the month of first public announcement,
which can differ from the submission month if a hold spans a month boundary.
2026 deferred-mailing holidays are listed on the same page (nine dates,
including 2026-01-01, 2026-06-19, 2026-07-03, 2026-11-26, 2026-12-25,
2026-12-29, 2026-12-31, plus two others) — none of these are close enough to
today (2026-07-29) to matter for near-term planning except that late-year
submissions should budget slack around the late-December cluster.

**The real bottleneck is not this schedule.** Once endorsed and submitted,
a paper clears in roughly a week including QA. The unbounded variable is
finding a willing personal endorser, which has no schedule at all — this is
the entire justification for the Zenodo-first sequencing in §(g).

**arXiv's general moderator-response-time note, from the 2019-08-29 official
blog post "Our Moderation Process"** (arXiv's own blog — primary source, blog
format): moderators *"resolve issues within 24 hours"* of a submission
landing in their queue before the daily 14:00 ET cutoff, and unresolved
submissions go *"on hold"* until the next cycle. This is consistent with,
not contradictory to, the 1–4-day QA window on the current help page; treat
the 2019 post as background color on *how* the queue works, and the current
`availability.html` page as the authoritative current SLA.

---

## (g) The de-risked publication plan

This is the requested deliverable, built from (b)–(f) above plus what is
already true about this project's Zenodo setup (confirmed live, not
assumed):

**Step 0 — already done, verify it stays true for the spoke paper.** The
hub paper's Zenodo record (`https://zenodo.org/doi/10.5281/zenodo.20738795`,
fetched and confirmed live this session: title *"Kontablo: A Graph-Based
Universal Accounting Ontology for the M2M Agentic Economy,"* currently
version v0.3.0 published 2026-07-21, CC BY 4.0 stated for the paper text
alongside the separately-licensed BSL 1.1 code) demonstrates the mechanism
works end-to-end for this project already. Per Zenodo's own documentation
(`https://support.zenodo.org/help/en-gb/1-upload-deposit/97-what-is-doi-versioning`,
fetched via `curl`): *"a DOI representing the specific version of your
record"* (Version DOI) and *"a DOI representing all of the versions of your
record"* (Concept DOI) are both minted on first publish, with a new Version
DOI on every subsequent version. **Recommendation, not confirmed by Zenodo's
docs (they do not address this case directly):** the Spoke 1 paper is a
distinct work, not a revision of the hub paper, so it should get its **own,
new Zenodo deposit with its own new concept DOI** — reusing the hub's
concept DOI would be a citation-graph error (a "version" of an unrelated
paper). This costs nothing beyond one more Zenodo upload and gives the spoke
paper a permanent, resolvable, versionable, DOI-bearing public record with
**zero endorsement gate, zero moderation queue of the arXiv kind, and no
minimum wait** — this should happen at or before the moment the paper is
considered "released," independent of arXiv status.

**Step 1 — pursue arXiv endorsement in parallel, non-blocking.** Given §(b),
the only realistic path is personal endorsement. Concrete, low-cost tactics
consistent with arXiv's stated etiquette (*"it is inappropriate to email
large numbers of potential endorsers at once"*): (i) identify authors of
recent `cs.MA` papers whose work is topically adjacent — DR1–DR4 already
surfaced candidate names and papers in the related-work literature search
that could double as a source of plausible endorsers; (ii) AAMAS 2026
workshop organizers/PC members (DR3's shortlist: GAIW, LaMAS, Trustworthy
Agentic AI, Agents in the Wild) are, by construction, active `cs.MA`-adjacent
arXiv authors and a natural first outreach list; (iii) treat this as an
ongoing background task with no deadline pressure, precisely because Step 0
already makes the paper citable without it.

**Step 2 — submit to arXiv the moment endorsement lands.** No new work is
needed at that point beyond the mechanical submission: CC BY 4.0 (§(d),
already the project's standard), primary `cs.MA`, cross-lists `cs.AI` /
`cs.CE` / `q-fin.GN` (§(e), all three verified as real, relevant categories).
Budget the 1–4 day QA window (§(f)) and do not assume weekend announcement.

**Step 3 — layer a workshop for faster, topically-exact community exposure,
independent of arXiv's timeline.** DR3 already built a five-venue shortlist
(AAMAS main track, GAIW, LaMAS, AAAI-26 Trustworthy Agentic AI, Agents in the
Wild) and found, as of 2026-07-24, that **every one of those deadlines had
already passed** for the current cycle — DR3's own words: *"every deadline
listed has already passed relative to the 2026-07-24 access date... these
establish the typical cycle timing for planning the next one."* This note's
own venue search (below, §(h)) independently found one genuinely open,
non-archival window in a different conference family DR3 did not cover
(NeurIPS, not the AAMAS/AAAI/ICLR/ICML cycle DR3 searched) that closes
**2026-08-22** — about three and a half weeks from this note's research
date. None of the venues in either DR3's shortlist or §(h) below route
through arXiv's submission system, so none of them are gated by the
endorsement problem at all — DR3's own framing applies here too: *"'does
this venue require arXiv endorsement' is category-inapplicable... not merely
'no' by policy."*

**Sequencing summary:** Zenodo (now, no gate) → workshop submission if a
topical, open window exists (weeks, no arXiv gate) → arXiv (whenever
endorsement clears, no fixed timeline, does not block the other two).
Nothing in this plan requires arXiv endorsement to happen before the paper
is public, citable, and has a DOI.

---

## (h) Candidate 2026 open venues beyond DR3's shortlist

DR3 (`dr3_mas_venues_priorart.md`, §d) already covers the AAMAS/AAAI/ICLR/
ICML-family workshops in depth and found all their 2026-cycle deadlines
already passed as of 2026-07-24. This note searched adjacent conference
families (NeurIPS's own cycle, ACM's finance-AI conference, and recent
provenance/accountability-focused workshops) to find what, if anything, is
**still open** relative to this note's 2026-07-29 research date. All rows
below were fetched directly from the venue's own site.

| Venue | Host / dates | Deadline | Archival? | Topical fit | Status vs. 2026-07-29 |
|---|---|---|---|---|---|
| **SLM-Agents: 1st Workshop on SLMs for Agentic Systems** | NeurIPS 2026, Paris, Dec 12–13 2026 | **2026-08-22 (AoE)** | **No** — *"Accepted workshop submissions are non-archival and may be submitted elsewhere after the workshop"* | Weak-to-moderate. Scope is "small language models as the foundation of agentic AI systems" — Kontablo's harness is explicitly *not* LLM-dependent for its deterministic core (I1/I2/I3), so this would need a framing angle (e.g. "how a deterministic ontology-as-constraint layer relieves an agentic system of needing a larger model for this specific decision") rather than a direct topical match. | **Open, ~3.5 weeks out.** The only genuinely open, non-archival, topically-adjacent window found in this session. |
| **ICAIF '26** (7th ACM Intl. Conf. on AI in Finance) | ACM, Bocconi University, Milan, Nov 14–17 2026 | **2026-08-02** | Yes (ACM proceedings, archival) — page identifies it as an "ACM International Conference," standard ACM practice is archival proceedings, not independently confirmed on the fetched page | Strong topical fit (finance + AI agents track named explicitly: *"AI Agents & Reinforcement Learning"*), but **archival**, so it is a different category from the "non-archival, no-blocking" venues this plan otherwise favors — publishing here first could complicate a later journal submission depending on the target journal's prior-publication policy. | **Open but only ~4 days out from this research date** — realistically too tight to prepare a submission responsibly; recorded for the **2027 cycle** (ICAIF runs annually; treat 2026-08-02 as this cycle's now-unrealistic deadline and expect a similarly-timed 2027 CFP). |
| **TAAPAAI @ ESWC'26** (Trust, Autonomy and Accountability in PKG-Based Agentic AI) | ESWC 2026, Dubrovnik, May 10–14 2026 | 2026-03-13 (already passed) | Yes — CEUR Workshop Proceedings, DBLP-indexed | Strong topical fit on *provenance/accountability* language (*"verifiable provenance,"* *"traceable, auditable links between actions and inferences"*) but framed around Personal Knowledge Graphs for personal/consumer agents, not financial/accounting semantics — would need reframing. | **Passed for 2026.** Second edition of a recurring workshop — worth watching for a 2027 edition given the strong I2/I3 topical overlap. |
| **GAIW @ AAMAS 2026** | Already covered by DR3 | 2026-02-11 (passed) | No | Covered in DR3 | Passed; DR3's advice to watch the 2027 cycle stands. |

**Reading on the NeurIPS SLM-Agents option specifically:** it is the only row
in this table that is simultaneously (a) genuinely open as of the research
date, (b) explicitly non-archival by the venue's own stated policy, and (c)
hosted by a top-tier, unambiguously legitimate conference (NeurIPS). Its
topical center of gravity (small *language* models) is not a tight match for
a paper whose central claim is that a deterministic, non-LLM layer resolves
~99% of cases — but that tension could be turned into the submission's own
framing rather than treated purely as a mismatch, since "when and why the
agentic system should *not* need to call a language model at all" is a
legitimate SLM-workshop question. This is a judgment call for whoever writes
the actual submission, not a research finding — flagged here as an option,
not a recommendation to submit.

---

## Sources

All fetched live this session (2026-07-29) via `curl` (raw HTML, then
stripped to plain text locally) or `WebFetch`/`WebSearch` as noted. "Primary"
= arXiv's/Zenodo's/the venue's own official page. "Secondary" = independent
commentary, forum posts, or personal notes, called out inline above wherever
used.

| # | Source | Type | Used for |
|---|---|---|---|
| 1 | `https://info.arxiv.org/help/endorsement.html` | Primary (arXiv official help, fetched raw via `curl`) | §(b) — full endorsement mechanics, verbatim quotes |
| 2 | `https://info.arxiv.org/help/moderation/index.html` | Primary (arXiv official help, fetched raw via `curl`) | §(c) — moderation criteria, decline grounds, appeals |
| 3 | `https://info.arxiv.org/help/policies/content-types.html` | Primary (arXiv official help, fetched raw via `curl`) | §(c) — accepted/not-accepted content types |
| 4 | `https://info.arxiv.org/help/license/index.html` | Primary (arXiv official help, fetched raw via `curl`) | §(d) — full license table, verbatim |
| 5 | `https://info.arxiv.org/help/cross.html` | Primary (arXiv official help, fetched raw via `curl`) | §(e) — cross-listing mechanism and etiquette |
| 6 | `https://info.arxiv.org/help/availability.html` | Primary (arXiv official help, fetched raw via `curl`) | §(f) — announcement schedule, QA timing, 2026 holidays |
| 7 | `https://info.arxiv.org/help/submit/index.html` | Primary (arXiv official help, fetched raw via `curl`) | §(e) — confirmed no submission-time cross-list procedural detail beyond a link |
| 8 | `https://arxiv.org/category_taxonomy` | Primary (arXiv official taxonomy, fetched raw via `curl`) | §(e) — verbatim `cs.MA`, `cs.AI`, `cs.CE`, `q-fin.GN` category descriptions |
| 9 | `https://arxiv.org/list/cs.MA/recent` and `.../2026-01` | Primary (arXiv live listing pages) | Confirmed `cs.MA` is an active category with regular submissions (211 papers in Jan 2026 alone); sampled recent titles/cross-lists |
| 10 | `https://blog.arxiv.org/2026/01/21/attention-authors-updated-endorsement-policy/` | Primary (arXiv's own blog, official but blog format) | §(a)/(b) — the institution-wide, dated policy tightening that hardens the independent-researcher barrier |
| 11 | `https://blog.arxiv.org/2025/12/10/updated-endorsement-policy-for-arxiv-mathematics/` | Primary (arXiv's own blog) | §(b) — the Math-only pilot that preceded and foreshadowed source #10; confirms the two-path structure and its stated rationale |
| 12 | `https://blog.arxiv.org/2025/10/31/attention-authors-updated-practice-for-review-articles-and-position-papers-in-arxiv-cs-category/` | Primary (arXiv's own blog) | §(c) — the CS-specific review/position-paper tightening, dated and quoted |
| 13 | `https://blog.arxiv.org/2019/08/29/our-moderation-process` | Primary (arXiv's own blog, older) | §(f) — background on moderator queue mechanics (24-hour resolution target, "on hold" status); corroborates, does not override, source #6 |
| 14 | `https://math.berkeley.edu/~gbergman/papers/arXiv.html` | **Secondary** (personal notes by an individual mathematician, not arXiv) | §(e) — the only source found describing cross-list timing (offered at end of initial submission, one at a time, informal 2-cross-list norm); explicitly caveated as non-official everywhere it is used |
| 15 | `https://support.zenodo.org/help/en-gb/1-upload-deposit/97-what-is-doi-versioning` | Primary (Zenodo official support docs, fetched via `WebFetch`) | §(g) — Concept DOI vs. Version DOI mechanics |
| 16 | `https://zenodo.org/doi/10.5281/zenodo.20738795` | Primary (this project's own live Zenodo record) | §(g) — confirms the Zenodo-first mechanism already works for this project today |
| 17 | `https://slmw2026.github.io/` | Primary (workshop's own site) | §(h) — SLM-Agents @ NeurIPS 2026: dates, deadline, explicit non-archival statement, scope |
| 18 | `https://icaif2026.org/` | Primary (conference's own site) | §(h) — ICAIF '26: deadline, scope, ACM-conference status |
| 19 | `https://taapaai.github.io/` | Primary (workshop's own site) | §(h) — TAAPAAI @ ESWC'26: deadline (passed), archival status (CEUR/DBLP), scope |
| 20 | `https://gtep-workshops.github.io/gaiw2026/` | Primary (workshop's own site) | §(h) cross-check against DR3's GAIW row (dates/scope consistent) |
| 21 | `https://conf.researchr.org/home/icse-2026/agent-2026` | Primary (ICSE 2026's own site) | Checked and excluded from §(h): archival (ACM proceedings), deadline already passed (2025-11-07) |
| 22 | `docs/papers/LICENSE` (this repo, read directly, not fetched from the web) | Primary (this project's own file) | §(d) — confirms CC BY 4.0 is already the paper's license across Zenodo/SSRN/ResearchGate, and the stated rationale for keeping it separate from the BSL 1.1 code license |
| 23 | `dr3_mas_venues_priorart.md` (this repo, read directly) | Primary (this project's own prior research note, dated 2026-07-24) | §(g)/(h) — the existing AAMAS/AAAI/ICLR/ICML venue shortlist this note builds on rather than duplicates; direct quotes quoted and attributed above |
| 24 | `WebSearch`: `"not appropriate for this archive" arxiv moderation reclassification meaning` | Secondary (search-engine synthesis of multiple sources, no single primary page found) | §(c) — could not find one arXiv page using this exact phrase; treated as community shorthand for the reclassification/decline discretion documented in source #2 |
| 25 | `WebSearch`: cross-listing endorsement question | Secondary (search-engine synthesis) | §(e) — the "cross-lists don't need separate endorsement" claim; explicitly flagged as unconfirmed against a primary source |
| 26 | `WebSearch`: `cs.AI`/`cs.MA` "separate endorsement domains" | Secondary (search-engine synthesis, no single authoritative page cited) | §(b) — flagged as unverified in the endorsement-domain-granularity discussion |

---

## Residual unknowns

- **UNVERIFIED — endorsement domain granularity for `cs.MA`.** I could not
  find a primary arXiv page that explicitly lists endorsement domains by
  category, or that states definitively whether `cs` is a single endorsement
  domain or each `cs.XX` subcategory is its own. What I tried: reading
  `endorsement.html` in full (it describes the *general* rule — *"most
  high-level subject areas... are currently endorsement domains, with the
  notable exception of physics"* — without naming CS's specific case);
  searching for a dedicated "list of endorsement domains" page (found none —
  only a `WebSearch` synthesis asserting `cs.AI`/`cs.MA` are separate, which
  cited no single authoritative source); noting one incidental data point, a
  URL pattern (`arxiv.org/auth/show-endorsers/cs/0610026`) using a
  pre-2007-style archive-level ID (`cs/NNNNNNN`, not `cs.MA/NNNNNNN`), which
  is weakly suggestive but not proof either way, and is itself a relic of
  the old flat-archive ID scheme rather than current category structure.
  **Does not change the recommended action** (§(g) Step 1) since the
  practical step — find one qualifying, willing endorser in the target
  category — is identical either way.
- **UNVERIFIED — whether cross-listed categories require their own
  endorsement.** See §(e) and source #25. I found no primary arXiv sentence
  that resolves this either way. If the eventual submission plan depends on
  this (e.g. wanting to cross-list into a category where no endorser has
  been found), verify by starting an actual arXiv submission session — the
  system itself will presumably enforce or not enforce this at submission
  time — before relying on the secondary-source answer.
- **UNVERIFIED — whether cross-lists can be added during the same
  submission session versus only afterward via the account page.** Section
  (e) relies on one secondary source (personal notes) for the "same session,
  one at a time" claim; arXiv's own `cross.html` only says the facility
  lives "on your user page," which is ambiguous about timing. Low-stakes
  ambiguity — either way, cross-listing is confirmed possible and not gated
  by anything beyond the primary submission's own endorsement.
- **Not investigated: the exact literal wording of the "not endorsed for
  this archive" message the Kontablo hub paper received.** This note treats
  that fact as given context from the task prompt (a prior session's
  experience) rather than something to re-derive, and did not find an
  arXiv page that reproduces that exact error string (it appears to be
  submission-flow UI copy, not documented help-page text) — a `WebSearch`
  for the literal phrase surfaced no primary source using those exact words,
  only community discussion consistent with the endorsement mechanics
  documented in §(b).
- **Not fully investigated: NeurIPS 2026's complete workshop list.** §(h)
  found SLM-Agents by name via search and confirmed it directly; I did not
  enumerate every accepted NeurIPS 2026 workshop (the official list link,
  `neurips.cc/Conferences/2026/CallForWorkshops`, was found but not crawled
  exhaustively) so there may be additional, better-topically-fitting
  NeurIPS 2026 workshops with similarly open windows not surfaced here. If
  the workshop-layer plan becomes a live priority, a dedicated pass over the
  full NeurIPS 2026 workshop list (available closer to the Aug/Sep 2026
  window) would be worth the hour.
- **Not investigated: whether ICAIF's archival status would actually
  conflict with a later journal submission of the same material.** Flagged
  as a consideration in §(h) but not researched — this would depend on the
  specific target journal's prior-publication policy, which is out of scope
  for this note and, in any case, moot for the current cycle given the
  ~4-day-away deadline.
- **Recommendation, not a verified Zenodo policy statement:** the claim in
  §(g) that the spoke paper should get its own new Zenodo concept DOI rather
  than a new version of the hub's existing one is this note's own reasoning
  from how Zenodo versioning is documented to work (a "version" is for
  revisions of the *same* record) — Zenodo's own docs do not directly
  address the "companion paper" case, so this is inference, not a quoted
  Zenodo policy.
