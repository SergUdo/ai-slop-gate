from ai_slop_gate.domain.decision import Decision, DecisionMode
from ai_slop_gate.domain.contracts import PolicyRule
from ai_slop_gate.domain.observation import Observation


class PolicyEngine:
    """
    Stage 0.7 policy evaluator.
    Uses the new PolicyRule contract:
    - rule.when: {category, signal, min_confidence}
    - rule.then: {action, message}
    """

    def __init__(self, rules):
        self.rules = rules or []

    def evaluate(self, observations):
        # No rules → ALLOW
        if not self.rules:
            return Decision(
                mode=DecisionMode.ALLOW,
                reasons=[],
                annotations=[]
            )

        reasons = []
        annotations = []
        mode = DecisionMode.ALLOW

        for obs in observations:
            for rule in self.rules:
                when = rule.when
                then = rule.then

                if (
                    obs.category == when.get("category")
                    and obs.signal == when.get("signal")
                    and obs.confidence >= when.get("min_confidence", 0.0)
                ):
                    # Add reason
                    reasons.append(then.get("message"))

                    # Blocking rule overrides everything
                    if then.get("action") == "blocking":
                        mode = DecisionMode.BLOCKING
                    else:
                        # advisory rule only applies if no blocking rule triggered
                        if mode != DecisionMode.BLOCKING:
                            mode = DecisionMode.ADVISORY

        return Decision(
            mode=mode,
            reasons=reasons,
            annotations=annotations,
        )
