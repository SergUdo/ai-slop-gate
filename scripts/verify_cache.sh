#!/bin/bash
# chmod +x scripts/verify_cache.sh
# ./scripts/verify_cache.sh
set -euo pipefail

echo "▶️ Verify CLI with cache"

POLICY_FILE="policy.yml"
K8S_TEST_MANIFEST="ai_slop_gate/fixtures/k8s_test.yaml"

# Define the providers to test
PROVIDERS=("static" "eslint" "terraform-plan")

for PROVIDER in "${PROVIDERS[@]}"; do
  echo ">>> Testing provider: $PROVIDER"
  python -m ai_slop_gate.cli.main run\
    --policy "$POLICY_FILE" \
    --provider "$PROVIDER" \
    --enforcement "advisory" \
    ${K8S_TEST_MANIFEST:+--k8s-manifests "$K8S_TEST_MANIFEST"}
done

echo "✔ All providers ran successfully with cache"
