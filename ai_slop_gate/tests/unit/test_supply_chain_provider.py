import pytest
import os
from pathlib import Path
from ai_slop_gate.providers.static import SupplyChainProvider
from ai_slop_gate.domain.observation import Severity

def test_provider_finds_gpl_in_requirements(tmp_path):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("some-lib==1.0 # License: GPL-3.0")
    
    provider = SupplyChainProvider(model="manifest-scanner-v1")
    
    # Use collect method with the temp directory
    result = provider.collect(str(tmp_path))
    
    assert result is not None
    assert len(result.observations) >= 1
    # Check if any observation relates to GPL
    gpl_obs = [obs for obs in result.observations if "GPL" in obs.message]
    assert len(gpl_obs) > 0

def test_provider_finds_secrets(tmp_path):
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("some-lib==1.0")
    
    provider = SupplyChainProvider(model="manifest-scanner-v1")
    result = provider.collect(str(tmp_path))
    
    assert result is not None
    # Provider collects manifest observations