from laya.advisory import autodev_questions, run_autodev_advisory


class StubRouter:
    def __init__(self):
        self.calls = []

    def predict(self, state, questions, **kwargs):
        self.calls.append((state, questions, kwargs))
        return {
            "answers": {
                "action": {"choice": "verify", "confidence": 0.91},
                "needs_review": {"noul": 0.72},
                "outcome": {"choice": "verification", "confidence": 0.88},
                "risk": {"score": 2.0},
                "urgency": {"score": 1.0},
            },
            "routing": {"model": "typed-decisions"},
        }


def test_autodev_question_ids_match_typed_decisions_workflow():
    assert set(autodev_questions()) == {
        "action",
        "needs_review",
        "outcome",
        "risk",
        "urgency",
    }


def test_autodev_questions_returns_fresh_copy():
    first = autodev_questions()
    first["action"]["criteria"]["new"] = "mutation"
    assert "new" not in autodev_questions()["action"]["criteria"]


def test_autodev_advisory_is_explicitly_non_authoritative():
    router = StubRouter()
    result = run_autodev_advisory(router, {"repo": "lucadeg/example", "risk": "unknown"})

    assert router.calls[0][2]["task"] == "typed_decisions"
    assert result["routing"]["model"] == "typed-decisions"
    assert result["advisory"]["authoritative"] is False
    assert result["advisory"]["provider"] == "laya"
    assert result["advisory"]["signals"]["action"] == "verify"
    assert result["advisory"]["signals"]["action_confidence"] == 0.91
    assert result["advisory"]["signals"]["needs_review_probability"] == 0.72
    assert result["advisory"]["required_next_authority"] == (
        "deterministic_autodev_policy_and_hermes_brain"
    )
    assert "merge" in result["advisory"]["forbidden_direct_effects"]
    assert "deploy" in result["advisory"]["forbidden_direct_effects"]
