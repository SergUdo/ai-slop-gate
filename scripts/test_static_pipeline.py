# python -m scripts.test_static_pipeline
# python -m ai_slop_gate.cli run --policy policy.yml --provider static

# scripts/test_static_pipeline.py
#!/usr/bin/env python3
import logging
from ai_slop_gate.providers.static import StaticPipelineProvider
from ai_slop_gate.domain.policy_engine import PolicyEngine
from ai_slop_gate.cli.utils import load_policy

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Loading policy configuration...")
    policy_config, rules = load_policy("policy.yml")

    logger.info("Initializing StaticPipelineProvider...")
    provider = StaticPipelineProvider()

    logger.info("Collecting observations...")
    result = provider.collect()

    logger.info(f"Collected {len(result.observations)} observations:")
    for obs in result.observations:
        logger.info(f"  - {obs.category}: {obs.signal} ({obs.confidence}) - {obs.message}")

    logger.info("Evaluating observations with PolicyEngine...")
    engine = PolicyEngine(rules)
    decision = engine.evaluate(result.observations)

    logger.info(f"Decision: {decision.mode.value}")
    for reason in decision.reasons:
        logger.info(f"- {reason}")

if __name__ == "__main__":
    main()


