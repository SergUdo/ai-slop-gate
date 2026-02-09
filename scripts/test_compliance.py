import os
import logging
import json
from pathlib import Path

from ai_slop_gate.cli.utils import load_policy
from ai_slop_gate.domain.policy_engine import PolicyEngine
from ai_slop_gate.domain.checks import CheckReport, CheckAnnotation
from ai_slop_gate.domain.compliance.pipeline import CompliancePipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("=== COMPLIANCE SMOKE TEST STARTED ===")

    TEST_REPO = "/home/serhiy/slop_test"
    POLICY_PATH = "/home/serhiy/ai-slop-gate/policy.yml"

    # Check if manifest exists, if not log a warning. The compliance pipeline relies on this manifest to perform license checks, so its absence should be highlighted for users running this test.
    manifest = Path(TEST_REPO) / ".slop" / "supply_chain.json"
    if not manifest.exists():
        logger.warning(f"⚠️ Missing manifest at {manifest}. License checks will be skipped!")

    # Load policy and log forbidden licenses. This is important for users to understand what the compliance pipeline is checking for, especially if they are testing with different AI regions that might have different policy configurations.
    try:
        policy_config, rules = load_policy(POLICY_PATH)
        logger.info(f"Policy loaded. Forbidden licenses: {policy_config.compliance.license_audit.forbidden_licenses}")
    except Exception as e:
        logger.error(f"Failed to load policy: {e}")
        return

    # Initialize the compliance pipeline with the loaded policy. This pipeline will be responsible for running the compliance checks based on the policy rules and the artifacts in the test repository.
    pipeline = CompliancePipeline(policy_config.compliance)
    
    # Determine AI provider region from policy config and log it. This is crucial for testing, as different regions might have different performance characteristics or even different policy rules, so users should be aware of which region they are testing against.
    provider_region = policy_config.ai_provider.get("region", "US")
    logger.info(f"Testing with AI region: {provider_region}")

    slop_dir = Path(TEST_REPO) / ".slop"
    slop_dir.mkdir(exist_ok=True)
    manifest_file = slop_dir / "supply_chain.json"

    mock_manifest = {
        "dependencies": [
            {"name": "bad-licensed-pkg", "license": "GPL-3.0"},
            {"name": "another-risk", "license": "AGPL-3.0"}
        ]
    }

    with open(manifest_file, "w") as f:
        json.dump(mock_manifest, f)
    logger.info(f"Generated mock manifest at {manifest_file}")

    # Run the compliance pipeline and collect observations. This step is where we actually execute the compliance checks against the test repository, and it's important to log the number of issues found to verify that the pipeline is working as expected.
    compliance_obs = pipeline.run(
        artifacts_path=TEST_REPO,
        ai_provider_region=provider_region
    )

    logger.info(f"--- Found {len(compliance_obs)} issues ---")

    # Output observations in a readable format. This helps users quickly understand the results of the compliance checks without having to parse raw JSON or logs, making it easier to identify any issues that were detected.
    for obs in compliance_obs:
        loc = f"{obs.location.file}:{obs.location.line}" if hasattr(obs.location, 'line') else obs.location.file
        print(f"[{obs.severity.upper()}] {obs.signal} at {loc} -> {obs.message}")

    # Evaluate the policy decision based on the compliance observations. This step is crucial to determine whether the detected issues lead to a blocking decision or not, and it also tests the integration between the compliance pipeline and the policy engine.
    engine = PolicyEngine(rules)
    decision = engine.evaluate(compliance_obs)

    print("-" * 60)
    print(f"FINAL DECISION: {decision.mode.name}")
    print(f"REASONS: {decision.reasons}")
    print("-" * 60)

    if len(compliance_obs) > 0:
        logger.info("✅ SUCCESS: Compliance pipeline detected violations.")
    else:
        logger.error("❌ FAILURE: Compliance pipeline returned 0 observations.")

if __name__ == "__main__":
    main()