from ai_slop_gate.domain.compliance.effective_policy import EffectiveCompliancePolicy
from ai_slop_gate.domain.compliance.profiles import EU_PROFILE, OSS_CLEAN_PROFILE

def test_profile_merge():
    policy = EffectiveCompliancePolicy([EU_PROFILE, OSS_CLEAN_PROFILE])
    assert "GPL-3.0" in policy.forbid_licenses
