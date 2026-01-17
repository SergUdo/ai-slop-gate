from dataclasses import dataclass
from typing import Optional, Dict, Any
from ai_slop_gate.domain.decision import DecisionMode


@dataclass(frozen=True)
class ComplianceObservation:
    """
    A single compliance violation detected by the gateway.
    Fully compatible with PolicyEngine.
    """

    license: str
    severity: str
    message: str

    category: str = "COMPLIANCE"
    signal: str = "FORBIDDEN_LICENSE"
    confidence: float = 1.0
    evidence: Optional[Dict[str, Any]] = None

    def suggested_decision(self):
        # Backward compatibility for older tests
        return DecisionMode.BLOCKING
