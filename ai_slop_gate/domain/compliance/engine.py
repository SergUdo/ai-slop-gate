# ai_slop_gate/domain/compliance/engine.py
from typing import List
from typing import Any, Optional
from ..observation import Observation

def evaluate_compliance_risks(observations, license_rules, secret_rules):
    risks = []
    for obs in observations:
        if obs.signal == "FORBIDDEN_LICENSE":
            risks.append(f"License risk: {obs.evidence['license']}")
        elif obs.signal == "SECRET_EXPOSED":
            risks.append("security-risk: secret exposed")
    return risks
