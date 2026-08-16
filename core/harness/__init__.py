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
from core.harness.fx_provider import (
    ChainedFXProvider,
    FXProvider,
    FXQuote,
    StaticFXProvider,
    convert,
    get_fx_provider,
    live_fx_provider,
    manual_quote,
    static_fx_provider,
    usd_per_unit,
)
from core.harness.oversight import (
    TIER_HELD,
    ReviewPolicy,
    RevocationImpact,
    held_rule_id,
    postings_by_rule,
    revocation_impact,
)
from core.harness.ontology import (
    FAMILIES_PATH,
    LOCALIZATIONS_DIR,
    ONTOLOGY_PATH,
    load_families,
    load_localization,
    load_ontology,
    merge_family_codes,
    node_fiber,
    rollup,
)
from core.harness.provenance import MappingQuote, mapping_quote
from core.harness.resolution import TIER2_RULES, resolve, resolve_with_rule
from core.harness.validation import (
    ensure_finite,
    ensure_positive_finite,
    is_finite_number,
)

__all__ = [
    "resolve",
    "resolve_with_rule",
    # Human oversight — the Co-responsibility Architecture as operations, not
    # prose. Deliberately NOT exposed on the agent-facing MCP tool surface: an
    # agent must not be able to place a hold or revoke a rule.
    "ReviewPolicy",
    "RevocationImpact",
    "TIER_HELD",
    "held_rule_id",
    "postings_by_rule",
    "revocation_impact",
    "MappingQuote",
    "mapping_quote",
    "TIER2_RULES",
    "cra_validate",
    "ensure_finite",
    "ensure_positive_finite",
    "is_finite_number",
    "load_ontology",
    "load_families",
    "load_localization",
    "merge_family_codes",
    "node_fiber",
    "rollup",
    "LOCALIZATIONS_DIR",
    "FX",
    "JCCY",
    "ONTOLOGY_PATH",
    "FAMILIES_PATH",
    # runtime FX resolution
    "FXProvider",
    "StaticFXProvider",
    "ChainedFXProvider",
    "FXQuote",
    "manual_quote",
    "get_fx_provider",
    "live_fx_provider",
    "static_fx_provider",
    "usd_per_unit",
    "convert",
]
