# ai_slop_gate/domain/observation_result.py
from typing import List
from .observation import Observation

class ObservationResult:
    def __init__(self, observations: List[Observation]):
        self.observations = observations
