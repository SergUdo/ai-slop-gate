from ai_slop_gate.domain.compliance.profile_resolver import ComplianceProfileResolver

def test_eu_strict_inheritance():
    resolver = ComplianceProfileResolver()
    profiles = resolver.resolve(["eu-strict"])

    names = [p.name for p in profiles]
    assert names == ["base", "oss-clean", "eu", "eu-strict"]
