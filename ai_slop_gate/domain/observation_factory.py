from typing import Any, Dict, Optional
from ai_slop_gate.domain.observation import Observation, Location

def make_observation(
    *,
    provider: str,
    category: str,
    signal: str,
    confidence: float,
    message: str,
    evidence: Optional[Dict[str, Any]] = None,
    rule: Optional[str] = None,
    severity: Optional[str] = None,
) -> Observation:
    """
    Canonical Observation factory.
    """
    evidence = evidence or {}

    file_path = evidence.get("file")
    line_num = evidence.get("line")

    rule_id = rule or f"{provider}.{category}.{signal}"

    resolved_location = None
    if file_path:
        resolved_location = Location(
            file=str(file_path),
            line=int(line_num) if line_num is not None else 1
        )

    return Observation(
        rule_id=rule_id,
        category=category,
        signal=signal,
        message=message,
        severity=severity or "medium",
        confidence=confidence,
        location=resolved_location,
        evidence=evidence
    )