# ai_slop_gate/tests/unit/domain/compliance/test_profiles.py
import pytest
from ai_slop_gate.domain.compliance.profile_resolver import ComplianceProfileResolver

def test_resolve_eu_profile():
    resolver = ComplianceProfileResolver()
    profiles = resolver.resolve(["eu-strict"])
    # Stage 0.6: eu-strict extends eu -> oss-clean -> base
    assert "eu" in profiles
    assert "oss-clean" in profiles
