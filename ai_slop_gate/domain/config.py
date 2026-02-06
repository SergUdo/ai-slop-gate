from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from ai_slop_gate.domain.compliance.config import ComplianceConfig
from ai_slop_gate.domain.policy import PolicyRule


@dataclass(frozen=True)
class PolicyConfig:
    enforcement: str
    ai_provider: Dict[str, Any]
    compliance: ComplianceConfig
    code_quality: Dict[str, Any]
    infrastructure_security: Dict[str, Any]
    ai_slop: Dict[str, Any]
    rules: List[PolicyRule]
    include_paths: Optional[List[str]] = None

