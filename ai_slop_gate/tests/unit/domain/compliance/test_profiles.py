from ai_slop_gate.domain.compliance.profiles import (
    ComplianceProfile,
    load_profiles,
    resolve_profile_chain,
)


def test_resolve_eu_profile():
    raw_profiles = [
        {"name": "base"},
        {
            "name": "oss-clean",
            "extends": "base",
            "forbid_licenses": ["GPL-3.0", "AGPL-3.0", "SSPL"],
        },
        {
            "name": "eu",
            "extends": "oss-clean",
            "data_regions": ["EU"],
        },
        {
            "name": "eu-strict",
            "extends": "eu",
            "forbid_licenses": ["LGPL-3.0"],
        },
    ]

    profiles = load_profiles(raw_profiles)

    eu = resolve_profile_chain("eu", profiles)
    eu_strict = resolve_profile_chain("eu-strict", profiles)

    assert isinstance(eu, ComplianceProfile)
    assert "GPL-3.0" in (eu.forbid_licenses or [])
    assert "EU" in (eu.data_regions or [])

    assert "LGPL-3.0" in (eu_strict.forbid_licenses or [])
    assert "GPL-3.0" in (eu_strict.forbid_licenses or [])
