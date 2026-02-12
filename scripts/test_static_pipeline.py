# python -m scripts.test_static_pipeline
# python -m ai_slop_gate.cli run --policy policy.yml --provider static

# scripts/test_static_pipeline.py
#!/usr/bin/env python3
import logging
from ai_slop_gate.providers.static.static_pipeline import StaticPipelineProvider
from ai_slop_gate.domain.policy_engine import PolicyEngine
from ai_slop_gate.cli.utils import load_policy

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def main():
    try:
        policy_config, rules = load_policy("policy.yml")
    except Exception as e:
        logger.error(f"Failed to load policy: {e}")
        return

    # 2. Ініціалізація Пайплайну
    logger.info("🚀 Starting Static Analysis Pipeline (Static + Trivy)...")
    provider = StaticPipelineProvider()

    result = provider.collect(".")

    logger.info(f"📊 Collected {len(result.observations)} findings:")
    for obs in result.observations:
        color = "🔴" if obs.severity == "critical" or obs.severity == "high" else "🟡"
        logger.info(f"  {color} [{obs.category.upper()}] {obs.message} (Sev: {obs.severity})")

    engine = PolicyEngine(rules)
    decision = engine.evaluate(result.observations)

    logger.info("---")
    logger.info(f"⚖️ Final Decision: {decision.mode.value.upper()}")
    for reason in decision.reasons:
        logger.info(f"  - {reason}")

if __name__ == "__main__":
    main()