"""Non-authoritative System-1 advisory contracts built on Laya.

These helpers deliberately separate prediction from authority. They may
classify or triage an AutoDev context, but callers must apply their own
deterministic governance, evidence and budget controls before mutation.
"""
from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Mapping


_AUTODEV_QUESTIONS: Dict[str, Dict[str, Any]] = {
    "action": {
        "type": "choice",
        "instructions": "What is the safest next development action for this admitted AutoDev context?",
        "criteria": {
            "analyze": "inspect evidence and architecture without repository mutation",
            "fix": "repair a concrete defect or failing test supported by evidence",
            "harden": "reduce security, reliability, governance, or operational risk",
            "converge": "finish or simplify an already documented implementation",
            "verify": "run or improve deterministic verification and evidence collection",
            "defer": "do not implement yet because evidence, authority, or prerequisites are insufficient",
        },
    },
    "needs_review": {
        "type": "noul",
        "instructions": "Does this context require independent human or higher-authority review before governed execution?",
    },
    "outcome": {
        "type": "choice",
        "instructions": "What outcome class best matches the current context?",
        "criteria": {
            "implementation": "bounded code or configuration change",
            "verification": "tests, evidence, audit, or reproduction work",
            "research": "additional evidence or requirements must be acquired first",
            "blocked": "a material blocker prevents safe progress",
        },
    },
    "risk": {
        "type": "score",
        "instructions": "How risky would it be to act on this context before additional verification?",
        "criteria": [
            "low and reversible",
            "moderate with contained blast radius",
            "high or materially uncertain",
            "critical, privileged, destructive, or difficult to reverse",
        ],
    },
    "urgency": {
        "type": "score",
        "instructions": "How urgent is it to address this development context?",
        "criteria": [
            "no immediate urgency",
            "should be scheduled",
            "important current blocker or quality risk",
            "critical incident, security issue, or release blocker",
        ],
    },
}


def autodev_questions() -> Dict[str, Dict[str, Any]]:
    """Return a fresh question schema for the typed-decisions checkpoint."""
    return deepcopy(_AUTODEV_QUESTIONS)


def run_autodev_advisory(router: Any, state: Mapping[str, Any] | str) -> Dict[str, Any]:
    """Run the AutoDev advisory workflow through a Laya Router."""
    result = router.predict(state, autodev_questions(), task="typed_decisions")
    payload = dict(result)
    payload["advisory"] = {
        "schema": "laya.autodev.system1-advisory.v1",
        "authoritative": False,
        "role": "fast_classification_and_triage",
        "required_next_authority": "deterministic_autodev_policy_and_hermes_brain",
        "forbidden_direct_effects": [
            "merge",
            "deploy",
            "budget_increase",
            "credential_mutation",
            "financial_transfer",
            "destructive_infrastructure",
            "evidence_rewrite",
        ],
    }
    return payload
