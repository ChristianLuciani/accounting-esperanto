# Citation title correction checklist — "Multi-Jurisdictional Financial Integration"

> **Purpose.** Audit trail for the correction of the preprint's public title from
> *"Kontablo: A Graph-Based Universal Accounting Ontology for the M2M Agentic
> Economy"* back to the author's intended *"…for Multi-Jurisdictional Financial
> Integration"*. The "M2M Agentic Economy" variant belonged to the spoke/agentic
> work; it entered the preprint's deposit metadata by accident (`.zenodo.json`
> and the compiled PDF carried it while the author's correction lived in
> `README.md`/`CITATION.cff` from 2026-05-28/29).
>
> **Repo work: DONE (PR #117).** All active surfaces corrected: `CITATION.cff`,
> `README.md`, `.zenodo.json`, `kontablo_preprint_modular.tex` + recompiled PDF
> (65 pp), `abstract.tex`, `docs/index.html`, `docs/essays/…html`. Archive
> copies (`archive/`, `*_v01.md`) left untouched as history.
>
> **Platform work: PENDING — owner (Christian).** This checklist tracks it.

---

## Baseline (captured 2026-08-07, before platform edits)

| Surface | Title before | Verification |
|---|---|---|
| Crossref/SSRN (`10.2139/ssrn.6960598`) | …for the M2M Agentic Economy | `api.crossref.org/works/10.2139/ssrn.6960598` (confirmed) |
| Zenodo (`10.5281/zenodo.20738795`) | …for the M2M Agentic Economy | Zenodo API (403 from agent IP; confirm via browser) |
| ResearchGate (publication 407549570) | …for the M2M Agentic Economy | Browser (slug `…_M2M_Agentic_Economy` is canonical, will stay) |
| ORCID (0000-0002-6955-5384) | …for the M2M Agentic Economy | Auto-sync via Crossref/DataCite |

---

## 1. Zenodo — https://zenodo.org

**Goal:** change the title of the published record + re-upload the corrected PDF.

1. Log in → https://zenodo.org → "Log in" (GitHub/ORCID account).
2. Go to the record: **https://zenodo.org/records/20738795** (or "My uploads").
3. Click **"Edit"** (pencil icon, top right).
4. Field **"Title"**: replace
   `Kontablo: A Graph-Based Universal Accounting Ontology for the M2M Agentic Economy`
   with
   `Kontablo: A Graph-Based Universal Accounting Ontology for Multi-Jurisdictional Financial Integration`
5. Do **not** touch anything else (description, creators, license, version).
6. **"Save"** → **"Publish"** (confirm the published record update). The **DOI does not change** (`10.5281/zenodo.20738795`).
7. **PDF:** if the edit form allows file changes, upload
   `docs/papers/drafts/kontablo_preprint_modular.pdf` (repo-recompiled, 65 pp,
   corrected cover). ⚠️ If Zenodo creates a **new version** when files change, a
   **new version DOI** (10.5281/zenodo.XXXXX) will be minted — inform the agent
   so the repo can be updated. The concept DOI stays the same.

**Evidence requested:** screenshot of the record page (title visible); screenshot
of the PDF first page downloaded from Zenodo; new version DOI if any.

---

## 2. SSRN — https://hq.ssrn.com (or papers.ssrn.com)

**Goal:** change the paper title + submit the PDF revision.

1. Log in → https://hq.ssrn.com.
2. Menu **"My Papers"** / **"My Submissions"** → click the Kontablo paper (abstract 6960598).
3. Button **"Edit"** / **"Revise"**.
4. Field **"Title"**: replace "…for the M2M Agentic Economy" → **"…for Multi-Jurisdictional Financial Integration"**.
5. If the revision form allows attaching the corrected PDF (revision v1.9.4), upload it. Otherwise edit the title now and the PDF in a separate revision.
6. **Submit / Save.** The DOI `10.2139/ssrn.6960598` does **not** change.

**Evidence requested:** screenshot of the public abstract page (title visible);
agent verifies Crossref via API after the save.

---

## 3. ResearchGate — https://www.researchgate.net

**Goal:** change the displayed title of publication 407549570.

1. Log in → researchgate.net.
2. Go to **https://www.researchgate.net/publication/407549570** (or search it).
3. Menu **"..."** / **"Edit"** → **"Edit"**.
4. Field **"Title"**: replace → "…for Multi-Jurisdictional Financial Integration".
5. **Save.**
6. ⚠️ The **URL/slug** stays `…_M2M_Agentic_Economy` (not regenerated) — normal;
   the publication ID `407549570` is canonical.

**Evidence requested:** screenshot of the publication (title visible).

---

## 4. ORCID — https://orcid.org/0000-0002-6955-5384

**Goal:** confirm the work updates (no manual action if Crossref/DataCite sync).

1. Wait **24–72 h** after the SSRN (Crossref → ORCID) and Zenodo (DataCite → ORCID) changes.
2. Log in → orcid.org → record → **"Works"** section.
3. Find the Kontablo work → should show the **Multi-Jurisdictional Financial Integration** title.
4. **If NOT auto-updated** (after ~3 days): edit the work manually → "Edit" → correct the title → save. Prefer waiting for auto-sync first.

**Evidence requested:** screenshot of the work on the ORCID record (title visible).

---

## Programmatic verification (agent-side, no owner effort)

| Check | How | Status |
|---|---|---|
| Crossref (post-SSRN) | `api.crossref.org/works/10.2139/ssrn.6960598` → title | Run after owner confirms SSRN save |
| Zenodo API | `zenodo.org/api/records/20738795` → title | 403 from agent IP on 2026-08-07; retry after owner change or rely on screenshot |
| Repo | `grep "M2M Agentic Economy"` on active surfaces | DONE — 0 matches |
| PDF | pdftotext first page | DONE — corrected |

---

## Final closure checklist

- [ ] Zenodo: title corrected + screenshot
- [ ] Zenodo: corrected PDF uploaded + cover screenshot
- [ ] Zenodo: new version DOI (if any) → passed to agent for repo update
- [ ] SSRN: title corrected + screenshot
- [ ] Crossref: new title verified via API (agent)
- [ ] ResearchGate: title corrected + screenshot (M2M slug stays, OK)
- [ ] ORCID: work updated + screenshot (auto or manual)
- [ ] PR #117 merged
- [ ] Repo re-checked post-merge: zero "M2M Agentic Economy" on active surfaces
