#!/bin/bash
# chmod +x scripts/verify_providers.sh
# ./scripts/verify_providers.sh
set -e

echo "▶️ Verify all providers"

rm -f .ai-slop-gate.yml

python -m ai_slop_gate.cli init --force --policy policy.yml --provider static
python -m ai_slop_gate.cli init --force --policy policy.yml --provider eslint
python -m ai_slop_gate.cli init --force --policy policy.yml --provider terraform-plan
python -m ai_slop_gate.cli init --force --policy policy.yml --provider k8s-runtime --k8s-manifests ai_slop_gate/fixtures/k8s_test.yaml

echo "✔ All providers invoked successfully"
