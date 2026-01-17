#!/bin/bash
# chmod +x scripts/verify_providers.sh
# ./scripts/verify_providers.sh
set -e

echo "▶️ Verify all providers"

# Initialize config file
rm -f .ai-slop-gate.yml
python -m ai_slop_gate.cli init --force

# Run with different providers
python -m ai_slop_gate.cli run --policy policy.yml --provider static
python -m ai_slop_gate.cli run --policy policy.yml --provider eslint
python -m ai_slop_gate.cli run --policy policy.yml --provider terraform-plan
python -m ai_slop_gate.cli run --policy policy.yml --provider k8s-runtime --k8s-manifests ai_slop_gate/fixtures/k8s_test.yaml

echo "✔ All providers invoked successfully"
