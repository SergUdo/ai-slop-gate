from pathlib import Path
from typing import List, Optional, Dict
import yaml

from ai_slop_gate.domain.observation import Observation
from .profiles import load_profiles, resolve_profile_chain, ComplianceProfile
from .gateway import ComplianceGateway


class CompliancePipeline:
    """
    Deterministic compliance pipeline for ai-slop-gate.

    Responsibilities:
    - Load compliance profiles from policy.yml
    - Resolve inheritance chains via 'extends'
    - Run deterministic analysis via ComplianceGateway
    - Return canonical Observations
    """

    def __init__(self, policy_path: str):
        self.policy_path = Path(policy_path)
        if not self.policy_path.exists():
            raise FileNotFoundError(f"Policy file not found: {policy_path}")

        with self.policy_path.open("r") as f:
            self.policy_dict: dict = yaml.safe_load(f)

        self.raw_profiles = self.policy_dict.get("compliance", {}).get("profiles", [])
        self.profiles: Dict[str, ComplianceProfile] = load_profiles(self.raw_profiles)

        self.enforcement: str = self.policy_dict.get("enforcement", "advisory")
        self.gateway: ComplianceGateway = ComplianceGateway(config=None)

    def run(
        self,
        artifacts_path: str,
        profile_name: Optional[str] = None
    ) -> List[Observation]:

        if not self.profiles:
            return []

        name = profile_name or (
            self.raw_profiles[0]["name"] if self.raw_profiles else "default"
        )

        merged_profile: ComplianceProfile = resolve_profile_chain(name, self.profiles)

        self.gateway.config = merged_profile

        observations: List[Observation] = self.gateway.analyze(artifacts_path)
        return observations
