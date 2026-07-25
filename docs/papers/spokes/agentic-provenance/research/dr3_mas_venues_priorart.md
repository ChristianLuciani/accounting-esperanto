# DR3 — Prior Art in Multi-Agent Systems & Venue Shortlist

> Deep-research output for Spoke 1 ("Deterministic Auditability Invariants for
> Autonomous Financial Agents"). Feeds `TASKS.md` **T1** (Related Work /
> `references.bib`) and the venue decision in the local publication playbook.
> All items below were retrieved live via WebSearch/WebFetch on **2026-07-24**;
> every URL was fetched and returned real content (not fabricated). Deadlines
> move every cycle — treat every date as **"as of 2026-07-24; verify before
> acting."**

---

## (a) Executive summary

Searched AAMAS (main track + workshops), AAAI/AIES, ICLR/ICML agent-safety
workshops, and arXiv cs.MA/cs.CR/q-fin.GN for work on autonomous-agent
economies, M2M financial infrastructure, and provenance/accountability for
agent actions. Found a **real and fast-growing 2025–2026 literature on agent
payments and agent accountability**, but it clusters into two camps that both
leave the paper's specific gap open: (1) **settlement/identity-layer**
work (blockchain payment rails, ERC-8004 trust registries, x402 security) that
explicitly names "limited accountability" as an open problem but solves it
with cryptographic/reputational mechanisms, not semantic correctness; and (2)
**accountability-as-reconstruction** work (audit trails, execution provenance,
responsibility logics) that captures and reasons about what an agent did
*after the fact*, not what it is *structurally prevented from doing*. The
single closest architectural cousin found is **AUDITFLOW** (arXiv:2606.03031),
which also uses a symbolic/graph-grounded environment to constrain an LLM
agent against a fixed financial taxonomy — but it verifies *already-produced*
filings (detection), where Kontablo's I1 constrains posting *at generation
time* (prevention) and I2 ledgers the residual. No item found makes
auditability an architectural precondition on the transaction-authoring path
itself — that is the paper's clearest novelty claim, and it now has literature
to stand next to rather than assert in a vacuum.

For venues: 15 papers found live in **cs.MA / cs.CR / q-fin.GN**, mostly
distributed via workshops with their own OpenReview instances or AAMAS's own
IFAAMAS+OpenReview pipeline — **none of the venues below require an arXiv
account or arXiv endorsement**, because none of them are arXiv submissions;
they're submissions to the venue's own portal. This fully sidesteps the cs.MA
endorsement gate the project already hit. Top picks: **AAMAS main track**
(GTEP or COINE track) for the archival, CC-BY, indexed record, paired with the
**AAAI-26 Trustworthy Agentic AI workshop** (or its next cycle) for the
fastest topically-exact community exposure while the AAMAS submission is in
flight.

---

## (b) Prior-art sources

All items VERIFIED by direct WebFetch of the arXiv abstract page, the AAAI/ACM
OJS article page, or (for the one PDF that wouldn't parse) cross-checked
against a second independent listing. Type: **P** = peer-reviewed
proceedings, **W** = arXiv working paper/preprint (not yet peer-reviewed —
cite as preprint, not as "published").

### Cluster 1 — Agent economies & M2M payment infrastructure

| # | Author(s) | Title | Year | Source | Type | Relevance to our invariants |
|---|---|---|---|---|---|---|
| 1 | Zhang, Xiang, Lei, Wang, Qiu, Sun, Zarkov, Yuen, Deppeler, Yu, Lam | [SoK: Blockchain Agent-to-Agent Payments](https://arxiv.org/abs/2604.03733) | 2026 | arXiv:2604.03733 (q-fin.GN) | W | Systematization-of-knowledge naming "weak intent binding," "payment-service decoupling," and **"limited accountability"** as open problems in agent payment rails — confirms the settlement layer knows it has an accountability gap but frames the fix as cryptographic, not semantic. Strong citation for positioning §5. |
| 2 | Hui Gong | [Agent-to-Agent Finance: Blockchain Payments and Trust Infrastructure for Autonomous AI Agents](https://arxiv.org/abs/2607.00245) | 2026 | arXiv:2607.00245 (q-fin.GN) | W | Defines "agent-to-agent finance" as identity+authorization+payment+**verifiable evidence**; evidence here means proof a transfer happened, not that it was booked to the right concept. |
| 3 | Minghui Xu | [The Agent Economy: A Blockchain-Based Foundation for Autonomous AI Agents](https://arxiv.org/abs/2602.14219) | 2026 | arXiv:2602.14219 (cs.CR) | W | Five-layer architecture (infra, on-chain identity, cognitive tooling, settlement, governance) for agents as economic peers; no accounting-semantic layer in the stack — a gap our paper's positioning (§5) can name directly. |
| 4 | Botao "Amber" Hu, Helena Rong | [Inter-Agent Trust Models: A Comparative Study of Brief, Claim, Proof, Stake, Reputation and Constraint in Agentic Web Protocol Design — A2A, AP2, ERC-8004, and Beyond](https://arxiv.org/abs/2511.03434) | 2025 | arXiv:2511.03434 (cs.HC/cs.AI/cs.MA/cs.NI/cs.SI) | W | Directly compares **A2A and AP2** (the two protocols our paper cites) plus ERC-8004 on trust mechanisms; evaluates on security/privacy/latency/social robustness — none of its six trust primitives (brief, claim, proof, stake, reputation, constraint) is "is the posted value semantically correct." Best single citation for "AP2/A2A operate at a different layer." |
| 5 | Xiong, Li, Wei, Wang, Knottenbelt, Wang | [Can Trustless Agents Be Trusted? An Empirical Study of the ERC-8004 Decentralized AI Agent Ecosystem](https://arxiv.org/abs/2606.26028) | 2026 | arXiv:2606.26028 (cs.CR/cs.AI/cs.MA) | W | Empirically finds ERC-8004's reputation layer is Sybil-able and feedback is unverifiable in practice — evidence that identity/reputation trust and transaction-content trust are separate problems; the latter is our paper's territory. |

### Cluster 2 — Accountability & responsibility frameworks (formal/normative)

| # | Author(s) | Title | Year | Source | Type | Relevance to our invariants |
|---|---|---|---|---|---|---|
| 6 | Vahid Yazdanpanah, Enrico H. Gerding, Sebastian Stein, Mehdi Dastani, Catholijn M. Jonker, Timothy J. Norman | [Responsibility Research for Trustworthy Autonomous Systems](https://www.ifaamas.org/Proceedings/aamas2021/pdfs/p57.pdf) (Blue Sky Ideas Track) | 2021 | AAMAS '21, pp. 57–62 | P | Establishes "responsibility research" as a standing AAMAS Blue-Sky theme since 2021 — the community has been asking this question for 5 years; useful as the historical anchor showing continuity, and a contrast case (their responsibility model is post-hoc/normative reasoning, not an architectural constraint). |
| 7 | Timothy Parker, Umberto Grandi, Emiliano Lorini | [Responsibility in a Multi-Value Strategic Setting](https://arxiv.org/abs/2410.17229) | 2024 | arXiv:2410.17229 (cs.AI) | W | Formal framework for assigning responsibility across multiple values in strategic multi-agent settings ("responsibility anticipation"). Reasons about responsibility *given* an outcome — does not constrain which outcomes/postings are reachable in the first place. Good contrast for I1. |
| 8 | Saad Alqithami | [Adaptive Accountability in Networked Multi-Agent Systems](https://ojs.aaai.org/index.php/AIES/article/view/36536) | 2025 | AIES-25 (AAAI/ACM Conf. on AI, Ethics & Society), Vol. 8 No. 1 | P | Peer-reviewed accountability mechanism: "lifecycle-based auditing, decentralized governance, and norm detection" catching collusion/hoarding in >90% of tested configs. Detection-based (norm-violation monitoring), not prevention-based (unreachable-by-construction) — the I1 contrast again, from a different angle (norms vs. ontology). |
| 9 | Virginia Dignum, Frank Dignum | [Agentifying Agentic AI](https://arxiv.org/abs/2511.17332) | 2025–26 | arXiv:2511.17332 (cs.AI/cs.MA); presented at WMAC 2026 (AAAI-26 bridge program) | W | Two senior MAS researchers argue for importing BDI/institutional concepts into agentic AI for "transparent, cooperative, and accountable" systems — a call to action, not a shipped architecture. Supports "the MAS community is asking for exactly this, nobody has shipped the constraint-based version." |

### Cluster 3 — Provenance & audit-trail systems (closest technical neighbors)

| # | Author(s) | Title | Year | Source | Type | Relevance to our invariants |
|---|---|---|---|---|---|---|
| 10 | Yan Wang, Xuguang Ai, Jaisal Patel, Xueqing Peng, Fengran Mo, Yupeng Cao, Haohang Li, Mingyu Cao, Lingfei Qian, Víctor Gutiérrez-Basulto | [AUDITFLOW: Executable Symbolic Environments for Structured Financial Reporting Verification](https://arxiv.org/abs/2606.03031) | 2026 | arXiv:2606.03031 (cs.AI/**cs.MA**/cs.SC) | W | **Closest architectural cousin found.** Graph-grounded multi-agent framework: builds a symbolic environment from a US-GAAP taxonomy + XBRL filing graph, exposes it via typed tools, and shows removing the deterministic-check layer collapses accuracy from 82% to 18%. Structurally parallel to ontology-as-constraint — but it *verifies already-filed* reports (a check/detection task on static documents), not *at-transaction-time posting* by an autonomous agent. Must be discussed explicitly, not just cited. |
| 11 | Bardia Mohammadi, Nearchos Potamitis, Lars Klein, Akhil Arora, Laurent Bindschaedler | [Atomix: Timely, Transactional Tool Use for Reliable Agentic Workflows](https://arxiv.org/abs/2602.14849) | 2026 | arXiv:2602.14849 (cs.LG/cs.AI/cs.DC/**cs.MA**) | W | General-purpose transactional semantics for LLM tool calls ("progress-aware transactions," clean recovery under injected faults). Domain-agnostic analog to I2 (no silent partial effects) at the systems/infra layer, not the accounting-semantic layer — good contrast citation: "conservation of *effects*" vs. our "conservation of *accounting entries with typed loss on every non-conservation*." |
| 12 | Yi Nian, Aojie Yuan, Haiyue Zhang, Jiate Li, Yue Zhao | [Auditable Agents](https://arxiv.org/abs/2604.05485) | 2026 | arXiv:2604.05485 (cs.AI) | W | Explicitly separates **accountability, auditability, and auditing**; defines 5 auditability dimensions (action recoverability, lifecycle coverage, policy checkability, responsibility attribution, evidence integrity) and an "Auditability Card." The most directly comparable *definitional* framework to our I2 — all 5 dimensions are about whether a past action *can be reconstructed and inspected*, none is about whether a class of malformed action is *unreachable*. Cite for definitional grounding, then differentiate. |
| 13 | Yiqi Wang, Jiaqi Zhang, Taotao Cai, Zirui Liu, Qingqiang Sun, Zequn Sun, Zhangkai Wu, Manqing Dong, Mingkai Zheng, Xuefei Yin, Yanming Zhu | [From Agent Traces to Trust: A Survey of Evidence Tracing and Execution Provenance in LLM Agents](https://arxiv.org/abs/2606.04990) | 2026 | arXiv:2606.04990 (cs.CR/cs.AI) | W | Survey defining execution provenance as a typed execution graph, evidence tracing as its projection onto support relationships. Useful for placing I2/I3 in the field's own taxonomy (feeds DR6 too); confirms provenance-as-reconstruction is the dominant framing across the surveyed literature, i.e. no surveyed system treats the *ontology itself* as the provenance-bounding mechanism. |

### Cluster 4 — Field-defining / security position pieces

| # | Author(s) | Title | Year | Source | Type | Relevance to our invariants |
|---|---|---|---|---|---|---|
| 14 | Schroeder de Witt, Krawiecka, Krawczuk, Hagag, Anderson, Belcak, Bucknall, Cai, Chopra, Cohen, Del Rosario, Draguns, Gray, Katz, Mavroudis, Mink, Motwani, Petit, Rembeck, Smith, Sotiropoulos, Young, Scheffler, Llewellyn | [Open Challenges in Multi-Agent Security: Towards Secure Systems of Interacting AI Agents](https://arxiv.org/abs/2505.02077) | 2025–26 | arXiv:2505.02077 (cs.CR/cs.AI/**cs.MA**), v2 Apr 2026 | W | Large-consortium field-defining paper taxonomizing MAS security threats (secret collusion, coordinated attacks) and proposing a research agenda. Does **not** name accounting-semantic correctness or per-transaction loss-tracking as a threat class — a citable absence supporting the novelty claim, used carefully ("absence in a broad taxonomy," not proof of a gap). |
| 15 | Seth Karten, Wenzhe Li, Zihan Ding, Samuel Kleiner, Yu Bai, Chi Jin | [LLM Economist: Large Population Models and Mechanism Design in Multi-Agent Generative Simulacra](https://arxiv.org/abs/2507.15815) | 2025 | arXiv:2507.15815 (**cs.MA**, cross-list cs.LG) | W | LLM agents as tax-planner/worker economic actors with RL-driven mechanism design. Direct cs.MA sibling on "agents as economic actors"; establishes the venue/category is receptive to this style of result — useful for the "this is a natural cs.MA paper" framing, not for the accountability argument specifically. |

**On x402 (adjacent, not tabled above):** three independent 2026 security
analyses of the x402 payment protocol were found — *Five Attacks on x402
Agentic Payment Protocol* (arXiv:2605.11781), *Free-Riding the Agentic Web*
(arXiv:2605.30998), and *When HTTP 402 Meets the Blockchain*
(arXiv:2607.19545) — all finding authorization/replay/binding
vulnerabilities in a settlement protocol. Not included as full rows (same
"settlement ≠ semantic correctness" point as Cluster 1, and three papers would
pad the table), but each is a real, fetchable arXiv ID if T1 wants a
settlement-layer-is-also-imperfect aside.

---

## (c) BibTeX (real metadata; append to `references.bib`)

Every entry below was built from fields returned by a direct WebFetch of the
cited URL. `note` fields flag anything the source page itself left
unspecified (e.g. author affiliations were not shown on most arXiv abstract
pages) — these are honest gaps in what's *displayed*, not fabricated filler.

```bibtex
% ---- Cluster 1: agent economies & M2M payment infrastructure ----

@misc{zhang2026sok,
  author       = {Zhang, Yuanzhe and Xiang, Yuexin and Lei, Yuchen and Wang, Qin
                  and Qiu, Tian and Sun, Yujing and Zarkov, Spiridon and Yuen, Tsz Hon
                  and Deppeler, Andreas and Yu, Jiangshan and Lam, Kwok-Yan},
  title        = {{SoK: Blockchain Agent-to-Agent Payments}},
  year         = {2026},
  eprint       = {2604.03733},
  archivePrefix= {arXiv},
  primaryClass = {q-fin.GN},
  url          = {https://arxiv.org/abs/2604.03733},
  note         = {Accessed 2026-07-24}
}

@misc{gong2026a2afinance,
  author       = {Gong, Hui},
  title        = {{Agent-to-Agent Finance: Blockchain Payments and Trust
                   Infrastructure for Autonomous AI Agents}},
  year         = {2026},
  eprint       = {2607.00245},
  archivePrefix= {arXiv},
  primaryClass = {q-fin.GN},
  url          = {https://arxiv.org/abs/2607.00245},
  note         = {Accessed 2026-07-24. Affiliation not stated on the arXiv
                  abstract page; TODO(T1) confirm before citing with
                  affiliation in prose.}
}

@misc{xu2026agenteconomy,
  author       = {Xu, Minghui},
  title        = {{The Agent Economy: A Blockchain-Based Foundation for
                   Autonomous AI Agents}},
  year         = {2026},
  eprint       = {2602.14219},
  archivePrefix= {arXiv},
  primaryClass = {cs.CR},
  url          = {https://arxiv.org/abs/2602.14219},
  note         = {Accessed 2026-07-24}
}

@misc{hu2025interagenttrust,
  author       = {Hu, Botao and Rong, Helena},
  title        = {{Inter-Agent Trust Models: A Comparative Study of Brief,
                   Claim, Proof, Stake, Reputation and Constraint in Agentic
                   Web Protocol Design---A2A, AP2, ERC-8004, and Beyond}},
  year         = {2025},
  eprint       = {2511.03434},
  archivePrefix= {arXiv},
  primaryClass = {cs.MA},
  url          = {https://arxiv.org/abs/2511.03434},
  note         = {Accessed 2026-07-24. Author given name stylized "Botao
                  `Amber' Hu" on the source; TODO(T1) confirm preferred
                  citation form.}
}

@misc{xiong2026trustlessagents,
  author       = {Xiong, Xihan and Li, Zelin and Wei, Wei and Wang, Qin
                  and Knottenbelt, William and Wang, Zhipeng},
  title        = {{Can Trustless Agents Be Trusted? An Empirical Study of the
                   ERC-8004 Decentralized AI Agent Ecosystem}},
  year         = {2026},
  eprint       = {2606.26028},
  archivePrefix= {arXiv},
  primaryClass = {cs.CR},
  url          = {https://arxiv.org/abs/2606.26028},
  note         = {Accessed 2026-07-24}
}

% ---- Cluster 2: accountability & responsibility frameworks ----

@inproceedings{yazdanpanah2021responsibility,
  author    = {Yazdanpanah, Vahid and Gerding, Enrico H. and Stein, Sebastian
               and Dastani, Mehdi and Jonker, Catholijn M. and Norman, Timothy J.},
  title     = {{Responsibility Research for Trustworthy Autonomous Systems}},
  booktitle = {Proceedings of the 20th International Conference on Autonomous
               Agents and MultiAgent Systems (AAMAS 2021), Blue Sky Ideas Track},
  pages     = {57--62},
  year      = {2021},
  url       = {https://www.ifaamas.org/Proceedings/aamas2021/pdfs/p57.pdf},
  note      = {Accessed 2026-07-24. Title/authors/pages cross-checked against
               the researchr.org AAMAS'21 listing; the IFAAMAS PDF itself
               fetched as binary and could not be text-extracted by the
               fetch tool used, so TODO(T1): open the PDF directly once more
               before final submission to confirm no transcription error.}
}

@misc{parker2024responsibility,
  author       = {Parker, Timothy and Grandi, Umberto and Lorini, Emiliano},
  title        = {{Responsibility in a Multi-Value Strategic Setting}},
  year         = {2024},
  eprint       = {2410.17229},
  archivePrefix= {arXiv},
  primaryClass = {cs.AI},
  url          = {https://arxiv.org/abs/2410.17229},
  note         = {Accessed 2026-07-24. No conference venue indicated on the
                  arXiv page as of access date; cite as preprint.}
}

@article{alqithami2025adaptiveaccountability,
  author  = {Alqithami, Saad},
  title   = {{Adaptive Accountability in Networked Multi-Agent Systems}},
  journal = {Proceedings of the AAAI/ACM Conference on AI, Ethics, and Society
             (AIES-25)},
  volume  = {8},
  number  = {1},
  year    = {2025},
  url     = {https://ojs.aaai.org/index.php/AIES/article/view/36536},
  note    = {Accessed 2026-07-24. Author affiliation (Al-Baha University,
             Saudi Arabia) per the OJS article page.}
}

@misc{dignum2025agentifying,
  author       = {Dignum, Virginia and Dignum, Frank},
  title        = {{Agentifying Agentic AI}},
  year         = {2025},
  eprint       = {2511.17332},
  archivePrefix= {arXiv},
  primaryClass = {cs.AI},
  url          = {https://arxiv.org/abs/2511.17332},
  note         = {Accessed 2026-07-24. v2 (2026-02-10) notes presentation at
                  WMAC 2026, the AAAI-26 bridge program on LLM-based
                  multi-agent collaboration; non-archival workshop context.}
}

% ---- Cluster 3: provenance & audit-trail systems ----

@misc{wang2026auditflow,
  author       = {Wang, Yan and Ai, Xuguang and Patel, Jaisal and Peng, Xueqing
                  and Mo, Fengran and Cao, Yupeng and Li, Haohang and Cao, Mingyu
                  and Qian, Lingfei and Guti{\'e}rrez-Basulto, V{\'i}ctor},
  title        = {{AUDITFLOW: Executable Symbolic Environments for Structured
                   Financial Reporting Verification}},
  year         = {2026},
  eprint       = {2606.03031},
  archivePrefix= {arXiv},
  primaryClass = {cs.MA},
  url          = {https://arxiv.org/abs/2606.03031},
  note         = {Accessed 2026-07-24. Closest architectural neighbor to I1;
                  discuss explicitly in Related Work, not just cite.}
}

@misc{mohammadi2026atomix,
  author       = {Mohammadi, Bardia and Potamitis, Nearchos and Klein, Lars
                  and Arora, Akhil and Bindschaedler, Laurent},
  title        = {{Atomix: Timely, Transactional Tool Use for Reliable
                   Agentic Workflows}},
  year         = {2026},
  eprint       = {2602.14849},
  archivePrefix= {arXiv},
  primaryClass = {cs.MA},
  url          = {https://arxiv.org/abs/2602.14849},
  note         = {Accessed 2026-07-24}
}

@misc{nian2026auditableagents,
  author       = {Nian, Yi and Yuan, Aojie and Zhang, Haiyue and Li, Jiate
                  and Zhao, Yue},
  title        = {{Auditable Agents}},
  year         = {2026},
  eprint       = {2604.05485},
  archivePrefix= {arXiv},
  primaryClass = {cs.AI},
  url          = {https://arxiv.org/abs/2604.05485},
  note         = {Accessed 2026-07-24. Defines accountability/auditability/
                  auditing distinction used in our Related Work contrast.}
}

@misc{wang2026agenttraces,
  author       = {Wang, Yiqi and Zhang, Jiaqi and Cai, Taotao and Liu, Zirui
                  and Sun, Qingqiang and Sun, Zequn and Wu, Zhangkai and
                  Dong, Manqing and Zheng, Mingkai and Yin, Xuefei and Zhu, Yanming},
  title        = {{From Agent Traces to Trust: A Survey of Evidence Tracing
                   and Execution Provenance in LLM Agents}},
  year         = {2026},
  eprint       = {2606.04990},
  archivePrefix= {arXiv},
  primaryClass = {cs.CR},
  url          = {https://arxiv.org/abs/2606.04990},
  note         = {Accessed 2026-07-24; v4 (2026-06-28) is the cited revision.}
}

% ---- Cluster 4: field-defining / security position pieces ----

@misc{schroederdewitt2025masopenchallenges,
  author       = {Schroeder de Witt, Christian and Krawiecka, Klaudia and
                  Krawczuk, Igor and Hagag, Ben and Anderson, William L. and
                  Belcak, Peter and Bucknall, Ben and Cai, Xiaohong and
                  Chopra, Ayush and Cohen, Doron and Del Rosario, Ron F. and
                  Draguns, Andis and Gray, Annie and Katz, Keren and
                  Mavroudis, Vasilios and Mink, Jaron and Motwani, Sumeet Ramesh
                  and Petit, Jonathan and Rembeck, Leif-Sebastian and
                  Smith, Chandler and Sotiropoulos, John and Young, Steven and
                  Scheffler, Sarah and Llewellyn, Mary},
  title        = {{Open Challenges in Multi-Agent Security: Towards Secure
                   Systems of Interacting AI Agents}},
  year         = {2025},
  eprint       = {2505.02077},
  archivePrefix= {arXiv},
  primaryClass = {cs.MA},
  url          = {https://arxiv.org/abs/2505.02077},
  note         = {Accessed 2026-07-24. v1 2025-05-04, v2 2026-04-29 (cited
                  revision).}
}

@misc{karten2025llmeconomist,
  author       = {Karten, Seth and Li, Wenzhe and Ding, Zihan and
                  Kleiner, Samuel and Bai, Yu and Jin, Chi},
  title        = {{LLM Economist: Large Population Models and Mechanism
                   Design in Multi-Agent Generative Simulacra}},
  year         = {2025},
  eprint       = {2507.15815},
  archivePrefix= {arXiv},
  primaryClass = {cs.MA},
  url          = {https://arxiv.org/abs/2507.15815},
  note         = {Accessed 2026-07-24}
}
```

---

## (d) Venue shortlist

All five confirmed live (CFP or workshop page fetched directly). **Every
deadline listed has already passed relative to the 2026-07-24 access date** —
none of these are "submit now" windows; they establish the *typical cycle
timing* for planning the next one. Re-verify exact dates when the next CFP
opens.

| Venue | Type | Archival? | CC-BY / license | Typical window (verify) | arXiv endorsement gate? |
|---|---|---|---|---|---|
| **AAMAS** main track — GTEP (Game Theory & Economic Paradigms) or COINE (Coordination, Organizations, Institutions, Norms, Ethics) track | Flagship peer-reviewed conference (IFAAMAS) | **Yes.** IFAAMAS proceedings, openly available; reviews + paper also posted on OpenReview. | **Yes** — confirmed: "papers will be published under CC BY license." | AAMAS 2026 (Paphos, Cyprus): abstract Oct 1 2025, full paper Oct 8 2025, conference ~May 25–29 2026 (already past). **Verify AAMAS 2027 dates when the CFP opens** — historically an Oct-deadline/following-May-conference cycle. | **No.** Submission is to AAMAS's own OpenReview instance, not to arXiv. The gate is structurally inapplicable — you never touch arXiv's submission system to get this peer-reviewed record. |
| **GAIW** (Games, Agents, and Incentives Workshop), 8th ed. @ AAMAS 2026 | Workshop, co-located with AAMAS (merges former CoopMAS/AMEC/EXPLORE) | **No.** Confirmed: "no formal publication of workshop proceedings... accepted papers posted online for the benefit of participants." | Not stated on the CFP. | GAIW 2026 deadline: Feb 4 2026, extended to Feb 11 2026 (AoE) (passed). **Verify GAIW 2027 timing** (co-located with AAMAS 2027). | **No.** OpenReview submission direct to the workshop. |
| **LaMAS** (LLM-based Multi-Agent Systems: Towards Responsible, Reliable, and Scalable Agentic Systems) @ AAAI'26 | Workshop | **No.** Confirmed explicitly: "non-archival... accepted papers will be featured on our website with the author's permission." | Not stated. | LaMAS 2026 deadline: Nov 3 2025 (AoE) (passed). **Verify LaMAS 2027 @ AAAI'27.** | **No.** AAAI-template submission via the workshop's own channel, not arXiv. |
| **AAAI-26 Trustworthy Agentic AI Workshop** ("How Can We Trust and Control Agentic AI? Toward Alignment, Robustness, and Verifiability in Autonomous LLM Agents") | Workshop | Not stated on the CFP page (neither confirmed archival nor confirmed non-archival — **unverified, check before relying on it**). | Not stated. | Deadline: Nov 3 2025 (AoE) (passed). **Verify next cycle.** | **No.** OpenReview-based, no stated affiliation/endorsement restriction. Topics explicitly include **"verification and auditable behavior of agentic LLMs"** and **"governance, transparency, and accountability frameworks"** — the single best topical match of all venues found. |
| **Agents in the Wild: Safety, Security, and Beyond** (rotates ICLR↔ICML; 2nd ed. was ICML 2026) | Workshop | Presumed non-archival (standard for this workshop family; page states papers go to the workshop website + OpenReview, but no explicit "non-archival" statement was found — **verify**). | Not stated. | 2nd edition (ICML 2026) extended deadline: May 8 2026 AoE (passed). Next edition venue/date **TBD — verify**, it alternates. | **No.** Submission via the workshop's own OpenReview venue. |

**Bonus (not counted in the 3–5, found during the same search, topically
excellent):** *Agentic AI in the Wild: From Hallucinations to Reliable
Autonomy*, ICLR 2026 workshop (distinct from the safety/security workshop
above, confusingly similar name), organized by Chrysos, Li, Ishii, Du, Sycara
— ties hallucination-mitigation framing directly to I1. Its 2026 session
already ran (Apr 27 2026); worth tracking for a 2027 edition.
`https://iclr.cc/virtual/2026/workshop/10000810`

**On the endorsement gate specifically:** every venue above is reached
through the venue's own submission portal (OpenReview instance or workshop
form), never through arXiv's submission interface — so "does this venue
require arXiv endorsement" is category-inapplicable for all five, not merely
"no" by policy. This is a structurally different, lower-friction path than
trying to get an independent-researcher arXiv cs.MA submission endorsed
directly. One caveat, stated honestly rather than assumed: having a
peer-reviewed AAMAS acceptance in hand does **not** itself grant arXiv
endorsement (endorsement is per-person/per-category on arXiv, not
paper-conditional) — it may make finding a willing endorser easier in
practice, but that is a plausible inference, not a confirmed arXiv policy.
Verify against `info.arxiv.org/help/endorsement.html` before relying on it
(fetched 2026-07-24; page describes institutional-email auto-endorsement and
personal endorsement by an existing endorser in the target category, with no
cs.MA-specific carve-out documented).

---

## (e) Gaps — where the contribution looks novel vs. the literature

1. **Prevention vs. reconstruction is the load-bearing distinction, and it
   holds up.** Every accountability/provenance item found (Cluster 2 and 3 in
   full — items 6–13) frames auditability as the ability to *reconstruct and
   inspect what happened after it happened*: responsibility logics assign
   blame given an outcome (7, 6); "Auditable Agents" (12) explicitly scopes
   auditability to recoverability/lifecycle-coverage/policy-checkability/
   attribution/evidence-integrity — all backward-looking; the provenance
   survey (13) frames the whole field as execution-graph reconstruction. None
   treats the **ontology itself as the mechanism that makes a class of error
   unreachable at generation time** (our I1). This is a citable, specific gap,
   not an assumed one.

2. **The settlement layer already admits the gap exists, just not where we'd
   put it.** Items 1, 2, 3 (blockchain agent-payment infrastructure papers)
   explicitly flag "limited accountability" / need for "verifiable evidence"
   as open problems in 2026 papers — independent confirmation, from the
   protocol-design literature itself, that AP2/A2A-adjacent settlement rails
   do not consider this solved. Their fixes are cryptographic (registries,
   proofs, stakes) — orthogonal to, not competing with, an accounting-semantic
   correctness layer. This directly substantiates the paper's own §5
   positioning claim ("AP2 and A2A operate at a different layer") with
   external literature instead of just internal assertion.

3. **AUDITFLOW (item 10) is close enough that it must be discussed, not just
   cited, and this is the paper's biggest related-work risk if skipped.** A
   reviewer who knows this paper will ask "how is your I1 different from
   AUDITFLOW's symbolic environment?" The honest answer — AUDITFLOW verifies
   *already-filed* XBRL reports against a US-GAAP taxonomy (a check/detection
   task performed after the fact on static documents), while I1 constrains
   what an autonomous agent can *post* at transaction time, and I2 ledgers
   the cases I1's constraint can't resolve — is defensible but must be stated
   explicitly in Related Work, not left for the reviewer to notice unaided.

4. **No item makes "silent loss" a first-class, typed, measured quantity.**
   Atomix (11) is the closest infra-layer analog (transactional effects must
   commit atomically, "clean recovery under injected faults") but operates on
   generic tool-call effects, not typed accounting entries with an explicit
   `silent_losses == 0` invariant and a loss-ledger taxonomy (collision /
   placeholder / escalation / CRA flag). This specific framing — a named,
   measured, CI-gated zero — was not found anywhere in the 15 items.

5. **Caveat against overclaiming:** absence-of-evidence framing (used for
   item 14, the MAS-security field survey, and more broadly) should be stated
   in the paper as "not addressed in the venues and papers surveyed," never
   as "no one has ever done this" — the search was thorough within its 2024–
   2026 / AAMAS-AAAI-ICLR-ICML-arXiv scope but is not exhaustive (it does not
   cover, e.g., non-English-language venues, patents, or closed industry
   whitepapers). T1 should keep this qualifier when drafting the novelty
   paragraph.

---

## Search log (for reproducibility of this note, not for the paper itself)

WebSearch queries run: AAMAS 2025/2026 agent-economy+accountability+
provenance; MAS auditable financial transactions; agents-as-economic-actors
mechanism design workshops; accountability/liability AAMAS/AAAI; Agent-to-
Agent Finance / AUDITFLOW direct lookups; AAMAS/AAAI/ICLR/ICML workshop CFPs
(GAIW, LaMAS, Trustworthy Agentic AI, Agents in the Wild, Agentic AI in the
Wild); ERC-8004/x402 academic treatment; provenance/audit-trail formal models;
AAMAS'21 responsibility paper identification; IJCAI 2025/2026 agent-economy
angle. WebFetch used to pull primary metadata (author list, dates, category,
abstract) directly from each arXiv abstract page, the AIES-25 OJS page, and
the relevant workshop CFP pages — every fact attributed to a specific source
above was fetched, not inferred from a search snippet alone, except where a
row/field explicitly says otherwise (e.g. the AAMAS'21 PDF text extraction,
and Hui Gong's affiliation).
