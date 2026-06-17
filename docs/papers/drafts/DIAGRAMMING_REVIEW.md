# Diagramming review — Kontablo preprint v1.9.2 (64 pp)

Review-only pass (no source edits this round). Notes drive the next editing round.
PDF reviewed: `kontablo_preprint_modular.pdf` @ commit f2cdd3c.

## Explicit requests from author (must-do next round)
1. **Abstract** — shorten a little (it fills page 1 edge-to-edge; trim ~3–5 lines).
2. **Front-page rule** — the teal horizontal line should match the **author-name width**, not a fixed `0.18\textwidth`. (clapps `\maketitle`: make the rule width = width of `\@author`, or visually align.)
3. **Font sizes** — keywords block and the metadata/footnote block are **too large**; reduce (keywords → `\small`; metadata block → `\scriptsize`).
4. **Acknowledgements** — add **"Wes Roth"** before "Matthew Berman".
5. Carry-over: figure-font parity for the densest diagrams; trace the remaining 117pt overfull.

## Per-page notes

**p1 — Title + abstract.** Title block good. (a) Teal rule under title is `0.18\textwidth`, narrower than "Christian Luciani" — widen to ~author-name width (author request #2). (b) Abstract fills the page edge-to-edge, last line jammed against bottom margin — shorten ~3–5 lines for breathing room (request #1). Epigraph placement good.
**p2 — Keywords + metadata + Contents.** (a) Keywords at full 12pt body size — too large, → `\small` (request #3). (b) Author/Etymology/Cite-as block at `\footnotesize` still too large + bulky → `\scriptsize`, and consider compressing the BibTeX (monospace block is heavy). (c) ToC clean, teal, sections-only — good. Two faint rules frame the metadata block; keep one, make it match content width.
**p3 — ToC tail + §1.** (a) ToC spills only **2 entries (18,19)** onto p3 — awkward split; tighten ToC line spacing so it fits on p2, or pull one line. (b) **Big empty bottom half of p3**: the AI-summary lead-in ends "…do not compress them away:" and the `summarynote` box floated to p4, leaving ~45% whitespace. Real layout defect — keep the box with its lead-in (`\needspace`/`samepage`) or let it break.
**p4 — summarynote box + §2 intro.** (a) `summarynote` renders as **top+bottom rules only** (tcolorbox absent) — looks unfinished; either install tcolorbox or upgrade fallback to a full ruled border + tinted background. (b) §2 "at a glance" intro paragraph sits alone, then **whitespace to bottom** (Tables 1–2 floated to p5). Another gap.
**p5 — Table 1 + Table 2.** Booktabs tables, consistent `\small` font — good. Minor: narrow col 1 forces hyphenation ("Three-Tier Reso-lution", header "Determinism guaran-tee"). Widen col 1 ~3mm. Bottom of page whitespace (Table 3 floated to p6).
**p6 — Table 3 + §3 intro.** Scorecard table good; caption cites generating commands. §3.1 crises begin; trimmed Crisis #2 with pointer to §5.1 reads well.
**p7 — crises tail + §3.2/§3.3.** Clean body text, no issues.
**p8 — resolution tiers + §4 start.** Clean. Tier bullets readable.

### Cross-cutting so far
- **Float/whitespace gaps (p3, p4, p5):** `[H]`/float placement leaves half-empty pages around §1 box and §2 tables. Biggest professional eyesore. Consider moving the signature tables inline (not floats) or reflowing §2 so intro + Table 1 share a page.
- **summarynote** needs a real box (tcolorbox) for a finished look.

**p9 — §4.2 Babel persistence.** Clean body text, 3 numbered barriers. No issues.
**p10 — Figure 1 (historical timeline).** Wide timeline; **box body text is noticeably smaller than body copy** (figure shrunk by fitwidth because it is wide) → font-parity offender #2. Color-coded boxes (orange/blue/green) read well. Caption good.
**p11 — §4.4 + §5 + §5.1.** New cost subsection Layer 1 reads well. Clean.
**p12 — §5.1 Layers 2–3 + §5.2 FIV.** Good. Eq.(1) clean. The "tens of billions" order-of-magnitude lands well.
**p13 — §5.3 SME + §5.4 RTA.** Eqs (2)(3) fine. Clean.
**p14 — §5.5 + §5.6 IAS 21.** Clean body text.
**p15 — §6 + Figure 2 (rigid tree) + §7 heading.** (a) **Figure 2 is the worst font-parity offender** — clearly smaller text than Figure 3 (it is wider than the text block, so fitwidth shrinks it). Next round: reduce its internal width (tighten node spacing, move the pink "Rigid tree constraint" box below the leaf row instead of to the right) so it renders near full size. (b) **§7 "The Ontological Bridge: Tree to Graph" heading is orphaned at the very bottom of p15** with its content (Figure 3) on p16 — add a `\needspace`/intro sentence so the heading isn't stranded.
**p16 — Figure 3 (graph architecture) + §7.1.** Figure 3 renders near natural size (good reference). Minor: rotated edge labels ("Exact Lookup", "AI Semantic Fallback") sit on/over the dashed arrows — nudge clear of the lines. §7.1 math `G=(V,E,λ,μ)` clean.

### Figure font parity — running list of offenders (shrunk too small)
- Figure 1 (timeline, p10), Figure 2 (rigid tree, p15) are the clear small-font cases. Figure 3 (p16) is the right size — use it as the reference scale. Fix by narrowing the wide figures' content, not by scaling.

**p17 — dimensions list + "What the dimensions mean".** Clean. No issues.
**p18 — Figure 4 (single node, radial).** **Good** — readable boxes, balanced radial layout, font ~matches Figure 3. Keep as-is. Caption good.
**p19 — Figure 5 (mapping bridge) + §7.2.** Figure 5 small/simple, readable. ADR footnote at bottom fine.
**p20 — §7.3 import/export + §7.4 CRA.** Eq.(4), inline monospace, clean.
**p21 — §7.5 + §8 heading.** **§8 heading hyphenates across the line break: "…Translation Mecha-nism"** — headings should never hyphenate. Next round: make section headings ragged-right + `\hyphenpenalty=10000` (or reword). Check §1 and §11 headings too (multi-line).
**p22 — §8.2/§8.3/§8.4.** Display math (adjoint Σ_F/Δ_F) clean. No issues.
**p23 — §8.4/§8.5 + §9 start.** Heavy math, reads fine.
**p24 — §9.1–§9.4.** Clean body text.

### New cross-cutting items
- **Heading hyphenation** (§8 "Mecha-nism"): set headings ragged-right, no hyphenation, in clapps.cls.
- Figures 4 & 5 are correctly sized — confirms the fix works; only the *wide* figures (1, 2) need content-narrowing.

**p25 — §9.4/§9.5 + §10 start.** Clean body text.
**p26 — §10.2 tiers + §10.3 checklist.** Clean.
**p27 — Figure 6 (three-tier pipeline flowchart).** ⚠️ **DEFECT: the figure is too tall — its caption collides with the page number "27"** (the word "mapping" in the last caption line overprints the folio). `fig_three_tier_pipeline` has no size cap and renders at natural (tall) size, overflowing into the footer. Next round: cap its height (e.g. `\fitheight`/`\resizebox{!}{0.7\textheight}`) or shorten the caption. **Highest-priority single fix.**
**p28 — Figure 7 (tiers on concrete inputs).** Readable, good size. Minor: the green output boxes ("asset.current.cash / posted") sit hard against the right margin — verify they don't clip; nudge left ~2mm.
**p29 — §10.6 RAG + §11 start.** §11 heading wraps 2 lines (clean break, no hyphenation). Fine.
**p30 — §11.2.** Heading wraps 2 lines, clean. Body fine.
**p31 — §11.3 residual error.** Clean numbered list.
**p32 — §11.4 reframe.** Indented italic reframe block reads well; some bottom whitespace (end of subsection) — acceptable.

### New defect (priority)
- **Figure 6 / p27 caption overprints the page number** — a true overflow defect, fix first.
- **Figure 7 / p28** right-edge box proximity — verify no clip.

**p33 — §11.5.** ⚠️ Heading hyphenates: "…Residual Error **Manage-ment**" — second heading-hyphenation case (with §8). Confirms the fix is needed.
**p34 — §11.7/§12.** Clean (L0–L5 list reads well).
**p35 — §13/§13.1/§13.2.** Payload pseudo-equation clean.
**p36 — §13.3/§13.4 + §14 heading.** Micro-transaction sum equation clean.
**p37 — §14.1.** Clean body text.
**p38 — §14.2/§14.3.** Clean; inline monospace fields fine.
**p39 — §14.4.** Clean.
**p40 — §14.5 + §15 Validation start.** Clean.
(Pages 33–40 are otherwise pure body text — no figures/tables, no layout issues beyond the §11.5 heading hyphenation.)

**p41 — Table 4 (10-point complexity, 21 jurisdictions).** Well-formatted, fits margins, readable. Style note: uses plain `\hline` rules whereas Tables 1/2/3/5 use **booktabs** (`\toprule/\midrule`) — make Table 4 booktabs for consistency. Italic tier-group subheader rows read well.
**p42 — FX provenance + §15.4.** Footnotes (frankfurter.dev, open-er-api.com) fine. Clean.
**p43 — §15.5.** Clean.
**p44 — jurisdiction enumeration.** ⚠️ **Long `\texttt{}` path overflows the right margin** — "…artifacts in `research/experiments/consolidation_v2/`" runs past the text block (this is almost certainly the **remaining 117pt overfull**). Next round: allow monospace/path breaking (`\seqsplit`, `\path`, or `\sloppy` + `\texttt` break hook) for long inline paths.
**p45 — Table 5 (coverage manifest + validation).** Booktabs, right-aligned values, detailed caption — **the best-formatted table in the paper**. Good. Keep as the table style reference.
**p46 — limitation para + §15.6.** §15.6 heading wraps 2 lines, clean. Inline paths OK here.
**p47 — §15.7 Remarks I–III.** ⚠️ **Straight ASCII quotes** in Remark III: `"benchmarked against thousands of SME ledger exports"` should be curly ``…''. (Source: `remarks.tex`.)
**p48 — Remarks IV–V + §16.** (a) ⚠️ Remark V has straight quotes too: `"deterministic core implemented, remainder planned,"` → curly. (b) ⚠️ **§16 heading hyphenates: "…Accountant Recom-position"** — 3rd heading-hyphenation case. (c) Minor: body has "automation- susceptible" with a stray space — check source for `automation-~susceptible` / stray break.

### New items (priority-ranked)
1. **Figure 6 / p27 caption overprints folio** — true defect, fix first.
2. **Heading hyphenation** — §8 "Mecha-nism", §11.5 "Manage-ment", §16 "Recom-position" → ragged-right + no hyphenation for all headings (clapps.cls).
3. **Straight quotes in Remarks III & V** (`remarks.tex`) → curly quotes.
4. **Monospace path overflow / p44** (the 117pt overfull) → enable `\texttt` path breaking.
5. **Table 4 → booktabs** for style consistency with Tables 1/2/3/5.

**p49 — §16.2/§16.3.** §16.2 heading wraps 2 lines (clean). Body fine.
**p50 — §16.4/§16.5.** Clean.
**p51 — §16.5 tail + §17 Conclusion.** Clean.
**p52 — roadmap + Acknowledgements + AI-use + §18.** ⚠️ **Acknowledgements: add "Wes Roth" before "Matthew Berman"** (currently "David Shapiro, and Matthew Berman" → "David Shapiro, Wes Roth, and Matthew Berman") — author request #4. Rest of ack reads well.
**p53 — Table 6 (Level 3 catalog).** Wide table, `\resizebox`-shrunk (small font) and uses **`\hline` + vertical rules** — double style inconsistency vs the booktabs tables. Consider booktabs + drop vertical rules; small font acceptable for a reference catalog.
**p54 — Appendix C + Appendix D.** (a) ⚠️ Appendix C heading hyphenates: "…Linearization **Pro-tocol**" — 4th heading-hyphenation case. (b) ⚠️ **The Appendix C figure (`fig_tree_graph_tree`, the round-trip diagram) is NOT visible** — page jumps from the Appendix C intro straight to Appendix D. Verify the PDF include renders / didn't silently drop or float away.
**p55 — Appendix D tail + §19 Glossary.** Glossary `description` list — bold terms, † for coinages — clean and professional.
**p56 — Glossary tail + Selected Bibliography.** URL breaking now works (ifrs.org / IMF URLs wrap cleanly) — confirms the fix. Bibliography itemize clean.

### More items
6. **Acknowledgements:** add "Wes Roth" before Matthew Berman (author request).
7. **Appendix C figure** (`fig_tree_graph_tree`) appears missing on p54 — investigate/restore.
8. **Table 6 → booktabs**, drop vertical rules (consistency).
9. Heading hyphenation list now: §8, §11.5, §16, **Appendix C** — fix globally.

**p57–60 — Selected Bibliography.** URLs now break cleanly across lines (a2a-protocol, nist.gov, treasury.gov, pwc, ey, bls, lse, harvard, globenewswire) — URL fix confirmed working throughout. p60 ends the bibliography with large bottom whitespace (acceptable — end of list).
**p61–64 — ⚠️⚠️ FOUR FIGURES ORPHANED AT THE END OF THE DOCUMENT (after the bibliography):**
- p61 = **Figure 8** (Deterministic Boundary Library validation gauntlet) — belongs near §10.3 / §15.
- p62 = **Figure 9** (Locus of error before/after) — belongs in §11.3.
- p63 = **Figure 10** (CRA feedback loop) — belongs in §14.2.
- p64 = **Figure 11** (Tree-to-Graph-to-Tree linearization, the isometric PDF diagram) — belongs in **Appendix C** (this is the "missing" p54 figure — it floated here).
All four render well individually (good size/legibility); they are simply **displaced 20–40 pages from their referencing text** because their `figure` floats were deferred to the end. This is the **single most serious layout defect in the document.**

## CONSOLIDATED ACTION LIST (next editing round, priority order)

### A. Critical layout defects
1. **Relocate Figures 8–11** (now dumped on pp61–64 after the bibliography) back to their sections. Fix float placement: use `[H]` (float pkg is loaded) on these `figure` environments, and/or add `\FloatBarrier` at section ends. Verify Figures 1–7 stay put.
2. **Figure 6 / p27 caption overprints the page number** — cap the flowchart height (`\resizebox{!}{0.7\textheight}` or scale) or shorten the caption.

### B. Author's explicit requests
3. **Shorten the abstract** ~3–5 lines (it fills p1 edge-to-edge).
4. **Front-page rule = author-name width** (clapps `\maketitle`; currently fixed `0.18\textwidth`).
5. **Keywords → `\small`; metadata/footnote block → `\scriptsize`** (both too large; abstract.tex + spacing).
6. **Acknowledgements: insert "Wes Roth" before "Matthew Berman."**

### C. Typography
7. **Heading hyphenation** (ragged-right + `\hyphenpenalty=10000` for section headings in clapps.cls): fixes §8 "Mecha-nism", §11.5 "Manage-ment", §16 "Recom-position", Appendix C "Pro-tocol".
8. **Straight quotes → curly** in `remarks.tex` (Remark III, Remark V).
9. **Monospace path overflow / p44** (the 117pt overfull): enable `\texttt`/path line-breaking.

### D. Consistency / polish
10. **Figure font parity:** narrow the *wide* figures' content so they aren't shrunk — Figure 1 (timeline, p10) and Figure 2 (rigid tree, p15). Figures 3/4/5 are the correct reference size.
11. **Tables 4 & 6 → booktabs** (drop `\hline`/vertical rules) to match Tables 1/2/3/5.
12. **Float/whitespace gaps** pp3–5 (summarynote orphaned, §2 tables on next page): consider making the signature tables non-floating or reflowing §1/§2.
13. **summarynote** → real bordered/tinted box (install `tcolorbox`, or upgrade the rules-only fallback).
14. Minor: Figure 7 right-edge box proximity (p28); "automation- susceptible" stray space (p48).
