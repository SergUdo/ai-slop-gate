from dataclasses import dataclass
from typing import Optional

from ai_slop_gate.domain.compliance.config import ComplianceConfig


@dataclass(frozen=True)
class PolicyConfig:
    """
    Top-level policy configuration used by the CLI and domain.
    This is the single entry point for policy-related settings.
    """

    compliance: Optional[ComplianceConfig] = None


__all__ = ["PolicyConfig", "ComplianceConfig"]
