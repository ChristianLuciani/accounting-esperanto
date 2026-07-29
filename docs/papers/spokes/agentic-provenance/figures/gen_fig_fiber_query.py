#!/usr/bin/env python3
"""Generate fig_fiber_query.tex — Figure 2 of the agentic-provenance spoke.

Claims-evidence rule: this figure asserts concrete local statutory codes, so it
is *generated from the live ontology* rather than hand-drawn. Every code, name,
``local_parent`` and ``source`` tag in the emitted TikZ comes from calling the
same deterministic ``core.harness.ontology.node_fiber`` that backs the MCP tool
``get_node_fiber`` and REST ``GET /accounts/{id}/fiber``. Re-running this script
after an ontology or localization change updates the figure, so the figure can
never silently drift from the data it depicts.

Usage (from the repository root):
  python docs/papers/spokes/agentic-provenance/figures/gen_fig_fiber_query.py

Output: docs/papers/spokes/agentic-provenance/figures/fig_fiber_query.tex
        (committed; \\input by main.tex)

Jurisdiction choice: DE, BR and MX are shown because each exhibits a different
lineage shape (two chart dialects; a dotted hierarchical code; a code carried by
the Tier-1 index and enriched by the localization). FR is deliberately not
shown: its PCG mapping currently carries a data defect (code 211 "Terrains"
points at the cash UUID), tracked separately as a hub-side fix. Depicting it
would put a known-wrong preimage in a published figure.
"""

from __future__ import annotations

import os
import sys

# figures/ -> agentic-provenance/ -> spokes/ -> papers/ -> docs/ -> repository root
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), *[".."] * 5))
sys.path.insert(0, REPO_ROOT)

from core.harness.ontology import (  # noqa: E402
    load_families,
    load_ontology,
    merge_family_codes,
    node_fiber,
)

NODE = "asset.current.cash"
JURISDICTIONS = ["de", "br", "mx"]
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fig_fiber_query.tex")

# Human-readable jurisdiction labels for the figure (ISO 3166-1 alpha-2 -> name).
JUR_LABEL = {"de": "DE --- SKR (Germany)", "br": "BR --- SPED (Brazil)", "mx": "MX --- SAT (Mexico)"}

# x positions of the three fiber columns, in TikZ cm.
JUR_X = {"de": -5.35, "br": 0.0, "mx": 5.35}


def tex_escape(s: str) -> str:
    """Escape the LaTeX specials that can appear in statutory names/codes."""
    out = str(s)
    for a, b in (
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ):
        out = out.replace(a, b)
    return out


def member_lines(members: list[dict]) -> str:
    """Render one jurisdiction's fiber members as TikZ-safe LaTeX lines."""
    lines = []
    for m in members:
        bits = [r"\texttt{%s}" % tex_escape(m["code"])]
        if m.get("name"):
            bits.append(tex_escape(m["name"]))
        line = " --- ".join(bits)
        extras = []
        if m.get("local_parent") is not None:
            extras.append(r"parent \texttt{%s}" % tex_escape(m["local_parent"]))
        if m.get("aggregation_group") is not None:
            extras.append(r"group \texttt{%s}" % tex_escape(m["aggregation_group"]))
        facets = m.get("facets")
        if isinstance(facets, dict):
            extras.extend(
                r"\texttt{%s: %s}" % (tex_escape(k), tex_escape(v)) for k, v in sorted(facets.items())
            )
        extras.append(r"{\itshape %s}" % tex_escape(m.get("source", "")).replace(r"\_", r"\_"))
        line += r"\\[-1pt] {\scriptsize " + " $\\cdot$ ".join(extras) + "}"
        lines.append(line)
    return r"\\[3pt] ".join(lines)


def main() -> int:
    accounts, by_code, _collisions, _placeholders = load_ontology()
    by_code = merge_family_codes(by_code, load_families())

    universal = node_fiber(accounts, by_code, NODE)
    if universal is None:
        raise SystemExit(f"node {NODE!r} not found in the ontology")

    per_jur = {}
    for iso in JURISDICTIONS:
        fib = node_fiber(accounts, by_code, NODE, iso)
        members = (fib or {}).get("jurisdictions", {}).get(iso, [])
        if not members:
            raise SystemExit(f"empty fiber for {NODE!r} in jurisdiction {iso!r}")
        per_jur[iso] = members

    body = []
    for iso in JURISDICTIONS:
        body.append(
            "\\node[fiber] (%s) at (%.2f,-2.60)\n  {\\textbf{%s}\\\\[3pt] %s};"
            % (iso, JUR_X[iso], JUR_LABEL[iso], member_lines(per_jur[iso]))
        )
        body.append("\\draw[->, thick, clappsAccent!70!black] (node.south) -- (%s.north);" % iso)

    with open(OUT, "w", encoding="utf-8") as fh:
        fh.write(
            TEMPLATE
            % {
                "node_id": tex_escape(NODE),
                "uuid": tex_escape(universal["kontablo_uuid"]),
                "label": tex_escape(universal["label_en"]),
                "total_codes": universal["total_codes"],
                "n_jurisdictions": len(universal["jurisdictions"]),
                "shown": ", ".join(j.upper() for j in JURISDICTIONS),
                "body": "\n".join(body),
                "script": "docs/papers/spokes/agentic-provenance/figures/gen_fig_fiber_query.py",
            }
        )
    print(f"Wrote {OUT}")
    print(
        f"  {NODE}: {universal['total_codes']} local codes across "
        f"{len(universal['jurisdictions'])} jurisdictions; shown: {JURISDICTIONS}"
    )
    return 0


TEMPLATE = r"""%%%% =====================================================================
%%%% Figure 2 --- the pre-transaction fiber query (invariant I3)
%%%%
%%%% GENERATED FILE --- do not edit by hand.
%%%% Regenerate with:  python %(script)s
%%%%
%%%% Every code, name, local_parent and source tag below is emitted by
%%%% core.harness.ontology.node_fiber() over the committed ontology and
%%%% localization files --- the same function behind the MCP tool
%%%% get_node_fiber and REST GET /accounts/{id}/fiber.
%%%% =====================================================================
\begin{figure}[t]
\centering
\fitwidth{%%
\begin{tikzpicture}[
    >=Latex,
    font=\small,
    ask/.style={draw=clappsInk!80, rounded corners=4pt, fill=clappsInk!7,
                text width=8.6cm, align=center, minimum height=0.9cm,
                font=\small},
    uni/.style={draw=clappsAccent!85!black, line width=1.0pt,
                rounded corners=4pt, fill=clappsAccent!10, text width=8.6cm,
                align=center, minimum height=1.1cm, font=\small},
    fiber/.style={draw=clappsAccent!60!black, rounded corners=4pt, fill=white,
                  text width=4.55cm, align=left, font=\scriptsize,
                  anchor=north},
    lbl/.style={font=\scriptsize, inner sep=2pt}
]

\node[ask] (ask) at (0,2.05)
  {\textbf{Agent, \emph{before} committing the transaction:}\\[2pt]
   \texttt{get\_node\_fiber("%(node_id)s", jurisdiction)}};

\node[uni] (node) at (0,-0.45)
  {\textbf{universal node} \texttt{%(node_id)s}\\[1pt]
   {\scriptsize \texttt{%(uuid)s} --- ``%(label)s''}\\[2pt]
   {\scriptsize preimage: %(total_codes)d local codes across
    %(n_jurisdictions)d jurisdictions (%(shown)s shown)}};

\draw[->, thick, clappsInk!70] (ask) -- (node);

%(body)s

\end{tikzpicture}%%
}
\caption{The pre-transaction fiber query (\textbf{I3}). Given a universal node,
the layer returns its \emph{preimage}: which local statutory codes collapse into
it in each jurisdiction, with the local structure the projection would otherwise
flatten away (the local parent, the analytical facets, the declared aggregation
group), and a \texttt{source} tag saying whether the member came from the
deterministic Tier-1 index or from the jurisdiction's localization file. Because
the query is available \emph{before} the agent posts, auditability is a
precondition of the transaction rather than a forensic reconstruction after it.
This figure is generated, not drawn: every code and label is emitted by
\texttt{node\_fiber} (\protect\pathtt{core/harness/ontology.py}) over the committed
ontology, via \protect\pathtt{%(script)s}.}
\label{fig:fiber-query}
\end{figure}
"""


if __name__ == "__main__":
    raise SystemExit(main())
