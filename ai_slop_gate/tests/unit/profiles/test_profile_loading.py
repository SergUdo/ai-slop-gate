from ai_slop_gate.domain.compliance.profiles import load_profiles, resolve_profile_chain


def test_load_profiles_basic():
    raw = [
        {"name": "base", "forbid_licenses": ["GPL-3.0"]},
        {"name": "eu", "extends": "base", "forbid_licenses": ["AGPL-3.0"]},
    ]

    profiles = load_profiles(raw)

    assert "base" in profiles
    assert "eu" in profiles
    assert profiles["base"].forbid_licenses == ["GPL-3.0"]
    assert profiles["eu"].extends == "base"


def test_resolve_profile_chain_merges_forbid_licenses():
    raw = [
        {"name": "base", "forbid_licenses": ["GPL-3.0"]},
        {"name": "eu", "extends": "base", "forbid_licenses": ["AGPL-3.0"]},
    ]

    profiles = load_profiles(raw)
    resolved = resolve_profile_chain("eu", profiles)

    assert resolved.forbid_licenses == ["GPL-3.0", "AGPL-3.0"]
