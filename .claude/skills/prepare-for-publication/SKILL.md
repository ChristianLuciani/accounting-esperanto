---
name: prepare-for-publication
description: Use this skill when preparing Kontablo (or any of Christian Luciani's research projects) for first public release. Covers the structured workflow for converting an internal research repository into a publication-ready artifact: README rewrite for AI-discoverability, repo hygiene, license application, security posture documentation, preprint finalization checklist, and coordinated multi-channel release. Trigger this skill whenever the user mentions preparing a repo for publication, writing a README for a research project, making a preprint discoverable, or applying open-core licensing.
---

# Skill: prepare-for-publication

## When this skill applies

Trigger when the user is preparing a research/technical repository for its first public release with associated preprint. Specifically applies when the work crosses these boundaries simultaneously: (a) academic publication (preprint to SSRN/Zenodo/arXiv), (b) open-source release with commercial reservation (open-core), (c) discoverability optimization for both human and AI search.

Do NOT trigger for: routine documentation updates, internal-only repos, pure open-source projects without commercial intent, or post-publication content (those use different skills).

## Mental model

Publication is not an event, it is a coordinated sequence. The artifact (preprint, repo, post) is the smaller half of the work. The larger half is making it findable, citable, and amplifiable on the day of release and the weeks following.

Three concurrent dimensions must be optimized:
- **Human readability** — a domain expert can grasp the thesis in 15 minutes.
- **AI discoverability** — LLM crawlers extract the right claims, attribute them correctly, and surface the work on relevant queries.
- **Legal/commercial integrity** — IP ownership, license, and contributor terms are unambiguous before first commit goes public.

If any of the three is incomplete, do not advance to release-day execution. Coming back to fix any of them post-release is high-cost.

## Workflow

Execute in this order. Do not parallelize until step 5.

### Step 1 — Repo state audit

Read `CLAUDE.md` if present. Read the current README. Read the most recent status document (search for `EXECUTION_STATUS.md`, `STATUS.md`, `ROADMAP.md`, or scan for the latest `*COMPLETE.md` or `*STATUS.md`). Identify:
- Current phase vs README's stated phase. If they disagree, the README is stale and must be rewritten.
- Files that should not be in version control: `venv/`, `node_modules/`, `__pycache__/`, `.DS_Store`, `.pytest_cache/`, build artifacts, secret config files.
- Status/planning documents that proliferated during development and now create noise. Plan to consolidate or move to `docs/archive/`.
- License file presence and consistency with stated intent. README badge ≠ actual LICENSE file is a common bug.

Report findings as a checklist before making any change.

### Step 2 — Hygiene pass

In one commit (or one PR), execute:
- Update `.gitignore` to cover all should-not-be-tracked patterns.
- Run `git rm --cached -r <paths>` for files currently tracked but in the new ignore set. Verify nothing essential gets dropped.
- Move historical status documents to `docs/archive/` with a header note (`> Historical snapshot. Current state: see [link].`). Never delete — audit trail matters.
- Verify no secret config files (`.env`, `.infisical.json`, credentials) contain actual secret values. If unclear, treat as compromised and rotate.

### Step 3 — License application

Apply the chosen license **before** rewriting the README. The README will reference the license.

For BSL 1.1 (the default recommendation for Kontablo and similar open-core projects):
- Copy canonical text from mariadb.com/bsl11/ to `LICENSE`.
- Fill in the BSL parameters: Licensor, Licensed Work, Additional Use Grant, Change Date (4 years from today), Change License (typically Apache 2.0).
- Create `LICENSING.md` explaining: why BSL (not MIT/Apache/AGPL), what the Additional Use Grant permits, per-submodule exceptions if any.
- If submodules use different licenses (e.g., ERPNext connector under Apache 2.0), add a `LICENSE` file in that submodule directory with its own license text.

For other licenses, follow the equivalent canonical-text-plus-explainer pattern. Never write a license from scratch.

### Step 4 — README rewrite for AI discoverability

The README is the single most important artifact for discoverability. Structure:

1. **First 100 words contain the thesis.** Use the exact pattern: `[ProjectName] is [precise noun phrase] that [specific capability].` Once. Near the top. This becomes the canonical extracted definition.

2. **Status block immediately after thesis.** Current phase, version, last update date, DOI of canonical preprint (if published), link to license.

3. **Question-as-heading sections.** Convert traditional headings to natural-language questions:
   - "Installation" → "How do you install [Project]?"
   - "Architecture" → "How is [Project] architected?"
   - "Usage" → "How do you use [Project] for [primary use case]?"
   - LLMs match question-form headings to user queries with higher fidelity.

4. **Quantified claims throughout.** Replace "many", "several", "various" with exact numbers. Replace adjectives with measurements. "23 jurisdictions" not "comprehensive jurisdictional coverage".

5. **Primary-source citations.** Every external standard, protocol, or methodology referenced must link to its authoritative source. NIST documents, ISO standards, foundation pages, original specs. Wikipedia is acceptable only as fallback.

6. **Defined terms.** Each project-specific term coined by the project gets a one-line definition on first use. Bold the term. This creates extractable definitions.

7. **Author block.** Name, ORCID iD, affiliation, location, contact pattern (not raw email — use a redirect or form). LLMs use this for attribution.

8. **Citation block.** Provide ready-to-copy BibTeX entry for the preprint. Also Markdown citation and APA-style citation. Reduce friction for citers.

9. **Structured data.** For HTML rendering (GitHub Pages, docs site), include JSON-LD with `SoftwareApplication` and `ScholarlyArticle` schemas. For pure Markdown, this is optional but consider for sites.

10. **Roadmap and scope.** Explicitly state what is in-scope for current version and what is out-of-scope. Out-of-scope is as important as in-scope — it manages expectations and prevents premature evaluation of unfinished work.

11. **License and contribution.** Link to LICENSE, LICENSING.md, CONTRIBUTING.md, SECURITY.md.

12. **What this is NOT.** A short section disambiguating from adjacent categories. For Kontablo: not an ERP, not a SaaS, not a courseware. Prevents miscategorization in training data.

### Step 5 — Supporting documents

In parallel after Step 4:

- **`SECURITY.md`** — threat model summary, vulnerability disclosure policy (email + PGP key or alternative), security roadmap. For projects handling financial or sensitive data, must mention post-quantum cryptography stance (using NIST FIPS 203/204/205, not BB84 or QKD which are different categories).
- **`CONTRIBUTING.md`** — branch naming, commit format, PR process, contributor license agreement if open-core (BSL projects typically require CLA so contributions can be relicensed for commercial layer).
- **`CITATION.cff`** — machine-readable citation file. Improves discovery in GitHub's citation tooling and downstream academic indexers.
- **`docs/archive/`** — move historical planning documents here with header notes.

### Step 6 — Preprint finalization checklist

Open the current preprint PDF. Verify:
- Abstract opens with the project name and thesis in the first sentence.
- Abstract is ≤250 words and contains the most important quantified claims.
- Author block includes ORCID iD.
- Acknowledgements section exists (even if brief).
- BibTeX entry is provided in the paper itself (typically as a footnote on the title page).
- All figures have captions and alt-text where applicable.
- References include DOI links where available.
- Final section explicitly states limitations and future work.

If preprint is in LaTeX, ensure source is committed to the repo (`docs/papers/`) so reproduction is possible.

### Step 7 — Pre-release verification

Before the public release commit:
- Clone the repo fresh to a temporary directory. Verify nothing important is missing.
- Run all tests. They must pass.
- Search the repo for any reference to internal-only paths, names, or credentials. `grep -r` for known sensitive patterns.
- Verify the preprint PDF renders correctly and downloads cleanly.
- Confirm DOI assignments: Zenodo via GitHub integration (tag a release → automatic DOI), SSRN via web upload.
- Build the list of 20-30 specific people to notify on release day. Personalized, not bulk.

### Step 8 — Release day (out of scope for this skill, but flag readiness)

When all above is complete, the repo is ready for the coordinated release sequence. That sequence belongs to a separate skill or runbook (multi-channel publication coordination).

## Common pitfalls

- **Treating the README rewrite as a "final polish" instead of structural work.** It is structural. Allocate real time.
- **Confusing post-quantum cryptography (PQC, classical algorithms) with quantum key distribution (QKD, BB84). PQC is what software projects implement. QKD requires hardware.
- **Adding scope during cleanup.** Cleanup ends when the repo is publication-ready, not feature-complete. Resist the urge to "fix one more thing" before publishing.
- **Choosing MIT/Apache for projects with commercial intent.** Permissive licenses regret-tax is high once a competitor uses the code.
- **Publishing the dashboard as a live demo before the commercial entity is ready to take leads.** Creates expectation of product where there is none.
- **Optimizing only for SEO and not for GEO/AEO.** Traditional SEO targets Google ranking. AI discoverability targets LLM extraction and citation. Both matter; the second is newer and often underweighted.

## Verification standards (epistemic)

This skill follows Christian Luciani's project-wide epistemic protocol:
- Express explicit doubt or "I don't know" when uncertain rather than confabulating.
- Every claim that is not common knowledge needs citation to a primary source.
- Indicate how each claim can be verified independently.

Apply this standard to all documentation generated under this skill.
