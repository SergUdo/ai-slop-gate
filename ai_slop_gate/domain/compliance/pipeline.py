import os
import logging
from typing import List, Optional

from ai_slop_gate.domain.observation import Observation, Location
from ai_slop_gate.domain.compliance.config import ComplianceConfig
from ai_slop_gate.providers.static.supply_chain import SupplyChainProvider

logger = logging.getLogger(__name__)


class CompliancePipeline:
    """
    Compliance Pipeline - focuses ONLY on license compliance checks.
    
    Responsibilities:
    - Forbidden license detection (GPL-2.0, GPL-3.0, AGPL-3.0, etc.)
    - Copy-left pattern alerts
    - Audit-ready output for legal teams
    
    Security checks (secrets, PII, endpoints) are handled by StaticSecurityProvider.
    """

    def __init__(self, cfg: ComplianceConfig):
        self.cfg = cfg

    def run(self, artifacts_path: str, ai_provider_region: Optional[str]) -> List[Observation]:
        observations = []
        
        logger.info(f"[CompliancePipeline] Starting compliance checks on: {artifacts_path}")
        logger.info(f"[CompliancePipeline] License audit config: {self.cfg.license_audit}")

        # Only license and data residency checks
        observations.extend(self._check_forbidden_licenses(artifacts_path))
        observations.extend(self._check_data_residency(ai_provider_region))
        
        logger.info(f"[CompliancePipeline] Total observations found: {len(observations)}")
        return observations

    # -------------------------------------------------------------------------
    # 1. Forbidden licenses - Core compliance functionality
    # -------------------------------------------------------------------------
    def _check_forbidden_licenses(self, artifacts_path: str) -> List[Observation]:
        """
        Analyzes code diffs and dependency metadata to detect high-risk 
        open-source licenses that may introduce legal or IP contamination risks.
        
        Checks for:
        - GPL-2.0, GPL-3.0, AGPL-3.0
        - Copy-left pattern alerts
        - AI-generated snippets resembling GPL-licensed code
        """
        logger.info(f"[_check_forbidden_licenses] Checking licenses in: {artifacts_path}")
        
        forbidden_list = self.cfg.license_audit.forbidden_licenses or []
        logger.info(f"[_check_forbidden_licenses] Forbidden licenses: {forbidden_list}")
        
        if not forbidden_list:
            logger.warning("[_check_forbidden_licenses] No forbidden licenses configured, skipping")
            return []

        logger.info("[_check_forbidden_licenses] Initializing SupplyChainProvider...")
        scanner = SupplyChainProvider()
        result = scanner.collect(base_path=artifacts_path)
        
        logger.info(f"[_check_forbidden_licenses] SupplyChainProvider found {len(result.observations)} observations")
        
        observations = []
        forbidden_upper = [lic.upper() for lic in forbidden_list]

        for obs in result.observations:
            message_upper = obs.message.upper()
            logger.debug(f"[_check_forbidden_licenses] Checking observation: {obs.message}")
            
            # Check if any forbidden license is mentioned
            if any(f in message_upper for f in forbidden_upper):
                logger.info(f"[_check_forbidden_licenses] ✅ Found violation: {obs.message}")
                observations.append(obs)

        logger.info(f"[_check_forbidden_licenses] Total license violations: {len(observations)}")
        return observations

    # -------------------------------------------------------------------------
    # 2. Data residency - Compliance requirement
    # -------------------------------------------------------------------------
    def _check_data_residency(self, ai_provider_region: Optional[str]) -> List[Observation]:
        """
        Validates that AI provider operates in required geographic region
        for data sovereignty compliance (GDPR, CCPA, etc.)
        """
        required = self.cfg.security_audit.enforce_data_residency
        mode = self.cfg.data_residency_mode  # advisory | blocking

        if not required:
            return []

        if not ai_provider_region:
            return [
                Observation(
                    category="compliance",
                    signal="data_residency_unknown",
                    confidence=1.0,
                    message="AI provider region is not specified.",
                    severity="medium",
                    location=Location(file="policy.yml"),
                )
            ]

        if ai_provider_region.upper() != required.upper():
            severity = "high" if mode == "blocking" else "medium"

            return [
                Observation(
                    category="compliance",
                    signal="data_residency_violation",
                    confidence=1.0,
                    message=(
                        f"AI provider region '{ai_provider_region}' does not satisfy "
                        f"required residency '{required}' (mode: {mode})."
                    ),
                    severity=severity,
                    location=Location(file="policy.yml"),
                )
            ]

        return []
    