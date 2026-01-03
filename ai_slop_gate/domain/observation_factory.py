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
    Ensures full domain contract and avoids provider-level divergence.
    """

    evidence = evidence or {}

    file = evidence.get("file")
    line = evidence.get("line")

    location = (
        f"{file}:{line}"
        if file is not None and line is not None
        else "unknown"
    )

    rule_id = rule or f"{provider}.{category}.{signal}"

    # severity is a POLICY-LEVEL concept, but providers must emit a baseline
    resolved_severity = severity or (
        "high" if confidence >= 0.9 else
        "medium" if confidence >= 0.6 else
        "low"
    )

    return Observation(
        rule_id=rule_id,
        category=category,
        signal=signal,
        message=message,
        severity=severity,
        confidence=confidence,
        location=Location(
            file=evidence.get("file"),
            line=evidence.get("line"),
        ) if evidence else None,
    )
