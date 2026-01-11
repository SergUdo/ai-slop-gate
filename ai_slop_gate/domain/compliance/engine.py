# ai_slop_gate/domain/compliance/engine.py
from typing import List
from typing import Any, Optional
from ..observation import Observation

def evaluate_compliance_risks(
    observations: List[Observation],
    license_rules: List[Any],
    secret_rules: List[Any]
) -> List[str]:
    detected_risks = []
    
    for obs in observations:
        if obs.signal == "license_violation":
            for rule in license_rules:
                for forbidden in rule.forbidden_licenses:
                    if forbidden in obs.message:
                        detected_risks.append(f"{rule.id}: {rule.message} ({forbidden})")

        if obs.signal == "secret_exposed":
            detected_risks.append(f"SECURITY-RISK: {obs.message}")
                
    return sorted(list(set(detected_risks)))