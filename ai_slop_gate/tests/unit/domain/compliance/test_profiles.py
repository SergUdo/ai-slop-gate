from ai_slop_gate.domain.compliance.profile_resolver import ComplianceProfileResolver

def test_resolve_eu_profile():
    resolver = ComplianceProfileResolver()
    profiles = resolver.resolve(["eu"])

    assert profiles[0].name == "eu"
