from dataclasses import dataclass
from typing import List, Optional

from .decision import Decision, DecisionMode, Annotation
from .observation import Observation

@dataclass(frozen=True)
class PolicyRule:
    id: str
    category: str
    signal: str
    min_confidence: float
    action: str          # "advisory" | "blocking"
    message: str

def evaluate_policy(
    observations: List[Observation],
    rules: List[PolicyRule],
) -> Decision:
    reasons: list[str] = []
    annotations: list[Annotation] = []
    mode = DecisionMode.ADVISORY

    for obs in observations:
        for rule in rules:
            if (
                obs.category == rule.category
                and obs.signal == rule.signal
                and obs.confidence >= rule.min_confidence
            ):
                reasons_set = set()
                reasons_set.add(rule.message)

                if hasattr(obs, 'evidence') and obs.evidence and "file" in obs.evidence:
                    annotations.append(
                        Annotation(
                            file=obs.evidence["file"],
                            line=obs.evidence.get("line", 1),
                            message=rule.message,
                            level="error" if rule.action == "blocking" else "warning"
                        )
                    )

                if rule.action == "blocking":
                    mode = DecisionMode.BLOCKING

    return Decision(
        mode=mode,
        reasons=sorted(reasons_set),
        annotations=annotations if annotations is not None else []
    )
