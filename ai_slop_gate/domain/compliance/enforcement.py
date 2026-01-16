from ai_slop_gate.domain.decision import DecisionMode

SEVERITY_TO_DECISION = {
    "low": DecisionMode.ADVISORY,
    "medium": DecisionMode.ADVISORY,
    "high": DecisionMode.BLOCKING,
}

def decision_for_severity(severity: str) -> DecisionMode:
    return SEVERITY_TO_DECISION.get(severity, DecisionMode.ADVISORY)
