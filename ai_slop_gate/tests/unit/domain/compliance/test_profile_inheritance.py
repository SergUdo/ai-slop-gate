from ai_slop_gate.domain.compliance.profiles import load_profiles, resolve_profile_chain


def test_profile_inheritance_merges_fields():
    raw_profiles = [
        {"name": "base", "forbid_licenses": ["GPL-2.0"]},
        {
            "name": "child",
            "extends": "base",
            "forbid_licenses": ["GPL-3.0"],
            "data_regions": ["EU"],
        },
    ]

    profiles = load_profiles(raw_profiles)
    child = resolve_profile_chain("child", profiles)

    assert "GPL-2.0" in (child.forbid_licenses or [])
    assert "GPL-3.0" in (child.forbid_licenses or [])
    assert "EU" in (child.data_regions or [])
