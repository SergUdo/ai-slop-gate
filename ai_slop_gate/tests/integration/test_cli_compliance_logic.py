import pytest
import yaml
import os
from ai_slop_gate.cli.main import run_compliance_enrichment

class MockArgs:
    def __init__(self, policy, compliance=False):
        self.policy = str(policy)
        self.compliance = compliance
        self.no_compliance = False

def test_run_compliance_enrichment_logic(tmp_path):
    policy_file = tmp_path / "policy.yml"
    policy_content = {
        "compliance": {
            "enabled": True,
            "license_audit": {"forbidden_licenses": ["GPL-3.0"]}
        }
    }
    policy_file.write_text(yaml.dump(policy_content))
    
    req_file = tmp_path / "requirements.txt"
    req_file.write_text("gpl-library==3.0.0 # License: GPL-3.0")

    old_cwd = os.getcwd()
    os.chdir(tmp_path)
    
    try:
        class Args:
            policy = str(policy_file)
            compliance = True
            no_compliance = False

        results = run_compliance_enrichment(Args(), [])
        
        if not results:
            print(f"Content of {req_file}: {req_file.read_text()}")
            
        assert len(results) > 0, "Should find GPL violation"
        assert any("GPL-3.0" in r for r in results)
    finally:
        os.chdir(old_cwd)
