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

    # Перевірка чи є файл маніфесту (без нього ліцензії не знайдуться)
    manifest = Path(TEST_REPO) / ".slop" / "supply_chain.json"
    if not manifest.exists():
        logger.warning(f"⚠️ Missing manifest at {manifest}. License checks will be skipped!")

    # Завантажуємо політику
    try:
        policy_config, rules = load_policy(POLICY_PATH)
        logger.info(f"Policy loaded. Forbidden licenses: {policy_config.compliance.license_audit.forbidden_licenses}")
    except Exception as e:
        logger.error(f"Failed to load policy: {e}")
        return

    # Ініціалізуємо пайплайн
    pipeline = CompliancePipeline(policy_config.compliance)
    
    # Визначаємо регіон провайдера (спеціально ставимо не EU для тесту)
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

    # Запуск аналізу
    compliance_obs = pipeline.run(
        artifacts_path=TEST_REPO,
        ai_provider_region=provider_region
    )

    logger.info(f"--- Found {len(compliance_obs)} issues ---")

    # Детальний вивід кожної знахідки
    for obs in compliance_obs:
        loc = f"{obs.location.file}:{obs.location.line}" if hasattr(obs.location, 'line') else obs.location.file
        print(f"[{obs.severity.upper()}] {obs.signal} at {loc} -> {obs.message}")

    # Оцінка політикою
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