#!/bin/bash
# chmod +x scripts/verify_cache.sh
# ./scripts/verify_cache.sh

echo "▶️ Verify CLI with cache"

INPUT="ai_slop_gate/fixtures/k8s_test.yaml"

python -m ai_slop_gate.cli.main run \
  --policy policy.yml \
  --provider static \
  --k8s-manifests "$INPUT" \
  --input-text "test cache input"

