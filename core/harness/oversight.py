"""Human oversight of the deterministic resolver — the Co-responsibility
Architecture made executable.

The CRA grants the accountable human two authorization modes: a *standing
ex-ante authorization* of the deterministic policy, and *per-exception
disposition* of the residual. Both were previously only describable — the
provenance to support them existed (every resolution carries the exact
``rule_id`` that fired, ``core.harness.provenance``) but nothing consumed it, so
the human's authority was a claim about the data rather than an operation over
it. This module closes that gap.

Two capabilities, one prospective and one retrospective:

  * :class:`ReviewPolicy` — the human can **withdraw** standing authorization
    from a rule, a jurisdiction, or a node at any moment. Matching entries stop
    resolving automatically and become typed, counted records instead. This is
    the ``potestad de pausar``: the power to interrupt automatic classification
    is continuous and never suspended, whether or not it is exercised.

  * :func:`postings_by_rule` / :func:`revocation_impact` — given a rule the human
    concludes was wrong, enumerate **every posting that rule produced**. This is
    what changes the unit of human decision from the transaction to the rule: one
    judgement disposes of a whole class, past and future.

**Deliberately not on the agent-facing tool surface.** An agent must not be able
to place or release a hold, or to revoke a rule — that would hand the constraint
to the party the constraint exists to bound. These are human-facing operations
(``core.harness`` and, above it, the operator surfaces), and the MCP tool surface
stays at its six deterministic agent tools.

Nothing here calls an LLM, and nothing here is stochastic. A hold is a set
membership test; a revocation impact is a filter over committed provenance.

**Default-off by construction.** ``ReviewPolicy()`` with no arguments holds
nothing and :func:`resolve_with_rule` behaves exactly as before, so the published
claims-evidence numbers are untouched (verified: ``results.json`` regenerates
byte-for-byte).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, Iterable, List, Optional, Sequence

# Tier value stamped on a resolution the human has withheld from automatic
# classification. It is NOT "escalated": an escalation means the resolver found
# no deterministic answer, whereas a hold means it found one and a human decided
# it must not be applied unreviewed. Conflating them would lose exactly the
# distinction the loss ledger exists to preserve.
TIER_HELD = "held"


@dataclass(frozen=True)
class ReviewPolicy:
    """Which resolutions the accountable human has withdrawn from standing
    ex-ante authorization.

    Empty by default — an empty policy holds nothing. Each field narrows
    automatic resolution without ever making it *silently* fail: a held entry
    produces a typed record, so ``silent_losses`` stays 0 (invariant I2).

    ``reason`` is free text for the human's own audit trail; it is never parsed
    or branched on (program logic must never key on free text — architectural
    principle #5).
    """

    held_rules: FrozenSet[str] = frozenset()
    held_jurisdictions: FrozenSet[str] = frozenset()
    held_nodes: FrozenSet[str] = frozenset()
    reason: str = ""

    @classmethod
    def build(
        cls,
        *,
        rules: Iterable[str] = (),
        jurisdictions: Iterable[str] = (),
        nodes: Iterable[str] = (),
        reason: str = "",
    ) -> "ReviewPolicy":
        """Convenience constructor accepting any iterables.

        Jurisdictions are lower-cased to match the resolver's convention.
        """
        return cls(
            held_rules=frozenset(str(r) for r in rules),
            held_jurisdictions=frozenset(str(j).lower() for j in jurisdictions),
            held_nodes=frozenset(str(n) for n in nodes),
            reason=reason,
        )

    @property
    def holds_nothing(self) -> bool:
        return not (self.held_rules or self.held_jurisdictions or self.held_nodes)

    def hold_scope(
        self,
        *,
        rule_id: Optional[str],
        jurisdiction: Optional[str],
        kontablo_id: Optional[str],
    ) -> Optional[str]:
        """Return which scope holds this resolution, or ``None`` if it is free.

        The returned string is a stable, machine-comparable scope name
        (``"rule"`` | ``"jurisdiction"`` | ``"node"``) — not a human message —
        so downstream logic can branch on it deterministically. Checked
        most-specific first so the recorded scope is the narrowest that applies.
        """
        if rule_id is not None and rule_id in self.held_rules:
            return "rule"
        if jurisdiction is not None and jurisdiction.lower() in self.held_jurisdictions:
            return "jurisdiction"
        if kontablo_id is not None and kontablo_id in self.held_nodes:
            return "node"
        return None


def held_rule_id(scope: str, original_rule_id: Optional[str]) -> str:
    """The ``rule_id`` stamped on a withheld resolution.

    Format ``held:<scope>:<the rule that would have fired>`` — so the audit
    records both *that* a human intervened and *what* the resolver would
    otherwise have done. Withholding a resolution must not destroy the
    information about which rule was withheld; that would be a silent loss of
    the very fact under review.
    """
    return f"held:{scope}:{original_rule_id if original_rule_id is not None else 'none'}"


def postings_by_rule(entries: Sequence[object]) -> Dict[Optional[str], List[object]]:
    """``rule_id`` -> the resolved entries that rule produced.

    The dual of ``ConsolidationResult.lineage()``: lineage groups entries by the
    consolidated line they aggregated into (*what* was produced), this groups
    them by the rule that produced them (*why*). Both views read the same
    committed provenance.

    Accepts anything carrying a ``.mapping`` with a ``.rule_id`` (a
    ``ResolvedEntry``), or a ``MappingQuote`` directly. Entries with no
    provenance at all are grouped under ``None`` rather than dropped.
    """
    out: Dict[Optional[str], List[object]] = {}
    for rec in entries:
        quote = getattr(rec, "mapping", rec)
        rule = getattr(quote, "rule_id", None)
        out.setdefault(rule, []).append(rec)
    return out


@dataclass
class RevocationImpact:
    """What revoking a set of rules would affect.

    Answers the question a human needs answered *before* revoking: how much of
    the ledger did this rule decide, and which consolidated figures move if the
    decision is withdrawn?
    """

    revoked_rules: FrozenSet[str]
    affected_entries: List[object] = field(default_factory=list)
    affected_nodes: FrozenSet[str] = frozenset()
    affected_jurisdictions: FrozenSet[str] = frozenset()

    @property
    def entry_count(self) -> int:
        return len(self.affected_entries)

    @property
    def is_empty(self) -> bool:
        return not self.affected_entries


def revocation_impact(
    entries: Sequence[object], rule_ids: Iterable[str]
) -> RevocationImpact:
    """Enumerate every posting produced by any of ``rule_ids``.

    This is the operation behind the claim that the human's unit of decision is
    the rule rather than the transaction: one judgement about a rule resolves the
    disposition of every entry it produced. Per-transaction review scales with
    volume; this does not.

    Deterministic and side-effect free — it reports, it does not mutate. Applying
    the revocation is a separate, human-authorized act (see :class:`ReviewPolicy`
    for the prospective half).
    """
    targets = frozenset(str(r) for r in rule_ids)
    by_rule = postings_by_rule(entries)
    affected: List[object] = []
    for rule in targets:
        affected.extend(by_rule.get(rule, []))
    nodes = {
        kid
        for rec in affected
        if (kid := getattr(rec, "kontablo_id", None)) is not None
    }
    jurisdictions = {
        j.lower()
        for rec in affected
        if (j := getattr(rec, "jurisdiction", None)) is not None
    }
    return RevocationImpact(
        revoked_rules=targets,
        affected_entries=affected,
        affected_nodes=frozenset(nodes),
        affected_jurisdictions=frozenset(jurisdictions),
    )
