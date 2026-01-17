from typing import Optional

from ai_slop_gate.domain.compliance.config import ComplianceConfig, PolicyConfig


class ComplianceObservation:
    """
    Runtime observation result of compliance checks.
    """

    def __init__(
        self,
        config: ComplianceConfig,
        violated: bool,
        reason: Optional[str] = None,
    ):
        self.config = config
        self.violated = violated
        self.reason = reason
