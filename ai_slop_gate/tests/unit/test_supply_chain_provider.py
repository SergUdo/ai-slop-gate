import pytest
import os
from ai_slop_gate.providers.supply_chain import SupplyChainProvider
from ai_slop_gate.domain.observation import Severity

def test_provider_finds_gpl_in_requirements(tmp_path):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("some-lib==1.0 # License: GPL-3.0")
    
    provider = SupplyChainProvider(policy={"enabled": True})
    
    observations = provider._scan_manifest(str(req_file))
    
    assert len(observations) == 1
    obs = observations[0]
    assert obs.signal == "license_violation"
    assert "GPL-3.0" in obs.message
    assert obs.severity == Severity.HIGH
    assert obs.location.file == str(req_file)

def test_provider_finds_secrets(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("API_KEY='secret123'")
    
    provider = SupplyChainProvider(policy={"enabled": True})
    observations = provider._scan_manifest(str(env_file))
    
    assert len(observations) == 1
    assert observations[0].signal == "secret_exposed"
    assert "secret" in observations[0].message.lower()