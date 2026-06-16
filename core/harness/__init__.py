"""Kontablo harness — the deterministic core of the reference implementation.

This package is the single importable home for the mechanics the preprint calls
the **harness** (``docs/papers/drafts/sections/harness_architecture.tex``):
the model-independent scaffold that turns a stochastic proposal into a
verifiable mapping. Paper-term -> code correspondence:

  * "three-tier router"               -> :func:`resolve` (``resolution``)
  * "ontology-as-constraint"          -> :func:`load_ontology` (``ontology``)
  * "Deterministic Boundary Library"  -> :func:`cra_validate` (``boundary``)

Everything here is deterministic — a graph lookup, a keyword rule, or an
accounting invariant. No module in this package calls an LLM.

It is the shared dependency of every consuming surface — ``core.engine``, the
gRPC servicer, and the ``scripts/mass_consolidation_v2.py`` validation runner —
so the published 97.3% deterministic-coverage number is produced by exactly one
implementation of the rules, behind the CI claims-evidence gate. (Before this
extraction the dependency ran backwards: ``core.engine`` imported its core logic
*from* the validation script.)
"""

from __future__ import annotations

from core.harness.boundary import cra_validate
from core.harness.fx import FX, JCCY
from core.harness.ontology import (
    FAMILIES_PATH,
    ONTOLOGY_PATH,
    load_families,
    load_ontology,
    merge_family_codes,
)
from core.harness.resolution import TIER2_RULES, resolve

__all__ = [
    "resolve",
    "TIER2_RULES",
    "cra_validate",
    "load_ontology",
    "load_families",
    "merge_family_codes",
    "FX",
    "JCCY",
    "ONTOLOGY_PATH",
    "FAMILIES_PATH",
]
