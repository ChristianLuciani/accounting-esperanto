# DR2 — Constraint as a Guardrail Against LLM Hallucination

**Research question:** Survey 2023–2026 work on reducing/eliminating LLM hallucination by
*constraining the output space* rather than post-hoc checking, and distinguish STATISTICAL
mitigation ("less likely to hallucinate") from CONSTRUCTIVE / "unreachable-by-design"
guarantees ("cannot emit an out-of-set identifier at all"). Supports **I1
(ontology-as-constraint)**, Related Work, and the adversarial threat-model section of
`main.tex`.

**Target claim under test** (main.tex §I1, lines 184–187): *"the space of possible outputs is
bounded by committed data, so a whole class of hallucinated or malformed bookings is
unreachable rather than merely unlikely."*

All sources below were retrieved live via WebSearch/WebFetch on 2026-07-24. Every URL/DOI was
opened and its title, author list, and date confirmed against the primary page (arXiv
abstract page, ACL Anthology, publisher page, or official GitHub repo) — see the "Verify"
column. Nothing here is asserted from memory alone.

---

## (a) Executive summary

- **The constructive/statistical distinction is a real, established line in the literature**,
  not a framing Kontablo invents. Grammar-/automaton-constrained decoding (Willard & Louf's
  Outlines; Koo, Liu & He's automata-based decoding, COLM 2024) masks token logits so that
  sequences outside a formal language have **zero** probability mass, not merely lower
  probability — and at least one paper (Koo et al.) supplies an explicit correctness proof.
  This is categorically different from statistical mitigations (fine-tuning, RAG, retrieval
  narrowing) that only shift a distribution.
- **The closest published mechanism to "an agent cannot emit an account UUID that doesn't
  exist in the graph" is entity-identifier-constrained decoding**, not JSON-grammar decoding.
  GENRE (De Cao et al., ICLR 2021) constrains autoregressive generation with a prefix trie
  built from a knowledge base so the model can only ever complete a real entity identifier.
  Graph-constrained Reasoning (Luo et al., ICML 2025) does the analogous thing over KG paths
  and reports "**zero** reasoning hallucination" — the strongest single empirical claim found
  that matches Kontablo's framing.
- **Important architectural nuance for the paper to state explicitly:** most of this
  literature constrains an LLM's *own* token-by-token decoding (logits get masked at
  generation time). Kontablo's Tier-1/Tier-2 resolvers are not decoding at all — they are
  plain deterministic lookups with no model in the loop (per the project's own principle #5;
  confirmed in `CLAUDE.md`). This makes I1 a **stricter instance of the same principle**
  (zero generative surface for the identifier, not just a masked one), but it also means the
  most literal prior-art match is tool-argument/entity-ID constraint (GENRE, closed-enum
  function calling), not general-purpose grammar decoding — cite grammar decoding for the
  *theoretical vocabulary* (hard vs. soft constraints, provable grammar membership) and
  entity/graph-constrained decoding for the *structural analogy*.
- **The guarantee is about syntactic/graph-membership validity, not semantic correctness** —
  this matters and the paper already scopes I1 correctly. No paper found claims constrained
  decoding prevents choosing the *wrong* valid identifier, only that it prevents fabricating
  an identifier that doesn't exist. Kontablo's own wording ("hallucinated or malformed
  bookings," not "incorrect bookings") is consistent with what the literature actually
  supports — do not let future edits widen the claim past this line.
- **Balancing critiques are real and should be cited, not omitted.** "Let Me Speak Freely?"
  (Tam et al., EMNLP 2024 Industry Track) and CRANE (Banerjee et al., ICML 2025) show that
  constraining an LLM's *reasoning* tokens to a rigid grammar measurably hurts accuracy on
  math/multi-hop tasks. Grammar-Aligned Decoding (Park et al., NeurIPS 2024) shows naive
  grammar-constrained decoding can distort the model's output distribution even while staying
  grammatical. This critique is **less damaging to I1 than it looks**, precisely because of
  the nuance above: Kontablo doesn't constrain reasoning tokens, it removes the LLM from the
  identifier-producing step entirely. The paper should say this explicitly to preempt the
  objection rather than let a reviewer raise it first.
- **Empirical evidence that "grounding" without a hard guarantee still hallucinates
  substantially**: Magesh et al. (Stanford RegLab, 2024) found commercial RAG-based legal-AI
  tools marketed as accurate still hallucinate 17–33% of the time; Dahl et al. (*Journal of
  Legal Analysis*, 2024, peer-reviewed) found 58–88% baseline hallucination rates on
  general-purpose LLMs for legal questions. These are strong, citable numbers for the
  threat-model section to justify *why* a merely-statistical safeguard is not sufficient for
  an unattended M2M financial pipeline.

---

## (b) Vetted sources table

All entries below are **VERIFIED** (retrieved and confirmed live). One entry (#19) is
verified-to-exist but flagged separately for low citation weight — see §(e).

### Grammar-/schema-constrained decoding (the mechanism, and the "provable" framing)

| # | Author/Org | Title | Year | URL/DOI | Type | Supports | Verify |
|---|---|---|---|---|---|---|---|
| 1 | Willard & Louf | Efficient Guided Generation for Large Language Models (Outlines) | 2023 | arXiv:2307.09702 | preprint | I1 mechanism | Open arXiv abstract page; confirm authors/date |
| 2 | Geng, Josifoski, Peyrard, West | Grammar-Constrained Decoding for Structured NLP Tasks without Finetuning | 2023 | arXiv:2305.13971 (EMNLP 2023) | peer-reviewed | I1 mechanism | Open arXiv abstract; cross-check ACL Anthology EMNLP 2023 listing |
| 3 | Scholak, Schucher, Bahdanau | PICARD: Parsing Incrementally for Constrained Auto-Regressive Decoding from LMs | 2021 | arXiv:2109.05093 (EMNLP 2021) | peer-reviewed | I1 mechanism, closest classic precedent (rejects invalid table/column names — direct structural analogue to rejecting invalid account codes) | ACL Anthology 2021.emnlp-main.779 |
| 4 | Dong, Ruan, Cai, Lai, Xu, Zhao, Chen | XGrammar: Flexible and Efficient Structured Generation Engine for LLMs | 2024 | arXiv:2411.15100 (MLSys 2025) | peer-reviewed | I1 mechanism, production-grade | Open arXiv abstract; cross-check MLSys 2025 poster page (mlsys.org/virtual/2025/poster/3235) |
| 5 | Koo, Liu, He (Google) | Automata-based constraints for language model decoding | 2024 | arXiv:2407.08103 (COLM 2024) | peer-reviewed | **I1 theoretical core** — explicit two-phase correctness proof that decoding cannot leave the grammar | Open arXiv abstract; confirm COLM 2024 acceptance |
| 6 | Park, Wang, Berg-Kirkpatrick, Polikarpova, D'Antoni | Grammar-Aligned Decoding | 2024 | arXiv:2405.21047 (NeurIPS 2024) | peer-reviewed | I1 mechanism **and** critique (naive GCD distributional distortion) | Open arXiv abstract; cross-check NeurIPS proceedings page |
| 7 | OpenAI | Introducing Structured Outputs in the API | 2024-08-06 | https://openai.com/index/introducing-structured-outputs-in-the-api/ | primary/blog | I1 mechanism, industry-scale evidence (100% vs. <40% schema-adherence eval, gpt-4o-2024-08-06) | Direct fetch returned HTTP 403 (bot-blocked); date/content corroborated independently via simonwillison.net/2024/Aug/6/openai-structured-outputs/ (fetched, confirms date + CFG mechanism) and two more independent secondary sources (pureai.com 2024-08-07, Azure blog) |
| 8 | Microsoft / guidance-ai | Guidance: A guidance language for controlling large language models | ongoing (2023–2026) | https://github.com/guidance-ai/guidance | spec/official docs | I1 mechanism | Fetched README directly; confirms regex/CFG constrained generation, "guarantees output syntax compliance" |
| 9 | ggml-org | GBNF grammar guide (llama.cpp) | ongoing | https://github.com/ggml-org/llama.cpp/blob/master/grammars/README.md | spec/official docs | I1 mechanism, "hard constraint" language confirmed | Fetched README directly; confirms grammars are hard constraints, not preferences |

### Identifier/ontology/KG-constrained generation (closest structural analogue to "resolve an account UUID")

| # | Author/Org | Title | Year | URL/DOI | Type | Supports | Verify |
|---|---|---|---|---|---|---|---|
| 10 | De Cao, Izacard, Riedel, Petroni (Meta AI) | Autoregressive Entity Retrieval (GENRE) | 2020 | arXiv:2010.00904 (ICLR 2021) | peer-reviewed | **I1 closest ML analogue** — prefix-trie-constrained beam search so the model can only complete real KB entity identifiers | Open arXiv abstract; confirm ICLR 2021; github.com/facebookresearch/GENRE README describes trie mechanism |
| 11 | Luo, Zhao, Haffari, Li, Gong, Pan | Graph-constrained Reasoning: Faithful Reasoning on Knowledge Graphs with LLMs | 2024 | arXiv:2410.13080 (ICML 2025) | peer-reviewed | **I1 strongest empirical claim** — "zero reasoning hallucination" via KG-Trie constraining decoding to valid KG paths | Open arXiv abstract; confirm ICML 2025 |
| 12 | Agrawal, Kumarage, Alghamdi, Liu (Arizona State) | Can Knowledge Graphs Reduce Hallucinations in LLMs? A Survey | 2023 | arXiv:2311.07914 (NAACL 2024) | peer-reviewed (survey) | Related Work anchor for KG-grounded generation category | Open arXiv abstract; confirm NAACL 2024 acceptance |

### Tool-use / function-calling with closed vocabulary (statistical narrowing — important contrast, not a hard guarantee)

| # | Author/Org | Title | Year | URL/DOI | Type | Supports | Verify |
|---|---|---|---|---|---|---|---|
| 13 | Patil, Zhang, Wang, Gonzalez (UC Berkeley) | Gorilla: Large Language Model Connected with Massive APIs | 2023 | arXiv:2305.15334 (NeurIPS 2024) | peer-reviewed | Threat-model contrast — retrieval + fine-tuning *reduces* API hallucination (measured via AST matching) but is not a closed-construction guarantee | Open arXiv abstract; gorilla.cs.berkeley.edu/blogs/2_hallucination.html for framing |

### Critiques — constraining decoding can hurt reasoning quality (balance)

| # | Author/Org | Title | Year | URL/DOI | Type | Supports | Verify |
|---|---|---|---|---|---|---|---|
| 14 | Tam, Wu, Tsai, Lin, Lee, Chen | Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of LLMs | 2024 | arXiv:2408.02442 (EMNLP 2024 Industry Track) | peer-reviewed | **Critique** — rigid grammars measurably hurt reasoning-heavy tasks (math, multi-hop QA); helps classification-like tasks | Open arXiv abstract; v3 (2024-10-14) is current |
| 15 | Banerjee, Suresh, Ugare, Misailovic, Singh | CRANE: Reasoning with constrained LLM generation | 2025 | arXiv:2502.09061 (ICML 2025) | peer-reviewed | **Critique + fix** — theoretical account of why over-constraining hurts reasoning; augmenting grammar with reasoning-preserving rules recovers accuracy | Open arXiv abstract; confirm ICML 2025 |

### Critiques — grounding/retrieval reduces but does not eliminate hallucination (statistical-guarantee gap, empirical stakes)

| # | Author/Org | Title | Year | URL/DOI | Type | Supports | Verify |
|---|---|---|---|---|---|---|---|
| 16 | Magesh, Surani, Dahl, Suzgun, Manning, Ho (Stanford RegLab) | Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools | 2024 | arXiv:2405.20362 | preprint (pre-registered empirical study) | **Threat-model motivation** — commercial RAG-grounded legal-AI tools marketed as reliable still hallucinate 17–33% of the time | Open arXiv abstract; confirms Lexis+ AI / Westlaw AI-Assisted Research / Ask Practical Law AI rates |
| 17 | Dahl, Magesh, Suzgun, Ho (Stanford) | Large Legal Fictions: Profiling Legal Hallucinations in Large Language Models | 2024 | arXiv:2401.01301; DOI via *Journal of Legal Analysis* 16(1):64 (academic.oup.com/jla/article/16/1/64/7699227) | **peer-reviewed journal** | Baseline evidence — 58–88% hallucination rate on general-purpose LLMs for verifiable legal questions, no constraint mechanism | Open arXiv abstract + Oxford Academic JLA page |

### Survey / taxonomy anchor

| # | Author/Org | Title | Year | URL/DOI | Type | Supports | Verify |
|---|---|---|---|---|---|---|---|
| 18 | Huang, Yu, Ma, Zhong, Feng, Wang, Chen, Peng, Feng, Qin, Liu | A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions | 2023 | arXiv:2311.05232 (ACM TOIS) | peer-reviewed (journal) | Related Work anchor — taxonomizes mitigation into prompt engineering / RAG / self-refinement / decoding strategies, situating constrained decoding as one branch | Open arXiv abstract; confirm ACM TOIS acceptance (v2, 2024-11-19) |

### Historical foundation (pre-LLM "hard constraint" tradition — grounds the vocabulary, not a direct hallucination paper)

| # | Author/Org | Title | Year | URL/DOI | Type | Supports | Verify |
|---|---|---|---|---|---|---|---|
| 19 | Hokamp & Liu | Lexically Constrained Decoding for Sequence Generation Using Grid Beam Search | 2017 | arXiv:1704.07138; ACL Anthology P17-1141 | peer-reviewed | Establishes "hard constraint" (guaranteed satisfaction) vs. "soft constraint" (biased, not guaranteed) as a pre-existing NLG distinction, predating the LLM-hallucination framing — use only for the historical/terminological point, **not** as an entity/UUID-constraint precedent (it guarantees *inclusion* of specified words, a different problem than *exclusion* of invalid identifiers) | ACL Anthology page P17-1141 |

---

## (c) BibTeX — strongest sources

Real metadata confirmed against primary pages. No fields invented; anything uncertain is
marked TODO per project epistemic rules.

```bibtex
@article{willard2023outlines,
  author  = {Willard, Brandon T. and Louf, R{\'e}mi},
  title   = {Efficient Guided Generation for Large Language Models},
  journal = {arXiv preprint arXiv:2307.09702},
  year    = {2023},
  url     = {https://arxiv.org/abs/2307.09702}
}

@inproceedings{geng2023gcd,
  author    = {Geng, Saibo and Josifoski, Martin and Peyrard, Maxime and West, Robert},
  title     = {Grammar-Constrained Decoding for Structured {NLP} Tasks without Finetuning},
  booktitle = {Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing (EMNLP)},
  year      = {2023},
  eprint    = {2305.13971},
  archivePrefix = {arXiv},
  url       = {https://arxiv.org/abs/2305.13971}
}

@inproceedings{scholak2021picard,
  author    = {Scholak, Torsten and Schucher, Nathan and Bahdanau, Dzmitry},
  title     = {{PICARD}: Parsing Incrementally for Constrained Auto-Regressive Decoding from Language Models},
  booktitle = {Proceedings of the 2021 Conference on Empirical Methods in Natural Language Processing (EMNLP)},
  year      = {2021},
  eprint    = {2109.05093},
  archivePrefix = {arXiv},
  url       = {https://aclanthology.org/2021.emnlp-main.779/}
}

@inproceedings{koo2024automata,
  author    = {Koo, Terry and Liu, Frederick and He, Luheng},
  title     = {Automata-based constraints for language model decoding},
  booktitle = {Conference on Language Modeling (COLM)},
  year      = {2024},
  eprint    = {2407.08103},
  archivePrefix = {arXiv},
  url       = {https://arxiv.org/abs/2407.08103},
  note      = {TODO: pin COLM 2024 proceedings page/DOI once available}
}

@inproceedings{park2024gad,
  author    = {Park, Kanghee and Wang, Jiayu and Berg-Kirkpatrick, Taylor and Polikarpova, Nadia and D'Antoni, Loris},
  title     = {Grammar-Aligned Decoding},
  booktitle = {Advances in Neural Information Processing Systems 37 (NeurIPS 2024)},
  year      = {2024},
  eprint    = {2405.21047},
  archivePrefix = {arXiv},
  url       = {https://proceedings.neurips.cc/paper_files/paper/2024/hash/2bdc2267c3d7d01523e2e17ac0a754f3-Abstract-Conference.html}
}

@inproceedings{decao2021genre,
  author    = {De Cao, Nicola and Izacard, Gautier and Riedel, Sebastian and Petroni, Fabio},
  title     = {Autoregressive Entity Retrieval},
  booktitle = {International Conference on Learning Representations (ICLR)},
  year      = {2021},
  eprint    = {2010.00904},
  archivePrefix = {arXiv},
  url       = {https://arxiv.org/abs/2010.00904}
}

@inproceedings{luo2024gcr,
  author    = {Luo, Linhao and Zhao, Zicheng and Haffari, Gholamreza and Li, Yuan-Fang and Gong, Chen and Pan, Shirui},
  title     = {Graph-constrained Reasoning: Faithful Reasoning on Knowledge Graphs with Large Language Models},
  booktitle = {International Conference on Machine Learning (ICML)},
  year      = {2025},
  eprint    = {2410.13080},
  archivePrefix = {arXiv},
  url       = {https://arxiv.org/abs/2410.13080}
}

@inproceedings{tam2024letmespeak,
  author    = {Tam, Zhi Rui and Wu, Cheng-Kuang and Tsai, Yi-Lin and Lin, Chieh-Yen and Lee, Hung-yi and Chen, Yun-Nung},
  title     = {Let Me Speak Freely? A Study on the Impact of Format Restrictions on Performance of Large Language Models},
  booktitle = {Proceedings of the 2024 Conference on Empirical Methods in Natural Language Processing: Industry Track},
  year      = {2024},
  eprint    = {2408.02442},
  archivePrefix = {arXiv},
  url       = {https://arxiv.org/abs/2408.02442}
}

@inproceedings{banerjee2025crane,
  author    = {Banerjee, Debangshu and Suresh, Tarun and Ugare, Shubham and Misailovic, Sasa and Singh, Gagandeep},
  title     = {{CRANE}: Reasoning with constrained {LLM} generation},
  booktitle = {International Conference on Machine Learning (ICML)},
  year      = {2025},
  eprint    = {2502.09061},
  archivePrefix = {arXiv},
  url       = {https://arxiv.org/abs/2502.09061}
}

@misc{magesh2024hallucinationfree,
  author = {Magesh, Varun and Surani, Faiz and Dahl, Matthew and Suzgun, Mirac and Manning, Christopher D. and Ho, Daniel E.},
  title  = {Hallucination-Free? Assessing the Reliability of Leading {AI} Legal Research Tools},
  year   = {2024},
  eprint = {2405.20362},
  archivePrefix = {arXiv},
  url    = {https://arxiv.org/abs/2405.20362},
  note   = {Pre-registered empirical study; not yet confirmed peer-reviewed venue as of this writing}
}

@article{dahl2024legalfictions,
  author  = {Dahl, Matthew and Magesh, Varun and Suzgun, Mirac and Ho, Daniel E.},
  title   = {Large Legal Fictions: Profiling Legal Hallucinations in Large Language Models},
  journal = {Journal of Legal Analysis},
  volume  = {16},
  number  = {1},
  pages   = {64},
  year    = {2024},
  url     = {https://academic.oup.com/jla/article/16/1/64/7699227},
  note    = {arXiv preprint: 2401.01301}
}

@online{openai2024structured,
  author       = {{OpenAI}},
  title        = {Introducing Structured Outputs in the {API}},
  year         = {2024},
  month        = {8},
  day          = {6},
  url          = {https://openai.com/index/introducing-structured-outputs-in-the-api/},
  urldate      = {2026-07-24},
  note         = {Primary fetch blocked by bot-detection (HTTP 403); date and content corroborated via simonwillison.net/2024/Aug/6/openai-structured-outputs/}
}

@article{huang2023survey,
  author  = {Huang, Lei and Yu, Weijiang and Ma, Weitao and Zhong, Weihong and Feng, Zhangyin and Wang, Haotian and Chen, Qianglong and Peng, Weihua and Feng, Xiaocheng and Qin, Bing and Liu, Ting},
  title   = {A Survey on Hallucination in Large Language Models: Principles, Taxonomy, Challenges, and Open Questions},
  journal = {ACM Transactions on Information Systems},
  year    = {2023},
  eprint  = {2311.05232},
  archivePrefix = {arXiv},
  url     = {https://arxiv.org/abs/2311.05232},
  note    = {TODO: pin final ACM TOIS volume/issue/DOI once assigned}
}

@inproceedings{hokamp2017lexically,
  author    = {Hokamp, Chris and Liu, Qun},
  title     = {Lexically Constrained Decoding for Sequence Generation Using Grid Beam Search},
  booktitle = {Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics (ACL)},
  year      = {2017},
  url       = {https://aclanthology.org/P17-1141/},
  note      = {Historical/terminological citation only — guarantees inclusion of specified tokens, not exclusion of invalid identifiers; do not overstate the analogy to I1}
}
```

---

## (d) Mapping to paper claims

**I1's exact claim** (main.tex): *"an agent cannot propose an account UUID that does not
exist in the graph, because resolution is a lookup into the graph, not a generation of free
text... the space of possible outputs is bounded by committed data, so a whole class of
hallucinated or malformed bookings is unreachable rather than merely unlikely."*

1. **The constructive/statistical distinction is defensible as stated, with one precision
   the paper should add.** Sources #1, #5, #6, #8, #9 establish that masking token
   probabilities to zero for out-of-grammar continuations is qualitatively different from
   biasing a distribution — Koo et al. (#5) go furthest, offering an actual correctness proof
   ("the constraint accepts exactly the token sequences desired"). This is real, peer-reviewed
   support for "unreachable" as a category distinct from "unlikely." Cite #5 as the anchor for
   the theoretical claim, #1/#8/#9 for the practitioner-facing versions, #7 for
   industrial-scale evidence (100% vs. <40%).

2. **The single best structural analogue is GENRE (#10), not a JSON-grammar paper.**
   Kontablo resolves a *local account code to a UUID that must already exist in a fixed
   graph* — this is an entity-linking/identifier-retrieval problem, not a syntax problem.
   GENRE's trie-constrained decoding is doing exactly this shape of thing (constrain
   generation so a *symbolic identifier* can only ever be a real one), and Luo et al.'s KG-Trie
   work (#11) reports the strongest matching empirical result in the literature: "zero
   reasoning hallucination." **Recommend citing #10 and #11 together as the closest prior art
   to I1's mechanism**, ahead of the JSON/grammar-decoding papers, which are closer to I2's
   concerns (structured, well-formed *output shape*) than to I1's concern (a *closed
   identifier space*).

3. **A nuance the paper does not yet state and should:** the cited literature constrains an
   LLM's own decoding process. Kontablo's Tier-1/Tier-2 (per `CLAUDE.md`: "an exact statutory
   index, a deterministic keyword rule") involve **no model at all** — `resolve_account` is a
   pure function over committed data, and the one tier that *would* involve a model (Tier-3,
   semantic/LLM fallback) is "deliberately not exposed as a tool." This means I1 is not an
   instance of constrained decoding in the technical sense the cited papers use the term — it
   is closer to the general principle those papers instantiate (bound the output space to a
   committed, checkable set) taken to its limit: zero generative surface, rather than a masked
   generative surface. **Recommend one sentence in §I1 making this explicit** — it preempts a
   knowledgeable reviewer's objection ("this isn't really constrained decoding") and turns it
   into a strength ("stricter than constrained decoding: no model in the loop for the
   identifier-producing step at all").

4. **The critiques (#14, #15, #6's distortion finding) are real but land on a different
   target than I1.** They show that constraining an LLM's *intermediate reasoning* tokens to a
   rigid final-answer grammar hurts benchmark accuracy on math/multi-hop tasks. Kontablo's
   deterministic tiers do no reasoning at all (rule lookup), and the one component that does
   reason (Tier-3) is explicitly walled off from the tool surface — so the "constraining
   reasoning hurts reasoning" critique has no purchase on the *deterministic* tools, by
   construction. It would apply if Kontablo ever exposed Tier-3 as a constrained-output tool;
   worth one explicit sentence noting the architecture avoids this failure mode on purpose,
   citing #14/#15 as the reason it's avoided rather than as a rebuttal to work around.

5. **Threat-model motivation is well served by #16/#17/#18.** These give the paper concrete,
   citable numbers for *why* "merely less likely" is an insufficient guarantee at M2M
   frequency: commercial, RAG-grounded, professionally marketed tools still hallucinate
   17–33% of the time (#16), and ungrounded general-purpose models hit 58–88% on the same
   class of task (#17, peer-reviewed). This is exactly the quantitative contrast the
   "Why does trust have to move into the architecture?" section (main.tex, opening section)
   is arguing informally — these sources let it argue it with numbers instead of intuition.

6. **Gorilla (#13) is best used as a foil, not a support.** It is frequently miscited in
   blog-level writing as "solving" API hallucination; the paper itself is honest that
   retrieval "significantly reduces" but does not claim eliminates hallucination, and measures
   it via an AST-matching *rate*, not a zero-hallucination *guarantee*. Useful precisely to
   show the field's own best statistical mitigation still reports a rate, not a proof —
   sharpens the contrast with #5/#10/#11.

---

## (e) Gaps / unverified / open questions / critiques

**Verification gaps:**
- Source #7 (OpenAI blog): WebFetch returned HTTP 403 (Cloudflare/bot-detection), consistent
  with WebFetch's known limitation on some corporate blogs, not a sign the content is wrong.
  Corroborated via three independent secondary sources with matching date and technical
  description (simonwillison.net, fetched directly; pureai.com; Microsoft Azure blog, both
  via search snippet only, not fetched). **Recommend the paper's author double-check the live
  URL manually before final submission**, since I could not render it myself.
- Source #16 (Hallucination-Free?, Magesh et al.): I found no confirmation of peer-reviewed
  venue placement — it reads as a standalone empirical study, possibly submitted to a law or
  law-and-technology venue since its 2024-05-30 arXiv posting, but I did not find a venue
  confirmation. Cite as "pre-registered empirical study (arXiv), venue TBD."
- XGrammar's exact MLSys 2025 proceedings page (vs. poster listing) was confirmed via the
  MLSys virtual program page, not the formal PMLR/proceedings.mlsys.org entry — minor, low
  risk, but flag for a final pin before submission.

**Flagged as weak — do not cite without independent re-verification:**
- **Chethan, G. (Siemens), "The Semantic Training Gap: Ontology-Grounded Tool Architectures
  for Industrial AI Agent Systems," arXiv:2605.11234 (submitted 2026-05-11).** This is, on
  paper, the *closest possible analogue* to I1 outside Kontablo itself: it reports embedding
  a domain ontology into an agent's tool layer as typed relational configuration, and finds
  unconstrained tool parameters produce 43% hallucinated domain identifiers vs. 0% with
  ontology-grounded parameters — almost exactly Kontablo's I1 claim, in a different domain
  (industrial/manufacturing, not accounting). **However:** it is a single-author paper posted
  ~10 weeks before this research pass, with no confirmed peer review, and I could not find any
  citing literature or independent replication. The author (with a co-author on a related,
  separately-found paper, "Self-Reflective APIs," arXiv:2606.05037) appears Siemens-affiliated
  based on search results, which is a mild positive signal (industry R&D, not an obviously
  low-quality source), but this is not confirmed from the paper itself. **Recommendation:**
  mention in Related Work as a very recent, structurally parallel, independently-arrived-at
  result if the paper wants breadth — but do not lean on its "0%" figure as load-bearing
  evidence, and do not describe it as peer-reviewed or established.

**Open questions the DR did not resolve:**
- I found no paper that directly benchmarks "tool-call argument validated server-side against
  a closed set, with hard rejection of non-members" (Kontablo's actual mechanism) as its own
  named category distinct from grammar decoding and entity-linking. It may be that this
  pattern is common enough in production systems (any strict API server doing foreign-key
  validation) that it has never been treated as a "hallucination mitigation technique" in the
  ML literature — it predates the hallucination framing entirely as ordinary input validation.
  **This might be worth stating outright in the paper**: part of I1's novelty claim is
  precisely *recognizing* that ordinary deterministic input validation, applied at the
  agent-tool boundary, is a hallucination-elimination mechanism for the identifier space —
  connecting a well-known software-engineering practice to a live ML research problem. If true,
  that connection itself may be a small original contribution worth stating as such rather than
  hunting for a paper that already says it.
- I did not find a formal treatment specifically of "hallucination" as inapplicable-by-definition
  to closed-set classification/retrieval tasks (as opposed to open-ended generation) — this is
  implicit in several sources (e.g., "Let Me Speak Freely?" notes format restriction *helps*
  classification-like tasks) but I found no paper making it a first-class theoretical point.
  Would strengthen §I1 if it existed; flagging as a possible gap rather than claiming it doesn't
  exist anywhere.
- Did not deeply pursue NeMo Guardrails / programmable-rails-style approaches (topical/dialogue
  rails) — initial scan suggested these are closer to runtime *filters* (detect-then-block,
  i.e., still statistical/post-hoc in the relevant sense) rather than construction-time
  constraints, which is why they were deprioritized versus grammar/trie decoding, but this was
  not exhaustively verified and could be revisited if the paper wants a NeMo-style contrast.

**Balance check (per epistemic rules — critiques are not omitted):** #14, #15, and #6 together
establish a genuine, peer-reviewed critique of naive constrained decoding (hurts reasoning,
distorts distribution) that any related-work section citing constrained decoding as
unambiguously good would be incomplete without. #16/#17 establish that the *alternative*
(statistical grounding) has a real, measured failure rate in a deployed, adjacent
high-stakes domain (legal), which is the strongest available argument for why I1's
architecture matters rather than merely being tidy. Recommend keeping both families in the
final Related Work section rather than only the papers that flatter I1.
