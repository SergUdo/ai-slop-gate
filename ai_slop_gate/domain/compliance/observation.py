from dataclasses import dataclass
from ai_slop_gate.domain.decision import DecisionMode

@dataclass(frozen=True)
class ComplianceObservation:
    license: str
    severity: str
    message: str

    def suggested_decision(self) -> DecisionMode:
        from ai_slop_gate.domain.compliance.enforcement import decision_for_severity
        return decision_for_severity(self.severity)
